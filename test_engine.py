import unittest
import csv
import os
import tempfile

from employees.employee_database import EmployeeDatabase
from projects import ProjectAllocationManager

try:
    from engine import ResourceAllocationEngine
except Exception as exc:  # pragma: no cover
    ResourceAllocationEngine = None
    ENGINE_IMPORT_ERROR = exc
else:
    ENGINE_IMPORT_ERROR = None

try:
    from engine import vector_database
except Exception as exc:  # pragma: no cover
    vector_database = None
    DATABASE_IMPORT_ERROR = exc
else:
    DATABASE_IMPORT_ERROR = None

try:
    from engine import RAG
except Exception as exc:  # pragma: no cover
    RAG = None
    RAG_IMPORT_ERROR = exc
else:
    RAG_IMPORT_ERROR = None


class TestResourceAllocationEngine(unittest.TestCase):
    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_project_weight_includes_skill_factor(self):
        weight = ResourceAllocationEngine.calculate_project_weight(
            investment=100000,
            roi=0.25,
            client_tier=3,
            sla_risk=2,
            skill_criticality=1.5,
        )
        self.assertIsInstance(weight, float)
        self.assertGreater(weight, 0)

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_project_sla_risk_uses_team_capacity_and_deadline(self):
        workers = [
            {"name": "Ana", "skills": ["python", "sql"], "available_hours": 30, "ability_score": 0.9, "utilization": 0.7},
            {"name": "Ben", "skills": ["sql"], "available_hours": 20, "ability_score": 0.6, "utilization": 0.8},
        ]
        risk = ResourceAllocationEngine.calculate_project_sla_risk(
            workers=workers,
            required_skills=["python", "sql"],
            project_hours=120,
            deadline_days=5,
        )
        self.assertGreater(risk, 0)
        self.assertLessEqual(risk, 100)

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_project_slack(self):
        slack = ResourceAllocationEngine.evaluate_active_project_slack(40, 100)
        self.assertEqual(slack, 60.0)

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_cost_penalty(self):
        penalty = ResourceAllocationEngine.compute_cost_to_skill_penalty(5, 3)
        self.assertEqual(penalty, 3.0)

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_semantic_worker_ranking_uses_similarity(self):
        workers = [
            {
                "name": "Alice",
                "skills": ["python", "sql", "fastapi"],
                "resume_text": "Senior backend engineer with Python, SQL, FastAPI, and API design experience.",
                "available_hours": 30,
                "ability_score": 0.9,
                "utilization": 0.2,
            },
            {
                "name": "Bob",
                "skills": ["java", "spring"],
                "resume_text": "Java developer focused on Spring ecosystem and enterprise apps.",
                "available_hours": 35,
                "ability_score": 0.8,
                "utilization": 0.1,
            },
        ]
        ranked = ResourceAllocationEngine.rank_workers_by_semantic_fit(
            workers=workers,
            required_skills=["python", "sql", "backend api development"],
            project_hours=80,
            deadline_days=10,
        )
        self.assertTrue(ranked)
        self.assertEqual(ranked[0]["name"], "Alice")
        self.assertGreater(ranked[0]["semantic_match"], 0.0)

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_available_worker_is_preferred_over_occupied_worker(self):
        workers = [
            {
                "name": "Occupied Specialist",
                "skills": ["python", "data engineering"],
                "resume_text": "Python data engineering specialist",
                "available_hours": 40,
                "ability_score": 1.0,
                "utilization": 0.2,
                "current_project": "Legacy Project",
                "current_project_weight": 100000.0,
            },
            {
                "name": "Available Engineer",
                "skills": ["python", "data engineering"],
                "resume_text": "Python data engineering engineer",
                "available_hours": 40,
                "ability_score": 1.0,
                "utilization": 0.0,
            },
        ]
        selected = ResourceAllocationEngine.select_worker_for_project(
            workers=workers,
            required_skills=["python", "data engineering"],
            project_hours=20,
            deadline_days=10,
            new_project={"investment": 500000, "roi": 0.8, "client_tier": 3, "sla_risk": 5},
        )
        self.assertEqual(selected["name"], "Available Engineer")
        self.assertEqual(selected["decision"], "assign_available_worker")

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_occupied_worker_requires_greatly_higher_project_weight(self):
        workers = [{
            "name": "Specialist",
            "skills": ["python"],
            "resume_text": "Python specialist",
            "available_hours": 40,
            "ability_score": 1.0,
            "utilization": 0.2,
            "current_project": "Current Project",
            "current_project_weight": 100.0,
        }]
        selected = ResourceAllocationEngine.select_worker_for_project(
            workers=workers,
            required_skills=["python"],
            project_hours=20,
            deadline_days=10,
            new_project={"investment": 1000, "roi": 1.0, "client_tier": 1, "sla_risk": 1},
        )
        self.assertIsNotNone(selected)
        self.assertEqual(selected["decision"], "reassign_occupied_worker")

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_burnout_threshold_rejects_overloaded_worker(self):
        worker = {
            "name": "Overloaded Specialist",
            "skills": ["python"],
            "resume_text": "Python specialist",
            "available_hours": 40,
            "ability_score": 1.0,
            "utilization": 0.6,
        }
        selected = ResourceAllocationEngine.select_worker_for_project(
            workers=[worker],
            required_skills=["python"],
            project_hours=20,
            deadline_days=10,
            new_project={"investment": 1000, "roi": 1.0},
            burnout_threshold=0.85,
        )
        self.assertIsNone(selected)

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_burnout_threshold_allows_safe_assignment(self):
        worker = {
            "name": "Available Specialist",
            "skills": ["python"],
            "resume_text": "Python specialist",
            "available_hours": 40,
            "ability_score": 1.0,
            "utilization": 0.2,
        }
        selected = ResourceAllocationEngine.select_worker_for_project(
            workers=[worker],
            required_skills=["python"],
            project_hours=20,
            deadline_days=10,
            new_project={"investment": 1000, "roi": 1.0},
            burnout_threshold=0.85,
        )
        self.assertEqual(selected["name"], "Available Specialist")
        self.assertEqual(selected["projected_utilization"], 0.7)

    @unittest.skipIf(ResourceAllocationEngine is None, "engine import failed")
    def test_project_switch_frequency_blocks_reassignment(self):
        worker = {
            "name": "Frequently Reassigned Specialist",
            "skills": ["python"],
            "resume_text": "Python specialist",
            "available_hours": 40,
            "ability_score": 1.0,
            "utilization": 0.1,
            "current_project": "Current Project",
            "current_project_weight": 100.0,
            "project_changes_last_30_days": 2,
            "days_on_current_project": 30,
        }
        selected = ResourceAllocationEngine.select_worker_for_project(
            workers=[worker],
            required_skills=["python"],
            project_hours=10,
            deadline_days=10,
            new_project={"investment": 1000, "roi": 1.0},
        )
        self.assertIsNone(selected)


