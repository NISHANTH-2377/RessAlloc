import atexit
import json
import os
import shutil
import socket
import sqlite3
import subprocess
import sys
import time
import webbrowser

from employees import EmployeeDatabase
from engine import ResourceAllocationEngine, WorkforceVectorStore, WorkforceRAGPipeline
from projects import ProjectAllocationManager


def remove_all_cache(target_dir=None):
    """Purges all __pycache__ directories and compiled .pyc/.pyo files across the project."""
    if target_dir is None:
        target_dir = os.path.dirname(os.path.abspath(__file__))
    removed_dirs = 0
    removed_files = 0
    for root, dirs, files in os.walk(target_dir, topdown=False):
        for file in files:
            if file.endswith((".pyc", ".pyo", ".pyd")):
                try:
                    os.remove(os.path.join(root, file))
                    removed_files += 1
                except Exception:
                    pass
        for d in list(dirs):
            if d in ("__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache"):
                try:
                    shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                    removed_dirs += 1
                    dirs.remove(d)
                except Exception:
                    pass
    if removed_dirs or removed_files:
        print(f"[Cache Cleanup] Purged {removed_dirs} cache directories and {removed_files} bytecode cache files.")
    return removed_dirs, removed_files


def main():
    print("=" * 60)
    print("   100% CPU TEXT-BASED PIPELINE   ")
    print("=" * 60)
    print("[Pipeline Mode] CPU-Only Text PDF Parsing (No OCR / No GPU)")
    print("-" * 60)

    start_time = time.time()
    print("[Step 1] Parsing Digital Text-Based Resumes on CPU...")
    db = EmployeeDatabase()
    imported_files = db.sync_resume_directory("employees/resume")
    pdf_parse_time = time.time() - start_time
    print(f"[Step 1] Parsed {len(imported_files)} digital text PDFs in {pdf_parse_time:.3f} seconds! (CPU)")

    print("\n[Step 2] Loading Candidate Metadata from SQLite Database...")
    employees = db.list_employees()
    print(f"[Step 2] Loaded {len(employees)} employee profiles from '{os.path.basename(db.db_path)}'.")

    # Step 3: Vector Database (vector_database.py)
    print("\n[Step 3] Invoking vector_database.py (Indexing in Qdrant Vector DB)...")
    vector_store = WorkforceVectorStore()
    indexed_count = vector_store.index_employee_records(employees)
    print(f"[vector_database.py] Successfully indexed {indexed_count} profiles in Qdrant collection '{vector_store.collection_name}'.")

    # Step 4: RAG Pipeline (RAG.py)
    print("\n[Step 4] Invoking RAG.py (Ingesting Documents into LlamaIndex & Preparing Context)...")
    rag_pipeline = WorkforceRAGPipeline(qdrant_client=vector_store.client, collection_name=vector_store.collection_name)
    rag_pipeline.ingest_employee_documents(employees)
    sample_context = rag_pipeline.retrieve_context("Java Spring Boot Microservices", top_k=2)
    print(f"[RAG.py] Successfully ingested {len(employees)} employee documents into RAG layer.")
    print(f"[RAG.py] Context retrieval check: {len(sample_context)} relevant context nodes found.")

    # Step 5: Resource Allocation Engine (engine.py) - Refresh All Ongoing Projects
    print("\n[Step 5] Invoking engine.py (Recalculating SLA Risks & Re-ranking All Ongoing Projects)...")
    project_manager = ProjectAllocationManager(db)
    refreshed_csvs = project_manager.refresh_all_projects()
    print(f"[engine.py] Refreshed allocations and generated ranked CSVs for {len(refreshed_csvs)} ongoing projects:")
    for csv_file in refreshed_csvs:
        print(f"  -> Generated: {os.path.basename(csv_file)}")

    # Step 6: Targeted Evaluation with Allocation Engine
    print("\n[Step 6] Running Allocation Engine Evaluation on Recruitment Specification...")
    java_project = {
        "project_id": "recruitment",
        "investment": 50000.0,
        "roi": 0.35,
        "client_tier": 4,
        "skill_criticality": 4.5,
        "estimated_people": 2,
        "skill_staffing": {
            "Java": 1,
            "Spring Boot": 1,
            "Microservices": 1,
            "SQL": 1,
        },
        "importance": 4.5,
        "required_skills": ["Java", "Spring Boot", "Microservices", "SQL", "REST API"],
        "project_hours": 160.0,
        "deadline_days": 25,
    }

    query_skills = " ".join(java_project["required_skills"])
    semantic_hits = vector_store.search_semantic_candidates(query_skills, top_k=15)
    candidate_pool = [hit["payload"] for hit in semantic_hits if hit.get("payload")]

    sla_risk = ResourceAllocationEngine.calculate_project_sla_risk(
        workers=candidate_pool,
        required_skills=java_project["required_skills"],
        project_hours=java_project["project_hours"],
        deadline_days=java_project["deadline_days"],
    )
    java_project["sla_risk"] = sla_risk

    ranked_candidates = ResourceAllocationEngine.rank_workers_by_semantic_fit(
        workers=candidate_pool,
        required_skills=java_project["required_skills"],
        project_hours=java_project["project_hours"],
        deadline_days=java_project["deadline_days"],
    )

    selected_worker = ResourceAllocationEngine.select_worker_for_project(
        workers=candidate_pool,
        required_skills=java_project["required_skills"],
        project_hours=java_project["project_hours"],
        deadline_days=java_project["deadline_days"],
        new_project=java_project,
    )

    project_weight = ResourceAllocationEngine.calculate_project_weight(
        investment=java_project["investment"],
        roi=java_project["roi"],
        client_tier=java_project["client_tier"],
        sla_risk=int(round(sla_risk)),
        skill_criticality=java_project["skill_criticality"],
        deadline_days=java_project["deadline_days"],
        required_skill_count=len(java_project["required_skills"]),
        estimated_people=java_project["estimated_people"],
        importance=java_project["importance"],
    )

    project_json_path = project_manager.save_project(java_project)
    total_pipeline_time = time.time() - start_time

    print("\n" + "=" * 65)
    print("             JAVA RECRUITMENT RESULTS (CPU MODE)             ")
    print("=" * 65)
    print(f"Project ID           : {java_project['project_id']}")
    print(f"Required Skills      : {', '.join(java_project['required_skills'])}")
    print(f"Project SLA Risk     : {sla_risk}%")
    print(f"Project Weight       : {project_weight}")
    print(f"PDF Parse Time (CPU) : {pdf_parse_time:.3f} seconds")
    print(f"Total Pipeline Time  : {total_pipeline_time:.3f} seconds")
    print(f"Saved Spec File      : {project_json_path}")

    print("\n[Top Ranked Candidates for Java Recruitment]:")
    print(f"{'Rank':<6} | {'Candidate Name':<25} | {'Semantic Match':<14} | {'Final Score':<12} | {'Reason'}")
    print("-" * 110)
    for rank, candidate in enumerate(ranked_candidates[:5], start=1):
        print(f"{rank:<6} | {candidate['name'][:25]:<25} | {candidate['semantic_match']:<14} | {candidate['final_score']:<12} | {candidate.get('reason', 'N/A')}")

    if selected_worker:
        print("\n" + "*" * 65)
        print("SELECTED WORKER FOR JAVA RECRUITMENT:")
        print(f"  Name: {selected_worker['name']}")
        print(f"  Decision Type: {selected_worker['decision']}")
        print(f"  Semantic Match: {selected_worker['semantic_match']}")
        print(f"  Effective Hours: {selected_worker['effective_hours']}")
        print(f"  Projected Utilization: {selected_worker.get('projected_utilization', 'N/A')}")
        print(f"  Reason: {selected_worker.get('reason', 'No explanation available')}")
        print("*" * 65)
    else:
        print("\nNo candidate met all capacity and project rules.")

    print("\n[SUCCESS] vector_database.py, RAG.py, and engine.py executed and synchronized successfully!")


