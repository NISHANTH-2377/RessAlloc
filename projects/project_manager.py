import csv
import json
import os
from pathlib import Path
from typing import Optional

from engine import ResourceAllocationEngine


class ProjectAllocationManager:
    """Stores ongoing projects and writes one ranked employee CSV per project."""

    def __init__(self, employee_database, project_dir: str = "projects"):
        self.employee_database = employee_database
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(parents=True, exist_ok=True)

    def save_project(self, project: dict) -> str:
        required = {"project_id", "required_skills", "project_hours", "deadline_days"}
        missing = required.difference(project)
        if missing:
            raise ValueError(f"Missing project fields: {', '.join(sorted(missing))}")

        project_id = str(project["project_id"]).strip()
        if not project_id:
            raise ValueError("project_id is required")
        project_path = self.project_dir / f"{project_id}.json"
        with project_path.open("w", encoding="utf-8") as file:
            json.dump(project, file, indent=2)
        self.refresh_project(project_id)
        return str(project_path)

    def load_project(self, project_id: str) -> dict:
        project_path = self.project_dir / f"{project_id}.json"
        with project_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def list_projects(self) -> list[dict]:
        projects = []
        for project_path in sorted(self.project_dir.glob("*.json")):
            with project_path.open("r", encoding="utf-8") as file:
                projects.append(json.load(file))
        return projects

    def refresh_all_projects(self) -> list[str]:
        refreshed = []
        for project in self.list_projects():
            csv_path = self.refresh_project(project["project_id"])
            if csv_path:
                refreshed.append(csv_path)
        return refreshed

    def _worker_records(self) -> list[dict]:
        records = self.employee_database.list_employees()
        return [
            {
                "employee_id": record.get("employee_id"),
                "name": record.get("full_name") or record.get("employee_id"),
                "skills": record.get("skills", []),
                "resume_text": record.get("resume_text", ""),
                "available_hours": float(record.get("availability_hours", 0.0)),
                "ability_score": float(record.get("ability_score", 0.5)),
                "utilization": float(record.get("utilization", 0.0)),
                "current_project": record.get("current_project"),
                "current_project_weight": record.get("current_project_weight"),
                "project_changes_last_30_days": int(record.get("project_changes_last_30_days", 0)),
                "days_on_current_project": int(record.get("days_on_current_project", 0)),
            }
            for record in records
        ]

    def refresh_project(self, project_id: str, output_path: Optional[str] = None) -> Optional[str]:
        project = self.load_project(project_id)
        workers = self._worker_records()
        if not workers:
            return None

        required_skills = [str(skill) for skill in project.get("required_skills", []) if str(skill).strip()]
        project_hours = float(project.get("project_hours", 0.0))
        deadline_days = int(project.get("deadline_days", 1))
        sla_risk = ResourceAllocationEngine.calculate_project_sla_risk(
            workers, required_skills, project_hours, deadline_days
        )
        project_weight = ResourceAllocationEngine.calculate_project_weight(
            investment=float(project.get("investment", 0.0)),
            roi=float(project.get("roi", 0.0)),
            client_tier=int(project.get("client_tier", 0)),
            sla_risk=int(round(sla_risk)),
            skill_criticality=float(project.get("skill_criticality", 0.0)),
            deadline_days=deadline_days,
            required_skill_count=len(required_skills),
            estimated_people=int(project.get("estimated_people", 0)),
            importance=float(project.get("importance", 0.0)),
        )
        project_for_selection = {**project, "sla_risk": sla_risk}
        selected = ResourceAllocationEngine.select_worker_for_project(
            workers,
            required_skills,
            project_hours,
            deadline_days,
            project_for_selection,
        )
        selected_name = selected.get("name") if selected else None
        ranked = ResourceAllocationEngine.rank_workers_by_semantic_fit(
            workers, required_skills, project_hours, deadline_days
        )
        workers_by_name = {worker["name"]: worker for worker in workers}
        csv_path = Path(output_path) if output_path else self.project_dir / f"{project_id}_ranked_employees.csv"
        csv_path = csv_path if csv_path.is_absolute() else Path(os.path.abspath(csv_path))

        fieldnames = [
            "rank", "project_id", "project_weight", "sla_risk", "employee_id",
            "employee_name", "semantic_match", "effective_hours", "projected_utilization",
            "final_score", "decision", "reason",
        ]
        with csv_path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            for rank, result in enumerate(ranked, start=1):
                worker = workers_by_name[result["name"]]
                available_hours = float(worker.get("available_hours", 0.0))
                utilization = float(worker.get("utilization", 0.0))
                projected_utilization = utilization + (
                    0.0 if available_hours <= 0 else project_hours / available_hours
                )
                if result["name"] == selected_name:
                    decision = selected["decision"]
                    reason = (
                        f"Selected for {decision}: semantic match {result['semantic_match']}, "
                        f"effective capacity {result['effective_hours']} hours, "
                        f"projected utilization {projected_utilization:.0%}, "
                        f"and project weight {project_weight:.2f}."
                    )
                else:
                    decision = "ranked_candidate"
                    reason = (
                        f"Ranked using semantic match {result['semantic_match']}, "
                        f"effective capacity {result['effective_hours']} hours, "
                        f"and current utilization {utilization:.0%}."
                    )
                writer.writerow({
                    "rank": rank,
                    "project_id": project_id,
                    "project_weight": round(project_weight, 2),
                    "sla_risk": sla_risk,
                    "employee_id": worker.get("employee_id", ""),
                    "employee_name": result["name"],
                    "semantic_match": result["semantic_match"],
                    "effective_hours": result["effective_hours"],
                    "projected_utilization": round(projected_utilization, 4),
                    "final_score": result["final_score"],
                    "decision": decision,
                    "reason": reason,
                })
        return str(csv_path)