class TestDatabaseLayer(unittest.TestCase):
    @unittest.skipIf(vector_database is None, "database import failed")
    def test_database_wrapper_initializes(self):
        store = vector_database.WorkforceVectorStore(host="localhost", port=6333)
        self.assertEqual(store.collection_name, "employee_workforce")
        self.assertIsNotNone(store.client)

    def test_resume_does_not_override_manual_employee_details(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            db_path = tmp.name
        db = EmployeeDatabase(db_path=db_path)

        resume_text = """
        Jane Smith
        Email: jane.smith@gmail.com
        Date of Birth: 1992-05-14
        7 years of experience in Python, SQL, and cloud architecture.
        Domain knowledge: fintech, banking, data engineering.
        """

        db.upsert_employee(
            employee_id="emp_100",
            full_name="Manual Employee",
            email="manual@example.com",
            date_of_birth="1988-01-20",
            years_experience=12.0,
            domain_knowledge="Insurance",
            resume_text=resume_text,
        )

        employee = db.get_employee("emp_100")
        self.assertEqual(employee["full_name"], "Manual Employee")
        self.assertEqual(employee["email"], "manual@example.com")
        self.assertEqual(employee["date_of_birth"], "1988-01-20")
        self.assertEqual(employee["years_experience"], 12.0)
        self.assertEqual(employee["domain_knowledge"], "Insurance")
        self.assertIn("Python", employee["resume_text"])

        if os.path.exists(db_path):
            try:
                os.remove(db_path)
            except PermissionError:
                pass

    def test_ranked_employee_csv_contains_reason_and_dynamic_rank(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            db = EmployeeDatabase(db_path=os.path.join(temp_dir, "records.db"))
            db.upsert_employee(
                employee_id="emp_200",
                full_name="CSV Candidate",
                availability_hours=40,
                ability_score=1.0,
                resume_text="Python backend API development",
            )
            manager = ProjectAllocationManager(db, project_dir=os.path.join(temp_dir, "projects"))
            manager.save_project({
                "project_id": "project_csv",
                "required_skills": ["python backend"],
                "project_hours": 10,
                "deadline_days": 10,
                "investment": 1000,
                "roi": 0.5,
                "client_tier": 2,
                "skill_criticality": 1,
                "estimated_people": 1,
                "importance": 3,
            })
            csv_path = manager.refresh_project("project_csv")

            with open(csv_path, "r", encoding="utf-8", newline="") as file:
                rows = list(csv.DictReader(file))
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["rank"], "1")
            self.assertEqual(rows[0]["employee_name"], "CSV Candidate")
            self.assertTrue(rows[0]["reason"])


class TestRAGLayer(unittest.TestCase):
    @unittest.skipIf(RAG is None, "RAG import failed")
    def test_rag_pipeline_can_be_created(self):
        pipeline = RAG.WorkforceRAGPipeline(qdrant_client=None, collection_name="employee_workforce")
        self.assertEqual(pipeline.collection_name, "employee_workforce")


if __name__ == "__main__":
    print("Testing engine modules...")
    if ENGINE_IMPORT_ERROR:
        print(f"engine import failed: {ENGINE_IMPORT_ERROR}")
    if DATABASE_IMPORT_ERROR:
        print(f"database import failed: {DATABASE_IMPORT_ERROR}")
    if RAG_IMPORT_ERROR:
        print(f"RAG import failed: {RAG_IMPORT_ERROR}")

    unittest.main(verbosity=2)