def get_db_state(db_path: str, conn: sqlite3.Connection = None) -> tuple:
    """
    Returns (mtime, wal_mtime, data_version, content_signature) for robust change detection.
    Detects any INSERT, UPDATE, DELETE, or file touch.
    """
    mtime = 0.0
    try:
        mtime = os.path.getmtime(db_path)
    except OSError:
        pass

    wal_mtime = 0.0
    for ext in ["-wal", "-journal"]:
        p = db_path + ext
        if os.path.exists(p):
            try:
                wal_mtime = max(wal_mtime, os.path.getmtime(p))
            except OSError:
                pass

    data_version = 0
    content_sig = (0, "", 0)

    # If persistent connection provided, PRAGMA data_version tracks external transactions
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("PRAGMA data_version;")
            row = cur.fetchone()
            if row:
                data_version = row[0]
            cur.execute("SELECT count(*), COALESCE(max(updated_at), ''), COALESCE(sum(length(coalesce(resume_text, ''))), 0) FROM employees;")
            crow = cur.fetchone()
            if crow:
                content_sig = (crow[0], crow[1], crow[2])
        except Exception:
            pass
    else:
        try:
            with sqlite3.connect(db_path) as c:
                cur = c.cursor()
                cur.execute("PRAGMA data_version;")
                row = cur.fetchone()
                if row:
                    data_version = row[0]
                cur.execute("SELECT count(*), COALESCE(max(updated_at), ''), COALESCE(sum(length(coalesce(resume_text, ''))), 0) FROM employees;")
                crow = cur.fetchone()
                if crow:
                    content_sig = (crow[0], crow[1], crow[2])
        except Exception:
            pass

    return (mtime, wal_mtime, data_version, content_sig)


