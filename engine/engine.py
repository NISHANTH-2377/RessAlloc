class ResourceAllocationEngine:
    @staticmethod
    def _normalize_skill_text(value: str) -> str:
        if value is None:
            return ""
        return " ".join(str(value).strip().lower().split())

    @staticmethod
    def _semantic_similarity_score(text_a: str, text_b: str) -> float:
        """
        Lightweight semantic similarity based on token overlap and phrase proximity.
        This keeps the logic deterministic without requiring a full vector database call,
        while still matching skill intent semantically rather than only by exact keywords.
        """
        if not text_a or not text_b:
            return 0.0

        left = ResourceAllocationEngine._normalize_skill_text(text_a)
        right = ResourceAllocationEngine._normalize_skill_text(text_b)
        if left == right:
            return 1.0

        left_tokens = set(left.split())
        right_tokens = set(right.split())
        if not left_tokens or not right_tokens:
            return 0.0

        overlap = len(left_tokens & right_tokens)
        union = len(left_tokens | right_tokens)
        token_score = overlap / max(union, 1)

        common_prefix = 0
        left_words = left.split()
        right_words = right.split()
        max_len = min(len(left_words), len(right_words))
        for i in range(max_len):
            if left_words[i] == right_words[i]:
                common_prefix += 1
            else:
                break

        phrase_bonus = common_prefix / max(max_len, 1)
        score = (0.75 * token_score) + (0.25 * phrase_bonus)
        return round(max(0.0, min(1.0, score)), 4)

    @staticmethod
    def rank_workers_by_semantic_fit(
        workers: list[dict],
        required_skills: list[str],
        project_hours: float,
        deadline_days: int,
    ) -> list[dict]:
        """
        Ranks workers by semantic fit to the required skills and then factors in
        capacity, ability, utilization, and urgency. The results are sorted from
        the most suitable worker to the least suitable one.
        """
        if not workers:
            return []

        normalized_required = [ResourceAllocationEngine._normalize_skill_text(skill) for skill in required_skills if skill and str(skill).strip()]
        if not normalized_required:
            return []

        required_text = " ".join(normalized_required)

        ranked = []
        for worker in workers:
            worker_name = str(worker.get("name", "Worker"))
            skill_tokens = [ResourceAllocationEngine._normalize_skill_text(skill) for skill in worker.get("skills", []) if skill and str(skill).strip()]
            resume_text = str(worker.get("resume_text", " "))
            worker_profile_text = " ".join(skill_tokens + [resume_text])

            semantic_match = 0.0
            for requirement in normalized_required:
                semantic_match = max(semantic_match, ResourceAllocationEngine._semantic_similarity_score(worker_profile_text, requirement))

            skill_overlap_bonus = 0.0
            for requirement in normalized_required:
                for skill in skill_tokens:
                    if requirement and requirement in skill:
                        skill_overlap_bonus += 0.2
                    elif requirement and skill in requirement:
                        skill_overlap_bonus += 0.2

            available_hours = float(worker.get("available_hours", 0.0))
            ability_score = float(worker.get("ability_score", 0.5))
            utilization = float(worker.get("utilization", 0.0))
            ability_score = max(0.0, min(1.0, ability_score))
            utilization = max(0.0, min(1.0, utilization))
            effective_hours = available_hours * (1.0 - utilization) * ability_score
            deadline_pressure = max(0.0, min(1.0, (30 - max(1, int(deadline_days))) / 30.0))
            capacity_score = 0.0 if project_hours <= 0 else min(1.0, effective_hours / max(project_hours, 1.0))

            final_score = (
                semantic_match * 0.55
                + min(1.0, capacity_score) * 0.25
                + (1.0 - utilization) * 0.10
                + (1.0 - deadline_pressure) * 0.10
                + min(1.0, skill_overlap_bonus) * 0.10
            )

            ranked.append(
                {
                    "name": worker_name,
                    "semantic_match": round(semantic_match, 4),
                    "effective_hours": round(effective_hours, 2),
                    "availability_score": round((1.0 - utilization) * ability_score, 4),
                    "final_score": round(final_score, 4),
                }
            )

        ranked.sort(key=lambda item: item["final_score"], reverse=True)
        return ranked

    @staticmethod
    def select_worker_for_project(
        workers: list[dict],
        required_skills: list[str],
        project_hours: float,
        deadline_days: int,
        new_project: dict,
        reassignment_multiplier: float = 1.5,
        burnout_threshold: float = 0.85,
        max_project_changes: int = 2,
        minimum_project_tenure_days: int = 14,
    ) -> dict | None:
        """Choose an available worker before considering reassignment.

        An occupied worker is eligible only when the new project weight is at
        least ``reassignment_multiplier`` times the worker's current project
        weight. Occupied records must provide ``current_project_weight``;
        otherwise they are protected from reassignment.
        """
        if not workers or reassignment_multiplier <= 1.0:
            return None
        burnout_threshold = max(0.0, min(1.0, float(burnout_threshold)))

        new_weight = ResourceAllocationEngine.calculate_project_weight(
            investment=float(new_project.get("investment", 0.0)),
            roi=float(new_project.get("roi", 0.0)),
            client_tier=int(new_project.get("client_tier", 0)),
            sla_risk=int(new_project.get("sla_risk", 0)),
            skill_criticality=float(new_project.get("skill_criticality", 0.0)),
        )
        ranked = ResourceAllocationEngine.rank_workers_by_semantic_fit(
            workers=workers,
            required_skills=required_skills,
            project_hours=project_hours,
            deadline_days=deadline_days,
        )
        ranked_by_name = {worker["name"]: worker for worker in ranked}
        minimum_capacity = max(0.0, float(project_hours))

        def is_sufficient(worker: dict) -> bool:
            ranked_worker = ranked_by_name.get(str(worker.get("name", "Worker")), {})
            available_hours = max(0.0, float(worker.get("available_hours", 0.0)))
            utilization = max(0.0, min(1.0, float(worker.get("utilization", 0.0))))
            project_load = 0.0 if available_hours == 0.0 else max(0.0, float(project_hours)) / available_hours
            projected_utilization = utilization + project_load
            return (
                ranked_worker.get("semantic_match", 0.0) > 0.0
                and ranked_worker.get("effective_hours", 0.0) >= minimum_capacity
                and projected_utilization <= burnout_threshold
            )

        available_workers = [
            worker for worker in workers
            if not worker.get("current_project")
            and float(worker.get("utilization", 0.0)) < 1.0
            and is_sufficient(worker)
        ]
        if available_workers:
            selected = max(
                available_workers,
                key=lambda worker: ranked_by_name[str(worker.get("name", "Worker"))]["final_score"],
            )
            return {
                **ranked_by_name[str(selected.get("name", "Worker"))],
                "decision": "assign_available_worker",
                "new_project_weight": round(new_weight, 2),
                "projected_utilization": round(
                    float(selected.get("utilization", 0.0))
                    + (0.0 if float(selected.get("available_hours", 0.0)) == 0.0 else max(0.0, float(project_hours)) / float(selected["available_hours"])),
                    4,
                ),
            }

        occupied_workers = [
            worker for worker in workers
            if worker.get("current_project") and is_sufficient(worker)
            and int(worker.get("project_changes_last_30_days", 0)) < max_project_changes
            and int(worker.get("days_on_current_project", minimum_project_tenure_days)) >= minimum_project_tenure_days
            and worker.get("current_project_weight") is not None
            and new_weight >= float(worker["current_project_weight"]) * reassignment_multiplier
        ]
        if not occupied_workers:
            return None

        selected = max(
            occupied_workers,
            key=lambda worker: ranked_by_name[str(worker.get("name", "Worker"))]["final_score"],
        )
        selected_name = str(selected.get("name", "Worker"))
        return {
            **ranked_by_name[selected_name],
            "decision": "reassign_occupied_worker",
            "current_project": selected.get("current_project"),
            "current_project_weight": float(selected["current_project_weight"]),
            "new_project_weight": round(new_weight, 2),
            "projected_utilization": round(
                float(selected.get("utilization", 0.0))
                + (0.0 if float(selected.get("available_hours", 0.0)) == 0.0 else max(0.0, float(project_hours)) / float(selected["available_hours"])),
                4,
            ),
        }

    @staticmethod
    def calculate_project_weight(
        investment: float,
        roi: float,
        client_tier: int,
        sla_risk: int,
        skill_criticality: float = 0.0,
        deadline_days: int = 30,
        required_skill_count: int = 0,
        estimated_people: int = 0,
        importance: float = 0.0,
    ) -> float:
        """
        Computes W_project for zero-sum arbitration.
        Higher weight means priority during resource collisions.
        skill_criticality reflects how essential a required skill is to the project
        and is added as a weighted factor so skill scarcity can affect dispatch priority.
        """
        deadline_days = max(1, int(deadline_days))
        deadline_urgency = max(0.0, min(1.0, (30 - deadline_days) / 30.0))
        skill_scope = max(0, int(required_skill_count))
        people_factor = max(0, int(estimated_people))
        importance = max(0.0, min(5.0, float(importance)))
        weight = (
            (investment * 0.3)
            + (roi * 0.3)
            + (client_tier * 20.0)
            + (sla_risk * 25.0)
            + (skill_criticality * 30.0)
            + (deadline_urgency * 50.0)
            + (skill_scope * 10.0)
            + (people_factor * 20.0)
            + (importance * 40.0)
        )
        return weight

    @staticmethod
    def calculate_project_sla_risk(
        workers: list[dict],
        required_skills: list[str],
        project_hours: float,
        deadline_days: int,
    ) -> float:
        """
        Calculates a project-level SLA risk score using the team state instead of a single-person input.
        Inputs are expected to look like:
        {
            "skills": ["python", "sql"],
            "available_hours": 20,
            "ability_score": 0.8,
            "utilization": 0.5
        }
        """
        if not workers:
            return 100.0

        normalized_required_skills = [skill.strip().lower() for skill in required_skills if skill and skill.strip()]
        if not normalized_required_skills:
            return 0.0

        total_effective_hours = 0.0
        covered_skill_count = 0
        unique_skill_pool = set()

        for worker in workers:
            skills = [str(skill).strip().lower() for skill in worker.get("skills", []) if str(skill).strip()]
            unique_skill_pool.update(skills)

            available_hours = float(worker.get("available_hours", 0.0))
            ability_score = float(worker.get("ability_score", 0.5))
            utilization = float(worker.get("utilization", 0.0))

            ability_score = max(0.0, min(1.0, ability_score))
            utilization = max(0.0, min(1.0, utilization))
            usable_hours = available_hours * (1.0 - utilization) * ability_score
            total_effective_hours += max(0.0, usable_hours)

            for required_skill in normalized_required_skills:
                if required_skill in skills:
                    covered_skill_count += 1

        total_required_skills = len(normalized_required_skills)
        skill_coverage = (covered_skill_count / max(total_required_skills, 1))
        skill_coverage = max(0.0, min(1.0, skill_coverage))

        if total_effective_hours <= 0:
            load_ratio = 1.0
        else:
            load_ratio = project_hours / total_effective_hours
        load_ratio = max(0.0, min(load_ratio, 10.0))

        deadline_days = max(1, int(deadline_days))
        deadline_pressure = max(0.0, min(1.0, (30 - deadline_days) / 30.0))

        risk_score = (load_ratio * 45.0) + ((1.0 - skill_coverage) * 35.0) + (deadline_pressure * 20.0)
        return round(max(0.0, min(100.0, risk_score)), 2)

    @staticmethod
    def evaluate_active_project_slack(current_workload_hours: float, capacity_hours: float) -> float:
        """
        Calculates active project slack (S_project).
        Positive slack means the project can safely loan out resources.
        """
        if capacity_hours == 0:
            return 0.0
        slack_percentage = ((capacity_hours - current_workload_hours) / capacity_hours) * 100.0
        return slack_percentage

    @staticmethod
    def compute_cost_to_skill_penalty(employee_seniority_tier: int, task_complexity_tier: int) -> float:
        """
        Applies over-qualification penalty to protect budget margins.
        """
        if employee_seniority_tier > task_complexity_tier:
            return float((employee_seniority_tier - task_complexity_tier) * 1.5)
        return 0.0