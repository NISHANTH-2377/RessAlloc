/**
 * Manager Dashboard Logic & Workflows
 */

const Manager = {
  async init() {
    this.bindEvents();
    await this.loadDashboard();
  },

  async loadDashboard() {
    try {
      const [projects, employees, hrRequests] = await Promise.all([
        API.getProjects(),
        API.getEmployees(),
        API.getHrRequests()
      ]);

      State.projects = projects;
      State.employees = employees;
      State.hrRequests = hrRequests;

      this.renderKPIs();
      this.renderProjects();
    } catch (err) {
      console.error('Failed to load manager dashboard:', err);
      showToast('Failed to load manager data', 'error');
    }
  },

  renderKPIs() {
    const totalProjects = State.projects.length;
    const highRiskProjects = State.projects.filter(p => p.risk_level === 'High').length;
    const benchWorkers = State.employees.filter(e => !e.current_project).length;
    const openHrRequests = State.hrRequests.filter(r => r.status === 'pending').length;

    document.getElementById('pm-kpi-total').textContent = totalProjects;
    document.getElementById('pm-kpi-high-risk').textContent = highRiskProjects;
    document.getElementById('pm-kpi-bench').textContent = benchWorkers;
    document.getElementById('pm-kpi-hr-req').textContent = openHrRequests;
  },

  renderProjects() {
    const container = document.getElementById('projects-grid');
    if (!container) return;

    if (State.projects.length === 0) {
      container.innerHTML = `<div class="empty-state">No projects found. Click "+ New Project" to create one.</div>`;
      return;
    }

    container.innerHTML = State.projects.map(proj => {
      const isHighRisk = proj.risk_level === 'High';
      const riskClass = isHighRisk ? 'high' : (proj.risk_level === 'Medium' ? 'medium' : 'low');
      const assigned = proj.assigned_employees || [];

      const avatarPills = assigned.map(emp => {
        const initials = emp.full_name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
        return `<div class="avatar-pill" title="${emp.full_name} (${emp.job_title})">${initials}</div>`;
      }).join('');

      return `
        <div class="project-card ${isHighRisk ? 'high-risk-card' : ''}" onclick="Manager.openProjectDetail('${proj.project_id}')">
          <div class="project-card-header">
            <div>
              <div class="project-name">${proj.name}</div>
              <div class="project-id-badge">${proj.project_id} • Tier ${proj.client_tier}</div>
            </div>
            <div style="display:flex; align-items:center; gap:0.4rem;">
              <button class="btn-card-action" title="Edit Project" onclick="event.stopPropagation(); Manager.openEditProjectModal('${proj.project_id}')">✏️</button>
              <button class="btn-card-action delete" title="Delete Project" onclick="event.stopPropagation(); Manager.confirmDeleteProject('${proj.project_id}')">🗑️</button>
              <div class="risk-badge ${riskClass}">
                <span>●</span> ${proj.sla_risk}% SLA Risk (${proj.risk_level})
              </div>
            </div>
          </div>

          <div class="project-desc">${proj.description || 'Enterprise project assignment.'}</div>

          <div class="progress-section">
            <div class="progress-labels">
              <span>Completion Progress</span>
              <span style="font-weight:700; color:var(--text-primary);">${proj.completion_pct}%</span>
            </div>
            <div class="progress-bar-container">
              <div class="progress-bar-fill ${isHighRisk ? 'warning' : ''}" style="width: ${Math.max(5, proj.completion_pct)}%;"></div>
            </div>
          </div>

          <div class="project-meta-grid">
            <div class="meta-item">
              <span class="meta-label">Total Hours</span>
              <span class="meta-val">${proj.project_hours} hrs</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Deadline</span>
              <span class="meta-val">${proj.deadline_days} days</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Target Team</span>
              <span class="meta-val">${proj.estimated_people} engineers</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">Investment</span>
              <span class="meta-val">$${(proj.investment || 0).toLocaleString()}</span>
            </div>
          </div>

          <div class="team-avatars-row">
            <div class="avatar-stack">
              ${avatarPills || '<span style="font-size:0.75rem; color:var(--text-muted);">No team assigned</span>'}
            </div>
            <div class="team-count-text">
              ${assigned.length} / ${proj.estimated_people} assigned
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  async openProjectDetail(projectId) {
    try {
      const proj = await API.getProject(projectId);
      State.activeProjectForRec = proj;

      // Check if project is high risk
      if (proj.risk_level === 'High') {
        // High Risk -> fetch and display Engine Recommendations
        await this.showHighRiskRecommendation(projectId);
      } else {
        // Normal progress modal
        this.showNormalProjectModal(proj);
      }
    } catch (err) {
      console.error(err);
      showToast('Error opening project details', 'error');
    }
  },

  showNormalProjectModal(proj) {
    document.getElementById('norm-proj-title').textContent = proj.name;
    document.getElementById('norm-proj-id').textContent = `${proj.project_id} (Client Tier ${proj.client_tier})`;
    document.getElementById('norm-proj-desc').textContent = proj.description || 'No description provided.';
    document.getElementById('norm-proj-progress').style.width = `${proj.completion_pct}%`;
    document.getElementById('norm-proj-pct').textContent = `${proj.completion_pct}%`;
    document.getElementById('norm-proj-hours').textContent = `${proj.project_hours} hrs`;
    document.getElementById('norm-proj-deadline').textContent = `${proj.deadline_days} days`;
    document.getElementById('norm-proj-risk').textContent = `${proj.sla_risk}% (${proj.risk_level})`;
    document.getElementById('norm-proj-weight').textContent = proj.project_weight || 'N/A';

    // Required Skills
    const skillsContainer = document.getElementById('norm-proj-skills');
    skillsContainer.innerHTML = (proj.required_skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('') || 'None specified';

    // Assigned Team
    const teamContainer = document.getElementById('norm-proj-team');
    if (!proj.assigned_employees || proj.assigned_employees.length === 0) {
      teamContainer.innerHTML = `<p style="color:var(--text-muted); font-size:0.85rem;">No employees currently assigned to this project.</p>`;
    } else {
      teamContainer.innerHTML = proj.assigned_employees.map(emp => `
        <div style="display:flex; justify-content:space-between; align-items:center; background:var(--bg-subtle); padding:0.6rem 0.85rem; border-radius:var(--radius-sm); margin-bottom:0.4rem;">
          <div>
            <strong>${emp.full_name}</strong>
            <div style="font-size:0.75rem; color:var(--text-muted);">${emp.job_title} • Ability: ${(emp.ability_score * 100).toFixed(0)}%</div>
          </div>
          <button class="btn btn-danger btn-sm" onclick="Manager.confirmRemoveEmployee('${proj.project_id}', '${emp.employee_id}', '${emp.full_name}')" style="padding:0.25rem 0.65rem; font-size:0.75rem;">
            ✕ Remove
          </button>
        </div>
      `).join('');
    }

    // Setup PM CSV Report & Refresh Actions
    const btnViewCsv = document.getElementById('btn-norm-view-csv');
    if (btnViewCsv) btnViewCsv.onclick = () => this.openRankedCsvReport(proj.project_id, proj.name);

    const btnDownloadCsv = document.getElementById('btn-norm-download-csv');
    if (btnDownloadCsv) {
      btnDownloadCsv.href = API.getProjectCsvDownloadUrl(proj.project_id);
      btnDownloadCsv.download = `${proj.project_id}_ranked_employees.csv`;
    }

    const btnRefreshProj = document.getElementById('btn-norm-refresh-proj');
    if (btnRefreshProj) btnRefreshProj.onclick = () => this.refreshProjectAllocation(proj.project_id);

    const btnNormEdit = document.getElementById('btn-norm-edit-proj');
    if (btnNormEdit) btnNormEdit.onclick = () => this.openEditProjectModal(proj.project_id);

    const btnNormDelete = document.getElementById('btn-norm-delete-proj');
    if (btnNormDelete) btnNormDelete.onclick = () => this.confirmDeleteProject(proj.project_id);

    document.getElementById('project-detail-modal').classList.add('active');
  },

  async showHighRiskRecommendation(projectId) {
    try {
      const rec = await API.getRecommendations(projectId);
      State.activeRecData = rec;

      document.getElementById('rec-project-title').textContent = rec.project_name;
      const riskLevel = rec.risk_level || (rec.sla_risk >= 65 ? 'High' : (rec.sla_risk >= 35 ? 'Medium' : 'Low'));
      const riskBadge = document.getElementById('rec-risk-badge');
      if (riskBadge) {
        riskBadge.textContent = `${rec.sla_risk}% ${riskLevel} Risk`;
        riskBadge.style.color = riskLevel === 'Low' ? '#86efac' : (riskLevel === 'Medium' ? '#fde047' : '#fca5a5');
      }
      document.getElementById('rec-headcount-needed').textContent = `${rec.headcount_needed} Engineers`;

      // Render Best Employee predicted by engine
      const best = rec.best_candidate;
      const bestContainer = document.getElementById('engine-best-candidate-slot');

      if (!best) {
        bestContainer.innerHTML = `
          <div style="padding:1.5rem; text-align:center; background:var(--bg-subtle); border-radius:var(--radius-md);">
            <p style="color:var(--text-muted); margin-bottom:1rem;">All company employees are currently committed to other high-priority initiatives or no direct matches were found.</p>
            <button class="btn btn-warning" onclick="Manager.openHrRequisitionModal('${projectId}')">
              Raise Request for HR to Add New Employee
            </button>
          </div>
        `;
      } else {
        bestContainer.innerHTML = `
          <div class="best-candidate-card" onclick="Manager.promptCandidateDecision('${best.employee_id}')">
            <div class="engine-pick-badge">★ Engine Best Match</div>
            <div class="cand-name">${best.name}</div>
            <div class="cand-role">${best.job_title} • ${best.department}</div>
            
            <div class="cand-reason-box">
              <strong>Engine Recommendation Rationale:</strong><br>
              ${best.reason}
            </div>

            <div class="cand-stats-row">
              <div class="cand-stat-item">Semantic Fit: <span>${best.semantic_match_pct}%</span></div>
              <div class="cand-stat-item">Experience: <span>${best.years_experience} yrs</span></div>
              <div class="cand-stat-item">Status: <span>${best.is_bench ? 'Bench (Available)' : 'On ' + best.current_project}</span></div>
              <div class="cand-stat-item">Final Engine Score: <span>${best.final_score_pct}%</span></div>
            </div>

            <div style="margin-top:1rem; text-align:right;">
              <span class="btn btn-primary btn-sm">Click to Allocate Candidate →</span>
            </div>
          </div>
        `;
      }

      // Check if all employees are busy
      const hrOptionBtn = document.getElementById('rec-raise-hr-btn');
      if (hrOptionBtn) {
        hrOptionBtn.onclick = () => Manager.openHrRequisitionModal(projectId);
      }

      // PM CSV Report & Export buttons
      const btnRecViewCsv = document.getElementById('btn-rec-view-csv');
      if (btnRecViewCsv) btnRecViewCsv.onclick = () => this.openRankedCsvReport(projectId, rec.project_name);

      const btnRecDownloadCsv = document.getElementById('btn-rec-download-csv');
      if (btnRecDownloadCsv) {
        btnRecDownloadCsv.href = API.getProjectCsvDownloadUrl(projectId);
        btnRecDownloadCsv.download = `${projectId}_ranked_employees.csv`;
      }

      const btnRecEdit = document.getElementById('btn-rec-edit-proj');
      if (btnRecEdit) btnRecEdit.onclick = () => this.openEditProjectModal(projectId);

      const btnRecDelete = document.getElementById('btn-rec-delete-proj');
      if (btnRecDelete) btnRecDelete.onclick = () => this.confirmDeleteProject(projectId);

      document.getElementById('high-risk-rec-modal').classList.add('active');
    } catch (err) {
      console.error(err);
      showToast('Failed to compute high-risk engine recommendations', 'error');
    }
  },

  promptCandidateDecision(employeeId) {
    const rec = State.activeRecData;
    if (!rec) return;

    const cand = (rec.ranked_candidates || []).find(c => c.employee_id === employeeId) || rec.best_candidate;
    if (!cand) return;

    document.getElementById('cand-decision-name').textContent = cand.name;
    document.getElementById('cand-decision-project').textContent = rec.project_name;
    document.getElementById('cand-decision-reason').textContent = cand.reason;

    // Button: Accept Engine Recommendation
    document.getElementById('btn-accept-engine-pick').onclick = async () => {
      document.getElementById('candidate-decision-modal').classList.remove('active');
      await Manager.executeAssignment(rec.project_id, cand.employee_id, cand.name);
    };

    // Button: Opt for Manual Selection
    document.getElementById('btn-opt-manual-selection').onclick = () => {
      document.getElementById('candidate-decision-modal').classList.remove('active');
      Manager.openManualSelectionModal();
    };

    document.getElementById('candidate-decision-modal').classList.add('active');
  },

  openManualSelectionModal() {
    const rec = State.activeRecData;
    if (!rec || !rec.ranked_candidates) return;

    document.getElementById('manual-modal-project-name').textContent = rec.project_name;
    const tbody = document.getElementById('manual-ranked-table-body');
    tbody.innerHTML = '';

    rec.ranked_candidates.forEach(cand => {
      const tr = document.createElement('tr');
      tr.className = 'clickable-row';
      tr.onclick = () => Manager.confirmManualCandidateAdd(cand);

      const isTop = cand.rank === 1;
      const skillsHtml = (cand.skills || []).slice(0, 3).map(s => `<span class="skill-tag">${s}</span>`).join('');

      tr.innerHTML = `
        <td><div class="rank-pill ${isTop ? 'top' : ''}">#${cand.rank}</div></td>
        <td>
          <strong>${cand.name}</strong>
          <div style="font-size:0.75rem; color:var(--text-muted);">${cand.job_title}</div>
        </td>
        <td><span style="font-weight:700; color:var(--primary);">${cand.semantic_match_pct}%</span></td>
        <td>
          <span class="role-badge ${cand.is_bench ? 'employee' : 'manager'}" style="font-size:0.7rem;">
            ${cand.is_bench ? 'Bench' : 'On Project'}
          </span>
        </td>
        <td>${skillsHtml}</td>
        <td style="max-width:320px; font-size:0.8rem; color:var(--text-secondary);">${cand.reason}</td>
        <td>
          <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); Manager.confirmManualCandidateAdd(JSON.parse(decodeURIComponent('${encodeURIComponent(JSON.stringify(cand))}')))">
            Select
          </button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    document.getElementById('manual-selection-modal').classList.add('active');
  },

  confirmManualCandidateAdd(candidate) {
    const rec = State.activeRecData;
    if (!rec) return;

    document.getElementById('confirm-add-emp-name').textContent = candidate.name;
    document.getElementById('confirm-add-proj-name').textContent = rec.project_name;
    document.getElementById('confirm-add-rank-reason').textContent = `Rank #${candidate.rank} (${candidate.semantic_match_pct}% match). ${candidate.reason}`;

    document.getElementById('btn-confirm-add-worker-ok').onclick = async () => {
      document.getElementById('confirm-add-worker-modal').classList.remove('active');
      document.getElementById('manual-selection-modal').classList.remove('active');
      await Manager.executeAssignment(rec.project_id, candidate.employee_id, candidate.name);
    };

    document.getElementById('confirm-add-worker-modal').classList.add('active');
  },

  async executeAssignment(projectId, employeeId, employeeName) {
    CalculationLockManager.lock(`Allocating ${employeeName} & recalculating SLA risks...`);
    try {
      const res = await API.assignEmployee(projectId, employeeId);

      // Close all modals
      document.querySelectorAll('.modal-overlay').forEach(m => m.classList.remove('active'));

      if (res.status === 'assigned_directly') {
        showToast(`✓ ${employeeName} has been directly assigned to the project! Database updated.`, 'success');
      } else if (res.status === 'transfer_offer_sent') {
        showToast(`Transfer invitation sent to ${employeeName} for confirmation.`, 'info');
      }

      await Manager.loadDashboard();
      await App.loadNotifications();
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to allocate employee', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  openNewProjectModal() {
    const form = document.getElementById('new-project-form');
    if (form) form.reset();
    const modal = document.getElementById('new-project-modal');
    if (modal) modal.classList.add('active');
  },

  async submitNewProject(e) {
    e.preventDefault();
    const form = e.target;

    const reqSkillsRaw = form.required_skills ? form.required_skills.value : '';
    const required_skills = reqSkillsRaw.split(',').map(s => s.trim()).filter(Boolean);

    const projectData = {
      project_id: (form.project_id && form.project_id.value.trim()) ? form.project_id.value.trim() : undefined,
      name: form.name ? form.name.value.trim() : '',
      client_tier: form.client_tier ? (parseInt(form.client_tier.value, 10) || 3) : 3,
      investment: form.investment ? (parseFloat(form.investment.value) || 100000) : 100000,
      roi: form.roi ? (parseFloat(form.roi.value) || 0.25) : 0.25,
      skill_criticality: form.skill_criticality ? (parseFloat(form.skill_criticality.value) || 3.0) : 3.0,
      estimated_people: form.estimated_people ? (parseInt(form.estimated_people.value, 10) || 2) : 2,
      importance: form.importance ? (parseFloat(form.importance.value) || 3.0) : 3.0,
      required_skills,
      project_hours: form.project_hours ? (parseFloat(form.project_hours.value) || 160) : 160,
      deadline_days: form.deadline_days ? (parseInt(form.deadline_days.value, 10) || 30) : 30,
      completion_pct: form.completion_pct ? (parseInt(form.completion_pct.value, 10) || 0) : 0,
      description: form.description ? form.description.value.trim() : ''
    };

    CalculationLockManager.lock(`Creating project "${projectData.name}" & computing allocation requirements...`);
    try {
      await API.createProject(projectData);
      showToast(`✓ Project "${projectData.name}" created successfully!`, 'success');
      const modal = document.getElementById('new-project-modal');
      if (modal) modal.classList.remove('active');
      await Manager.loadDashboard();
      await App.loadNotifications();
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to create project', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  async openEditProjectModal(projectId) {
    let proj = State.projects.find(p => p.project_id === projectId) || State.activeProjectForRec;
    if (!proj) {
      try {
        proj = await API.getProject(projectId);
      } catch (e) {
        showToast('Project details not found', 'error');
        return;
      }
    }

    // Close active detail/recommendation modals if open
    const normModal = document.getElementById('project-detail-modal');
    if (normModal) normModal.classList.remove('active');
    const recModal = document.getElementById('high-risk-rec-modal');
    if (recModal) recModal.classList.remove('active');

    // Prepopulate edit form
    const idBadge = document.getElementById('edit-proj-id-badge');
    if (idBadge) idBadge.textContent = proj.project_id;
    const idInput = document.getElementById('edit-proj-id');
    if (idInput) idInput.value = proj.project_id;

    const nameInput = document.getElementById('edit-proj-name');
    if (nameInput) nameInput.value = proj.name || '';
    const tierInput = document.getElementById('edit-proj-tier');
    if (tierInput) tierInput.value = proj.client_tier !== undefined ? proj.client_tier : 3;
    const peopleInput = document.getElementById('edit-proj-people');
    if (peopleInput) peopleInput.value = proj.estimated_people !== undefined ? proj.estimated_people : 3;
    const hoursInput = document.getElementById('edit-proj-hours');
    if (hoursInput) hoursInput.value = proj.project_hours !== undefined ? proj.project_hours : 160;
    const deadlineInput = document.getElementById('edit-proj-deadline');
    if (deadlineInput) deadlineInput.value = proj.deadline_days !== undefined ? proj.deadline_days : 30;
    const compInput = document.getElementById('edit-proj-completion');
    if (compInput) compInput.value = proj.completion_pct !== undefined ? proj.completion_pct : 0;
    const statusInput = document.getElementById('edit-proj-status');
    if (statusInput) statusInput.value = proj.status || 'active';
    const investInput = document.getElementById('edit-proj-investment');
    if (investInput) investInput.value = proj.investment !== undefined ? proj.investment : 100000;
    const roiInput = document.getElementById('edit-proj-roi');
    if (roiInput) roiInput.value = proj.roi !== undefined ? proj.roi : 0.3;
    const critInput = document.getElementById('edit-proj-criticality');
    if (critInput) critInput.value = proj.skill_criticality !== undefined ? proj.skill_criticality : 3.0;

    const skillsInput = document.getElementById('edit-proj-skills');
    if (skillsInput) {
      if (Array.isArray(proj.required_skills)) {
        skillsInput.value = proj.required_skills.join(', ');
      } else if (typeof proj.required_skills === 'string') {
        skillsInput.value = proj.required_skills;
      } else {
        skillsInput.value = '';
      }
    }

    const descInput = document.getElementById('edit-proj-desc');
    if (descInput) descInput.value = proj.description || '';

    const modal = document.getElementById('edit-project-modal');
    if (modal) modal.classList.add('active');
  },

  async submitEditProject(e) {
    e.preventDefault();
    const form = e.target;
    const projectId = form.project_id ? form.project_id.value.trim() : '';
    if (!projectId) {
      showToast('Missing project ID for update', 'error');
      return;
    }

    const reqSkillsRaw = form.required_skills ? form.required_skills.value : '';
    const required_skills = reqSkillsRaw.split(',').map(s => s.trim()).filter(Boolean);

    const projectData = {
      name: form.name ? form.name.value.trim() : '',
      client_tier: form.client_tier ? (parseInt(form.client_tier.value, 10) || 3) : 3,
      investment: form.investment ? (parseFloat(form.investment.value) || 100000) : 100000,
      roi: form.roi ? (parseFloat(form.roi.value) || 0.25) : 0.25,
      skill_criticality: form.skill_criticality ? (parseFloat(form.skill_criticality.value) || 3.0) : 3.0,
      estimated_people: form.estimated_people ? (parseInt(form.estimated_people.value, 10) || 2) : 2,
      required_skills,
      project_hours: form.project_hours ? (parseFloat(form.project_hours.value) || 160) : 160,
      deadline_days: form.deadline_days ? (parseInt(form.deadline_days.value, 10) || 30) : 30,
      completion_pct: form.completion_pct ? (parseInt(form.completion_pct.value, 10) || 0) : 0,
      status: form.status ? form.status.value : 'active',
      description: form.description ? form.description.value.trim() : ''
    };

    CalculationLockManager.lock(`Updating project "${projectData.name}" & recomputing SLA risk...`);
    try {
      showToast(`Saving updates for project "${projectData.name}"...`, 'info');
      await API.updateProject(projectId, projectData);
      showToast(`✓ Project "${projectData.name}" updated successfully!`, 'success');

      const modal = document.getElementById('edit-project-modal');
      if (modal) modal.classList.remove('active');

      await Manager.loadDashboard();
      await App.loadNotifications();

      // If project detail was open, update with latest values
      const normModal = document.getElementById('project-detail-modal');
      if (normModal && normModal.classList.contains('active')) {
        const updatedProj = await API.getProject(projectId);
        this.showNormalProjectModal(updatedProj);
      }
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to update project', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  confirmDeleteProject(projectId) {
    const proj = State.projects.find(p => p.project_id === projectId) || State.activeProjectForRec;
    const projName = proj ? proj.name : projectId;

    const normModal = document.getElementById('project-detail-modal');
    if (normModal) normModal.classList.remove('active');
    const recModal = document.getElementById('high-risk-rec-modal');
    if (recModal) recModal.classList.remove('active');

    const nameEl = document.getElementById('delete-proj-name');
    if (nameEl) nameEl.textContent = projName;
    const idEl = document.getElementById('delete-proj-id');
    if (idEl) idEl.textContent = projectId;

    const confirmBtn = document.getElementById('btn-confirm-delete-proj-ok');
    if (confirmBtn) {
      confirmBtn.onclick = async () => {
        await Manager.executeDeleteProject(projectId);
      };
    }

    const modal = document.getElementById('confirm-delete-project-modal');
    if (modal) modal.classList.add('active');
  },

  async executeDeleteProject(projectId) {
    const modal = document.getElementById('confirm-delete-project-modal');
    if (modal) modal.classList.remove('active');

    const normModal = document.getElementById('project-detail-modal');
    if (normModal) normModal.classList.remove('active');
    const recModal = document.getElementById('high-risk-rec-modal');
    if (recModal) recModal.classList.remove('active');

    CalculationLockManager.lock(`Deleting project ${projectId} and returning staff to Bench...`);
    try {
      showToast(`Deleting project ${projectId}...`, 'info');
      await API.deleteProject(projectId);
      showToast(`✓ Project deleted successfully. Team members returned to Bench.`, 'success');

      await Manager.loadDashboard();
      await App.loadNotifications();
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to delete project', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  confirmRemoveEmployee(projectId, employeeId, employeeName) {
    const proj = State.projects.find(p => p.project_id === projectId) || State.activeProjectForRec;
    const projName = proj ? proj.name : projectId;

    const nameEl = document.getElementById('confirm-remove-emp-name');
    if (nameEl) nameEl.textContent = employeeName;
    const projEl = document.getElementById('confirm-remove-proj-name');
    if (projEl) projEl.textContent = projName;

    const confirmBtn = document.getElementById('btn-confirm-remove-worker-ok');
    if (confirmBtn) {
      confirmBtn.onclick = async () => {
        await Manager.executeRemoveEmployee(projectId, employeeId, employeeName);
      };
    }

    const modal = document.getElementById('confirm-remove-worker-modal');
    if (modal) modal.classList.add('active');
  },

  async executeRemoveEmployee(projectId, employeeId, employeeName) {
    const modal = document.getElementById('confirm-remove-worker-modal');
    if (modal) modal.classList.remove('active');

    CalculationLockManager.lock(`Removing ${employeeName} from project and returning to Bench...`);
    try {
      showToast(`Removing ${employeeName} from project...`, 'info');
      await API.removeEmployeeFromProject(projectId, employeeId);
      showToast(`✓ ${employeeName} returned to Bench successfully.`, 'success');

      await Manager.loadDashboard();
      await App.loadNotifications();

      // Refresh project modal if open
      const normModal = document.getElementById('project-detail-modal');
      if (normModal && normModal.classList.contains('active')) {
        const updatedProj = await API.getProject(projectId);
        this.showNormalProjectModal(updatedProj);
      }
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to remove employee', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  openHrRequisitionModal(projectId = null) {
    const form = document.getElementById('hr-req-form');
    if (form) form.reset();
    if (projectId) {
      const projInput = document.getElementById('hr-req-project-id');
      if (projInput) projInput.value = projectId;
    }
    const modal = document.getElementById('hr-requisition-modal');
    if (modal) modal.classList.add('active');
  },

  async submitHrRequisition(e) {
    e.preventDefault();
    const form = e.target;

    const reqData = {
      project_id: (form.project_id && form.project_id.value.trim()) ? form.project_id.value.trim() : 'General Workforce',
      role_title: form.role_title ? form.role_title.value.trim() : '',
      required_skills: form.required_skills ? form.required_skills.value.trim() : '',
      urgency: form.urgency ? form.urgency.value : 'High',
      description: form.description ? form.description.value.trim() : ''
    };

    try {
      await API.createHrRequest(reqData);
      showToast(`✓ Requisition submitted to HR for "${reqData.role_title}"!`, 'success');
      const modal = document.getElementById('hr-requisition-modal');
      if (modal) modal.classList.remove('active');
      await Manager.loadDashboard();
      await App.loadNotifications();
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to submit HR requisition', 'error');
    }
  },

  async openRankedCsvReport(projectId, projectName) {
    try {
      showToast('Loading PM Ranked Allocation Report...', 'info');
      const data = await API.getProjectRankedCsv(projectId);
      
      document.getElementById('csv-report-project-name').textContent = projectName || data.project_name || projectId;
      document.getElementById('csv-report-file-name').textContent = data.csv_file || `${projectId}_ranked_employees.csv`;
      
      const downloadBtn = document.getElementById('btn-csv-report-download');
      if (downloadBtn) {
        downloadBtn.href = API.getProjectCsvDownloadUrl(projectId);
        downloadBtn.download = data.csv_file || `${projectId}_ranked_employees.csv`;
      }

      const tbody = document.getElementById('csv-report-table-body');
      tbody.innerHTML = '';

      if (!data.rows || data.rows.length === 0) {
        tbody.innerHTML = `<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:2rem;">No ranked candidate records found. Click Recalculate to generate report.</td></tr>`;
      } else {
        data.rows.forEach(row => {
          const tr = document.createElement('tr');
          const isTop = row.rank === '1' || row.rank === 1;
          const isSelected = row.decision && row.decision !== 'ranked_candidate';
          const matchVal = parseFloat(row.semantic_match || 0);
          const matchPct = Math.round(matchVal * 100);
          const utilVal = parseFloat(row.projected_utilization || 0);
          const utilPct = Math.round(utilVal * 100);

          tr.innerHTML = `
            <td><div class="rank-pill ${isTop ? 'top' : ''}">#${row.rank}</div></td>
            <td>
              <strong>${row.employee_name}</strong>
              <div style="font-size:0.72rem; color:var(--text-muted); font-family:var(--font-mono);">${row.employee_id || ''}</div>
            </td>
            <td><span style="font-weight:700; color:var(--primary);">${matchPct}%</span></td>
            <td>${row.effective_hours || '0'} hrs</td>
            <td>
              <span style="color:${utilVal > 1.0 ? '#f87171' : 'var(--text-primary)'}; font-weight:600;">
                ${utilPct}%
              </span>
            </td>
            <td><span style="font-weight:600;">${row.final_score ? (parseFloat(row.final_score) * 100).toFixed(0) + '%' : 'N/A'}</span></td>
            <td>
              <span class="role-badge ${isSelected ? 'manager' : 'employee'}" style="font-size:0.7rem;">
                ${row.decision || 'ranked_candidate'}
              </span>
            </td>
            <td style="max-width:280px; font-size:0.78rem; color:var(--text-secondary); line-height:1.35;">
              ${row.reason || ''}
            </td>
          `;
          tbody.appendChild(tr);
        });
      }

      document.getElementById('pm-csv-report-modal').classList.add('active');
    } catch (err) {
      console.error(err);
      showToast('Failed to load project ranked CSV report', 'error');
    }
  },

  async refreshProjectAllocation(projectId) {
    CalculationLockManager.lock(`Recalculating allocations & SLA risk for project ${projectId}...`);
    try {
      showToast('Recalculating project allocations via ProjectAllocationManager...', 'info');
      const res = await API.refreshProject(projectId);
      showToast(`✓ Allocations and CSV refreshed successfully!`, 'success');
      await this.loadDashboard();
      if (document.getElementById('project-detail-modal').classList.contains('active')) {
        const updatedProj = await API.getProject(projectId);
        this.showNormalProjectModal(updatedProj);
      }
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to refresh project allocation', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  async refreshAllProjectsAllocation() {
    const btnRefreshAll = document.getElementById('btn-pm-refresh-all');
    CalculationLockManager.lock('Recalculating allocations, SLA risks & ranked CSVs for all projects...');
    if (btnRefreshAll) {
      btnRefreshAll.disabled = true;
      btnRefreshAll.textContent = '🔄 Recalculating...';
    }
    showToast('Invoking engine & vector pipeline to recalculate all projects...', 'info');

    try {
      const res = await API.refreshAllProjects();
      showToast(`✓ Recalculations complete! Refreshed ${res.refreshed_count} projects & regenerated ranked CSVs.`, 'success');
      await this.loadDashboard();
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to refresh all projects', 'error');
    } finally {
      if (btnRefreshAll) {
        btnRefreshAll.disabled = false;
        btnRefreshAll.textContent = '🔄 Refresh All Allocations';
      }
      CalculationLockManager.unlock(false);
    }
  },

  bindEvents() {
    const btnNew = document.getElementById('btn-open-new-proj');
    if (btnNew) btnNew.onclick = () => this.openNewProjectModal();

    const btnRefreshAll = document.getElementById('btn-pm-refresh-all');
    if (btnRefreshAll) btnRefreshAll.onclick = () => this.refreshAllProjectsAllocation();

    const btnReqHr = document.getElementById('btn-open-hr-req');
    if (btnReqHr) btnReqHr.onclick = () => this.openHrRequisitionModal();

    const formNewProj = document.getElementById('new-project-form');
    if (formNewProj) formNewProj.onsubmit = (e) => this.submitNewProject(e);

    const formEditProj = document.getElementById('edit-project-form');
    if (formEditProj) formEditProj.onsubmit = (e) => this.submitEditProject(e);

    const formHrReq = document.getElementById('hr-req-form');
    if (formHrReq) formHrReq.onsubmit = (e) => this.submitHrRequisition(e);
  }
};

window.Manager = Manager;
