import math
from typing import Dict, Any, List, Optional
from engine import ResourceAllocationEngine
import db

def prepare_worker_payloads(employees: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    workers = []
    for emp in employees:
        skills = emp.get("skills", [])
        if not skills and emp.get("domain_knowledge"):
            skills = [s.strip() for s in emp["domain_knowledge"].split(",") if s.strip()]
        
        workers.append({
            "employee_id": emp["employee_id"],
            "name": emp.get("full_name") or emp["employee_id"],
            "skills": skills,
            "current_project": emp.get("current_project"),
            "current_project_weight": float(emp.get("current_project_weight") or 0.0),
            "project_changes_last_30_days": int(emp.get("project_changes_last_30_days") or 0),
            "days_on_current_project": int(emp.get("days_on_current_project") or 0),
            "available_hours": float(emp.get("availability_hours") or 40.0),
            "ability_score": float(emp.get("ability_score") or 0.8),
            "utilization": float(emp.get("utilization") or 0.0),
            "resume_text": emp.get("resume_text") or "",
            "job_title": emp.get("job_title") or "",
            "department": emp.get("department") or "",
            "years_experience": float(emp.get("years_experience") or 1.0),
            "seniority_tier": int(emp.get("seniority_tier") or 1),
        })
    return workers

def evaluate_project_risk(project: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate SLA risk and weight for a project using its assigned team or organization capacity."""
    all_employees = db.list_employees()
    workers = prepare_worker_payloads(all_employees)
    
    # Filter workers currently assigned to this project
    assigned_workers = [w for w in workers if w["current_project"] == project["project_id"]]
    
    required_skills = project.get("required_skills", [])
    project_hours = float(project.get("project_hours", 160.0))
    deadline_days = max(1, int(project.get("deadline_days", 30)))
    
    # Calculate SLA risk based on assigned team
    sla_risk = ResourceAllocationEngine.calculate_project_sla_risk(
        workers=assigned_workers,
        required_skills=required_skills,
        project_hours=project_hours,
        deadline_days=deadline_days,
    )
    
    # Determine risk level
    if sla_risk >= 65.0:
        risk_level = "High"
    elif sla_risk >= 35.0:
        risk_level = "Medium"
    else:
        risk_level = "Low"
        
    project_weight = ResourceAllocationEngine.calculate_project_weight(
        investment=float(project.get("investment", 100000.0)),
        roi=float(project.get("roi", 0.25)),
        client_tier=int(project.get("client_tier", 3)),
        sla_risk=int(round(sla_risk)),
        skill_criticality=float(project.get("skill_criticality", 3.0)),
        deadline_days=deadline_days,
        required_skill_count=len(required_skills),
        estimated_people=int(project.get("estimated_people", 2)),
        importance=float(project.get("importance", 3.0)),
    )
    
    return {
        "sla_risk": round(sla_risk, 2),
        "risk_level": risk_level,
        "project_weight": round(project_weight, 2),
        "assigned_count": len(assigned_workers),
    }

def get_recommendations_for_project(project_id: str) -> Dict[str, Any]:
    """
    Evaluates project risk and if high risk, computes:
    - Number of employees required
    - Best employee predicted by engine with reason
    - Full ranked list of employees with ranks and reasons for manual selection
    """
    project = db.get_project(project_id)
    if not project:
        raise ValueError(f"Project '{project_id}' not found")
        
    all_employees = db.list_employees()
    workers = prepare_worker_payloads(all_employees)
    assigned_workers = [w for w in workers if w["current_project"] == project["project_id"]]
    
    required_skills = project.get("required_skills", [])
    project_hours = float(project.get("project_hours", 160.0))
    deadline_days = max(1, int(project.get("deadline_days", 30)))
    
    sla_risk = ResourceAllocationEngine.calculate_project_sla_risk(
        workers=assigned_workers,
        required_skills=required_skills,
        project_hours=project_hours,
        deadline_days=deadline_days,
    )
    
    risk_level = "High" if sla_risk >= 65.0 else ("Medium" if sla_risk >= 35.0 else "Low")
    
    # Calculate required employees needed
    # Formula considers effective capacity (avg 32 usable hrs/week) and skill coverage deficit
    assigned_effective_hours = sum(w["available_hours"] * (1.0 - w["utilization"]) * w["ability_score"] for w in assigned_workers)
    remaining_hours = max(0.0, project_hours - assigned_effective_hours)
    
    weeks_available = max(1.0, deadline_days / 7.0)
    needed_by_hours = math.ceil(remaining_hours / (32.0 * weeks_available))
    target_people = max(int(project.get("estimated_people", 2)), needed_by_hours)
    headcount_needed = max(1, target_people - len(assigned_workers))
    
    # Calculate candidates (excluding already assigned to this project)
    candidate_workers = [w for w in workers if w["current_project"] != project["project_id"]]
    
    # Run engine ranking
    ranked_results = ResourceAllocationEngine.rank_workers_by_semantic_fit(
        workers=candidate_workers,
        required_skills=required_skills,
        project_hours=project_hours,
        deadline_days=deadline_days,
    )
    
    # Merge rich details & build human-readable reasons
    workers_by_name = {w["name"]: w for w in candidate_workers}
    ranked_candidates = []
    
    for rank, item in enumerate(ranked_results, start=1):
        worker_info = workers_by_name.get(item["name"])
        if not worker_info:
            continue
            
        is_bench = not worker_info.get("current_project")
        match_pct = int(round(item["semantic_match"] * 100))
        final_pct = int(round(item["final_score"] * 100))
        
        # Build reason to hire
        reason_parts = []
        if is_bench:
            reason_parts.append("Currently available on Bench with immediate capacity")
        else:
            reason_parts.append(f"Currently on '{worker_info['current_project']}', eligible for strategic transfer")
            
        if match_pct >= 25:
            reason_parts.append(f"strong {match_pct}% semantic skill alignment to project requirements")
        elif match_pct >= 12:
            reason_parts.append(f"solid {match_pct}% matching domain competencies")
        else:
            reason_parts.append(f"general foundational match ({match_pct}%)")
            
        reason_parts.append(f"{worker_info['years_experience']} yrs exp, ability score {worker_info['ability_score']:.1f}")
        
        reason = "; ".join(reason_parts) + "."
        
        action_type = "direct_assignment" if is_bench else "transfer_offer"

        ranked_candidates.append({
            "rank": rank,
            "employee_id": worker_info["employee_id"],
            "name": worker_info["name"],
            "job_title": worker_info["job_title"],
            "department": worker_info["department"],
            "current_project": worker_info["current_project"] or "None (Bench)",
            "is_bench": is_bench,
            "skills": worker_info["skills"],
            "years_experience": worker_info["years_experience"],
            "semantic_match": item["semantic_match"],
            "semantic_score": item["semantic_match"],
            "semantic_match_pct": match_pct,
            "effective_hours": item["effective_hours"],
            "effective_capacity": item["effective_hours"],
            "days_on_current_project": worker_info.get("days_on_current_project", 0),
            "recommendation_action": action_type,
            "final_score": item["final_score"],
            "final_score_pct": final_pct,
            "reason": reason,
        })
        
    # Engine Best Pick using select_worker_for_project
    project_weight = ResourceAllocationEngine.calculate_project_weight(
        investment=float(project.get("investment", 100000.0)),
        roi=float(project.get("roi", 0.25)),
        client_tier=int(project.get("client_tier", 3)),
        sla_risk=int(round(sla_risk)),
        skill_criticality=float(project.get("skill_criticality", 3.0)),
        deadline_days=deadline_days,
        required_skill_count=len(required_skills),
        estimated_people=int(project.get("estimated_people", 2)),
        importance=float(project.get("importance", 3.0)),
    )
    
    project_for_selection = {**project, "sla_risk": sla_risk, "weight": project_weight}
    selected_worker_dict = ResourceAllocationEngine.select_worker_for_project(
        workers=candidate_workers,
        required_skills=required_skills,
        project_hours=project_hours,
        deadline_days=deadline_days,
        new_project=project_for_selection,
    )
    
    best_candidate = None
    if selected_worker_dict:
        # Match with rich candidate info
        best_name = selected_worker_dict.get("name")
        for cand in ranked_candidates:
            if cand["name"] == best_name:
                best_candidate = dict(cand)
                decision_label = selected_worker_dict.get("decision")
                if decision_label == "assign_available_worker":
                    best_candidate["engine_decision"] = "Direct Allocation (Bench Worker Available)"
                else:
                    best_candidate["engine_decision"] = "Strategic Reassignment (High Priority Project Threshold Met)"
                break
                
    # Fallback to rank 1 candidate if strict rules found no unconstrained candidate
    if not best_candidate and ranked_candidates:
        best_candidate = dict(ranked_candidates[0])
        best_candidate["engine_decision"] = "Top Ranked Candidate by Overall Semantic Fit"
        
    # Check if all qualified workers are busy
    bench_count = sum(1 for c in ranked_candidates if c["is_bench"])
    all_workers_busy = (bench_count == 0)

    # Sub-objects for full Gradio and API compatibility
    proj_risk_info = {
        "sla_risk": round(sla_risk, 2),
        "risk_level": risk_level,
        "project_weight": round(project_weight, 2),
        "assigned_count": len(assigned_workers),
    }

    if sla_risk >= 65.0:
        summary_status = "high_risk_reallocation_needed"
        summary_message = f"High SLA Risk ({round(sla_risk, 1)}%). The project requires at least {headcount_needed} additional resource(s) to meet delivery commitments."
    elif sla_risk >= 35.0:
        summary_status = "moderate_risk_staffing_review"
        summary_message = f"Medium SLA Risk ({round(sla_risk, 1)}%). Staffing reinforcements recommended to mitigate timeline and skill slippage."
    else:
        summary_status = "optimal_allocation"
        summary_message = f"Low SLA Risk ({round(sla_risk, 1)}%). Team capacity and skill coverage are within target parameters."

    slack_hours = round(max(0.0, assigned_effective_hours - project_hours), 1)

    summary_info = {
        "status": summary_status,
        "message": summary_message,
        "slack_hours": slack_hours,
        "headcount_needed": headcount_needed,
    }
    
    return {
        "project_id": project_id,
        "project_name": project.get("name", project_id),
        "sla_risk": round(sla_risk, 2),
        "risk_level": risk_level,
        "project_weight": round(project_weight, 2),
        "completion_pct": project.get("completion_pct", 0),
        "headcount_needed": headcount_needed,
        "best_candidate": best_candidate,
        "ranked_candidates": ranked_candidates,
        "all_workers_busy": all_workers_busy,
        "assigned_count": len(assigned_workers),
        "bench_count": bench_count,
        "project_risk": proj_risk_info,
        "summary": summary_info,
    }
