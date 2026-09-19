import os
import sys
import time
import uuid
import json
import re
import threading
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS

try:
    from werkzeug.utils import secure_filename
except ImportError:
    def secure_filename(filename: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_.-]', '_', os.path.basename(filename))

ROOT_DIR = Path(__file__).resolve().parent.parent
backend_dir = str(Path(__file__).resolve().parent)
root_str = str(ROOT_DIR)

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if root_str not in sys.path:
    sys.path.insert(0, root_str)

import db
import engine_service

from engine import ResourceAllocationEngine, WorkforceVectorStore, WorkforceRAGPipeline
from projects.project_manager import ProjectAllocationManager
from employees.employee_database import EmployeeDatabase

def to_float(val, default=0.0) -> float:
    try:
        if val is None or val == "":
            return float(default)
        return float(val)
    except (ValueError, TypeError):
        return float(default)

def to_int(val, default=0) -> int:
    try:
        if val is None or val == "":
            return int(default)
        return int(val)
    except (ValueError, TypeError):
        return int(default)

def resolve_frontend_dir() -> str:
    """Dynamically determine frontend path (supports font_end or frontend) avoiding directory conflicts."""
    root = db.get_project_root()
    for name in ["font_end", "frontend"]:
        p = root / name
        if p.is_dir():
            return str(p.resolve())
    return str((root / "font_end").resolve())

FRONTEND_DIR = resolve_frontend_dir()
app = Flask(__name__, static_folder=FRONTEND_DIR)
CORS(app)

def resolve_resume_dir() -> str:
    """Dynamically determine the employees/resume directory for resume uploads."""
    root = db.get_project_root()
    resume_dir = root / "employees" / "resume"
    resume_dir.mkdir(parents=True, exist_ok=True)
    return str(resume_dir.resolve())

RESUME_FOLDER = resolve_resume_dir()
app.config["UPLOAD_FOLDER"] = RESUME_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max

def extract_text_from_file(file_path: str) -> str:
    """Extract text from PDF or plain text file with fallbacks across PDF extractors."""
    if not os.path.exists(file_path):
        return ""
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        try:
            from pypdf import PdfReader
            reader = PdfReader(file_path)
            extracted = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
            if extracted:
                return extracted
        except Exception:
            pass

        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            extracted = "\n".join((page.extract_text() or "") for page in reader.pages).strip()
            if extracted:
                return extracted
        except Exception:
            pass

        try:
            import pypdfium2 as pdfium
            pdf = pdfium.PdfDocument(file_path)
            text_parts = []
            for page in pdf:
                textpage = page.get_textpage()
                text_parts.append(textpage.get_text_range())
            return "\n".join(text_parts).strip()
        except Exception as e:
            print(f"Notice: PDF text parsing fallback warning for {file_path}: {e}")
            return ""
    else:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return ""

# Initialize DB on startup
db.init_db()
employee_db = EmployeeDatabase(db_path=db.DB_PATH)
project_manager = ProjectAllocationManager(employee_database=employee_db, project_dir=str(ROOT_DIR / "projects"))

# Singletons for Vector DB and RAG Pipeline
_vector_store = None
_rag_pipeline = None

def get_vector_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = WorkforceVectorStore()
    return _vector_store

def get_rag_pipeline():
    global _rag_pipeline
    if _rag_pipeline is None:
        v_store = get_vector_store()
        _rag_pipeline = WorkforceRAGPipeline(
            qdrant_client=v_store.client,
            collection_name=v_store.collection_name,
        )
    return _rag_pipeline

CALC_LOCK_FILE = os.path.join(str(ROOT_DIR), ".calculation_lock.json")