def get_resume_dir_mtime(resume_dir: str) -> float:
    """Returns highest mtime of the resume directory and its PDF files."""
    mtime = 0.0
    if os.path.exists(resume_dir):
        try:
            mtime = os.path.getmtime(resume_dir)
            for entry in os.scandir(resume_dir):
                if entry.is_file() and entry.name.endswith(".pdf"):
                    mtime = max(mtime, entry.stat().st_mtime)
        except OSError:
            pass
    return mtime


CALC_LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".calculation_lock.json")

def set_calculation_lock(is_active: bool, message: str = ""):
    """Updates shared calculation lock file so frontend and backend know calculations are in progress."""
    data = {
        "is_calculating": bool(is_active),
        "message": message or ("Database modified. Recalculating workforce allocations & SLA risks..." if is_active else ""),
        "timestamp": time.time(),
    }
    try:
        with open(CALC_LOCK_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f)
    except Exception:
        pass


def watch_and_run(poll_interval: float = 1.0):
    """
    Watches employee_records.db (and resume directory) for modifications,
    automatically executing main() whenever data changes.
    """
    db = EmployeeDatabase()
    db_path = db.db_path
    resume_dir = os.path.join(os.path.dirname(db_path), "resume")

    print("=" * 65)
    print("   AUTOMATED RESALLOC DATABASE WATCHER   ")
    print("=" * 65)
    print(f"  Target Database   : {db_path}")
    print(f"  Resume Directory  : {resume_dir}")
    print(f"  Poll Interval     : {poll_interval}s")
    print("  Mode              : Continuous Auto-Run on Data Modification")
    print("  Modules Invoked   : vector_database.py, RAG.py, engine.py")
    print("  (Press Ctrl+C to stop watching)")
    print("=" * 65 + "\n")

    # Initial execution
    set_calculation_lock(True, "Initializing workforce calculations and Qdrant vector index...")
    try:
        main()
    finally:
        set_calculation_lock(False)

    # Create persistent connection to monitor PRAGMA data_version from external processes
    watcher_conn = None
    try:
        watcher_conn = sqlite3.connect(db_path)
    except Exception:
        pass

    # Capture baseline state immediately after initial main()
    last_db_state = get_db_state(db_path, watcher_conn)
    last_resume_mtime = get_resume_dir_mtime(resume_dir)

    print(f"\n[Watcher Active] Monitoring '{os.path.basename(db_path)}' for data modifications...")

    while True:
        try:
            time.sleep(poll_interval)
        except KeyboardInterrupt:
            print("\n[Watcher] Stopped by user.")
            if watcher_conn:
                try:
                    watcher_conn.close()
                except Exception:
                    pass
            break

        current_db_state = get_db_state(db_path, watcher_conn)
        current_resume_mtime = get_resume_dir_mtime(resume_dir)

        db_changed = current_db_state != last_db_state
        resume_changed = current_resume_mtime != last_resume_mtime

        if db_changed or resume_changed:
            change_label = "Database records modified" if db_changed else "Resume directory modified"
            set_calculation_lock(True, f"{change_label}. Recalculating vectors, RAG context, and SLA risks...")
            # Debounce 0.5s to let batched writes settle
            time.sleep(0.5)

            print(f"\n{'=' * 65}")
            print(f"[Change Detected] {change_label} in '{os.path.basename(db_path)}'!")
            print(f"Triggering vector_database.py, RAG.py, and engine.py calculations...")
            print(f"{'=' * 65}\n")

            try:
                main()
            except Exception as e:
                print(f"[Watcher Error during execution] {e}")
            finally:
                set_calculation_lock(False)

            # Reconnect watcher if needed and refresh baseline
            if watcher_conn:
                try:
                    watcher_conn.close()
                except Exception:
                    pass
            try:
                watcher_conn = sqlite3.connect(db_path)
            except Exception:
                watcher_conn = None

            last_db_state = get_db_state(db_path, watcher_conn)
            last_resume_mtime = get_resume_dir_mtime(resume_dir)
            print(f"\n[Watcher Active] Monitoring '{os.path.basename(db_path)}' for data modifications...")


