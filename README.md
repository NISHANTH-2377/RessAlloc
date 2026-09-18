# Resource Allocation Engine

A Python system that ranks employees for multiple ongoing projects using semantic resume matching and rule-based allocation safeguards.

## How It Works

1. Employee details are stored in SQLite at `employees/employee_records.db`.
2. PDF resumes in `employees/resume/` are converted to text.
3. Resume text is indexed in Qdrant using SentenceTransformers for semantic skill matching.
4. Projects are stored as JSON files in `projects/`.
5. Each project receives a separate employee ranking CSV.
6. Rankings consider skill fit, capacity, utilization, deadlines, project priority, burnout, and project-switching limits.

## Project Files

```text
employees/
  employee_database.py
  resume/
  employee_records.db
engine/
  engine.py
  vector_database.py
  RAG.py
projects/
  project_manager.py
main.py
```

## Project Ranking

Project weight considers:

- Investment and ROI
- Deadline urgency and SLA risk
- Required skill scope and criticality
- Approximate number of employees required
- Client tier and business importance

A worker is normally selected when they have suitable semantic skill relevance and enough effective capacity. Reassignment from another project is allowed only when the new project is significantly higher priority and the worker passes the safety rules.

Default safeguards:

- Maximum projected utilization: `85%`
- Maximum project changes in 30 days: `2`
- Minimum time on current project: `14 days`
- Reassignment priority multiplier: `1.5`

## Generated Project Files

For a project with ID `website_upgrade`, the system creates:

```text
projects/website_upgrade.json
projects/website_upgrade_ranked_employees.csv
```

The CSV contains rank, project weight, SLA risk, semantic match, effective hours, projected utilization, decision, and a human-readable reason.

## Run

Place PDF resumes in `employees/resume/`, then run:

```text
python main.py
```

The database script can synchronize resumes and refresh project rankings:

```text
python employees/employee_database.py
```

Run tests with:

```text
python -m unittest test_engine.py -v
```

The Qdrant service and the SentenceTransformers model must be available when semantic indexing or search is performed. Database initialization and tests do not load the embedding model until it is needed.