def set_calculation_lock(is_active: bool, message: str = ""):
    """Updates shared calculation lock state so frontend and watchers know data calculations are in progress."""
    data = {
        "is_calculating": bool(is_active),
        "message": message or ("Database records modified. Performing workforce calculations & SLA risk updates..." if is_active else ""),
        "timestamp": time.time()
    }
    try:
        with open(CALC_LOCK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass

def get_calculation_lock() -> dict:
    """Reads current calculation lock state. Automatically expires locks older than 60s."""
    if os.path.exists(CALC_LOCK_FILE):
        try:
            with open(CALC_LOCK_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if data.get("is_calculating") and (time.time() - data.get("timestamp", 0) > 60):
                data["is_calculating"] = False
                set_calculation_lock(False)
            return data
        except Exception:
            pass
    return {"is_calculating": False, "message": "", "timestamp": 0}

def sync_vector_rag_and_engine():
    """
    Invoked whenever employee records in SQLite are modified (add, edit, delete, transfer).
    Synchronizes:
      1. vector_database.py: re-indexes active employees in Qdrant collection
      2. RAG.py: updates LlamaIndex documents and contexts
      3. engine.py: recalculates SLA risk and refreshes ranked CSVs for all projects
    """
    set_calculation_lock(True, "Database modified. Synchronizing Qdrant vectors, RAG contexts, and SLA risks...")
    try:
        employees = employee_db.list_employees()
        v_store = get_vector_store()
        v_store.index_employee_records(employees)

        rag = get_rag_pipeline()
        rag.ingest_employee_documents(employees)

        refreshed = project_manager.refresh_all_projects()
        print(f"[Backend Sync] vector_database, RAG, and engine calculations completed. Refreshed {len(refreshed)} project CSVs.")
    except Exception as e:
        print(f"[Backend Sync Warning] Error during calculation sync: {e}")
    finally:
        set_calculation_lock(False)

def trigger_async_sync():
    """Run vector, RAG, and project SLA re-indexing in a background daemon thread so HTTP requests return instantaneously."""
    thread = threading.Thread(target=sync_vector_rag_and_engine, daemon=True)
    thread.start()

# ==================== STATIC ROUTES ====================
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(FRONTEND_DIR, path)

# ==================== SYSTEM STATUS ENDPOINTS ====================
@app.route("/api/system/calculation-status", methods=["GET"])
def get_system_calculation_status():
    return jsonify(get_calculation_lock())

@app.route("/api/system/reset-database", methods=["GET", "POST"])
def reset_database_endpoint():
    try:
        import seed_data
        seed_data.seed(reset=True)
        
        # Clean test/orphan PDF resumes
        root = db.get_project_root()
        resume_dir = root / "employees" / "resume"
        if resume_dir.is_dir():
            for f in resume_dir.glob("*.pdf"):
                try:
                    f.unlink()
                except Exception:
                    pass
        
        db.vacuum_database()
        trigger_async_sync()
        return jsonify({
            "success": True, 
            "message": "employee_records.db cleaned, compacted, and re-seeded with pristine workforce data."
        })
    except Exception as e:
        print(f"[Error resetting database] {e}")
        return jsonify({"error": str(e)}), 500

# ==================== PROJECT ENDPOINTS ====================
@app.route("/api/projects", methods=["GET"])
def get_projects():
    projects = db.list_projects()
    results = []
    for p in projects:
        risk_info = engine_service.evaluate_project_risk(p)
        p.update(risk_info)
        results.append(p)
    return jsonify(results)

@app.route("/api/projects", methods=["POST"])
def create_project():
    data = request.json or {}
    project_id = data.get("project_id") or f"proj_{uuid.uuid4().hex[:8]}"
    name = data.get("name") or project_id
    
    # Format required skills
    raw_skills = data.get("required_skills", [])
    if isinstance(raw_skills, str):
        required_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
    else:
        required_skills = raw_skills

    project_data = {
        "project_id": project_id,
        "name": name,
        "client_tier": int(data.get("client_tier", 3)),
        "investment": float(data.get("investment", 100000.0)),
        "roi": float(data.get("roi", 0.25)),
        "skill_criticality": float(data.get("skill_criticality", 3.0)),
        "estimated_people": int(data.get("estimated_people", 2)),
        "skill_staffing": data.get("skill_staffing", {}),
        "importance": float(data.get("importance", 3.0)),
        "required_skills": required_skills,
        "project_hours": float(data.get("project_hours", 160.0)),
        "deadline_days": int(data.get("deadline_days", 30)),
        "completion_pct": int(data.get("completion_pct", 0)),
        "status": "active",
        "description": data.get("description", "")
    }
    
    db.save_project(project_data)

    # Sync and compute initial rankings via ProjectAllocationManager
    try:
        project_manager.save_project(project_data)
    except Exception as e:
        print(f"Notice: project_manager.save_project failed: {e}")
    
    # Send notification to Manager
    db.create_notification(
        recipient_role="manager",
        title=f"Project Created: {name}",
        message=f"Project '{name}' (ID: {project_id}) has been added to ongoing projects.",
        notif_type="info",
        metadata={"project_id": project_id}
    )
    
    return jsonify({"success": True, "project": project_data}), 201

@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project_detail(project_id):
    project = db.get_project(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
        
    risk_info = engine_service.evaluate_project_risk(project)
    project.update(risk_info)
    return jsonify(project)

@app.route("/api/projects/<project_id>", methods=["PUT"])
def update_project(project_id):
    existing = db.get_project(project_id)
    if not existing:
        return jsonify({"error": "Project not found"}), 404

    data = request.json or {}
    name = data.get("name") or existing.get("name", project_id)

    raw_skills = data.get("required_skills", existing.get("required_skills", []))
    if isinstance(raw_skills, str):
        required_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
    else:
        required_skills = raw_skills

    project_data = {
        "project_id": project_id,
        "name": name,
        "client_tier": int(data.get("client_tier", existing.get("client_tier", 3))),
        "investment": float(data.get("investment", existing.get("investment", 100000.0))),
        "roi": float(data.get("roi", existing.get("roi", 0.25))),
        "skill_criticality": float(data.get("skill_criticality", existing.get("skill_criticality", 3.0))),
        "estimated_people": int(data.get("estimated_people", existing.get("estimated_people", 2))),
        "skill_staffing": data.get("skill_staffing", existing.get("skill_staffing", {})),
        "importance": float(data.get("importance", existing.get("importance", 3.0))),
        "required_skills": required_skills,
        "project_hours": float(data.get("project_hours", existing.get("project_hours", 160.0))),
        "deadline_days": int(data.get("deadline_days", existing.get("deadline_days", 30))),
        "completion_pct": int(data.get("completion_pct", existing.get("completion_pct", 0))),
        "status": data.get("status", existing.get("status", "active")),
        "description": data.get("description", existing.get("description", ""))
    }

    db.save_project(project_data)

    try:
        project_manager.save_project(project_data)
        project_manager.refresh_project(project_id)
    except Exception as e:
        print(f"Notice: project_manager.save_project update failed: {e}")

    risk_info = engine_service.evaluate_project_risk(project_data)
    project_data.update(risk_info)

    db.create_notification(
        recipient_role="manager",
        title=f"Project Updated: {name}",
        message=f"Project '{name}' scope and parameters have been updated.",
        notif_type="info",
        metadata={"project_id": project_id}
    )

    return jsonify({"success": True, "project": project_data})

@app.route("/api/projects/<project_id>", methods=["DELETE"])
def delete_project_endpoint(project_id):
    existing = db.get_project(project_id)
    if not existing:
        return jsonify({"error": "Project not found"}), 404

    name = existing.get("name", project_id)

    db.delete_project(project_id)
    try:
        project_manager.delete_project(project_id)
    except Exception as e:
        print(f"Notice: project_manager.delete_project failed: {e}")

    try:
        sync_vector_rag_and_engine()
    except Exception as e:
        print(f"Notice: sync_vector_rag_and_engine failed: {e}")

    db.create_notification(
        recipient_role="manager",
        title=f"Project Deleted: {name}",
        message=f"Project '{name}' ({project_id}) has been removed. Any assigned staff have returned to Bench.",
        notif_type="warning",
        metadata={"project_id": project_id}
    )

    return jsonify({"success": True, "message": f"Project '{name}' deleted successfully."})

@app.route("/api/projects/<project_id>/remove-employee", methods=["POST"])
def remove_employee_from_project(project_id):
    data = request.json or {}
    employee_id = data.get("employee_id")
    if not employee_id:
        return jsonify({"error": "employee_id is required"}), 400

    project = db.get_project(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404

    employee = db.get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404

    # Unassign employee back to bench
    db.update_employee_project(employee_id, None, 0.0)

    # Re-evaluate project SLA risk and save
    try:
        project_manager.refresh_project(project_id)
    except Exception as e:
        print(f"Notice: project_manager.refresh_project failed after removal: {e}")

    try:
        sync_vector_rag_and_engine()
    except Exception as e:
        print(f"Notice: sync_vector_rag_and_engine failed: {e}")

    # Notify employee
    db.create_notification(
        recipient_role="employee",
        recipient_id=employee_id,
        title=f"Unassigned from Project: {project['name']}",
        message=f"You have been unassigned from project '{project['name']}' and returned to the Bench.",
        notif_type="info",
        metadata={"employee_id": employee_id, "project_id": project_id}
    )

    # Notify manager
    db.create_notification(
        recipient_role="manager",
        title=f"Resource Removed: {employee['full_name']}",
        message=f"{employee['full_name']} has been removed from project '{project['name']}' and returned to Bench.",
        notif_type="warning",
        metadata={"employee_id": employee_id, "project_id": project_id}
    )

    return jsonify({
        "success": True,
        "message": f"{employee['full_name']} removed from project '{project['name']}' and returned to Bench.",
        "project": db.get_project(project_id),
        "employee": db.get_employee(employee_id)
    })

@app.route("/api/projects/<project_id>/recommendations", methods=["GET"])
def get_recommendations(project_id):
    try:
        recommendations = engine_service.get_recommendations_for_project(project_id)
        return jsonify(recommendations)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<project_id>/refresh", methods=["POST"])
def refresh_project_allocation(project_id):
    project = db.get_project(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    set_calculation_lock(True, f"Recalculating allocations & SLA risk for {project.get('name', project_id)}...")
    try:
        csv_path = project_manager.refresh_project(project_id)
        risk_info = engine_service.evaluate_project_risk(project)
        project.update(risk_info)
        return jsonify({
            "success": True,
            "project_id": project_id,
            "csv_path": csv_path,
            "project": project,
            "message": "Successfully refreshed project allocations and updated CSV report."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        set_calculation_lock(False)

@app.route("/api/projects/refresh-all", methods=["POST"])
def refresh_all_projects_allocation():
    set_calculation_lock(True, "Recalculating allocations, vector index & SLA risks for all projects...")
    print("\n" + "=" * 65)
    print("   [MANAGER ACTION] REFRESH ALL ALLOCATIONS TRIGGERED")
    print("=" * 65)
    try:
        db_projects = db.list_projects()
        for p in db_projects:
            try:
                project_manager.save_project(p)
            except Exception:
                pass

        # 1. Load active employees
        employees = employee_db.list_employees()
        print(f"[Step 1] Loading {len(employees)} employee profiles from database...")

        # 2. Re-index active workforce in Qdrant Vector Store
        print(f"[Step 2] Re-indexing {len(employees)} profiles in Qdrant vector database (vector_database.py)...")
        v_store = get_vector_store()
        indexed_count = v_store.index_employee_records(employees)
        print(f"[Step 2] Successfully indexed {indexed_count} profiles in Qdrant collection '{v_store.collection_name}'.")

        # 3. Ingest documents into RAG layer
        print(f"[Step 3] Updating LlamaIndex RAG layer with employee documents (RAG.py)...")
        rag = get_rag_pipeline()
        rag.ingest_employee_documents(employees)

        # 4. Recalculate SLA risks, project weights, and regenerate ranked candidate CSVs
        print(f"[Step 4] Recalculating SLA risks and regenerating ranked candidate CSVs (engine.py & project_manager.py)...")
        refreshed = project_manager.refresh_all_projects()
        for f in refreshed:
            print(f"  -> Regenerated ranked CSV: {os.path.basename(f)}")

        # 5. Touch employee records to notify database watcher
        try:
            with db.get_connection() as conn:
                conn.execute("UPDATE employees SET updated_at = CURRENT_TIMESTAMP WHERE employee_id = (SELECT employee_id FROM employees LIMIT 1)")
                conn.commit()
        except Exception:
            pass

        print(f"[Calculations Completed] All {len(refreshed)} ongoing project allocations refreshed.")
        print("=" * 65 + "\n")

        return jsonify({
            "success": True,
            "refreshed_count": len(refreshed),
            "csv_files": [os.path.basename(f) for f in refreshed],
            "message": f"Full calculation completed: synchronized vector database, RAG context, and refreshed allocations for {len(refreshed)} projects."
        })
    except Exception as e:
        print(f"[Error during refresh-all calculations] {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        set_calculation_lock(False)

@app.route("/api/projects/<project_id>/ranked-csv", methods=["GET"])
def get_project_ranked_csv(project_id):
    project = db.get_project(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
    try:
        rows = project_manager.load_ranked_csv(project_id)
        csv_path = project_manager.get_ranked_csv_path(project_id)
        return jsonify({
            "project_id": project_id,
            "project_name": project.get("name", project_id),
            "csv_file": csv_path.name if csv_path else "",
            "rows": rows,
            "count": len(rows),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/projects/<project_id>/download-csv", methods=["GET"])
def download_project_ranked_csv(project_id):
    csv_path = project_manager.get_ranked_csv_path(project_id)
    if not csv_path.exists():
        project = db.get_project(project_id)
        if project:
            try:
                project_manager.save_project(project)
            except Exception:
                pass
        else:
            try:
                project_manager.refresh_project(project_id)
            except Exception:
                pass
    if not csv_path.exists():
        return jsonify({"error": "Ranked CSV report not found for this project"}), 404
    return send_file(
        str(csv_path),
        mimetype="text/csv",
        as_attachment=True,
        download_name=csv_path.name
    )

@app.route("/api/projects/<project_id>/assign", methods=["POST"])
def assign_employee_to_project(project_id):
    data = request.json or {}
    employee_id = data.get("employee_id")
    if not employee_id:
        return jsonify({"error": "employee_id is required"}), 400
        
    project = db.get_project(project_id)
    if not project:
        return jsonify({"error": "Project not found"}), 404
        
    employee = db.get_employee(employee_id)
    if not employee:
        return jsonify({"error": "Employee not found"}), 404
        
    risk_info = engine_service.evaluate_project_risk(project)
    
    # Case 1: Employee is NOT currently working on any project (Bench)
    if not employee.get("current_project"):
        db.update_employee_project(employee_id, project_id, risk_info["project_weight"])
        sync_vector_rag_and_engine()
        
        # Notify manager
        db.create_notification(
            recipient_role="manager",
            title=f"Resource Assigned: {employee['full_name']}",
            message=f"{employee['full_name']} has been directly assigned to project '{project['name']}'.",
            notif_type="transfer_accepted",
            metadata={"employee_id": employee_id, "project_id": project_id}
        )
        return jsonify({
            "status": "assigned_directly",
            "message": f"{employee['full_name']} was available on bench and has been assigned to '{project['name']}'.",
            "employee": db.get_employee(employee_id)
        })
        
    # Case 2: Employee IS currently on another project -> initiate transfer offer workflow
    offer_id = f"offer_{uuid.uuid4().hex[:8]}"
    db.create_transfer_offer(
        offer_id=offer_id,
        employee_id=employee_id,
        from_project=employee["current_project"],
        to_project=project_id
    )
    
    # Notify employee of the transfer offer
    db.create_notification(
        recipient_role="employee",
        recipient_id=employee_id,
        title=f"Project Transfer Offer: {project['name']}",
        message=f"You have been nominated to join project '{project['name']}'. Please review the project details to accept or stick with your current assignment.",
        notif_type="transfer_offer",
        metadata={"offer_id": offer_id, "to_project": project_id, "from_project": employee["current_project"]}
    )
    
    return jsonify({
        "status": "transfer_offer_sent",
        "message": f"{employee['full_name']} is currently on '{employee['current_project']}'. A transfer offer has been sent to them for confirmation.",
        "offer_id": offer_id
    })

# ==================== HR REQUISITION ENDPOINTS ====================
@app.route("/api/hr/requests", methods=["GET"])
def get_hr_requests():
    status = request.args.get("status")
    requests = db.list_hr_requests(status=status)
    return jsonify(requests)

@app.route("/api/hr/requests", methods=["POST"])
def create_hr_request():
    data = request.json or {}
    role_title = data.get("role_title")
    if not role_title:
        return jsonify({"error": "role_title is required"}), 400
        
    request_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"
    req_data = {
        "request_id": request_id,
        "project_id": data.get("project_id"),
        "role_title": role_title,
        "required_skills": data.get("required_skills", ""),
        "urgency": data.get("urgency", "Medium"),
        "description": data.get("description", "")
    }
    db.create_hr_request(req_data)
    
    # Notify HR
    db.create_notification(
        recipient_role="hr",
        title=f"New Hiring Request: {role_title}",
        message=f"Project Manager requested new employee for project '{data.get('project_id', 'General')}': {role_title}.",
        notif_type="hr_request",
        metadata=req_data
    )
    
    # Notify Manager of submission
    db.create_notification(
        recipient_role="manager",
        title="Hiring Requisition Submitted",
        message=f"Requisition {request_id} for '{role_title}' has been submitted to HR.",
        notif_type="info"
    )
    
    return jsonify({"success": True, "request": req_data}), 201

@app.route("/api/hr/requests/<request_id>", methods=["PUT"])
def update_hr_request(request_id):
    data = request.json or {}
    status = data.get("status", "fulfilled")
    existing = db.get_hr_request(request_id)
    if not existing:
        return jsonify({"error": "Hiring request not found"}), 404
        
    db.update_hr_request_status(request_id, status)
    
    # Notify manager that HR fulfilled/updated the requisition
    db.create_notification(
        recipient_role="manager",
        title=f"Hiring Request {status.title()}: {existing.get('role_title', request_id)}",
        message=f"Requisition {request_id} for '{existing.get('role_title')}' was marked as {status} by HR.",
        notif_type="hr_fulfilled",
        metadata={"request_id": request_id, "status": status}
    )
    
    return jsonify({"success": True, "request_id": request_id, "status": status})

@app.route("/api/hr/requests/<request_id>", methods=["DELETE"])
def delete_hr_request(request_id):
    existing = db.get_hr_request(request_id)
    if not existing:
        return jsonify({"error": "Hiring request not found"}), 404
    db.delete_hr_request(request_id)
    return jsonify({"success": True, "deleted": request_id})

# ==================== TALENT DIRECTORY (HR) ====================
@app.route("/api/employees", methods=["GET"])
def get_all_employees():
    employees = db.list_employees()
    return jsonify(employees)

@app.route("/api/employees", methods=["POST"])
def add_employee():
    try:
        fulfills_request_id = None
        # Supports both multipart form-data (with file upload) and JSON
        if request.content_type and "multipart/form-data" in request.content_type:
            form = request.form
            fulfills_request_id = form.get("fulfills_request_id") or form.get("requisition_id")
            employee_id = form.get("employee_id") or f"EMP-{uuid.uuid4().hex[:6].upper()}"
            full_name = form.get("full_name")
            if not full_name:
                return jsonify({"error": "full_name is required"}), 400
                
            resume_path = None
            resume_text = ""
            resume_file = request.files.get("resume")
            if resume_file and resume_file.filename:
                safe_name = secure_filename(resume_file.filename)
                filename = f"{employee_id}_{safe_name}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                resume_file.save(save_path)
                resume_path = save_path
                resume_text = extract_text_from_file(save_path)
                
            emp_data = {
                "employee_id": employee_id,
                "full_name": full_name,
                "email": form.get("email", ""),
                "phone": form.get("phone", ""),
                "date_of_birth": form.get("date_of_birth", ""),
                "job_title": form.get("job_title", "Software Engineer"),
                "department": form.get("department", "Engineering"),
                "location": form.get("location", ""),
                "years_experience": to_float(form.get("years_experience"), 1.0),
                "domain_knowledge": form.get("domain_knowledge", ""),
                "seniority_tier": to_int(form.get("seniority_tier"), 1),
                "is_lead": 1 if form.get("is_lead") in ["1", "true", "True", True, 1] else 0,
                "current_project": form.get("current_project") or None,
                "current_project_weight": to_float(form.get("current_project_weight"), 0.0),
                "project_changes_last_30_days": 0,
                "days_on_current_project": 0,
                "availability_hours": to_float(form.get("availability_hours"), 40.0),
                "ability_score": to_float(form.get("ability_score"), 0.8),
                "utilization": to_float(form.get("utilization"), 0.0),
                "resume_path": resume_path,
                "resume_status": "processed" if resume_path else "no_resume",
                "resume_text": resume_text,
            }
        else:
            data = request.json or {}
            fulfills_request_id = data.get("fulfills_request_id") or data.get("requisition_id")
            employee_id = data.get("employee_id") or f"EMP-{uuid.uuid4().hex[:6].upper()}"
            full_name = data.get("full_name")
            if not full_name:
                return jsonify({"error": "full_name is required"}), 400
                
            emp_data = {
                "employee_id": employee_id,
                "full_name": full_name,
                "email": data.get("email", ""),
                "phone": data.get("phone", ""),
                "date_of_birth": data.get("date_of_birth", ""),
                "job_title": data.get("job_title", "Software Engineer"),
                "department": data.get("department", "Engineering"),
                "location": data.get("location", ""),
                "years_experience": to_float(data.get("years_experience"), 1.0),
                "domain_knowledge": data.get("domain_knowledge", ""),
                "seniority_tier": to_int(data.get("seniority_tier"), 1),
                "is_lead": to_int(data.get("is_lead"), 0),
                "current_project": data.get("current_project") or None,
                "current_project_weight": to_float(data.get("current_project_weight"), 0.0),
                "project_changes_last_30_days": 0,
                "days_on_current_project": 0,
                "availability_hours": to_float(data.get("availability_hours"), 40.0),
                "ability_score": to_float(data.get("ability_score"), 0.8),
                "utilization": to_float(data.get("utilization"), 0.0),
                "resume_path": None,
                "resume_status": "no_resume",
                "resume_text": data.get("resume_text", ""),
            }

        # Check if this fulfills an HR hiring requisition
        if fulfills_request_id and str(fulfills_request_id).lower().strip() in ["", "none", "null", "undefined"]:
            fulfills_request_id = None

        # Auto-match if not explicitly given: check pending requisitions matching the role title
        if not fulfills_request_id:
            emp_title = (emp_data.get("job_title") or "").strip().lower()
            if emp_title:
                pending_reqs = db.list_hr_requests(status="pending")
                for pr in pending_reqs:
                    pr_title = (pr.get("role_title") or "").strip().lower()
                    if pr_title and (pr_title == emp_title or pr_title in emp_title or emp_title in pr_title):
                        fulfills_request_id = pr["request_id"]
                        break

        fulfilled_req = None
        if fulfills_request_id:
            fulfilled_req = db.get_hr_request(fulfills_request_id)
            if fulfilled_req:
                db.update_hr_request_status(fulfills_request_id, "fulfilled")
                # If target project was specified in requisition and employee has no project assigned, assign to project
                target_pid = fulfilled_req.get("project_id")
                if target_pid and target_pid not in ["General", "General Workforce", "None", None, ""] and not emp_data.get("current_project"):
                    target_proj = db.get_project(target_pid)
                    if target_proj:
                        risk_info = engine_service.evaluate_project_risk(target_proj)
                        emp_data["current_project"] = target_pid
                        emp_data["current_project_weight"] = risk_info.get("project_weight", 0.85)
                        emp_data["utilization"] = 0.85

        db.upsert_employee(emp_data)
        trigger_async_sync()
        
        # Notify Manager and HR that new employee joined workforce
        if fulfilled_req:
            db.create_notification(
                recipient_role="manager",
                title=f"Hiring Requisition Fulfilled: {fulfilled_req.get('role_title')}",
                message=f"Requisition {fulfills_request_id} has been fulfilled! HR onboarded {emp_data['full_name']} ({emp_data['job_title']}) to address '{fulfilled_req.get('role_title')}' for project '{fulfilled_req.get('project_id', 'General')}'.",
                notif_type="hr_fulfilled",
                metadata={"request_id": fulfills_request_id, "employee_id": employee_id}
            )
        else:
            db.create_notification(
                recipient_role="manager",
                title=f"New Talent Added: {emp_data['full_name']}",
                message=f"HR onboarded {emp_data['full_name']} ({emp_data['job_title']}, {emp_data['department']}) into workforce records.",
                notif_type="hr_fulfilled"
            )
        
        return jsonify({
            "success": True, 
            "employee": db.get_employee(employee_id),
            "fulfilled_requisition_id": fulfills_request_id if fulfilled_req else None
        }), 201
    except Exception as e:
        print(f"[Error adding employee] {e}")
        return jsonify({"error": f"Failed to add employee: {e}"}), 500

@app.route("/api/employees/<employee_id>", methods=["GET"])
def get_employee_detail(employee_id):
    clean_id = (employee_id or "").strip()
    emp = db.get_employee(clean_id)
    if not emp:
        return jsonify({"error": f"Employee {clean_id} not found"}), 404
    return jsonify(emp)

@app.route("/api/employees/<employee_id>", methods=["PUT"])
def update_employee(employee_id):
    try:
        clean_id = (employee_id or "").strip()
        existing = db.get_employee(clean_id)
        if not existing:
            return jsonify({"error": f"Employee {clean_id} not found"}), 404
            
        data = {}
        if request.content_type and "multipart/form-data" in request.content_type:
            data = request.form.to_dict()
            resume_file = request.files.get("resume")
            if resume_file and resume_file.filename:
                safe_name = secure_filename(resume_file.filename)
                filename = f"{clean_id}_{safe_name}"
                save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
                resume_file.save(save_path)
                existing["resume_path"] = save_path
                existing["resume_status"] = "processed"
                existing["resume_text"] = extract_text_from_file(save_path)
        else:
            data = request.json or {}

        updated_data = dict(existing)
        
        for key in ["full_name", "email", "phone", "date_of_birth", "job_title", "department", 
                    "location", "years_experience", "domain_knowledge", "seniority_tier", 
                    "is_lead", "current_project", "current_project_weight", "availability_hours", 
                    "ability_score", "utilization", "resume_text"]:
            if key in data:
                val = data[key]
                if key in ["years_experience", "current_project_weight", "availability_hours", "ability_score", "utilization"]:
                    val = to_float(val, existing.get(key, 0.0))
                elif key in ["seniority_tier", "is_lead"]:
                    val = to_int(val, existing.get(key, 1 if key == "seniority_tier" else 0))
                updated_data[key] = val
                
        db.upsert_employee(updated_data)
        trigger_async_sync()
        return jsonify({"success": True, "employee": db.get_employee(clean_id)})
    except Exception as e:
        print(f"[Error updating employee] {e}")
        return jsonify({"error": f"Failed to update employee: {e}"}), 500

@app.route("/api/employees/<employee_id>", methods=["DELETE"])
def delete_employee_record(employee_id):
    try:
        clean_id = (employee_id or "").strip()
        existing = db.get_employee(clean_id)
        if not existing:
            return jsonify({"error": f"Employee {clean_id} not found"}), 404

        success = db.delete_employee(clean_id)
        if not success:
            return jsonify({"error": f"Employee {clean_id} not found"}), 404

        trigger_async_sync()
        return jsonify({"success": True, "message": f"Employee {clean_id} deleted and calculations updated."})
    except Exception as e:
        print(f"[Error deleting employee] {e}")
        return jsonify({"error": f"Failed to delete employee: {e}"}), 500

# ==================== EMPLOYEE PORTAL ENDPOINTS ====================
@app.route("/api/employees/<employee_id>/dashboard", methods=["GET"])
def get_employee_dashboard(employee_id):
    emp = db.get_employee(employee_id)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
        
    current_project = None
    project_members = []
    if emp.get("current_project"):
        current_project = db.get_project(emp["current_project"])
        if current_project:
            project_members = [m for m in current_project.get("assigned_employees", []) if m["employee_id"] != employee_id]
            
    # Check for pending transfer offers
    pending_offer = db.get_pending_transfer_offer(employee_id)
    offer_details = None
    if pending_offer:
        new_project = db.get_project(pending_offer["to_project"])
        offer_details = {
            "offer_id": pending_offer["offer_id"],
            "from_project_id": pending_offer["from_project"],
            "to_project_id": pending_offer["to_project"],
            "project_name": new_project.get("name") if new_project else pending_offer["to_project"],
            "description": new_project.get("description", "") if new_project else "",
            "required_skills": new_project.get("required_skills", []) if new_project else [],
            "project_hours": new_project.get("project_hours", 0) if new_project else 0,
            "deadline_days": new_project.get("deadline_days", 0) if new_project else 0,
            "created_at": pending_offer["created_at"],
            "is_currently_working": bool(emp.get("current_project"))
        }
        
    return jsonify({
        "employee": emp,
        "current_project": current_project,
        "project_members": project_members,
        "pending_offer": offer_details
    })

@app.route("/api/employees/<employee_id>/transfer-response", methods=["POST"])
def handle_transfer_response(employee_id):
    emp = db.get_employee(employee_id)
    if not emp:
        return jsonify({"error": "Employee not found"}), 404
        
    data = request.json or {}
    offer_id = data.get("offer_id")
    action = data.get("action")  # 'accept' or 'decline'
    reason = data.get("reason", "").strip()
    
    pending_offer = db.get_pending_transfer_offer(employee_id)
    if not pending_offer or (offer_id and pending_offer["offer_id"] != offer_id):
        return jsonify({"error": "No matching pending transfer offer found."}), 400
        
    to_project_id = pending_offer["to_project"]
    to_project = db.get_project(to_project_id)
    project_name = to_project.get("name") if to_project else to_project_id
    
    if action == "accept":
        # Calculate new project weight
        risk_info = engine_service.evaluate_project_risk(to_project) if to_project else {"project_weight": 50.0}
        db.update_employee_project(employee_id, to_project_id, risk_info.get("project_weight", 50.0))
        sync_vector_rag_and_engine()
        db.resolve_transfer_offer(pending_offer["offer_id"], "accepted", decline_reason="")
        
        # Send confirmation notification to Manager
        db.create_notification(
            recipient_role="manager",
            title=f"Transfer Accepted: {emp['full_name']}",
            message=f"{emp['full_name']} has accepted the assignment and joined project '{project_name}'. Database records updated.",
            notif_type="transfer_accepted",
            metadata={"employee_id": employee_id, "project_id": to_project_id}
        )
        
        return jsonify({
            "success": True,
            "status": "accepted",
            "message": f"You have successfully joined '{project_name}'!",
            "employee": db.get_employee(employee_id)
        })
        
    elif action == "decline":
        # Decline must provide a valid reason
        if not reason:
            return jsonify({"error": "A valid reason for declining must be provided."}), 400
            
        db.resolve_transfer_offer(pending_offer["offer_id"], "declined", decline_reason=reason)
        
        # Send notification to Manager with the specific reason
        db.create_notification(
            recipient_role="manager",
            title=f"Transfer Declined: {emp['full_name']}",
            message=f"{emp['full_name']} declined the transfer to '{project_name}'. Reason: \"{reason}\". You may choose another employee.",
            notif_type="transfer_declined",
            metadata={"employee_id": employee_id, "project_id": to_project_id, "decline_reason": reason}
        )
        
        return jsonify({
            "success": True,
            "status": "declined",
            "message": "You chose to stick with your current project. Your reason has been submitted to the manager.",
            "employee": db.get_employee(employee_id)
        })
        
    else:
        return jsonify({"error": "Invalid action. Must be 'accept' or 'decline'."}), 400

# ==================== NOTIFICATION ENDPOINTS ====================
@app.route("/api/notifications", methods=["GET"])
def get_notifications():
    role = request.args.get("role")
    emp_id = request.args.get("employee_id")
    notifs = db.list_notifications(recipient_role=role, recipient_id=emp_id)
    return jsonify(notifs)

@app.route("/api/notifications/mark-read", methods=["POST"])
def mark_read():
    data = request.json or {}
    role = data.get("role", "all")
    db.mark_notifications_read(role)
    return jsonify({"success": True})

@app.route("/api/notifications/<int:notif_id>/dismiss", methods=["POST", "DELETE"])
@app.route("/api/notifications/<int:notif_id>", methods=["DELETE"])
def dismiss_notification(notif_id):
    success = db.dismiss_notification(notif_id)
    if not success:
        return jsonify({"error": "Notification not found or already dismissed"}), 404
    return jsonify({"success": True, "message": "Notification dismissed successfully."})

# ==================== AUTHENTICATION ENDPOINTS ====================
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    role = data.get("role")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    user = db.authenticate_user(username, password, role=role)
    if not user:
        return jsonify({"error": "Invalid username or password for the specified role."}), 401

    token = f"tok_{uuid.uuid4().hex}"
    return jsonify({
        "success": True,
        "token": token,
        "user": {
            "username": user["username"],
            "role": user["role"],
            "full_name": user["full_name"],
            "employee_id": user.get("employee_id")
        }
    })

@app.route("/api/auth/logout", methods=["POST"])
def logout():
    return jsonify({"success": True, "message": "Logged out successfully."})

@app.route("/api/auth/me", methods=["GET"])
def current_user():
    # Helper to check session if token passed
    token = request.headers.get("Authorization")
    return jsonify({"authenticated": True})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
