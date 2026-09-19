import re


class ResourceAllocationEngine:
    @staticmethod
    def _normalize_skill_text(value: str) -> str:
        if value is None:
            return ""
        return " ".join(str(value).strip().lower().split())

    @staticmethod
    def _semantic_similarity_score(text_a: str, text_b: str) -> float:
        """
        Lightweight semantic similarity based on token overlap, containment, and phrase proximity.
        This keeps the logic deterministic without requiring a full vector database call,
        while still matching skill intent semantically rather than only by exact keywords.
        """
        if not text_a or not text_b:
            return 0.0

        left = ResourceAllocationEngine._normalize_skill_text(text_a)
        right = ResourceAllocationEngine._normalize_skill_text(text_b)
        if not left or not right:
            return 0.0
        if left == right:
            return 1.0

        # Direct containment check (e.g., 'spring' in 'spring boot', 'sql' in 'postgresql')
        shorter, longer = (left, right) if len(left) <= len(right) else (right, left)
        if shorter in longer:
            containment_score = max(0.65, min(1.0, len(shorter) / max(len(longer), 1)))
        else:
            containment_score = 0.0

        left_tokens = set(left.split())
        right_tokens = set(right.split())
        if not left_tokens or not right_tokens:
            return containment_score

        overlap = len(left_tokens & right_tokens)
        min_tokens = min(len(left_tokens), len(right_tokens))
        union = len(left_tokens | right_tokens)

        # Overlap relative to the smaller phrase (precision of the requirement)
        overlap_precision = overlap / max(min_tokens, 1)
        jaccard = overlap / max(union, 1)
        token_score = (0.70 * overlap_precision) + (0.30 * jaccard)

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
        score = max(containment_score, (0.75 * token_score) + (0.25 * phrase_bonus))
        return round(max(0.0, min(1.0, score)), 4)

    @staticmethod
    def _build_candidate_reason(
        semantic_match: float,
        effective_hours: float,
        utilization: float,
        deadline_days: int,
        project_hours: float,
        skill_overlap_bonus: float,
    ) -> str:
        if semantic_match >= 0.25:
            match_text = "strong skill match"
        elif semantic_match >= 0.12:
            match_text = "good skill match"
        else:
            match_text = "limited skill match"

        if effective_hours >= max(project_hours, 1.0):
            capacity_text = "enough effective capacity"
        elif effective_hours > 0:
            capacity_text = f"{effective_hours:.1f}h effective capacity"
        else:
            capacity_text = "very low effective capacity"

        if utilization < 0.35:
            load_text = "low utilization"
        elif utilization < 0.7:
            load_text = "manageable utilization"
        else:
            load_text = "high utilization"

        if deadline_days <= 7:
            deadline_text = "tight deadline"
        elif deadline_days <= 21:
            deadline_text = "moderate deadline"
        else:
            deadline_text = "comfortable deadline"

        if skill_overlap_bonus > 0.5:
            overlap_text = "clear overlap with required skills"
        else:
            overlap_text = "some overlap with required skills"

        return f"{match_text}, {capacity_text}, {load_text}, {deadline_text}, {overlap_text}."

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

        ranked = []
        for worker in workers:
            worker_name = str(worker.get("name", "Worker"))

            # Consolidate candidate skill tokens from skills, domain_knowledge, and job_title
            raw_skills = worker.get("skills") or []
            if isinstance(raw_skills, str):
                raw_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
            elif not isinstance(raw_skills, list):
                raw_skills = list(raw_skills) if raw_skills else []
            else:
                raw_skills = list(raw_skills)

            domain_k = worker.get("domain_knowledge") or ""
            if domain_k and isinstance(domain_k, str):
                raw_skills.extend([s.strip() for s in domain_k.split(",") if s.strip()])

            job_title = worker.get("job_title") or ""
            if job_title and isinstance(job_title, str):
                raw_skills.append(job_title.strip())

            skill_tokens = [ResourceAllocationEngine._normalize_skill_text(skill) for skill in raw_skills if skill and str(skill).strip()]

            # Normalize resume text
            resume_text = str(worker.get("resume_text", "")).strip().lower()
            resume_word_tokens = set(re.findall(r"\b[a-z0-9+#.-]+\b", resume_text)) if resume_text else set()

            # Evaluate each required skill
            req_scores = []
            skill_overlap_count = 0

            for requirement in normalized_required:
                # 1. Best match against worker declared skills
                best_skill_match = 0.0
                for skill in skill_tokens:
                    if skill == requirement:
                        best_skill_match = 1.0
                        break
                    sim = ResourceAllocationEngine._semantic_similarity_score(skill, requirement)
                    best_skill_match = max(best_skill_match, sim)

                # 2. Match against resume text
                resume_match = 0.0
                if resume_text:
                    if requirement in resume_text:
                        resume_match = 0.90
                    else:
                        req_words = [w for w in requirement.split() if w]
                        if req_words:
                            matched_words = sum(1 for w in req_words if w in resume_word_tokens or w in resume_text)
                            if matched_words > 0:
                                resume_match = 0.75 * (matched_words / len(req_words))

                # 3. Combine skill match and resume match
                req_score = max(best_skill_match, resume_match)
                if best_skill_match >= 0.70 and resume_match >= 0.70:
                    req_score = min(1.0, req_score + 0.10)

                if req_score >= 0.35:
                    skill_overlap_count += 1

                req_scores.append(req_score)

            if req_scores:
                avg_match = sum(req_scores) / len(req_scores)
                max_match = max(req_scores)
                coverage = skill_overlap_count / len(req_scores)
                raw_fit = (0.60 * avg_match) + (0.25 * max_match) + (0.15 * coverage)
                # Moderate scale: gently lift score slightly above baseline (~0.12 to 0.35) without extreme inflation
                semantic_match = round(min(0.35, raw_fit * 0.32), 4) if raw_fit > 0 else 0.0
            else:
                semantic_match = 0.0

            # Scale skill overlap bonus between 0.0 and 1.0
            skill_overlap_bonus = min(1.0, skill_overlap_count / max(len(normalized_required), 1))

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
                    "reason": ResourceAllocationEngine._build_candidate_reason(
                        semantic_match=semantic_match,
                        effective_hours=effective_hours,
                        utilization=utilization,
                        deadline_days=deadline_days,
                        project_hours=project_hours,
                        skill_overlap_bonus=skill_overlap_bonus,
                    ),
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
        skill_people_count: int = 0,
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
        skill_people_factor = max(0, int(skill_people_count))
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
            + (skill_people_factor * 25.0)
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
        Calculates a project-level SLA risk score using the team state.
        Considers project workload versus total delivery capacity over the deadline period,
        skill coverage across the assigned team, and deadline urgency.
        """
        deadline_days = max(1, int(deadline_days))
        project_hours = max(1.0, float(project_hours))
        normalized_required_skills = [skill.strip().lower() for skill in required_skills if skill and skill.strip()]

        if not workers:
            # When no workers are assigned, risk scales with deadline urgency
            if deadline_days <= 12:
                return 85.0
            elif deadline_days <= 25:
                return 70.0
            elif deadline_days <= 40:
                return 55.0
            else:
                return 40.0

        # Calculate realistic team delivery capacity over the deadline timeframe (weeks)
        weeks_available = max(1.0, deadline_days / 7.0)
        total_weekly_effective_hours = 0.0
        team_skills = set()

        for worker in workers:
            raw_skills = worker.get("skills") or []
            if isinstance(raw_skills, str):
                raw_skills = [s.strip() for s in raw_skills.split(",") if s.strip()]
            domain_k = worker.get("domain_knowledge") or ""
            if domain_k and isinstance(domain_k, str):
                raw_skills.extend([s.strip() for s in domain_k.split(",") if s.strip()])
            job_title = worker.get("job_title") or ""
            if job_title and isinstance(job_title, str):
                raw_skills.append(job_title.strip())

            for s in raw_skills:
                team_skills.add(str(s).strip().lower())

            avail = float(worker.get("available_hours") or 40.0)
            ability = max(0.5, min(1.0, float(worker.get("ability_score") or 0.8)))
            util = max(0.0, min(1.0, float(worker.get("utilization") or 0.0)))

            # For assigned workers, active dedication contributes to delivery
            if worker.get("current_project"):
                dedicated_factor = max(0.5, util)
            else:
                dedicated_factor = max(0.2, 1.0 - util)

            total_weekly_effective_hours += avail * dedicated_factor * ability

        total_capacity_hours = total_weekly_effective_hours * weeks_available

        # 1. Workload pressure (0.0 to 1.0)
        if total_capacity_hours >= project_hours:
            workload_ratio = project_hours / total_capacity_hours
            workload_risk = max(0.0, (workload_ratio - 0.4) / 0.6)
        else:
            deficit = (project_hours - total_capacity_hours) / project_hours
            workload_risk = min(1.0, 0.6 + (0.4 * deficit))

        # 2. Skill coverage risk (0.0 to 1.0)
        if normalized_required_skills:
            covered_count = 0
            for req in normalized_required_skills:
                if any(req in s or s in req for s in team_skills):
                    covered_count += 1
            skill_coverage = covered_count / len(normalized_required_skills)
        else:
            skill_coverage = 1.0

        skill_risk = 1.0 - skill_coverage

        # 3. Deadline pressure risk (0.0 to 1.0)
        if deadline_days <= 10:
            deadline_risk = 0.90
        elif deadline_days <= 20:
            deadline_risk = 0.60
        elif deadline_days <= 30:
            deadline_risk = 0.35
        else:
            deadline_risk = 0.10

        # Weighted composition: workload (45%), skills (35%), deadline (20%)
        risk_score = (workload_risk * 45.0) + (skill_risk * 35.0) + (deadline_risk * 20.0)
        return round(max(5.0, min(95.0, risk_score)), 2)

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