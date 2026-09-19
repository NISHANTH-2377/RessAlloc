import db

def seed(reset: bool = True):
    print("Initializing database and seeding initial workforce data...")
    if reset:
        db.reset_database()
    else:
        db.init_db()

    # 1. Seed Employees
    employees = [
        {
            "employee_id": "EMP-001",
            "full_name": "Alex Rivera",
            "email": "alex.rivera@enginecorp.com",
            "phone": "+1 555-0101",
            "date_of_birth": "1992-04-15",
            "job_title": "Senior Full-Stack Engineer",
            "department": "Engineering",
            "location": "New York, USA",
            "years_experience": 8.0,
            "domain_knowledge": "Python, React, FastAPI, PostgreSQL, Docker, AWS",
            "seniority_tier": 3,
            "is_lead": 1,
            "current_project": "proj_cloud_migration",
            "current_project_weight": 85.0,
            "project_changes_last_30_days": 0,
            "days_on_current_project": 45,
            "availability_hours": 40.0,
            "ability_score": 0.92,
            "utilization": 0.85,
            "resume_path": None,
            "resume_status": "processed",
            "resume_text": "Alex Rivera: Senior Full-Stack Developer with 8 years building cloud architectures, microservices in Python FastAPI and React frontend dashboards. Expert in AWS, Docker, Kubernetes and scalable database designs.",
        },
        {
            "employee_id": "EMP-002",
            "full_name": "Marcus Brody",
            "email": "marcus.brody@enginecorp.com",
            "phone": "+1 555-0102",
            "date_of_birth": "1994-08-22",
            "job_title": "Senior Backend & Data Engineer",
            "department": "Engineering",
            "location": "Austin, USA",
            "years_experience": 6.5,
            "domain_knowledge": "Python, SQL, Microservices, Kafka, PostgreSQL, PyTorch",
            "seniority_tier": 3,
            "is_lead": 0,
            "current_project": None,  # On Bench!
            "current_project_weight": 0.0,
            "project_changes_last_30_days": 0,
            "days_on_current_project": 0,
            "availability_hours": 40.0,
            "ability_score": 0.95,
            "utilization": 0.0,
            "resume_path": None,
            "resume_status": "processed",
            "resume_text": "Marcus Brody: Senior Backend & Data Engineer with strong background in distributed systems, SQL, Python backend APIs, Kafka event streams, and relational data models. Currently available for immediate assignment.",
        },
        {
            "employee_id": "EMP-003",
            "full_name": "Elena Rostova",
            "email": "elena.rostova@enginecorp.com",
            "phone": "+1 555-0103",
            "date_of_birth": "1995-11-10",
            "job_title": "Lead UI/UX Designer & Frontend",
            "department": "Design & UI",
            "location": "San Francisco, USA",
            "years_experience": 7.0,
            "domain_knowledge": "Figma, React, TypeScript, CSS, Design Systems, HTML5",
            "seniority_tier": 3,
            "is_lead": 1,
            "current_project": "proj_fintech_portal",
            "current_project_weight": 110.0,
            "project_changes_last_30_days": 1,
            "days_on_current_project": 30,
            "availability_hours": 40.0,
            "ability_score": 0.90,
            "utilization": 0.90,
            "resume_path": None,
            "resume_status": "processed",
            "resume_text": "Elena Rostova: Lead UX Designer and Frontend Architect. Expert in modern Figma design systems, React UI components, CSS styling, responsive layout engineering and customer journey prototyping.",
        },
        {
            "employee_id": "EMP-004",
            "full_name": "Devon Vance",
            "email": "devon.vance@enginecorp.com",
            "phone": "+1 555-0104",
            "date_of_birth": "1993-02-28",
            "job_title": "DevOps & Cloud Architect",
            "department": "Infrastructure",
            "location": "Seattle, USA",
            "years_experience": 9.0,
            "domain_knowledge": "Kubernetes, Terraform, AWS, Docker, CI/CD, Linux, Go",
            "seniority_tier": 4,
            "is_lead": 1,
            "current_project": "proj_cloud_migration",
            "current_project_weight": 85.0,
            "project_changes_last_30_days": 0,
            "days_on_current_project": 60,
            "availability_hours": 40.0,
            "ability_score": 0.94,
            "utilization": 0.80,
            "resume_path": None,
            "resume_status": "processed",
            "resume_text": "Devon Vance: Staff SRE and Infrastructure Architect. Expert in Kubernetes cluster lifecycle, Terraform infrastructure as code, AWS cloud security, CI/CD automation pipelines.",
        },
        {
            "employee_id": "EMP-005",
            "full_name": "Priya Sharma",
            "email": "priya.sharma@enginecorp.com",
            "phone": "+1 555-0105",
            "date_of_birth": "1996-06-18",
            "job_title": "AI/ML Solutions Engineer",
            "department": "AI Research",
            "location": "Boston, USA",
            "years_experience": 5.0,
            "domain_knowledge": "Python, Machine Learning, PyTorch, NLP, Vector Search, SQL",
            "seniority_tier": 2,
            "is_lead": 0,
            "current_project": None,  # On Bench!
            "current_project_weight": 0.0,
            "project_changes_last_30_days": 0,
            "days_on_current_project": 0,
            "availability_hours": 40.0,
            "ability_score": 0.88,
            "utilization": 0.0,
            "resume_path": None,
            "resume_status": "processed",
            "resume_text": "Priya Sharma: Machine Learning Engineer with 5 years experience implementing NLP models, RAG vector search embeddings, PyTorch training pipelines, and data analytics workflows in Python.",
        },
        {
            "employee_id": "EMP-006",
            "full_name": "Sarah Chen",
            "email": "sarah.chen@enginecorp.com",
            "phone": "+1 555-0106",
            "date_of_birth": "1997-09-05",
            "job_title": "Frontend Software Engineer",
            "department": "Engineering",
            "location": "Chicago, USA",
            "years_experience": 4.0,
            "domain_knowledge": "React, JavaScript, HTML5, CSS, Redux, Jest",
            "seniority_tier": 2,
            "is_lead": 0,
            "current_project": None,  # On Bench!
            "current_project_weight": 0.0,
            "project_changes_last_30_days": 0,
            "days_on_current_project": 0,
            "availability_hours": 40.0,
            "ability_score": 0.85,
            "utilization": 0.0,
            "resume_path": None,
            "resume_status": "processed",
            "resume_text": "Sarah Chen: Frontend software engineer specialized in responsive React applications, modern CSS layouts, JavaScript state management, and test automation with Jest.",
        },
        {
            "employee_id": "EMP-007",
            "full_name": "Tariq Mansoor",
            "email": "tariq.m@enginecorp.com",
            "phone": "+1 555-0107",
            "date_of_birth": "1991-03-12",
            "job_title": "Principal Database Architect",
            "department": "Engineering",
            "location": "Dallas, USA",
            "years_experience": 11.0,
            "domain_knowledge": "SQL, PostgreSQL, Database Optimization, Python, Redis, Cloud",
            "seniority_tier": 4,
            "is_lead": 1,
            "current_project": "proj_fintech_portal",
            "current_project_weight": 110.0,
            "project_changes_last_30_days": 0,
            "days_on_current_project": 80,
            "availability_hours": 40.0,
            "ability_score": 0.97,
            "utilization": 0.95,
            "resume_path": None,
            "resume_status": "processed",
            "resume_text": "Tariq Mansoor: Principal Database Architect with over a decade optimizing high-throughput SQL engines, PostgreSQL sharding, multi-region replication and backend query plans.",
        }
    ]

    for emp in employees:
        db.upsert_employee(emp)
    print(f"Seeded {len(employees)} employees.")

    # 2. Seed Projects
    # Proj 1: High Risk Project (short deadline, heavy hours, unmet staffing, high investment)
    # Proj 2: Medium Risk Project
    # Proj 3: Low Risk Project (on track, well staffed)
    projects = [
        {
            "project_id": "proj_ecommerce_overhaul",
            "name": "E-Commerce Core Engine Upgrade",
            "client_tier": 5,
            "investment": 320000.0,
            "roi": 0.45,
            "skill_criticality": 4.5,
            "estimated_people": 4,
            "skill_staffing": {"Python": 2, "SQL": 1, "React": 1},
            "importance": 4.8,
            "required_skills": ["Python", "SQL", "Microservices", "PostgreSQL"],
            "project_hours": 380.0,
            "deadline_days": 12,  # Tight deadline -> high SLA risk!
            "completion_pct": 25,
            "status": "active",
            "description": "High-priority enterprise core overhaul converting monolithic billing to scalable microservices with strict 12-day launch SLA."
        },
        {
            "project_id": "proj_cloud_migration",
            "name": "Enterprise Cloud Native Migration",
            "client_tier": 4,
            "investment": 210000.0,
            "roi": 0.35,
            "skill_criticality": 3.8,
            "estimated_people": 3,
            "skill_staffing": {"AWS": 1, "Docker": 1, "Python": 1},
            "importance": 4.0,
            "required_skills": ["AWS", "Docker", "Kubernetes", "Python"],
            "project_hours": 240.0,
            "deadline_days": 28,
            "completion_pct": 60,
            "status": "active",
            "description": "Migrating legacy VM clusters into managed AWS Kubernetes infrastructure with automated continuous delivery."
        },
        {
            "project_id": "proj_fintech_portal",
            "name": "NextGen FinTech Client Portal",
            "client_tier": 5,
            "investment": 450000.0,
            "roi": 0.50,
            "skill_criticality": 4.2,
            "estimated_people": 3,
            "skill_staffing": {"React": 1, "SQL": 1, "Figma": 1},
            "importance": 4.9,
            "required_skills": ["React", "TypeScript", "SQL", "Figma"],
            "project_hours": 200.0,
            "deadline_days": 45,
            "completion_pct": 80,
            "status": "active",
            "description": "Premium customer-facing portfolio dashboard with real-time financial metrics and compliance reporting."
        }
    ]

    for proj in projects:
        db.save_project(proj)
    print(f"Seeded {len(projects)} projects.")

    # 3. Seed sample HR Requisition
    hr_requests = [
        {
            "request_id": "REQ-101",
            "project_id": "proj_ecommerce_overhaul",
            "role_title": "Senior Cloud Infrastructure Engineer",
            "required_skills": "Terraform, AWS, Kubernetes, Helm",
            "urgency": "High",
            "description": "Urgent hire needed for microservices infrastructure hardening and high availability setup.",
        }
    ]
    for req in hr_requests:
        db.create_hr_request(req)
    print(f"Seeded {len(hr_requests)} HR requests.")

    # 4. Seed sample Notifications
    db.create_notification(
        recipient_role="manager",
        title="Welcome to Resource Allocation Engine",
        message="System ready. Monitor active projects and review engine recommendations.",
        notif_type="info"
    )
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed()
