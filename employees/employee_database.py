import csv
import json
import os
import sqlite3
from concurrent.futures import ProcessPoolExecutor
from contextlib import contextmanager
from pathlib import Path
from typing import Optional


def _extract_pdf_text(pdf_path: str) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        try:
            from PyPDF2 import PdfReader
        except Exception:
            return ""

    try:
        reader = PdfReader(pdf_path)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        return ""


class EmployeeDatabase:
    def __init__(self, db_path: str = "employees/employee_records.db"):
        self.db_path = os.path.abspath(db_path)
        self.db_dir = os.path.dirname(self.db_path)
        self.ranking_context_path = os.path.join(self.db_dir, "ranking_context.json")
        self.ranked_csv_path = os.path.join(self.db_dir, "ranked_employees.csv")
        if self.db_dir:
            os.makedirs(self.db_dir, exist_ok=True)
        self.initialize_database()

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_database(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS employees (
                    employee_id TEXT PRIMARY KEY,
                    full_name TEXT,
                    email TEXT,
                    date_of_birth TEXT,
                    phone TEXT,
                    job_title TEXT,
                    department TEXT,
                    location TEXT,
                    years_experience REAL,
                    domain_knowledge TEXT,
                    seniority_tier INTEGER,
                    is_lead INTEGER DEFAULT 0,
                    current_project TEXT,
                    current_project_weight REAL,
                    project_changes_last_30_days INTEGER DEFAULT 0,
                    days_on_current_project INTEGER DEFAULT 0,
                    availability_hours REAL DEFAULT 0,
                    ability_score REAL DEFAULT 0.5,
                    utilization REAL DEFAULT 0.0,
                    resume_path TEXT,
                    resume_status TEXT DEFAULT 'not_processed',
                    resume_text TEXT,
                    raw_metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            existing_columns = {
                row[1] for row in conn.execute("PRAGMA table_info(employees)").fetchall()
            }
            for column_name, column_sql in {
                "date_of_birth": "date_of_birth TEXT",
                "domain_knowledge": "domain_knowledge TEXT",
                "current_project_weight": "current_project_weight REAL",
                "project_changes_last_30_days": "project_changes_last_30_days INTEGER DEFAULT 0",
                "days_on_current_project": "days_on_current_project INTEGER DEFAULT 0",
            }.items():
                if column_name not in existing_columns:
                    conn.execute(f"ALTER TABLE employees ADD COLUMN {column_sql}")

    def extract_resume_text_from_pdf(self, pdf_path: str) -> str:
        return _extract_pdf_text(pdf_path)

    def upsert_employee(
        self,
        employee_id: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None,
        date_of_birth: Optional[str] = None,
        phone: Optional[str] = None,
        job_title: Optional[str] = None,
        department: Optional[str] = None,
        location: Optional[str] = None,
        years_experience: Optional[float] = None,
        domain_knowledge: Optional[str] = None,
        seniority_tier: Optional[int] = None,
        is_lead: bool = False,
        current_project: Optional[str] = None,
        current_project_weight: Optional[float] = None,
        project_changes_last_30_days: int = 0,
        days_on_current_project: int = 0,
        availability_hours: float = 0.0,
        ability_score: float = 0.5,
        utilization: float = 0.0,
        resume_path: Optional[str] = None,
        resume_text: Optional[str] = None,
        raw_metadata: Optional[dict] = None,
        refresh_rankings: bool = True,
    ) -> None:
        if not employee_id:
            raise ValueError("employee_id is required")

        source_resume_text = resume_text or ""
        if resume_path and not source_resume_text:
            source_resume_text = self.extract_resume_text_from_pdf(resume_path)

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO employees (
                    employee_id, full_name, email, date_of_birth, phone, job_title, department, location,
                    years_experience, domain_knowledge, seniority_tier, is_lead, current_project, current_project_weight,
                    project_changes_last_30_days, days_on_current_project,
                    availability_hours, ability_score, utilization, resume_path,
                    resume_status, resume_text, raw_metadata, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(employee_id)
                DO UPDATE SET
                    full_name=excluded.full_name,
                    email=excluded.email,
                    date_of_birth=excluded.date_of_birth,
                    phone=excluded.phone,
                    job_title=excluded.job_title,
                    department=excluded.department,
                    location=excluded.location,
                    years_experience=excluded.years_experience,
                    domain_knowledge=excluded.domain_knowledge,
                    seniority_tier=excluded.seniority_tier,
                    is_lead=excluded.is_lead,
                    current_project=excluded.current_project,
                    current_project_weight=excluded.current_project_weight,
                    project_changes_last_30_days=excluded.project_changes_last_30_days,
                    days_on_current_project=excluded.days_on_current_project,
                    availability_hours=excluded.availability_hours,
                    ability_score=excluded.ability_score,
                    utilization=excluded.utilization,
                    resume_path=excluded.resume_path,
                    resume_status=excluded.resume_status,
                    resume_text=excluded.resume_text,
                    raw_metadata=excluded.raw_metadata,
                    updated_at=CURRENT_TIMESTAMP
                """,
                (
                    employee_id,
                    full_name,
                    email,
                    date_of_birth,
                    phone,
                    job_title,
                    department,
                    location,
                    years_experience,
                    domain_knowledge,
                    seniority_tier,
                    1 if is_lead else 0,
                    current_project,
                    current_project_weight,
                    project_changes_last_30_days,
                    days_on_current_project,
                    availability_hours,
                    ability_score,
                    utilization,
                    resume_path,
                    "processed" if source_resume_text or resume_path else "not_processed",
                    source_resume_text,
                    json.dumps(raw_metadata or {}, ensure_ascii=False),
                ),
            )
        if refresh_rankings:
            self.refresh_project_rankings()

    def refresh_project_rankings(self) -> list[str]:
        """Refresh every ongoing project's ranking after employee data changes."""
        from projects import ProjectAllocationManager

        return ProjectAllocationManager(self).refresh_all_projects()

    def set_ranking_context(self, context: dict) -> None:
        """Save the project request used for automatic CSV ranking refreshes."""
        required = {"required_skills", "project_hours", "deadline_days"}
        missing = required.difference(context)
        if missing:
            raise ValueError(f"Missing ranking context fields: {', '.join(sorted(missing))}")
        with open(self.ranking_context_path, "w", encoding="utf-8", newline="") as file:
            json.dump(context, file, indent=2)

    def refresh_ranked_employees_csv(self, output_path: Optional[str] = None) -> Optional[str]:
        """Regenerate the ranked employee CSV when a project context exists."""
        if not os.path.exists(self.ranking_context_path):
            return None

        with open(self.ranking_context_path, "r", encoding="utf-8") as file:
            context = json.load(file)

        employees = self.list_employees()
        if not employees:
            return None

        from engine import ResourceAllocationEngine

        workers = [
            {
                "employee_id": employee.get("employee_id"),
                "name": employee.get("full_name") or employee.get("employee_id"),
                "skills": employee.get("skills", []),
                "resume_text": employee.get("resume_text", ""),
                "available_hours": float(employee.get("availability_hours", 0.0)),
                "ability_score": float(employee.get("ability_score", 0.5)),
                "utilization": float(employee.get("utilization", 0.0)),
                "current_project": employee.get("current_project"),
                "current_project_weight": employee.get("current_project_weight"),
                "project_changes_last_30_days": int(employee.get("project_changes_last_30_days", 0)),
                "days_on_current_project": int(employee.get("days_on_current_project", 0)),
            }
            for employee in employees
        ]
        required_skills = list(context.get("required_skills", []))
        project_hours = float(context.get("project_hours", 0.0))
        deadline_days = int(context.get("deadline_days", 1))
        sla_risk = ResourceAllocationEngine.calculate_project_sla_risk(
            workers, required_skills, project_hours, deadline_days
        )
        project = {**context, "sla_risk": sla_risk}
        selected = ResourceAllocationEngine.select_worker_for_project(
            workers, required_skills, project_hours, deadline_days, project
        )
        selected_name = selected.get("name") if selected else None
        ranked = ResourceAllocationEngine.rank_workers_by_semantic_fit(
            workers, required_skills, project_hours, deadline_days
        )
        employee_by_name = {worker["name"]: worker for worker in workers}
        csv_path = os.path.abspath(output_path or self.ranked_csv_path)
        with open(csv_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "rank", "employee_id", "employee_name", "semantic_match",
                    "effective_hours", "projected_utilization", "final_score",
                    "decision", "reason",
                ],
            )
            writer.writeheader()
            for rank, result in enumerate(ranked, start=1):
                worker = employee_by_name.get(result["name"], {})
                available_hours = float(worker.get("available_hours", 0.0))
                utilization = float(worker.get("utilization", 0.0))
                projected_utilization = utilization + (
                    0.0 if available_hours == 0 else project_hours / available_hours
                )
                if result["name"] == selected_name:
                    decision = selected["decision"]
                    reason = (
                        f"Selected because semantic match was {result['semantic_match']}, "
                        f"effective capacity was {result['effective_hours']} hours, "
                        f"and projected utilization was {projected_utilization:.0%}."
                    )
                else:
                    decision = "ranked_candidate"
                    reason = (
                        f"Ranked by semantic match ({result['semantic_match']}), "
                        f"effective capacity ({result['effective_hours']} hours), "
                        f"and utilization ({utilization:.0%})."
                    )
                writer.writerow({
                    "rank": rank,
                    "employee_id": worker.get("employee_id", ""),
                    "employee_name": result["name"],
                    "semantic_match": result["semantic_match"],
                    "effective_hours": result["effective_hours"],
                    "projected_utilization": round(projected_utilization, 4),
                    "final_score": result["final_score"],
                    "decision": decision,
                    "reason": reason,
                })
        return csv_path

    def sync_resume_directory(
        self,
        resume_dir: str = "employees/resume",
        max_workers: Optional[int] = None,
    ) -> list[str]:
        resume_path = Path(resume_dir)
        if not resume_path.exists():
            resume_path.mkdir(parents=True, exist_ok=True)

        pdf_files = sorted(resume_path.glob("*.pdf"))
        resume_texts = []
        if pdf_files:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                resume_texts = list(executor.map(_extract_pdf_text, (str(path) for path in pdf_files)))

        imported_files = []
        for pdf_file, text in zip(pdf_files, resume_texts):
            full_name = pdf_file.stem.replace("_", " ").replace("-", " ").strip()
            employee_id = pdf_file.stem
            self.upsert_employee(
                employee_id=employee_id,
                full_name=full_name,
                resume_path=str(pdf_file),
                resume_text=text,
                raw_metadata={"filename": pdf_file.name, "resume_dir": str(resume_path)},
                refresh_rankings=False,
            )
            imported_files.append(str(pdf_file))
        self.refresh_ranked_employees_csv()
        return imported_files

    def get_employee(self, employee_id: str):
        self.refresh_project_rankings()
        with self._connect() as conn:
            employee = conn.execute(
                "SELECT * FROM employees WHERE employee_id = ?",
                (employee_id,),
            ).fetchone()
            if not employee:
                return None
            return dict(employee)

    def list_employees(self) -> list[dict]:
        with self._connect() as conn:
            employees = conn.execute("SELECT * FROM employees ORDER BY full_name").fetchall()
            return [dict(employee) for employee in employees]


if __name__ == "__main__":
    db = EmployeeDatabase()
    imported = db.sync_resume_directory("employees/resume")
    print(f"Employee database initialized at: {db.db_path}")
    print(f"Resumes scanned: {len(imported)}")
    if imported:
        print("Imported files:")
        for path in imported:
            print(f" - {path}")
    else:
        print("No PDF resumes found in employees/resume yet.")
    refreshed = db.refresh_project_rankings()
    if refreshed:
        print(f"Project ranking CSVs updated: {len(refreshed)}")
    if db.refresh_ranked_employees_csv():
        print(f"Ranked employee CSV updated at: {db.ranked_csv_path}")
