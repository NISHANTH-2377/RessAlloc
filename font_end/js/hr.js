/**
 * HR Portal Logic: Requisitions, Employee Onboarding & Talent Directory
 */

const HR = {
  async init() {
    await this.loadData();
    this.bindEvents();
  },

  async loadData() {
    try {
      const [employees, hrRequests] = await Promise.all([
        API.getEmployees(),
        API.getHrRequests()
      ]);

      State.employees = employees;
      State.hrRequests = hrRequests;

      this.renderRequisitions();
      this.renderDirectory();
    } catch (err) {
      console.error('Failed to load HR data:', err);
      showToast('Failed to load HR data', 'error');
    }
  },

  renderRequisitions() {
    const container = document.getElementById('hr-requests-list');
    if (!container) return;

    // Filter to active pending requisitions so fulfilled ones vanish
    const pendingRequests = (State.hrRequests || []).filter(req => req.status === 'pending' || !req.status);

    if (pendingRequests.length === 0) {
      container.innerHTML = `
        <div style="padding:1.5rem; text-align:center; color:var(--text-muted); background:var(--bg-card); border-radius:var(--radius-md); border:1px dashed var(--border-color);">
          <div style="font-size:1.5rem; margin-bottom:0.25rem;">✨</div>
          <strong style="color:var(--text-primary); font-size:0.95rem;">No open hiring requisitions</strong>
          <p style="font-size:0.8rem; margin-top:0.25rem; color:var(--text-muted);">All manager requisitions have been fulfilled or none have been submitted yet.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = pendingRequests.map(req => {
      const isUrgent = req.urgency === 'High' || req.urgency === 'Critical';

      return `
        <div class="kpi-card" style="margin-bottom:1rem;" id="hr-req-card-${req.request_id}">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
            <div>
              <div style="font-weight:700; font-size:1.05rem; color:var(--text-primary);">${req.role_title}</div>
              <div style="font-size:0.75rem; color:var(--text-muted); font-family:var(--font-mono);">
                Requisition ${req.request_id} • Target Project: <strong>${req.project_id || 'General'}</strong>
              </div>
            </div>
            <span class="risk-badge ${isUrgent ? 'high' : 'medium'}">${req.urgency} Priority</span>
          </div>

          <p style="font-size:0.85rem; color:var(--text-secondary); margin-bottom:0.75rem;">
            ${req.description || 'No description provided.'}
          </p>

          <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem; border-top:1px solid var(--border-color); padding-top:0.75rem;">
            <div style="font-size:0.8rem; color:var(--text-muted);">
              Required Skills: <strong style="color:var(--text-primary);">${req.required_skills || 'Any'}</strong>
            </div>
            <div style="display:flex; gap:0.5rem;">
              <button class="btn btn-secondary btn-sm" onclick="HR.fulfillRequisition('${req.request_id}', '${encodeURIComponent(req.role_title)}')">
                ✓ Mark Fulfilled
              </button>
              <button class="btn btn-primary btn-sm" onclick="HR.prefillAddEmployee('${encodeURIComponent(JSON.stringify(req))}')">
                + Onboard Matching Talent
              </button>
            </div>
          </div>
        </div>
      `;
    }).join('');
  },

  renderDirectory(filterText = '') {
    const tbody = document.getElementById('hr-directory-table-body');
    if (!tbody) return;

    let emps = State.employees;
    if (filterText) {
      const q = filterText.toLowerCase();
      emps = emps.filter(e => 
        e.full_name.toLowerCase().includes(q) ||
        (e.job_title && e.job_title.toLowerCase().includes(q)) ||
        (e.department && e.department.toLowerCase().includes(q)) ||
        (e.domain_knowledge && e.domain_knowledge.toLowerCase().includes(q))
      );
    }

    if (emps.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding:2rem; color:var(--text-muted);">No employees found matching filter.</td></tr>`;
      return;
    }

    tbody.innerHTML = emps.map(emp => {
      const skillsHtml = (emp.skills || []).slice(0, 3).map(s => `<span class="skill-tag">${s}</span>`).join('');
      const statusBadge = emp.current_project
        ? `<span class="role-badge manager" style="font-size:0.72rem;">On ${emp.current_project}</span>`
        : `<span class="role-badge employee" style="font-size:0.72rem;">Bench (Available)</span>`;

      return `
        <tr>
          <td>
            <strong>${emp.full_name}</strong>
            <div style="font-size:0.75rem; color:var(--text-muted);">${emp.employee_id} • ${emp.email || 'No email'}</div>
          </td>
          <td>
            <div>${emp.job_title || 'Engineer'}</div>
            <div style="font-size:0.75rem; color:var(--text-muted);">${emp.department || 'Engineering'}</div>
          </td>
          <td>${statusBadge}</td>
          <td>${emp.years_experience} yrs (Tier ${emp.seniority_tier})</td>
          <td>${skillsHtml || '<span style="color:var(--text-muted); font-size:0.75rem;">None</span>'}</td>
          <td>
            ${emp.resume_text 
              ? `<button class="btn btn-secondary btn-sm" onclick="HR.viewResumeText('${emp.employee_id}')">View Resume</button>`
              : '<span style="font-size:0.75rem; color:var(--text-muted);">No Resume</span>'
            }
          </td>
          <td>
            <div style="display:flex; gap:0.4rem;">
              <button class="btn btn-secondary btn-sm" onclick="HR.openEditModal('${emp.employee_id}')">Edit</button>
              <button class="btn btn-danger btn-sm" onclick="HR.confirmDelete('${emp.employee_id}')">Delete</button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  populateRequisitionSelect(selectedReqId = '') {
    const select = document.getElementById('emp-fulfills-request');
    if (!select) return;

    const pendingRequests = (State.hrRequests || []).filter(r => r.status === 'pending' || !r.status);
    let options = `<option value="">None (General Workforce Onboarding)</option>`;
    pendingRequests.forEach(req => {
      const isSelected = req.request_id === selectedReqId ? 'selected' : '';
      const projLabel = req.project_id && req.project_id !== 'General' ? ` [Project: ${req.project_id}]` : '';
      options += `<option value="${req.request_id}" ${isSelected}>${req.request_id} — ${req.role_title}${projLabel}</option>`;
    });
    select.innerHTML = options;
    if (selectedReqId) {
      select.value = selectedReqId;
    }
  },

  clearRequisitionLink() {
    const select = document.getElementById('emp-fulfills-request');
    if (select) select.value = '';
    const banner = document.getElementById('emp-fulfills-banner');
    if (banner) banner.style.display = 'none';
  },

  prefillAddEmployee(encodedReq) {
    try {
      const req = JSON.parse(decodeURIComponent(encodedReq));
      this.openAddModal();

      // Prefill fields
      if (document.getElementById('emp-job-title')) document.getElementById('emp-job-title').value = req.role_title || '';
      if (document.getElementById('emp-domain-knowledge')) document.getElementById('emp-domain-knowledge').value = req.required_skills || '';

      // Setup requisition linkage
      this.populateRequisitionSelect(req.request_id);

      const banner = document.getElementById('emp-fulfills-banner');
      const bannerText = document.getElementById('emp-fulfills-banner-text');
      if (banner && bannerText) {
        bannerText.textContent = `${req.role_title} (${req.request_id}${req.project_id ? ' • ' + req.project_id : ''})`;
        banner.style.display = 'flex';
      }
    } catch (e) {
      console.error('Failed to prefill from requisition:', e);
      this.openAddModal();
    }
  },

  async fulfillRequisition(requestId, encodedRoleTitle = '') {
    const roleTitle = encodedRoleTitle ? decodeURIComponent(encodedRoleTitle) : requestId;
    if (!confirm(`Mark requisition "${roleTitle}" (${requestId}) as fulfilled? This will close the request and remove it from manager alerts.`)) {
      return;
    }

    CalculationLockManager.lock(`Marking requisition ${requestId} as fulfilled...`);
    try {
      await API.updateHrRequestStatus(requestId, 'fulfilled');
      showToast(`✓ Requisition ${requestId} marked as fulfilled!`, 'success');
      await this.loadData();
      if (typeof Manager !== 'undefined' && Manager.loadDashboard) {
        await Manager.loadDashboard();
      }
      await App.loadNotifications();
    } catch (err) {
      console.error('Failed to fulfill requisition:', err);
      showToast(err.message || 'Failed to fulfill requisition', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  openAddModal() {
    const form = document.getElementById('add-emp-form');
    if (form) form.reset();

    const titleEl = document.getElementById('add-emp-modal-title');
    if (titleEl) titleEl.textContent = 'Onboard New Employee';

    const idInput = document.getElementById('emp-id-input');
    if (idInput) {
      idInput.readOnly = false;
      idInput.value = `EMP-${Math.floor(100 + Math.random() * 900)}`;
    }

    const utilEl = document.getElementById('emp-utilization');
    if (utilEl) utilEl.value = '0.0';

    const submitBtn = document.querySelector('#add-emp-form button[type="submit"]');
    if (submitBtn) submitBtn.textContent = 'Save Employee Record';

    // Show requisition dropdown for onboarding
    const reqGroup = document.getElementById('emp-fulfills-group');
    if (reqGroup) reqGroup.style.display = 'block';

    const banner = document.getElementById('emp-fulfills-banner');
    if (banner) banner.style.display = 'none';

    this.populateRequisitionSelect('');

    const modal = document.getElementById('add-employee-modal');
    if (modal) modal.classList.add('active');
  },

  async openEditModal(employeeId) {
    let emp = (State.employees || []).find(e => e.employee_id === employeeId);
    if (!emp) {
      try {
        emp = await API.getEmployee(employeeId);
      } catch (err) {
        console.warn('Employee not found:', employeeId, err);
        showToast(`Employee ${employeeId} not found`, 'error');
        return;
      }
    }

    const form = document.getElementById('add-emp-form');
    if (form) form.reset();

    const titleEl = document.getElementById('add-emp-modal-title');
    if (titleEl) titleEl.textContent = `Edit Employee: ${emp.full_name || emp.employee_id}`;

    const idInput = document.getElementById('emp-id-input');
    if (idInput) {
      idInput.value = emp.employee_id;
      idInput.readOnly = true;
    }

    // Hide requisition dropdown when editing an existing employee
    const reqGroup = document.getElementById('emp-fulfills-group');
    if (reqGroup) reqGroup.style.display = 'none';
    const banner = document.getElementById('emp-fulfills-banner');
    if (banner) banner.style.display = 'none';

    if (document.getElementById('emp-full-name')) document.getElementById('emp-full-name').value = emp.full_name || '';
    if (document.getElementById('emp-email')) document.getElementById('emp-email').value = emp.email || '';
    if (document.getElementById('emp-phone')) document.getElementById('emp-phone').value = emp.phone || '';
    if (document.getElementById('emp-dob')) document.getElementById('emp-dob').value = emp.date_of_birth || '';
    if (document.getElementById('emp-job-title')) document.getElementById('emp-job-title').value = emp.job_title || '';
    if (document.getElementById('emp-department')) document.getElementById('emp-department').value = emp.department || 'Engineering';
    if (document.getElementById('emp-location')) document.getElementById('emp-location').value = emp.location || '';
    if (document.getElementById('emp-years-exp')) document.getElementById('emp-years-exp').value = emp.years_experience ?? 1.0;
    if (document.getElementById('emp-domain-knowledge')) document.getElementById('emp-domain-knowledge').value = emp.domain_knowledge || (emp.skills ? emp.skills.join(', ') : '');
    if (document.getElementById('emp-seniority-tier')) document.getElementById('emp-seniority-tier').value = emp.seniority_tier ?? 1;
    if (document.getElementById('emp-availability-hours')) document.getElementById('emp-availability-hours').value = emp.availability_hours ?? 40;
    if (document.getElementById('emp-ability-score')) document.getElementById('emp-ability-score').value = emp.ability_score ?? 0.8;
    
    const utilEl = document.getElementById('emp-utilization');
    if (utilEl) utilEl.value = emp.utilization ?? 0.0;

    const submitBtn = document.querySelector('#add-emp-form button[type="submit"]');
    if (submitBtn) submitBtn.textContent = 'Update Employee';

    const modal = document.getElementById('add-employee-modal');
    if (modal) modal.classList.add('active');
  },

  async handleEmployeeSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const idInput = document.getElementById('emp-id-input');
    const isEditing = idInput ? idInput.readOnly : false;
    const empId = idInput ? (idInput.value || '').trim() : '';

    // Use FormData to allow file upload
    const formData = new FormData(form);
    const empName = (formData.get('full_name') || empId || 'employee').toString();

    CalculationLockManager.lock(
      isEditing 
        ? `Updating ${empName} in database & recalculating Qdrant vector index...`
        : `Onboarding ${empName} to database & recalculating workforce allocations...`
    );

    try {
      if (isEditing) {
        if (!empId) {
          throw new Error('Employee ID is missing.');
        }
        const fileInput = document.getElementById('emp-resume-file');
        const hasNewResume = fileInput && fileInput.files && fileInput.files.length > 0;
        if (hasNewResume) {
          await API.updateEmployee(empId, formData);
        } else {
          // Clean JSON payload
          const jsonBody = {};
          formData.forEach((val, key) => {
            if (key !== 'resume') {
              if (key === 'years_experience' || key === 'availability_hours' || key === 'ability_score' || key === 'utilization') {
                jsonBody[key] = parseFloat(val) || 0;
              } else if (key === 'seniority_tier') {
                jsonBody[key] = parseInt(val, 10) || 1;
              } else {
                jsonBody[key] = val;
              }
            }
          });
          jsonBody.employee_id = empId;
          await API.updateEmployee(empId, jsonBody);
        }
        showToast(`✓ Employee ${empName} updated successfully!`, 'success');
      } else {
        const result = await API.addEmployee(formData);
        const fulfilledId = result && result.fulfilled_requisition_id;
        if (fulfilledId) {
          showToast(`✓ New employee ${empName} onboarded & requisition ${fulfilledId} fulfilled!`, 'success');
        } else {
          showToast(`✓ New employee ${empName} onboarded!`, 'success');
        }
      }

      const modal = document.getElementById('add-employee-modal');
      if (modal) modal.classList.remove('active');
      await this.loadData();
      if (typeof Manager !== 'undefined' && Manager.loadDashboard) {
        await Manager.loadDashboard();
      }
      await App.loadNotifications();
    } catch (err) {
      console.error('Save employee error:', err);
      showToast(err.message || 'Failed to save employee', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  confirmDelete(employeeId) {
    const emp = (State.employees || []).find(e => e.employee_id === employeeId);
    const fullName = emp ? emp.full_name : employeeId;
    if (!confirm(`Are you sure you want to delete employee "${fullName}" (${employeeId})? This will permanently remove their records.`)) {
      return;
    }
    this.executeDelete(employeeId);
  },

  async executeDelete(employeeId) {
    CalculationLockManager.lock(`Deleting employee ${employeeId} from database & recalculating allocations...`);
    try {
      await API.deleteEmployee(employeeId);
      showToast(`✓ Employee ${employeeId} deleted from database.`, 'info');
      await this.loadData();
      if (typeof Manager !== 'undefined' && Manager.loadDashboard) {
        await Manager.loadDashboard();
      }
      await App.loadNotifications();
    } catch (err) {
      console.error('Delete employee error:', err);
      showToast(err.message || 'Failed to delete employee', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  viewResumeText(employeeId) {
    const emp = State.employees.find(e => e.employee_id === employeeId);
    if (!emp) return;

    document.getElementById('resume-view-name').textContent = emp.full_name;
    document.getElementById('resume-view-body').textContent = emp.resume_text || 'No resume content available.';
    document.getElementById('resume-viewer-modal').classList.add('active');
  },

  bindEvents() {
    const btnAdd = document.getElementById('btn-open-add-employee');
    if (btnAdd) btnAdd.onclick = () => this.openAddModal();

    const form = document.getElementById('add-emp-form');
    if (form) form.onsubmit = (e) => this.handleEmployeeSubmit(e);

    const searchInput = document.getElementById('hr-search-talent');
    if (searchInput) {
      searchInput.oninput = (e) => this.renderDirectory(e.target.value);
    }

    const reqSelect = document.getElementById('emp-fulfills-request');
    if (reqSelect) {
      reqSelect.onchange = (e) => {
        const reqId = e.target.value;
        const banner = document.getElementById('emp-fulfills-banner');
        const bannerText = document.getElementById('emp-fulfills-banner-text');
        if (reqId) {
          const req = (State.hrRequests || []).find(r => r.request_id === reqId);
          if (banner && bannerText) {
            bannerText.textContent = req ? `${req.role_title} (${req.request_id}${req.project_id ? ' • ' + req.project_id : ''})` : reqId;
            banner.style.display = 'flex';
          }
          if (req) {
            const jobTitleInput = document.getElementById('emp-job-title');
            if (jobTitleInput && !jobTitleInput.value) {
              jobTitleInput.value = req.role_title || '';
            }
            const domainInput = document.getElementById('emp-domain-knowledge');
            if (domainInput && !domainInput.value) {
              domainInput.value = req.required_skills || '';
            }
          }
        } else {
          if (banner) banner.style.display = 'none';
        }
      };
    }
  }
};

window.HR = HR;
