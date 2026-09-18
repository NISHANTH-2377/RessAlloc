from employees import EmployeeDatabase
from engine import ResourceAllocationEngine, WorkforceVectorStore
from projects import ProjectAllocationManager


def main():
    print("Project Resource Allocation Engine Demo")
    print("=" * 40)

    project_id = input("Enter project ID: ").strip()
    investment = float(input("Enter project investment: "))
    roi = float(input("Enter project ROI (e.g. 0.25): "))
    client_tier = int(input("Enter client tier (1-5): "))
    skill_criticality = float(input("Enter skill criticality (0.0-5.0): "))
    estimated_people = int(input("Enter approximate number of people required: "))
    importance = float(input("Enter project importance (0.0-5.0): "))

    required_skills_text = input("Enter required skills (comma-separated): ")
    required_skills = [skill.strip() for skill in required_skills_text.split(",") if skill.strip()]
    skill_staffing = {}
    for skill in required_skills:
        skill_staffing[skill] = int(input(f"Number of people required for {skill}: "))

    project_hours = float(input("Enter total project hours estimate: "))
    deadline_days = int(input("Enter deadline in days: "))

    db = EmployeeDatabase()
    employees = db.list_employees()

    if not employees:
        print("\nNo employees are stored yet. Add PDF resumes inside the employees/resume folder first.")
        return

    vector_store = WorkforceVectorStore()
    vector_store.index_employee_records(employees)
    semantic_query = " ".join(required_skills)
    semantic_hits = vector_store.search_semantic_candidates(semantic_query, top_k=10)

    worker_candidates = []
    for hit in semantic_hits:
        payload = hit.get("payload", {})
        worker_candidates.append(
            {
                "name": payload.get("full_name") or payload.get("employee_id"),
                "skills": payload.get("skills", []),
                "current_project": payload.get("current_project"),
                "current_project_weight": payload.get("current_project_weight"),
                "project_changes_last_30_days": int(payload.get("project_changes_last_30_days", 0)),
                "days_on_current_project": int(payload.get("days_on_current_project", 0)),
                "available_hours": float(payload.get("availability_hours", 0.0)),
                "ability_score": float(payload.get("ability_score", 0.5)),
                "utilization": float(payload.get("utilization", 0.0)),
                "resume_text": payload.get("resume_text", ""),
            }
        )

    if not worker_candidates:
        print("\nNo semantic matches found in Qdrant. Falling back to raw employee data ordering.")
        worker_candidates = [
            {
                "name": employee.get("full_name") or employee.get("employee_id"),
                "skills": [],
                "current_project": employee.get("current_project"),
                "current_project_weight": employee.get("current_project_weight"),
                "project_changes_last_30_days": int(employee.get("project_changes_last_30_days", 0)),
                "days_on_current_project": int(employee.get("days_on_current_project", 0)),
                "available_hours": float(employee.get("availability_hours", 0.0)),
                "ability_score": float(employee.get("ability_score", 0.5)),
                "utilization": float(employee.get("utilization", 0.0)),
                "resume_text": employee.get("resume_text", ""),
            }
            for employee in employees
        ]

    ranked_workers = ResourceAllocationEngine.rank_workers_by_semantic_fit(
        workers=worker_candidates,
        required_skills=required_skills,
        project_hours=project_hours,
        deadline_days=deadline_days,
    )

    sla_risk = ResourceAllocationEngine.calculate_project_sla_risk(
        workers=worker_candidates,
        required_skills=required_skills,
        project_hours=project_hours,
        deadline_days=deadline_days,
    )

    project = {
        "project_id": project_id,
        "investment": investment,
        "roi": roi,
        "client_tier": client_tier,
        "skill_criticality": skill_criticality,
        "estimated_people": estimated_people,
        "skill_staffing": skill_staffing,
        "importance": importance,
        "required_skills": required_skills,
        "project_hours": project_hours,
        "deadline_days": deadline_days,
        "sla_risk": sla_risk,
    }
    project_manager = ProjectAllocationManager(db)
    project_path = project_manager.save_project(project)
    ranked_csv_path = project_manager.refresh_project(project_id)

    selected_worker = ResourceAllocationEngine.select_worker_for_project(
        workers=worker_candidates,
        required_skills=required_skills,
        project_hours=project_hours,
        deadline_days=deadline_days,
        new_project=project,
    )

    project_weight = ResourceAllocationEngine.calculate_project_weight(
        investment=investment,
        roi=roi,
        client_tier=client_tier,
        sla_risk=int(round(sla_risk)),
        skill_criticality=skill_criticality,
        deadline_days=deadline_days,
        required_skill_count=len(required_skills),
        estimated_people=estimated_people,
        importance=importance,
    )
    db.set_ranking_context({
        "required_skills": required_skills,
        "project_hours": project_hours,
        "deadline_days": deadline_days,
        "investment": investment,
        "roi": roi,
        "client_tier": client_tier,
        "skill_criticality": skill_criticality,
    })
    ranked_csv_path = db.refresh_ranked_employees_csv()

    current_workload_hours = sum(worker["available_hours"] * (1.0 - worker["utilization"]) for worker in worker_candidates)
    project_slack = ResourceAllocationEngine.evaluate_active_project_slack(
        current_workload_hours=current_workload_hours,
        capacity_hours=current_workload_hours,
    )

    employee_seniority_tier = int(input("Enter a benchmark seniority tier for the project: "))
    task_complexity_tier = int(input("Enter benchmark task complexity tier: "))
    cost_penalty = ResourceAllocationEngine.compute_cost_to_skill_penalty(
        employee_seniority_tier=employee_seniority_tier,
        task_complexity_tier=task_complexity_tier,
    )

    print("\nSemantic worker ranking:")
    for rank, worker in enumerate(ranked_workers, start=1):
        print(f"{rank}. {worker['name']} | match={worker['semantic_match']} | final_score={worker['final_score']}")

    if selected_worker:
        print(f"\nSelected worker: {selected_worker['name']} ({selected_worker['decision']})")
    else:
        print("\nNo worker meets the skill, capacity, and project-priority rules.")

    print("\nResults:")
    print(f"Project SLA risk: {sla_risk}%")
    print(f"Project weight: {project_weight}")
    print(f"Project slack: {project_slack}%")
    print(f"Cost-to-skill penalty: {cost_penalty}")
    print(f"Project details: {project_path}")
    print(f"Project ranking CSV: {ranked_csv_path}")
    if ranked_csv_path:
        print(f"Ranked employee CSV: {ranked_csv_path}")


if __name__ == "__main__":
    main()
