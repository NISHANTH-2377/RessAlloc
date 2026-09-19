"""
Resource Allocation Engine (RessAlloc) - Hugging Face Spaces Entrypoint
Powered by Gradio Blocks, SQLite, Qdrant Semantic Matching & Deterministic Allocation Engine.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    pd = None
    HAS_PANDAS = False

# Ensure backend and root are on sys.path
ROOT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = ROOT_DIR / "backend"
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

try:
    import gradio as gr
except ImportError:
    import subprocess
    print("\n" + "=" * 70)
    print("  [NOTICE] 'gradio' is not installed in this Python environment.")
    print(f"  Active Python: {sys.executable}")
    print("  Attempting to install 'gradio' automatically...")
    print("=" * 70 + "\n")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "gradio"])
        import gradio as gr
        print("\n✓ 'gradio' successfully installed! Proceeding to launch...\n")
    except Exception as e:
        print(f"\n[Error] Auto-install failed: {e}")
        print("\nPlease run this command in your terminal:")
        print(f'    "{sys.executable}" -m pip install gradio')
        print("=" * 70 + "\n")
        sys.exit(1)
import backend.db as db
import backend.engine_service as engine_service
import backend.seed_data as seed_data
from engine import ResourceAllocationEngine
import clean_cache

# Initialize database with clean seed data if empty
try:
    existing_emps = db.list_employees()
    if len(existing_emps) == 0:
        print("[Startup] Initializing empty database with seed workforce records...")
        seed_data.seed(reset=False)
except Exception as e:
    print(f"[Startup Warning] Error verifying database initialization: {e}")

# ==================== HELPER FUNCTIONS ====================

def make_table_data(rows: List[Dict[str, Any]], columns: List[str]):
    """Returns pandas DataFrame if available, otherwise native list of lists for Gradio."""
    if HAS_PANDAS and pd is not None:
        if not rows:
            return pd.DataFrame(columns=columns)
        return pd.DataFrame(rows)
    if not rows:
        return []
    return [[r.get(c, "") for c in columns] for r in rows]

def get_live_metrics_html() -> str:
    try:
        emps = db.list_employees()
        projs = db.list_projects()
        reqs = db.list_hr_requests(status="pending")
        
        total_emps = len(emps)
        bench_workers = len([e for e in emps if not e.get("current_project")])
        total_projs = len(projs)
        
        high_risk_projs = 0
        for p in projs:
            risk = engine_service.evaluate_project_risk(p)
            if risk.get("risk_level") == "High":
                high_risk_projs += 1
                
        open_reqs = len(reqs)
        
        return f"""
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:1rem; margin-bottom:1.5rem;">
            <div style="background:rgba(37,99,235,0.08); border:1px solid rgba(37,99,235,0.25); border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:0.8rem; color:#6b7280; font-weight:600; text-transform:uppercase;">Total Workforce</div>
                <div style="font-size:1.8rem; font-weight:800; color:#2563eb;">{total_emps}</div>
                <div style="font-size:0.75rem; color:#6b7280;">Employees on Record</div>
            </div>
            <div style="background:rgba(160,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:0.8rem; color:#6b7280; font-weight:600; text-transform:uppercase;">Bench (Available)</div>
                <div style="font-size:1.8rem; font-weight:800; color:#10b981;">{bench_workers}</div>
                <div style="font-size:0.75rem; color:#6b7280;">Ready for Assignment</div>
            </div>
            <div style="background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.25); border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:0.8rem; color:#6b7280; font-weight:600; text-transform:uppercase;">Active Projects</div>
                <div style="font-size:1.8rem; font-weight:800; color:#6366f1;">{total_projs}</div>
                <div style="font-size:0.75rem; color:#6b7280;">Monitored by Engine</div>
            </div>
            <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.25); border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:0.8rem; color:#6b7280; font-weight:600; text-transform:uppercase;">High SLA Risk</div>
                <div style="font-size:1.8rem; font-weight:800; color:#ef4444;">{high_risk_projs}</div>
                <div style="font-size:0.75rem; color:#6b7280;">Projects Understaffed</div>
            </div>
            <div style="background:rgba(168,85,247,0.08); border:1px solid rgba(168,85,247,0.25); border-radius:10px; padding:1rem; text-align:center;">
                <div style="font-size:0.8rem; color:#6b7280; font-weight:600; text-transform:uppercase;">Open HR Requisitions</div>
                <div style="font-size:1.8rem; font-weight:800; color:#a855f7;">{open_reqs}</div>
                <div style="font-size:0.75rem; color:#6b7280;">Manager Requests to HR</div>
            </div>
        </div>
        """
    except Exception as e:
        return f"<div style='color:red;'>Failed to load metrics: {e}</div>"

def get_projects_dataframe():
    projs = db.list_projects()
    rows = []
    for p in projs:
        risk = engine_service.evaluate_project_risk(p)
        skills = ", ".join(p.get("required_skills", []))
        rows.append({
            "Project ID": p["project_id"],
            "Name": p.get("name", p["project_id"]),
            "Client Tier": p.get("client_tier", 3),
            "Investment ($)": f"{float(p.get('investment', 0)):,.0f}",
            "Required Skills": skills,
            "Deadline (Days)": p.get("deadline_days", 30),
            "SLA Risk (%)": f"{risk['sla_risk']}%",
            "Risk Level": risk["risk_level"],
            "Project Weight": risk["project_weight"],
            "Assigned Team": risk["assigned_count"],
        })
    cols = ["Project ID", "Name", "Client Tier", "Investment ($)", "Required Skills", "Deadline (Days)", "SLA Risk (%)", "Risk Level", "Project Weight", "Assigned Team"]
    return make_table_data(rows, cols)

def get_employees_dataframe(search_term: str = ""):
    emps = db.list_employees()
    q = (search_term or "").strip().lower()
    rows = []
    for e in emps:
        full_str = f"{e['full_name']} {e.get('job_title', '')} {e.get('department', '')} {e.get('domain_knowledge', '')}".lower()
        if q and q not in full_str:
            continue
        skills = ", ".join(e.get("skills", []))
        status = f"On {e['current_project']}" if e.get("current_project") else "Bench (Available)"
        rows.append({
            "ID": e["employee_id"],
            "Name": e["full_name"],
            "Job Title": e.get("job_title", "Engineer"),
            "Department": e.get("department", "Engineering"),
            "Status": status,
            "Experience (Yrs)": e.get("years_experience", 1.0),
            "Tier": e.get("seniority_tier", 1),
            "Skills": skills or e.get("domain_knowledge", ""),
            "Ability Score": e.get("ability_score", 0.8),
        })
    cols = ["ID", "Name", "Job Title", "Department", "Status", "Experience (Yrs)", "Tier", "Skills", "Ability Score"]
    return make_table_data(rows, cols)

def get_requisitions_dataframe():
    reqs = db.list_hr_requests(status="pending")
    rows = []
    for r in reqs:
        rows.append({
            "Req ID": r["request_id"],
            "Role Title": r["role_title"],
            "Target Project": r.get("project_id", "General"),
            "Urgency": r.get("urgency", "Medium"),
            "Required Skills": r.get("required_skills", ""),
            "Description": r.get("description", ""),
            "Status": r.get("status", "pending")
        })
    cols = ["Req ID", "Role Title", "Target Project", "Urgency", "Required Skills", "Description", "Status"]
    return make_table_data(rows, cols)

def get_project_choices() -> List[str]:
    projs = db.list_projects()
    return [p["project_id"] for p in projs]

def get_requisition_choices() -> List[str]:
    reqs = db.list_hr_requests(status="pending")
    choices = ["None (Independent Hire)"]
    for r in reqs:
        choices.append(f"{r['request_id']}: {r['role_title']} [{r.get('project_id', 'General')}]")
    return choices

def get_employee_choices() -> List[str]:
    emps = db.list_employees()
    return [f"{e['employee_id']} - {e['full_name']} ({'On ' + e['current_project'] if e.get('current_project') else 'Bench'})" for e in emps]

# ==================== ENGINE & ACTIONS ====================

def run_allocation_engine(project_id: str):
    if not project_id:
        return "Please select a project.", pd.DataFrame(), gr.update(choices=[]), ""
    
    project = db.get_project(project_id)
    if not project:
        return f"Project '{project_id}' not found.", pd.DataFrame(), gr.update(choices=[]), ""

    try:
        report = engine_service.get_recommendations_for_project(project_id)
        proj_risk = report["project_risk"]
        summary = report["summary"]
        candidates = report["ranked_candidates"]

        status_html = f"""
        <div style="background:rgba(37,99,235,0.08); border-left:4px solid #2563eb; padding:1rem; border-radius:6px; margin-bottom:1rem;">
            <div style="font-weight:700; font-size:1.1rem; color:#1e3a8a; margin-bottom:0.3rem;">
                Recommendation: {summary['status'].replace('_', ' ').title()}
            </div>
            <p style="margin:0 0 0.5rem 0; color:#374151;">{summary['message']}</p>
            <div style="display:flex; gap:1.5rem; font-size:0.85rem; color:#4b5563;">
                <span><strong>SLA Risk:</strong> {proj_risk['sla_risk']}% ({proj_risk['risk_level']})</span>
                <span><strong>Project Weight:</strong> {proj_risk['project_weight']}</span>
                <span><strong>Slack:</strong> {summary['slack_hours']} hrs</span>
                <span><strong>Assigned Workers:</strong> {proj_risk['assigned_count']}</span>
            </div>
        </div>
        """

        rows = []
        candidate_choices = []
        for c in candidates:
            cand_status = f"On {c['current_project']}" if c.get("current_project") else "Bench (Available)"
            rows.append({
                "Rank": c["rank"],
                "ID": c["employee_id"],
                "Name": c["name"],
                "Status": cand_status,
                "Semantic Fit": f"{round(c['semantic_score'] * 100, 1)}%",
                "Score": round(c["final_score"], 2),
                "Effective Capacity": f"{c['effective_capacity']} hrs",
                "Days on Project": c["days_on_current_project"],
                "Action Type": c["recommendation_action"].replace('_', ' ').title()
            })
            candidate_choices.append(f"{c['employee_id']} - {c['name']} ({cand_status})")

        cols = ["Rank", "ID", "Name", "Status", "Semantic Fit", "Score", "Effective Capacity", "Days on Project", "Action Type"]
        df = make_table_data(rows, cols)
        return status_html, df, gr.update(choices=candidate_choices, value=candidate_choices[0] if candidate_choices else None), f"Analysis complete: {len(candidates)} candidates evaluated."
    except Exception as e:
        cols = ["Rank", "ID", "Name", "Status", "Semantic Fit", "Score", "Effective Capacity", "Days on Project", "Action Type"]
        return f"<div style='color:red;'>Engine calculation failed: {e}</div>", make_table_data([], cols), gr.update(choices=[]), str(e)

def assign_candidate_to_project(project_id: str, candidate_selection: str):
    if not project_id or not candidate_selection:
        return "Please select both a project and a candidate.", get_live_metrics_html(), get_projects_dataframe()
    
    emp_id = candidate_selection.split(" - ")[0].strip()
    project = db.get_project(project_id)
    employee = db.get_employee(emp_id)
    
    if not project or not employee:
        return "Project or Employee record not found.", get_live_metrics_html(), get_projects_dataframe()
    
    risk_info = engine_service.evaluate_project_risk(project)

    # Case 1: Bench employee -> assign directly
    if not employee.get("current_project"):
        db.update_employee_project(emp_id, project_id, risk_info["project_weight"])
        db.create_notification(
            recipient_role="manager",
            title=f"Resource Assigned: {employee['full_name']}",
            message=f"{employee['full_name']} was available on bench and has been assigned to '{project['name']}'.",
            notif_type="transfer_accepted",
            metadata={"employee_id": emp_id, "project_id": project_id}
        )
        msg = f"✓ Success: {employee['full_name']} (Bench) was assigned directly to project '{project['name']}'!"
    else:
        # Case 2: Employee on another project -> initiate transfer offer workflow
        import uuid
        offer_id = f"offer_{uuid.uuid4().hex[:8]}"
        db.create_transfer_offer(offer_id, emp_id, employee["current_project"], project_id)
        db.create_notification(
            recipient_role="employee",
            recipient_id=emp_id,
            title=f"Project Transfer Offer: {project['name']}",
            message=f"You have been nominated to transfer to '{project['name']}'. Please review in Employee portal.",
            notif_type="transfer_offer",
            metadata={"offer_id": offer_id, "to_project": project_id, "from_project": employee["current_project"]}
        )
        msg = f"✓ Transfer Offer sent: {employee['full_name']} is currently on '{employee['current_project']}'. A transfer offer has been sent to them for review."

    return msg, get_live_metrics_html(), get_projects_dataframe()

def create_hr_requisition_action(project_id: str, role_title: str, required_skills: str, urgency: str, description: str):
    if not role_title:
        return "Role title is required to raise an HR requisition.", get_requisitions_dataframe(), get_live_metrics_html()
    
    import uuid
    request_id = f"REQ-{uuid.uuid4().hex[:6].upper()}"
    req_data = {
        "request_id": request_id,
        "project_id": project_id or "General",
        "role_title": role_title,
        "required_skills": required_skills,
        "urgency": urgency or "Medium",
        "description": description or ""
    }
    db.create_hr_request(req_data)
    db.create_notification(
        recipient_role="hr",
        title=f"New Hiring Request: {role_title}",
        message=f"Manager requested talent for '{project_id}': {role_title}.",
        notif_type="hr_request",
        metadata=req_data
    )
    return f"✓ Hiring requisition {request_id} for '{role_title}' submitted to HR!", get_requisitions_dataframe(), get_live_metrics_html()

def fulfill_requisition_action(req_id: str):
    if not req_id:
        return "No requisition selected.", get_requisitions_dataframe(), get_live_metrics_html()
    
    req = db.get_hr_request(req_id)
    if not req:
        return f"Requisition '{req_id}' not found.", get_requisitions_dataframe(), get_live_metrics_html()
    
    db.update_hr_request_status(req_id, "fulfilled")
    db.create_notification(
        recipient_role="manager",
        title=f"Hiring Requisition Fulfilled: {req.get('role_title')}",
        message=f"Requisition {req_id} ({req.get('role_title')}) was marked as fulfilled.",
        notif_type="hr_fulfilled",
        metadata={"request_id": req_id}
    )
    return f"✓ Requisition {req_id} marked as fulfilled and cleared from active hiring list!", get_requisitions_dataframe(), get_live_metrics_html()

def onboard_new_employee_action(full_name: str, job_title: str, department: str, years_exp: float, seniority_tier: int, skills: str, resume_file, fulfills_req: str):
    if not full_name or not job_title:
        return "Full Name and Job Title are required.", get_employees_dataframe(), get_requisitions_dataframe(), get_live_metrics_html()
    
    import uuid
    employee_id = f"EMP-{uuid.uuid4().hex[:6].upper()}"
    
    # Extract resume text if PDF provided
    resume_text = ""
    resume_path = None
    if resume_file is not None:
        try:
            import pypdf
            reader = pypdf.PdfReader(resume_file.name)
            for page in reader.pages:
                t = page.extract_text()
                if t:
                    resume_text += t + "\n"
            resume_path = resume_file.name
        except Exception as e:
            print(f"Error parsing resume PDF: {e}")

    req_id = None
    if fulfills_req and "None" not in fulfills_req:
        req_id = fulfills_req.split(":")[0].strip()

    emp_data = {
        "employee_id": employee_id,
        "full_name": full_name,
        "email": f"{full_name.lower().replace(' ', '.')}@enginecorp.com",
        "phone": "+1 555-0199",
        "date_of_birth": "1994-01-01",
        "job_title": job_title,
        "department": department or "Engineering",
        "location": "HQ",
        "years_experience": float(years_exp or 2.0),
        "domain_knowledge": skills or "",
        "seniority_tier": int(seniority_tier or 2),
        "is_lead": 0,
        "current_project": None,
        "current_project_weight": 0.0,
        "project_changes_last_30_days": 0,
        "days_on_current_project": 0,
        "availability_hours": 40.0,
        "ability_score": 0.85,
        "utilization": 0.0,
        "resume_path": resume_path,
        "resume_status": "processed" if resume_text else "no_resume",
        "resume_text": resume_text or f"{full_name} is a {job_title} skilled in {skills} with {years_exp} years experience.",
    }

    # If linked to a requisition or auto-matched by role title, mark fulfilled
    if not req_id:
        pending_reqs = db.list_hr_requests(status="pending")
        for pr in pending_reqs:
            if pr["role_title"].strip().lower() in job_title.strip().lower() or job_title.strip().lower() in pr["role_title"].strip().lower():
                req_id = pr["request_id"]
                break

    fulfilled_req = None
    if req_id:
        fulfilled_req = db.get_hr_request(req_id)
        if fulfilled_req:
            db.update_hr_request_status(req_id, "fulfilled")
            target_pid = fulfilled_req.get("project_id")
            if target_pid and target_pid not in ["General", "General Workforce", "None", None, ""]:
                target_proj = db.get_project(target_pid)
                if target_proj:
                    risk_info = engine_service.evaluate_project_risk(target_proj)
                    emp_data["current_project"] = target_pid
                    emp_data["current_project_weight"] = risk_info.get("project_weight", 0.85)
                    emp_data["utilization"] = 0.85

    db.upsert_employee(emp_data)

    if fulfilled_req:
        msg = f"✓ Success: Onboarded {full_name} ({job_title}) and fulfilled requisition {req_id}!"
    else:
        msg = f"✓ Success: Onboarded {full_name} ({job_title}) into workforce records!"

    return msg, get_employees_dataframe(), get_requisitions_dataframe(), get_live_metrics_html()

def create_project_action(proj_id: str, name: str, client_tier: int, investment: float, roi: float, importance: float, deadline_days: int, hours: float, skills_str: str):
    if not proj_id or not name:
        return "Project ID and Name are required.", get_projects_dataframe(), gr.update(choices=get_project_choices()), get_live_metrics_html()
    
    skills = [s.strip() for s in (skills_str or "").split(",") if s.strip()]
    proj_data = {
        "project_id": proj_id.strip(),
        "name": name.strip(),
        "client_tier": int(client_tier or 3),
        "investment": float(investment or 100000.0),
        "roi": float(roi or 0.25),
        "skill_criticality": 3.0,
        "estimated_people": 2,
        "skill_staffing": {},
        "importance": float(importance or 3.0),
        "required_skills": skills,
        "project_hours": float(hours or 160.0),
        "deadline_days": int(deadline_days or 30),
        "completion_pct": 0,
        "status": "active",
        "description": f"New project: {name}"
    }
    db.save_project(proj_data)
    return f"✓ Project '{name}' ({proj_id}) saved successfully!", get_projects_dataframe(), gr.update(choices=get_project_choices()), get_live_metrics_html()

def get_employee_portal_details(emp_selection: str):
    if not emp_selection:
        return "Select an employee to inspect their details.", "None", "None", "None", ""
    
    emp_id = emp_selection.split(" - ")[0].strip()
    emp = db.get_employee(emp_id)
    if not emp:
        return "Employee not found.", "None", "None", "None", ""

    curr_proj = emp.get("current_project") or "Bench (Available)"
    
    # Check team members
    teammates = "None"
    if emp.get("current_project"):
        all_emps = db.list_employees()
        members = [e["full_name"] for e in all_emps if e.get("current_project") == emp["current_project"] and e["employee_id"] != emp_id]
        if members:
            teammates = ", ".join(members)

    # Check pending transfer offer
    offer = db.get_pending_transfer_offer(emp_id)
    offer_info = ""
    offer_id = ""
    if offer:
        offer_id = offer["offer_id"]
        to_p = db.get_project(offer["to_project"])
        to_name = to_p.get("name") if to_p else offer["to_project"]
        offer_info = f"⚡ You have an active transfer offer to join: '{to_name}' ({offer['to_project']}) from '{offer.get('from_project', 'Current')}'. Do you accept?"

    details_md = f"""
    ### 👤 {emp['full_name']} (`{emp['employee_id']}`)
    - **Title & Department:** {emp.get('job_title', 'Engineer')} • {emp.get('department', 'Engineering')}
    - **Experience:** {emp.get('years_experience', 1.0)} years (Seniority Tier {emp.get('seniority_tier', 1)})
    - **Weekly Capacity:** {emp.get('availability_hours', 40)} hours • Ability Score: {emp.get('ability_score', 0.8)}
    - **Skills:** {', '.join(emp.get('skills', [])) or emp.get('domain_knowledge', 'None')}
    """

    return details_md, curr_proj, teammates, offer_info, offer_id

def respond_transfer_offer_action(offer_id: str, action: str, reason: str):
    if not offer_id:
        return "No active transfer offer selected."
    
    status = "accepted" if action == "Accept" else "declined"
    db.resolve_transfer_offer(offer_id, status, decline_reason=reason or "")
    
    with db.get_connection() as conn:
        row = conn.execute("SELECT * FROM transfer_offers WHERE offer_id = ?", (offer_id,)).fetchone()
        if row:
            emp_id = row["employee_id"]
            to_proj = row["to_project"]
            if status == "accepted":
                p = db.get_project(to_proj)
                risk = engine_service.evaluate_project_risk(p) if p else {"project_weight": 1.0}
                db.update_employee_project(emp_id, to_proj, risk["project_weight"])
                db.create_notification("manager", "Transfer Offer Accepted", f"Employee {emp_id} accepted transfer to project {to_proj}.", notif_type="transfer_accepted")
            else:
                db.create_notification("manager", "Transfer Offer Declined", f"Employee {emp_id} declined transfer to project {to_proj}. Reason: {reason or 'None'}", notif_type="transfer_declined")
                
    return f"✓ Transfer offer {offer_id} {status} successfully!"

def reset_and_clean_database():
    try:
        clean_cache.remove_all_cache()
        seed_data.seed(reset=True)
        return "✓ Database cleanly reset to default initial state! Cache cleaned.", get_live_metrics_html(), get_projects_dataframe(), get_employees_dataframe(), get_requisitions_dataframe()
    except Exception as e:
        return f"Database reset failed: {e}", get_live_metrics_html(), get_projects_dataframe(), get_employees_dataframe(), get_requisitions_dataframe()

# ==================== GRADIO APPLICATION LAYOUT ====================

theme = gr.themes.Soft(
    primary_hue="blue",
    secondary_hue="slate",
)

with gr.Blocks(title="Resource Allocation Engine", theme=theme) as demo:
    gr.Markdown("""
    # ⚡ Resource Allocation Engine (RessAlloc)
    **Autonomous Workforce Optimization, Semantic Skill Search & Deterministic Project Staffing**
    """)

    # Live Metrics Header
    metrics_box = gr.HTML(value=get_live_metrics_html())

    with gr.Tabs():
        # ----------------- TAB 1: DASHBOARD & PROJECTS -----------------
        with gr.TabItem("📊 Projects & SLA Dashboard"):
            with gr.Row():
                with gr.Column(scale=3):
                    gr.Markdown("### 📂 Ongoing Projects Overview")
                    projects_table = gr.Dataframe(
                        value=get_projects_dataframe,
                        headers=["Project ID", "Name", "Client Tier", "Investment ($)", "Required Skills", "Deadline (Days)", "SLA Risk (%)", "Risk Level", "Project Weight", "Assigned Team"],
                        interactive=False
                    )
                    refresh_projs_btn = gr.Button("🔄 Refresh Projects", size="sm")

                with gr.Column(scale=2):
                    gr.Markdown("### ➕ Create New Project")
                    new_pid = gr.Textbox(label="Project ID *", placeholder="e.g. proj_ai_copilot")
                    new_pname = gr.Textbox(label="Project Name *", placeholder="e.g. AI Copilot Integration")
                    with gr.Row():
                        new_tier = gr.Slider(label="Client Tier (1-5)", minimum=1, maximum=5, value=3, step=1)
                        new_imp = gr.Slider(label="Importance (1.0 - 5.0)", minimum=1.0, maximum=5.0, value=3.5, step=0.1)
                    with gr.Row():
                        new_invest = gr.Number(label="Investment ($)", value=150000)
                        new_roi = gr.Number(label="Expected ROI (0.0-1.0)", value=0.35)
                    with gr.Row():
                        new_deadline = gr.Number(label="Deadline (Days)", value=30)
                        new_hours = gr.Number(label="Estimated Hours", value=200)
                    new_skills = gr.Textbox(label="Required Skills (Comma-separated)", placeholder="Python, FastAPI, Docker, React")
                    create_proj_btn = gr.Button("Create Project", variant="primary")
                    create_proj_status = gr.Markdown()

        # ----------------- TAB 2: SMART ALLOCATION ENGINE -----------------
        with gr.TabItem("🎯 Smart Allocation Engine"):
            gr.Markdown("### 🧠 Deterministic Project Staffing & Semantic Fit Analysis")
            with gr.Row():
                with gr.Column(scale=2):
                    project_selector = gr.Dropdown(label="Select Project to Analyze", choices=get_project_choices(), value=get_project_choices()[0] if get_project_choices() else None)
                    run_engine_btn = gr.Button("🚀 Run AI Candidate Ranking", variant="primary")
                with gr.Column(scale=3):
                    engine_summary_html = gr.HTML(value="<div style='color:#6b7280; padding:1rem;'>Select a project and click 'Run AI Candidate Ranking' to inspect allocations.</div>")

            gr.Markdown("#### 📋 Evaluated & Ranked Candidates")
            ranked_candidates_table = gr.Dataframe(
                headers=["Rank", "ID", "Name", "Status", "Semantic Fit", "Score", "Effective Capacity", "Days on Project", "Action Type"],
                interactive=False
            )

            with gr.Row():
                with gr.Column():
                    gr.Markdown("#### 🛠️ Allocate Recommended Candidate")
                    cand_action_select = gr.Dropdown(label="Select Candidate to Assign", choices=[])
                    assign_cand_btn = gr.Button("Execute Assignment / Transfer Offer", variant="primary")
                    assign_status = gr.Markdown()

                with gr.Column():
                    gr.Markdown("#### 📋 Raise Urgent Requisition to HR")
                    req_role = gr.Textbox(label="Role Title", placeholder="e.g. Senior Kubernetes SRE")
                    req_skills = gr.Textbox(label="Required Skills", placeholder="Kubernetes, Go, AWS")
                    req_urgency = gr.Dropdown(label="Urgency", choices=["Medium", "High", "Critical"], value="High")
                    req_desc = gr.Textbox(label="Description", placeholder="Immediate talent required due to all existing staff commitment.")
                    raise_req_btn = gr.Button("Submit Requisition to HR", variant="secondary")
                    req_status = gr.Markdown()

        # ----------------- TAB 3: HR TALENT PORTAL -----------------
        with gr.TabItem("👥 HR Talent Portal & Requisitions"):
            with gr.Tabs():
                with gr.TabItem("Talent Directory"):
                    with gr.Row():
                        hr_search = gr.Textbox(label="Search Talent", placeholder="Search by name, role, department or skill...", scale=4)
                        hr_refresh_btn = gr.Button("Search / Refresh", scale=1)
                    hr_directory_table = gr.Dataframe(
                        value=get_employees_dataframe,
                        headers=["ID", "Name", "Job Title", "Department", "Status", "Experience (Yrs)", "Tier", "Skills", "Ability Score"],
                        interactive=False
                    )

                with gr.TabItem("Onboard New Employee"):
                    gr.Markdown("### ➕ Onboard Talent (with Automatic Resume Parsing)")
                    with gr.Row():
                        with gr.Column():
                            onboard_name = gr.Textbox(label="Full Name *", placeholder="e.g. Jordan Cole")
                            onboard_title = gr.Textbox(label="Job Title *", placeholder="e.g. Senior Backend Engineer")
                            onboard_dept = gr.Dropdown(label="Department", choices=["Engineering", "Design & UI", "Infrastructure", "AI Research", "Product"], value="Engineering")
                            onboard_exp = gr.Number(label="Years of Experience", value=4.0)
                            onboard_tier = gr.Slider(label="Seniority Tier (1-5)", minimum=1, maximum=5, value=3, step=1)
                        with gr.Column():
                            onboard_skills = gr.Textbox(label="Skills & Domain Knowledge", placeholder="Python, Docker, FastAPI, PostgreSQL")
                            onboard_resume = gr.File(label="Upload Resume (PDF)", file_types=[".pdf"])
                            onboard_fulfills = gr.Dropdown(label="Fulfills Manager Requisition (Optional)", choices=get_requisition_choices(), value="None (Independent Hire)")
                    onboard_submit_btn = gr.Button("Onboard Employee Record", variant="primary")
                    onboard_status = gr.Markdown()

                with gr.TabItem("Manager Hiring Requisitions"):
                    gr.Markdown("### 📋 Manager Hiring Requests")
                    reqs_table = gr.Dataframe(
                        value=get_requisitions_dataframe,
                        headers=["Req ID", "Role Title", "Target Project", "Urgency", "Required Skills", "Description", "Status"],
                        interactive=False
                    )
                    with gr.Row():
                        req_fulfill_id = gr.Textbox(label="Requisition ID to Mark Fulfilled", placeholder="e.g. REQ-101")
                        req_fulfill_btn = gr.Button("✓ Mark Requisition Fulfilled", variant="secondary")
                    req_fulfill_status = gr.Markdown()

        # ----------------- TAB 4: EMPLOYEE SELF-SERVICE -----------------
        with gr.TabItem("💼 Employee Self-Service"):
            gr.Markdown("### 👤 Employee Dashboard & Project Assignments")
            emp_picker = gr.Dropdown(label="Select Employee Identity", choices=get_employee_choices(), value=get_employee_choices()[0] if get_employee_choices() else None)
            emp_details_box = gr.Markdown()
            with gr.Row():
                emp_proj_display = gr.Textbox(label="Current Project Assignment", interactive=False)
                emp_team_display = gr.Textbox(label="Project Teammates", interactive=False)
            
            with gr.Group():
                gr.Markdown("#### 📩 Project Transfer Nominations")
                emp_offer_display = gr.Markdown(value="No pending transfer nominations.")
                emp_offer_id_hidden = gr.Textbox(visible=False)
                with gr.Row():
                    emp_decline_reason = gr.Textbox(label="Reason (Optional if declining)", placeholder="e.g. Committed to ongoing client deliverables")
                with gr.Row():
                    accept_offer_btn = gr.Button("Accept Transfer Offer", variant="primary")
                    decline_offer_btn = gr.Button("Decline Transfer Offer", variant="secondary")
                emp_offer_status = gr.Markdown()

        # ----------------- TAB 5: SYSTEM & DATABASE CLEANUP -----------------
        with gr.TabItem("⚙️ System Maintenance & Clean Database"):
            gr.Markdown("""
            ### 🧹 Database & Cache Maintenance
            Reset all employee, project, and requisition records back to clean deterministic seed data. Cleans compiled cache files (`__pycache__`, `.pyc`).
            """)
            reset_db_btn = gr.Button("⚠️ Clean & Re-seed Database to Default State", variant="stop")
            reset_status = gr.Markdown()
            gr.Markdown(f"""
            - **Database Path:** `{db.DB_PATH}`
            - **Python Version:** `{sys.version.split()[0]}`
            - **Root Directory:** `{ROOT_DIR}`
            """)

    # ==================== EVENT BINDINGS ====================

    # Refresh Projects
    refresh_projs_btn.click(
        fn=lambda: (get_projects_dataframe(), get_live_metrics_html(), gr.update(choices=get_project_choices())),
        outputs=[projects_table, metrics_box, project_selector]
    )

    # Create Project
    create_proj_btn.click(
        fn=create_project_action,
        inputs=[new_pid, new_pname, new_tier, new_invest, new_roi, new_imp, new_deadline, new_hours, new_skills],
        outputs=[create_proj_status, projects_table, project_selector, metrics_box]
    )

    # Run Allocation Engine
    run_engine_btn.click(
        fn=run_allocation_engine,
        inputs=[project_selector],
        outputs=[engine_summary_html, ranked_candidates_table, cand_action_select, assign_status]
    )

    # Assign Candidate
    assign_cand_btn.click(
        fn=assign_candidate_to_project,
        inputs=[project_selector, cand_action_select],
        outputs=[assign_status, metrics_box, projects_table]
    )

    # Submit HR Requisition
    raise_req_btn.click(
        fn=create_hr_requisition_action,
        inputs=[project_selector, req_role, req_skills, req_urgency, req_desc],
        outputs=[req_status, reqs_table, metrics_box]
    )

    # Fulfill HR Requisition
    req_fulfill_btn.click(
        fn=fulfill_requisition_action,
        inputs=[req_fulfill_id],
        outputs=[req_fulfill_status, reqs_table, metrics_box]
    )

    # Onboard Employee
    onboard_submit_btn.click(
        fn=onboard_new_employee_action,
        inputs=[onboard_name, onboard_title, onboard_dept, onboard_exp, onboard_tier, onboard_skills, onboard_resume, onboard_fulfills],
        outputs=[onboard_status, hr_directory_table, reqs_table, metrics_box]
    )

    # HR Search
    hr_refresh_btn.click(
        fn=get_employees_dataframe,
        inputs=[hr_search],
        outputs=[hr_directory_table]
    )
    hr_search.submit(
        fn=get_employees_dataframe,
        inputs=[hr_search],
        outputs=[hr_directory_table]
    )

    # Employee Portal
    emp_picker.change(
        fn=get_employee_portal_details,
        inputs=[emp_picker],
        outputs=[emp_details_box, emp_proj_display, emp_team_display, emp_offer_display, emp_offer_id_hidden]
    )

    accept_offer_btn.click(
        fn=lambda oid: respond_transfer_offer_action(oid, "Accept", ""),
        inputs=[emp_offer_id_hidden],
        outputs=[emp_offer_status]
    ).then(
        fn=get_employee_portal_details,
        inputs=[emp_picker],
        outputs=[emp_details_box, emp_proj_display, emp_team_display, emp_offer_display, emp_offer_id_hidden]
    ).then(
        fn=get_live_metrics_html,
        outputs=[metrics_box]
    )

    decline_offer_btn.click(
        fn=lambda oid, r: respond_transfer_offer_action(oid, "Decline", r),
        inputs=[emp_offer_id_hidden, emp_decline_reason],
        outputs=[emp_offer_status]
    ).then(
        fn=get_employee_portal_details,
        inputs=[emp_picker],
        outputs=[emp_details_box, emp_proj_display, emp_team_display, emp_offer_display, emp_offer_id_hidden]
    )

    # Clean & Reset Database
    reset_db_btn.click(
        fn=reset_and_clean_database,
        outputs=[reset_status, metrics_box, projects_table, hr_directory_table, reqs_table]
    ).then(
        fn=lambda: gr.update(choices=get_project_choices()),
        outputs=[project_selector]
    ).then(
        fn=lambda: gr.update(choices=get_requisition_choices()),
        outputs=[onboard_fulfills]
    )

if __name__ == "__main__":
    server_port = int(os.environ.get("PORT", 7860))
    is_hf = "SPACE_ID" in os.environ or "HF_SPACE_ID" in os.environ
    server_name = "0.0.0.0" if is_hf else "127.0.0.1"
    
    print("\n" + "=" * 60)
    print(f"  ⚡ Resource Allocation Engine is running!")
    print(f"  👉 Open in your browser: http://localhost:{server_port} or http://127.0.0.1:{server_port}")
    print("=" * 60 + "\n")
    
    demo.launch(
        server_name=server_name,
        server_port=server_port,
        share=False,
        inbrowser=not is_hf
    )
