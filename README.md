# Resource Allocation Engine

A Python resource-allocation system for organizations running multiple projects at the same time. It uses resume text and vector search to find semantically suitable employees, then applies deterministic business rules to rank and select workers safely.

The system is intentionally hybrid:

```text
Resume text -> embedding model -> Qdrant semantic retrieval
            -> rule-based ranking and safety checks
            -> per-project employee ranking CSV
```

Qdrant stores and searches vectors. SentenceTransformers provides the embedding model that converts text into vectors. The allocation engine makes the final decision using explainable calculations; no generative language model makes the staffing decision.

## Main Components

### Employee database

`employees/employee_database.py` manages SQLite storage at `employees/employee_records.db`.

It stores manually supplied employee information such as:

- Employee ID and contact details
- Job title, department, location, and experience
- Ability score and availability hours
- Current project and current project priority
- Utilization and project history
- Project-change count and days on the current project
- Resume path and extracted resume text

PDF resumes are read from `employees/resume/`. Resume text is stored for semantic skill matching. Structured employee details remain manual inputs and are not automatically overwritten by resume content.

### Vector database

`engine/vector_database.py` manages the Qdrant collection `employee_workforce`.

The default embedding model is `all-MiniLM-L6-v2`. Resume text is converted into 384-dimensional vectors. Project skill requirements are embedded using the same model, allowing Qdrant to retrieve employees based on semantic similarity instead of exact keyword equality.

Embedding model loading is lazy. The model is loaded only when indexing or searching requires it. Employee indexing uses batches of 64 texts by default, which is more appropriate for large resume collections.

### Allocation engine

`engine/engine.py` contains deterministic calculations for:

- Semantic-fit ranking
- Effective employee capacity
- Project SLA risk
- Project slack
- Project weight and priority
- Cost-to-skill penalty
- Available-worker selection
- Safe reassignment from an existing project

### Project manager

`projects/project_manager.py` stores ongoing projects as JSON and produces one ranking CSV per project. It recalculates project weight, SLA risk, candidate ranking, and selection decisions from the current employee records.

## Project Data

Each project is stored as `projects/<project_id>.json`. Required fields are:

```json
{
  "project_id": "website_upgrade",
  "required_skills": ["python", "sql", "backend api development"],
  "project_hours": 320,
  "deadline_days": 21
}
```

Additional project-priority fields include:

```json
{
  "investment": 250000,
  "roi": 0.35,
  "client_tier": 4,
  "skill_criticality": 4,
  "estimated_people": 4,
  "importance": 5
}
```

Skill-specific staffing requirements are represented separately from total staffing:

```json
{
  "estimated_people": 4,
  "skill_staffing": {
    "python": 2,
    "sql": 1,
    "frontend": 1
  }
}
```

The effective total staffing requirement is at least the sum of `skill_staffing`. In this example, the project needs four people, including two Python-capable employees, one SQL-capable employee, and one frontend-capable employee.

## Project Weight

Project priority combines business, deadline, staffing, and delivery factors:

```text
weight = investment * 0.3
       + roi * 0.3
       + client_tier * 20
       + sla_risk * 25
       + skill_criticality * 30
       + deadline_urgency * 50
       + required_skill_count * 10
       + estimated_people * 20
       + skill_people_count * 25
       + importance * 40
```

Deadline urgency increases as the deadline becomes shorter. SLA risk is calculated from project hours, team capacity, skill coverage, utilization, and deadline pressure.

The coefficients are policy values, not machine-learned values. They should be calibrated against the organization's business priorities and historical outcomes.

## Employee Ranking and Selection

Employees are ranked using:

- Semantic relevance between project requirements and resume text
- Effective hours
- Ability score
- Current utilization
- Deadline pressure
- Skill overlap

Effective capacity is calculated as:

```text
effective_hours = availability_hours
                * (1 - utilization)
                * ability_score
```

The selection order is:

1. Find workers with relevant skills and enough effective capacity.
2. Reject workers whose projected utilization exceeds the burnout threshold.
3. Prefer a currently unassigned worker.
4. Consider an occupied worker only when no suitable available worker exists.
5. Allow reassignment only when the new project weight is at least 1.5 times the current project weight.
6. Block frequent project switching and short-tenure reassignment.

Default safeguards are:

- Maximum projected utilization: `85%`
- Maximum project changes in 30 days: `2`
- Minimum time on the current project: `14 days`
- Reassignment priority multiplier: `1.5`

Projected utilization is:

```text
projected_utilization = current_utilization
                      + project_hours / availability_hours
```

These rules do not perform the actual HR or project-management transfer. They produce a recommendation and an explanation for the selected worker.

## Generated Files

For `website_upgrade`, the project manager creates:

```text
projects/website_upgrade.json
projects/website_upgrade_ranked_employees.csv
```

Each ranking CSV contains:

- Rank and employee identity
- Project weight and SLA risk
- Total and skill-specific staffing requirements
- Semantic match score
- Effective hours and projected utilization
- Final score
- Selection decision
- Human-readable reason

Possible decisions include:

```text
assign_available_worker
reassign_occupied_worker
ranked_candidate
```

Rankings are refreshed when projects are saved, employee records change, resumes are synchronized, or `employee_database.py` is executed. Bulk resume synchronization refreshes project rankings once after the full import rather than once per resume.

## Performance for Large Resume Collections

The resume synchronization path uses `ProcessPoolExecutor` to extract PDF text concurrently across CPU processes. The worker function is defined at module level so it works with Windows process spawning.

Qdrant indexing embeds resume text in batches of 64. The batch size can be configured:

```python
store = WorkforceVectorStore(embedding_batch_size=128)
```

For very large collections, the Qdrant service, model cache, available RAM, CPU count, and disk throughput should be monitored. Batch size and process count should be benchmarked on the deployment machine.

## Installation

The dependency file is `Requirements.txt`.

Install dependencies in the project's configured Python environment:

```text
python -m pip install -r Requirements.txt
```

The project does not create a virtual environment automatically. Qdrant must also be running at `localhost:6333` when vector indexing or semantic search is performed.

## Running the System

1. Place PDF resumes in `employees/resume/`.
2. Synchronize the resumes and employee records:

```text
python employees/employee_database.py
```

3. Run the interactive project-allocation workflow:

```text
python main.py
```

The CLI asks for project identity, investment, ROI, client tier, importance, deadlines, total staffing, required skills, and the number of employees needed for each skill.

## Testing

Run the complete test suite:

```text
python -m unittest test_engine.py -v
```

Compile all Python modules:

```text
python -m compileall -q employees engine projects main.py test_engine.py
```

The tests cover project weighting, SLA risk, semantic ranking, reassignment rules, burnout protection, project-switching limits, database behavior, per-project CSV output, and batched embeddings.

## RAG Clarification

The project uses the retrieval side of a RAG-style architecture:

- Resume text is embedded.
- Qdrant retrieves semantically relevant employee profiles.
- The rule engine evaluates those profiles.

It is not a full generative RAG application because no LLM generates a natural-language answer from the retrieved documents. `engine/RAG.py` contains an optional LlamaIndex/Qdrant pipeline, while the main allocation path uses `WorkforceVectorStore` directly.
