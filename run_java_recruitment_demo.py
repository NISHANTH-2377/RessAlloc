import os
import re
import random
import time
from employees import EmployeeDatabase
from engine import ResourceAllocationEngine, WorkforceVectorStore
from projects import ProjectAllocationManager


def run_java_recruitment_demo():
    print("=" * 60)
    print("   JAVA RECRUITMENT DEMO — 100% CPU TEXT-BASED PIPELINE   ")
    print("=" * 60)
    print("[Pipeline Mode] CPU-Only Text PDF Parsing (No OCR / No GPU)")
    print("-" * 60)

    # 1. Initialize Database & Sync Resumes on CPU
    start_time = time.time()
    print("[Step 1] Parsing Digital Text-Based Resumes on CPU...")
    db = EmployeeDatabase()
    imported_files = db.sync_resume_directory("employees/resume")
    pdf_parse_time = time.time() - start_time
    print(f"[Step 1] Parsed {len(imported_files)} digital text PDFs in {pdf_parse_time:.3f} seconds! (CPU)")

    # 2. Populate Database Attributes
    print("\n[Step 2] Populating Database with Candidate Metadata...")
    employees = db.list_employees()
    print(f"[Step 2] Loaded {len(employees)} employee profiles in SQLite.")

    sample_departments = ["Engineering", "Backend Systems", "Cloud Solutions", "Platform Team", "Data Infra"]
    sample_titles = ["Software Engineer", "Java Developer", "Backend Developer", "Systems Engineer", "Full Stack Developer"]
    sample_domain = ["Enterprise Software", "Fintech", "E-commerce", "SaaS", "Cloud Infrastructure"]

    random.seed(42)

    def _extract_years(text: str) -> float:
        """Extract years of experience from resume text using regex. Falls back to random."""
        if not text:
            return round(random.uniform(2.0, 10.0), 1)
        # Matches patterns like "9 years", "9 Years", "9+ years", "9.5 years"
        match = re.search(r'(\d+(?:\.\d+)?)\+?\s*[Yy]ears?', text)
        if match:
            return float(match.group(1))
        return round(random.uniform(2.0, 10.0), 1)

    for emp in employees:
        emp_id = emp["employee_id"]
        resume_text = emp.get("resume_text", "")
        extracted_years = _extract_years(resume_text)
        db.upsert_employee(
            employee_id=emp_id,
            full_name=emp.get("full_name") or f"Engineer_{emp_id}",
            email=f"{emp_id}@techcorp.com",
            job_title=random.choice(sample_titles),
            department=random.choice(sample_departments),
            years_experience=extracted_years,
            domain_knowledge=random.choice(sample_domain),
            seniority_tier=random.randint(1, 5),
            is_lead=(random.random() < 0.15),
            current_project="Project_Alpha" if random.random() < 0.3 else None,
            current_project_weight=round(random.uniform(100.0, 300.0), 2) if random.random() < 0.3 else None,
            project_changes_last_30_days=random.randint(0, 1),
            days_on_current_project=random.randint(15, 90),
            availability_hours=random.choice([30.0, 40.0, 50.0]),
            ability_score=round(random.uniform(0.75, 0.95), 2),
            utilization=round(random.uniform(0.10, 0.50), 2),
            resume_path=emp.get("resume_path"),
            resume_text=resume_text,
            refresh_rankings=False,
        )

    # 3. Vector Database Indexing
    print("\n[Step 3] Indexing Resumes in Qdrant Vector DB...")
    updated_employees = db.list_employees()
    vector_store = WorkforceVectorStore()
    indexed_count = vector_store.index_employee_records(updated_employees)
    print(f"[Step 3] Indexed {indexed_count} text profiles in Qdrant collection 'employee_workforce'.")

    # 4. Java Recruitment Project Specification
    print("\n[Step 4] Querying Vector Database for Java Recruitment...")
    java_project = {
        "project_id": "java_recruitment_backend_cpu_v1",
        "investment": 50000.0,
        "roi": 0.35,
        "client_tier": 4,
        "skill_criticality": 4.5,
        "estimated_people": 2,
        "skill_staffing": {
            "Java": 1,
            "Spring Boot": 1,
            "Microservices": 1,
            "SQL": 1
        },
        "importance": 4.5,
        "required_skills": ["Java", "Spring Boot", "Microservices", "SQL", "REST API"],
        "project_hours": 160.0,
        "deadline_days": 25,
    }

    query_skills = " ".join(java_project["required_skills"])
    semantic_hits = vector_store.search_semantic_candidates(query_skills, top_k=15)
    print(f"[Step 4] Retrieved {len(semantic_hits)} top semantic candidate matches.")

    candidate_pool = []
    for hit in semantic_hits:
        payload = hit.get("payload", {})
        candidate_pool.append({
            "employee_id": payload.get("employee_id"),
            "name": payload.get("full_name") or payload.get("employee_id"),
            "skills": payload.get("skills", []),
            "current_project": payload.get("current_project"),
            "current_project_weight": payload.get("current_project_weight"),
            "project_changes_last_30_days": int(payload.get("project_changes_last_30_days", 0)),
            "days_on_current_project": int(payload.get("days_on_current_project", 0)),
            "available_hours": float(payload.get("availability_hours", 40.0)),
            "ability_score": float(payload.get("ability_score", 0.8)),
            "utilization": float(payload.get("utilization", 0.2)),
            "resume_text": payload.get("resume_text", ""),
        })

    # 5. Allocation & SLA Risk Engine Evaluation
    print("\n[Step 5] Evaluating Allocation Engine Rules & SLA Risk...")
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

    pm = ProjectAllocationManager(db)
    project_json_path = pm.save_project(java_project)

    total_pipeline_time = time.time() - start_time

    # 6. Results Summary
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
    print(f"{'Rank':<6} | {'Candidate Name':<25} | {'Semantic Match':<14} | {'Final Score':<12}")
    print("-" * 65)
    for rank, candidate in enumerate(ranked_candidates[:5], start=1):
        print(f"{rank:<6} | {candidate['name'][:25]:<25} | {candidate['semantic_match']:<14} | {candidate['final_score']:<12}")

    if selected_worker:
        print("\n" + "*" * 65)
        print("SELECTED WORKER FOR JAVA RECRUITMENT:")
        print(f"  Name: {selected_worker['name']}")
        print(f"  Decision Type: {selected_worker['decision']}")
        print(f"  Semantic Match: {selected_worker['semantic_match']}")
        print(f"  Effective Hours: {selected_worker['effective_hours']}")
        print(f"  Projected Utilization: {selected_worker.get('projected_utilization', 'N/A')}")
        print("*" * 65)
    else:
        print("\nNo candidate met all capacity and project rules.")

    print("\n[SUCCESS] 100% CPU text-based Java recruitment pipeline executed successfully!")


if __name__ == "__main__":
    run_java_recruitment_demo()
