import unittest
import json
import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app import app
import db

class TestResAllocAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        db.init_db()

    def test_01_get_projects(self):
        resp = self.client.get("/api/projects")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        # Verify SLA risk and risk_level are populated
        first = data[0]
        self.assertIn("sla_risk", first)
        self.assertIn("risk_level", first)

    def test_02_get_recommendations(self):
        resp = self.client.get("/api/projects/proj_ecommerce_overhaul/recommendations")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["project_id"], "proj_ecommerce_overhaul")
        self.assertEqual(data["risk_level"], "High")
        self.assertIn("headcount_needed", data)
        self.assertIn("best_candidate", data)
        self.assertIsNotNone(data["best_candidate"])
        self.assertIn("reason", data["best_candidate"])
        self.assertIn("ranked_candidates", data)
        self.assertGreater(len(data["ranked_candidates"]), 0)

    def test_03_direct_assign_bench_worker(self):
        # Marcus Brody is on bench (EMP-002)
        resp = self.client.post("/api/projects/proj_ecommerce_overhaul/assign", json={
            "employee_id": "EMP-002"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "assigned_directly")
        # Verify DB updated
        emp = db.get_employee("EMP-002")
        self.assertEqual(emp["current_project"], "proj_ecommerce_overhaul")

    def test_04_transfer_offer_occupied_worker(self):
        # Alex Rivera is on proj_cloud_migration (EMP-001)
        resp = self.client.post("/api/projects/proj_fintech_portal/assign", json={
            "employee_id": "EMP-001"
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "transfer_offer_sent")
        self.assertIn("offer_id", data)

        # Check pending transfer offer in DB
        pending = db.get_pending_transfer_offer("EMP-001")
        self.assertIsNotNone(pending)
        self.assertEqual(pending["to_project"], "proj_fintech_portal")

    def test_05_employee_transfer_decline_with_reason(self):
        pending = db.get_pending_transfer_offer("EMP-001")
        self.assertIsNotNone(pending)

        # Try decline without reason -> should fail 400
        fail_resp = self.client.post("/api/employees/EMP-001/transfer-response", json={
            "offer_id": pending["offer_id"],
            "action": "decline",
            "reason": ""
        })
        self.assertEqual(fail_resp.status_code, 400)

        # Decline with valid reason -> should succeed
        resp = self.client.post("/api/employees/EMP-001/transfer-response", json={
            "offer_id": pending["offer_id"],
            "action": "decline",
            "reason": "Currently leading architecture sprint on Cloud Migration, cannot context switch."
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "declined")

        # Verify manager received notification with the reason
        notifs = db.list_notifications(recipient_role="manager")
        declined_notifs = [n for n in notifs if n["type"] == "transfer_declined"]
        self.assertGreater(len(declined_notifs), 0)
        self.assertIn("Currently leading architecture sprint", declined_notifs[0]["message"])

    def test_06_hr_requisition_and_talent(self):
        # Create HR Request
        req_resp = self.client.post("/api/hr/requests", json={
            "project_id": "proj_ecommerce_overhaul",
            "role_title": "Senior React Frontend Lead",
            "required_skills": "React, TypeScript, Redux, Webpack",
            "urgency": "High",
            "description": "Urgent hire for responsive checkout flow"
        })
        self.assertEqual(req_resp.status_code, 201)
        
        # Check list HR requests
        list_resp = self.client.get("/api/hr/requests")
        self.assertEqual(list_resp.status_code, 200)
        self.assertGreaterEqual(len(list_resp.get_json()), 1)

        # Add Employee by HR
        add_resp = self.client.post("/api/employees", json={
            "employee_id": "EMP-999",
            "full_name": "Jordan Cole",
            "email": "jordan.c@enginecorp.com",
            "phone": "+1 555-9999",
            "job_title": "React Frontend Specialist",
            "department": "Engineering",
            "location": "Denver, USA",
            "years_experience": 5.0,
            "domain_knowledge": "React, TypeScript, Redux",
            "seniority_tier": 2,
            "availability_hours": 40.0,
            "ability_score": 0.88,
            "resume_text": "Jordan Cole: Senior frontend specialist with expertise in React, Redux and modern UI engineering."
        })
        self.assertEqual(add_resp.status_code, 201)

        # Verify HR can update and delete
        upd_resp = self.client.put("/api/employees/EMP-999", json={"location": "Boulder, USA"})
        self.assertEqual(upd_resp.status_code, 200)
        self.assertEqual(upd_resp.get_json()["employee"]["location"], "Boulder, USA")

        del_resp = self.client.delete("/api/employees/EMP-999")
        self.assertEqual(del_resp.status_code, 200)
        self.assertIsNone(db.get_employee("EMP-999"))

    def test_07_auth_login_all_roles(self):
        # Manager login
        resp_mgr = self.client.post("/api/auth/login", json={"username": "manager", "password": "password123", "role": "manager"})
        self.assertEqual(resp_mgr.status_code, 200)
        self.assertEqual(resp_mgr.get_json()["user"]["role"], "manager")

        # HR login
        resp_hr = self.client.post("/api/auth/login", json={"username": "hr", "password": "password123", "role": "hr"})
        self.assertEqual(resp_hr.status_code, 200)
        self.assertEqual(resp_hr.get_json()["user"]["role"], "hr")

        # Employee login by ID
        resp_emp = self.client.post("/api/auth/login", json={"username": "EMP-001", "password": "password123", "role": "employee"})
        self.assertEqual(resp_emp.status_code, 200)
        self.assertEqual(resp_emp.get_json()["user"]["role"], "employee")
        self.assertEqual(resp_emp.get_json()["user"]["employee_id"], "EMP-001")

        # Employee login by alias/username
        resp_emp2 = self.client.post("/api/auth/login", json={"username": "marcus", "password": "password123", "role": "employee"})
        self.assertEqual(resp_emp2.status_code, 200)
        self.assertEqual(resp_emp2.get_json()["user"]["role"], "employee")

    def test_08_auth_invalid_credentials(self):
        resp = self.client.post("/api/auth/login", json={"username": "manager", "password": "wrongpassword"})
        self.assertEqual(resp.status_code, 401)

    def test_09_dismiss_notification_persists_without_affecting_project(self):
        # 1. Create a test notification
        db.create_notification(
            recipient_role="employee",
            recipient_id="EMP-002",
            title="Test Dismiss Notification",
            message="This notification should be dismissed without changing assignments.",
            notif_type="info"
        )

        notifs = db.list_notifications(recipient_role="employee", recipient_id="EMP-002")
        test_notif = next((n for n in notifs if n["title"] == "Test Dismiss Notification"), None)
        self.assertIsNotNone(test_notif)
        notif_id = test_notif["id"]

        # Record employee project state before dismiss
        emp_before = db.get_employee("EMP-002")
        proj_before = emp_before["current_project"]

        # 2. Call dismiss endpoint
        dismiss_resp = self.client.post(f"/api/notifications/{notif_id}/dismiss")
        self.assertEqual(dismiss_resp.status_code, 200)

        # 3. Verify notification is no longer in list_notifications (persists in DB as dismissed)
        notifs_after = db.list_notifications(recipient_role="employee", recipient_id="EMP-002")
        self.assertIsNone(next((n for n in notifs_after if n["id"] == notif_id), None))

        # 4. Verify employee assignment was NOT touched
        emp_after = db.get_employee("EMP-002")
        self.assertEqual(emp_after["current_project"], proj_before)

    def test_10_hr_requisition_fulfillment_and_lifecycle(self):
        # 1. Create a specific hiring request
        req_resp = self.client.post("/api/hr/requests", json={
            "project_id": "proj_ecommerce_overhaul",
            "role_title": "Kubernetes Site Reliability Lead",
            "required_skills": "Kubernetes, Go, Prometheus",
            "urgency": "Critical",
            "description": "Cluster reliability expert required"
        })
        self.assertEqual(req_resp.status_code, 201)
        req_id = req_resp.get_json()["request"]["request_id"]

        # 2. Verify it appears in pending requests
        pending_resp = self.client.get("/api/hr/requests?status=pending")
        self.assertEqual(pending_resp.status_code, 200)
        pending_ids = [r["request_id"] for r in pending_resp.get_json()]
        self.assertIn(req_id, pending_ids)

        # 3. Onboard a new employee that fulfills this requisition
        add_resp = self.client.post("/api/employees", json={
            "employee_id": "EMP-SRE-01",
            "full_name": "Taylor Swiftly",
            "job_title": "Kubernetes Site Reliability Lead",
            "department": "Infrastructure",
            "fulfills_request_id": req_id,
            "years_experience": 6.0,
            "domain_knowledge": "Kubernetes, Go, Prometheus",
            "seniority_tier": 4,
            "availability_hours": 40.0
        })
        self.assertEqual(add_resp.status_code, 201)
        self.assertEqual(add_resp.get_json().get("fulfilled_requisition_id"), req_id)

        # 4. Verify the requisition has vanished from pending requests
        pending_after = self.client.get("/api/hr/requests?status=pending")
        pending_after_ids = [r["request_id"] for r in pending_after.get_json()]
        self.assertNotIn(req_id, pending_after_ids)

        # 5. Verify manual PUT status update and DELETE
        req_resp2 = self.client.post("/api/hr/requests", json={
            "role_title": "Temporary Graphic Designer",
            "urgency": "Low"
        })
        req2_id = req_resp2.get_json()["request"]["request_id"]

        put_resp = self.client.put(f"/api/hr/requests/{req2_id}", json={"status": "fulfilled"})
        self.assertEqual(put_resp.status_code, 200)
        self.assertEqual(put_resp.get_json()["status"], "fulfilled")

        del_resp = self.client.delete(f"/api/hr/requests/{req2_id}")
        self.assertEqual(del_resp.status_code, 200)
        self.assertIsNone(db.get_hr_request(req2_id))

        # Cleanup test employee
        db.delete_employee("EMP-SRE-01")

if __name__ == "__main__":
    unittest.main()
