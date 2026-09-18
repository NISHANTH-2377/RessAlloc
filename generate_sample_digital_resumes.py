import os
import random
from fpdf import FPDF

def create_sample_digital_resumes():
    resume_dir = "employees/resume"
    os.makedirs(resume_dir, exist_ok=True)

    names = [
        "Alexander Wright", "Sophia Martinez", "Liam Johnson", "Emma Watson",
        "Noah Brown", "Olivia Davis", "Ethan Wilson", "Ava Taylor",
        "Mason Anderson", "Isabella Thomas", "Lucas Jackson", "Mia White",
        "Oliver Harris", "Amelia Martin", "Elijah Thompson", "Harper Garcia",
        "James Martinez", "Evelyn Robinson", "Benjamin Clark", "Abigail Rodriguez",
        "Logan Lewis", "Emily Lee", "Jacob Walker", "Elizabeth Hall",
        "Michael Allen", "Sofia Young", "Daniel Hernandez", "Avery King",
        "Henry Wright", "Ella Lopez", "Jackson Hill", "Scarlett Scott",
        "Sebastian Green", "Grace Adams", "Aiden Baker", "Chloe Gonzalez",
        "Matthew Nelson", "Victoria Carter", "Samuel Mitchell", "Riley Perez",
        "David Roberts", "Aria Turner", "Joseph Phillips", "Lily Campbell",
        "Carter Parker", "Aubrey Evans", "Owen Edwards", "Zoey Collins",
        "Wyatt Stewart", "Penelope Sanchez"
    ]

    domains = [
        ("Java", "Spring Boot", "Microservices", "SQL", "REST API", "Docker", "Kafka"),
        ("Python", "Django", "FastAPI", "PostgreSQL", "Redis", "AWS", "Celery"),
        ("React", "TypeScript", "Node.js", "GraphQL", "Tailwind CSS", "Next.js"),
        ("Java", "Spring Cloud", "Kubernetes", "PostgreSQL", "gRPC", "JUnit"),
        ("Data Engineering", "Python", "PySpark", "Snowflake", "SQL", "Airflow", "AWS"),
        ("DevOps", "Kubernetes", "Terraform", "Docker", "CI/CD", "AWS", "Prometheus"),
        ("Full Stack Java", "Java", "Spring Boot", "React", "SQL", "Docker"),
        ("Backend Engineer", "Java", "Hibernate", "Spring Security", "PostgreSQL", "Redis"),
    ]

    print(f"Generating {len(names)} digital text-based PDF resumes...")

    for i, name in enumerate(names, start=1):
        emp_id = f"emp_text_{i:03d}"
        role_type, *skills = random.choice(domains)
        exp_years = random.randint(3, 12)
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, f"Resume - {name}", new_x="LMARGIN", new_y="NEXT", align="L")
        
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, f"Role: {role_type} | Experience: {exp_years} Years", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.cell(0, 8, f"Email: {name.lower().replace(' ', '.')}@techcorp.com", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Core Technical Skills:", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 8, ", ".join(skills), new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.ln(5)

        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 8, "Professional Experience Summary:", new_x="LMARGIN", new_y="NEXT", align="L")
        pdf.set_font("Helvetica", "", 11)
        summary_text = (
            f"Experienced {role_type} with {exp_years} years of expertise building scalable enterprise applications. "
            f"Proficient in {', '.join(skills[:4])}. Demonstrated track record of optimizing system throughput, "
            "designing REST APIs, managing database migrations, and implementing automated testing suites."
        )
        pdf.multi_cell(0, 6, summary_text)
        
        pdf_path = os.path.join(resume_dir, f"{emp_id}.pdf")
        pdf.output(pdf_path)

    print(f"[SUCCESS] Created {len(names)} digital text-based PDFs in {resume_dir}.")

if __name__ == "__main__":
    create_sample_digital_resumes()
