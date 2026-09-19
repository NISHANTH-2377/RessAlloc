import csv
import json
import os
from pathlib import Path
from typing import Optional

from engine import ResourceAllocationEngine


class ProjectAllocationManager:
    """Stores ongoing projects and writes one ranked employee CSV per project."""

    def __init__(self, employee_database, project_dir: Optional[str] = None):
        self.employee_database = employee_database
        if project_dir is None or project_dir == "projects":
            # Dynamically anchor relative to employee_database.db_dir or repository root
            base_dir = Path(getattr(employee_database, "db_dir", Path(__file__).resolve().parent.parent))
            if base_dir.name == "employees":
                self.project_dir = (base_dir.parent / "projects").resolve()
            else:
                self.project_dir = (base_dir / "projects").resolve()
        else:
            self.project_dir = Path(project_dir).resolve()
        self.project_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _normalize_project_id(project_id: str) -> str:
        clean_id = str(project_id).strip()
        if clean_id.endswith(".json"):
            clean_id = clean_id[:-5]
        if "java_recruitment" in clean_id:
            clean_id = clean_id.replace("java_recruitment", "recruitment")
        return clean_id

    def save_project(self, project: dict) -> str:
        required = {"project_id", "required_skills", "project_hours", "deadline_days"}
        missing = required.difference(project)
        if missing:
            raise ValueError(f"Missing project fields: {', '.join(sorted(missing))}")

        project_id = self._normalize_project_id(project["project_id"])
        if not project_id:
            raise ValueError("project_id is required")
        project["project_id"] = project_id
        
        # Save as recruitment.json (or {project_id}.json)
        project_path = self.project_dir / f"{project_id}.json"
        with project_path.open("w", encoding="utf-8") as file:
            json.dump(project, file, indent=2)

        # Clean up legacy java_recruitment file if migrating
        if "recruitment" in project_id:
            legacy_name = project_id.replace("recruitment", "java_recruitment")
            legacy_file = self.project_dir / f"{legacy_name}.json"
            if legacy_file.exists() and legacy_file != project_path:
                legacy_file.unlink(missing_ok=True)

        self.refresh_project(project_id)
        return str(project_path)

    def load_project(self, project_id: str) -> dict:
        project_id = self._normalize_project_id(project_id)
        project_path = self.project_dir / f"{project_id}.json"
        # If loading legacy file, redirect to normalized project
        if not project_path.exists() and "recruitment" in project_id:
            legacy_name = project_id.replace("recruitment", "java_recruitment")
            legacy_file = self.project_dir / f"{legacy_name}.json"
            if legacy_file.exists():
                project_path = legacy_file
        with project_path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def delete_project(self, project_id: str) -> bool:
        normalized_id = self._normalize_project_id(project_id)
        candidates = [project_id, normalized_id]
        if "recruitment" in project_id:
            candidates.append(project_id.replace("recruitment", "java_recruitment"))
            candidates.append("recruitment")
            candidates.append("java_recruitment")

        deleted = False
        for pid in set(candidates):
            j_path = self.project_dir / f"{pid}.json"
            c_path = self.project_dir / f"{pid}_ranked_employees.csv"
            if j_path.exists():
                try:
                    j_path.unlink(missing_ok=True)
                    deleted = True
                except Exception:
                    pass
            if c_path.exists():
                try:
                    c_path.unlink(missing_ok=True)
                    deleted = True
                except Exception:
                    pass
        return deleted

    def get_ranked_csv_path(self, project_id: str) -> Path:
        project_id = self._normalize_project_id(project_id)
        return self.project_dir / f"{project_id}_ranked_employees.csv"

    def load_ranked_csv(self, project_id: str) -> list[dict]:
        project_id = self._normalize_project_id(project_id)
        csv_path = self.get_ranked_csv_path(project_id)
        if not csv_path.exists():
            self.refresh_project(project_id)
        if not csv_path.exists():
            return []
        with csv_path.open("r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            return list(reader)

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
        worker_list = []
        for record in records:
            skills = record.get("skills") or []
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(",") if s.strip()]
            if not skills and record.get("domain_knowledge"):
                skills = [s.strip() for s in str(record["domain_knowledge"]).split(",") if s.strip()]

            worker_list.append({
                "employee_id": record.get("employee_id"),
                "name": record.get("full_name") or record.get("employee_id"),
                "skills": skills,
                "domain_knowledge": record.get("domain_knowledge", ""),
                "job_title": record.get("job_title", ""),
                "resume_text": record.get("resume_text", ""),
                "available_hours": float(record.get("availability_hours", 0.0)),
                "ability_score": float(record.get("ability_score", 0.5)),
                "utilization": float(record.get("utilization", 0.0)),
                "current_project": record.get("current_project"),
                "current_project_weight": record.get("current_project_weight"),
                "project_changes_last_30_days": int(record.get("project_changes_last_30_days", 0)),
                "days_on_current_project": int(record.get("days_on_current_project", 0)),
            })
        return worker_list

    def refresh_project(self, project_id: str, output_path: Optional[str] = None) -> Optional[str]:
        project_id = self._normalize_project_id(project_id)
        project = self.load_project(project_id)
        workers = self._worker_records()
        if not workers:
            return None

        required_skills = [str(skill) for skill in project.get("required_skills", []) if str(skill).strip()]
        skill_staffing = {
            str(skill): max(0, int(count))
            for skill, count in project.get("skill_staffing", {}).items()
            if str(skill).strip()
        }
        skill_people_count = sum(skill_staffing.values())
        estimated_people = max(
            int(project.get("estimated_people", 0)),
            skill_people_count,
        )
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
            estimated_people=estimated_people,
            skill_people_count=skill_people_count,
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
        # Generate ranked CSV (e.g., recruitment_ranked_employees.csv)
        csv_path = Path(output_path) if output_path else self.project_dir / f"{project_id}_ranked_employees.csv"
        csv_path = csv_path if csv_path.is_absolute() else Path(os.path.abspath(csv_path))

        # Clean up legacy CSV if migrating
        if "recruitment" in project_id:
            legacy_name = project_id.replace("recruitment", "java_recruitment")
            legacy_csv = self.project_dir / f"{legacy_name}_ranked_employees.csv"
            if legacy_csv.exists() and legacy_csv != csv_path:
                legacy_csv.unlink(missing_ok=True)

        fieldnames = [
            "rank", "project_id", "project_weight", "sla_risk", "employee_id",
            "estimated_people", "skill_staffing",
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
                    "estimated_people": estimated_people,
                    "skill_staffing": json.dumps(skill_staffing, sort_keys=True),
                    "employee_name": result["name"],
                    "semantic_match": result["semantic_match"],
                    "effective_hours": result["effective_hours"],
                    "projected_utilization": round(projected_utilization, 4),
                    "final_score": result["final_score"],
                    "decision": decision,
                    "reason": reason,
                })
        return str(csv_path)