def is_backend_running(host: str = "127.0.0.1", port: int = 5000) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.5)
    try:
        s.connect((host, port))
        s.close()
        return True
    except OSError:
        return False


def launch_backend_and_frontend():
    """
    Executes backend/app.py if not already running,
    and opens font_end/index.html in the default web browser.
    """
    root_dir = os.path.dirname(os.path.abspath(__file__))
    backend_script = os.path.join(root_dir, "backend", "app.py")
    frontend_url = "http://127.0.0.1:5000"

    backend_proc = None
    if not is_backend_running():
        print(f"\n[Launcher] Launching backend server ({backend_script})...")
        backend_proc = subprocess.Popen(
            [sys.executable, backend_script],
            cwd=root_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        def cleanup():
            if backend_proc and backend_proc.poll() is None:
                backend_proc.terminate()

        atexit.register(cleanup)

        # Wait up to 5s for the backend server to respond
        for _ in range(25):
            time.sleep(0.2)
            if is_backend_running():
                break

    if is_backend_running():
        print(f"[Launcher] Backend API active on {frontend_url}")
        print(f"[Launcher] Opening font_end/index.html in web browser...")
        webbrowser.open(frontend_url)
    else:
        frontend_html = os.path.join(root_dir, "font_end", "index.html")
        print(f"[Launcher] Opening font_end/index.html directly: {frontend_html}")
        webbrowser.open(f"file://{frontend_html}")

    return backend_proc


if __name__ == "__main__":
    # 0. Clean any stale cache files
    remove_all_cache()

    # 1. Execute backend/app.py and open font_end/index.html
    launch_backend_and_frontend()

    # 2. Run pipeline / watch database for changes
    if "--once" in sys.argv:
        main()
    else:
        watch_and_run()
