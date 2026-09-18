class ResourceAllocationEngine:
    @staticmethod
    def calculate_project_weight(investment: float, roi: float, client_tier: int, sla_risk: int) -> float:
        """
        Computes W_project for zero-sum arbitration.
        Higher weight means priority during resource collisions.
        """
        weight = (investment * 0.3) + (roi * 0.3) + (client_tier * 20.0) + (sla_risk * 25.0)
        return weight

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