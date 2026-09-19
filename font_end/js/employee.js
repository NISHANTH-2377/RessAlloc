/**
 * Employee Portal Logic: Project Assignment Viewer & Transfer Negotiation
 */

const Employee = {
  activeDashboardData: null,

  async init(employeeId = State.currentEmployeeId) {
    State.currentEmployeeId = employeeId;
    await this.loadDashboard();
    this.bindEvents();
  },

  async loadDashboard() {
    try {
      const data = await API.getEmployeeDashboard(State.currentEmployeeId);
      this.activeDashboardData = data;
      this.renderProfile();
      this.renderCurrentProject();
      this.renderTransferOffer();
      this.renderNotificationsList();
    } catch (err) {
      console.error('Failed to load employee dashboard:', err);
      showToast('Failed to load employee details', 'error');
    }
  },

  renderProfile() {
    const emp = this.activeDashboardData.employee;
    if (!emp) return;

    document.getElementById('emp-portal-name').textContent = emp.full_name;
    document.getElementById('emp-portal-role').textContent = `${emp.job_title} • ${emp.department}`;
    document.getElementById('emp-portal-id').textContent = `ID: ${emp.employee_id} • ${emp.location || 'Remote'}`;
    document.getElementById('emp-portal-exp').textContent = `${emp.years_experience} Years`;
    document.getElementById('emp-portal-avail').textContent = `${emp.availability_hours} hrs/wk`;
    document.getElementById('emp-portal-ability').textContent = `${(emp.ability_score * 100).toFixed(0)}%`;
    document.getElementById('emp-portal-util').textContent = `${(emp.utilization * 100).toFixed(0)}%`;

    const skillsContainer = document.getElementById('emp-portal-skills');
    skillsContainer.innerHTML = (emp.skills || []).map(s => `<span class="skill-tag">${s}</span>`).join('') || 'None listed';
  },

  renderCurrentProject() {
    const data = this.activeDashboardData;
    const project = data.current_project;
    const container = document.getElementById('emp-current-project-slot');
    if (!container) return;

    if (!project) {
      container.innerHTML = `
        <div style="text-align:center; padding:2rem; background:rgba(16, 185, 129, 0.05); border:1px dashed rgba(16, 185, 129, 0.3); border-radius:var(--radius-lg);">
          <div style="font-size:1.15rem; font-weight:700; color:var(--success); margin-bottom:0.4rem;">
            Currently on Bench / Available for Deployment
          </div>
          <p style="color:var(--text-secondary); font-size:0.88rem; max-width:500px; margin:0 auto;">
            You have 100% capacity available. When a Project Manager assigns you to an initiative, you will receive your project mandate here.
          </p>
        </div>
      `;
      return;
    }

    const membersHtml = (data.project_members || []).map(m => `
      <div style="display:inline-flex; align-items:center; gap:0.5rem; background:var(--bg-subtle); padding:0.4rem 0.75rem; border-radius:var(--radius-full); margin:0.25rem;">
        <span style="font-size:0.8rem; font-weight:600;">${m.full_name}</span>
        <span style="font-size:0.7rem; color:var(--text-muted);">(${m.job_title})</span>
      </div>
    `).join('') || '<span style="font-size:0.8rem; color:var(--text-muted);">Sole contributor assigned so far</span>';

    container.innerHTML = `
      <div style="background:var(--bg-card); border:1px solid var(--border-color); border-radius:var(--radius-lg); padding:1.5rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
          <div>
            <div style="font-size:1.3rem; font-weight:800; color:var(--text-primary);">${project.name}</div>
            <div style="font-family:var(--font-mono); font-size:0.8rem; color:var(--primary); margin-top:0.2rem;">
              Project Code: ${project.project_id} • Client Tier: ${project.client_tier}
            </div>
          </div>
          <span class="role-badge manager">Active Assignment</span>
        </div>

        <p style="font-size:0.9rem; color:var(--text-secondary); margin-bottom:1.25rem;">
          ${project.description || 'Enterprise project assignment.'}
        </p>

        <div class="kpi-grid" style="margin-bottom:1.25rem;">
          <div class="kpi-card" style="padding:1rem;">
            <div class="kpi-header">Project Scope</div>
            <div style="font-size:1.4rem; font-weight:800; margin-top:0.25rem;">${project.project_hours} hrs</div>
          </div>
          <div class="kpi-card" style="padding:1rem;">
            <div class="kpi-header">Deadline Horizon</div>
            <div style="font-size:1.4rem; font-weight:800; margin-top:0.25rem;">${project.deadline_days} days</div>
          </div>
          <div class="kpi-card" style="padding:1rem;">
            <div class="kpi-header">Completion Status</div>
            <div style="font-size:1.4rem; font-weight:800; margin-top:0.25rem;">${project.completion_pct}%</div>
          </div>
        </div>

        <div style="border-top:1px solid var(--border-color); padding-top:1rem;">
          <div style="font-size:0.85rem; font-weight:600; color:var(--text-secondary); margin-bottom:0.5rem;">Project Teammates:</div>
          <div>${membersHtml}</div>
        </div>
      </div>
    `;
  },

  renderTransferOffer() {
    const offer = this.activeDashboardData.pending_offer;
    const banner = document.getElementById('emp-transfer-banner-slot');
    if (!banner) return;

    if (!offer) {
      banner.style.display = 'none';
      banner.innerHTML = '';
      return;
    }

    banner.style.display = 'block';
    const isCurrentlyWorking = offer.is_currently_working;

    banner.innerHTML = `
      <div class="transfer-alert-banner">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:1rem;">
          <div>
            <div style="font-size:0.8rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--primary); margin-bottom:0.25rem;">
              ⚡ Urgent Project Allocation Invitation
            </div>
            <div style="font-size:1.35rem; font-weight:800;">
              Project Manager has nominated you for "${offer.project_name}"
            </div>
          </div>
          <span class="risk-badge high">Action Required</span>
        </div>

        <p style="font-size:0.92rem; color:var(--text-secondary); margin-bottom:1.25rem; background:rgba(0,0,0,0.25); padding:1rem; border-radius:var(--radius-md);">
          <strong>Project Description:</strong> ${offer.description || 'High-priority initiative requiring your specialized domain competencies.'}
          <br><br>
          <strong>Scope:</strong> ${offer.project_hours} estimated total hours • <strong>Deadline:</strong> ${offer.deadline_days} days
          <br>
          <strong>Required Skills:</strong> ${(offer.required_skills || []).join(', ') || 'Domain Engineering'}
        </p>

        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:1rem;">
          <div style="font-size:0.85rem; color:var(--text-muted);">
            ${isCurrentlyWorking 
              ? 'You are currently on an active project. You may choose to accept the transfer, stick with your current assignment, or dismiss this notification.'
              : 'You are currently available on the bench. You may accept the assignment or dismiss this notification.'
            }
          </div>

          <div style="display:flex; gap:0.75rem; flex-wrap:wrap;">
            <button class="btn btn-secondary" onclick="Employee.dismissOfferNotification('${offer.offer_id}')" title="Dismiss notification without accepting or rejecting">
              ✕ Dismiss Notification
            </button>
            ${isCurrentlyWorking ? `
              <button class="btn btn-secondary" onclick="Employee.openDeclineModal('${offer.offer_id}', '${offer.project_name}')">
                Stick with Old Project
              </button>
              <button class="btn btn-primary" onclick="Employee.acceptTransfer('${offer.offer_id}')">
                Accept New Project
              </button>
            ` : `
              <button class="btn btn-primary" onclick="Employee.acceptTransfer('${offer.offer_id}')">
                Accept Project Assignment
              </button>
            `}
          </div>
        </div>
      </div>
    `;
  },

  renderNotificationsList() {
    const container = document.getElementById('emp-notifications-container');
    const badge = document.getElementById('emp-notif-count-badge');
    if (!container) return;

    // Filter notifications relevant to this employee
    const empNotifs = (State.notifications || []).filter(n => 
      (n.recipient_role === 'employee' || n.recipient_role === 'all') &&
      (!n.recipient_id || n.recipient_id === State.currentEmployeeId)
    );

    if (badge) {
      const unreadCount = empNotifs.filter(n => !n.read_status).length;
      badge.textContent = unreadCount;
      badge.style.display = unreadCount > 0 ? 'inline-block' : 'none';
    }

    if (empNotifs.length === 0) {
      container.innerHTML = `
        <div style="text-align:center; padding:1.5rem; color:var(--text-muted); font-size:0.85rem; background:rgba(0,0,0,0.15); border-radius:var(--radius-md);">
          No active notifications or pending allocation requests for this profile.
        </div>
      `;
      return;
    }

    container.innerHTML = empNotifs.map(n => {
      const timeStr = new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      return `
        <div class="emp-notif-card ${n.type || 'info'}" id="emp-notif-card-${n.id}">
          <div style="flex:1; padding-right:1rem;">
            <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.25rem;">
              <strong style="font-size:0.92rem; color:var(--text-primary);">${n.title}</strong>
              <span style="font-size:0.72rem; color:var(--text-muted);">${timeStr}</span>
            </div>
            <p style="font-size:0.85rem; color:var(--text-secondary); margin:0;">${n.message}</p>
          </div>
          <div style="display:flex; align-items:center; gap:0.5rem;">
            <button class="notif-dismiss-btn" onclick="Employee.dismissNotification(${n.id}, event)" title="Dismiss this notification without affecting project assignments">
              Cancel
            </button>
          </div>
        </div>
      `;
    }).join('');
  },

  async dismissNotification(notifId, event = null) {
    if (event) event.stopPropagation();
    try {
      await API.dismissNotification(notifId);
      // Remove from State.notifications
      State.notifications = State.notifications.filter(n => n.id !== notifId);
      // Remove from DOM
      const card = document.getElementById(`emp-notif-card-${notifId}`);
      if (card) card.remove();
      this.renderNotificationsList();
      App.loadNotifications();
      showToast('Notification dismissed. Task and project assignment remain unchanged.', 'info');
    } catch (err) {
      console.error(err);
      showToast('Failed to dismiss notification', 'error');
    }
  },

  async dismissOfferNotification(offerId) {
    const banner = document.getElementById('emp-transfer-banner-slot');
    if (banner) {
      banner.style.display = 'none';
    }

    // Also dismiss any corresponding notification in DB if found
    const matchingNotif = (State.notifications || []).find(n => 
      n.metadata && n.metadata.offer_id === offerId
    );
    if (matchingNotif) {
      try {
        await API.dismissNotification(matchingNotif.id);
        State.notifications = State.notifications.filter(n => n.id !== matchingNotif.id);
        this.renderNotificationsList();
        App.loadNotifications();
      } catch (err) {
        console.warn('Could not dismiss matching notification in DB:', err);
      }
    }

    showToast('Notification dismissed. Your project status was neither accepted nor declined.', 'info');
  },

  async acceptTransfer(offerId) {
    CalculationLockManager.lock('Accepting project assignment & recalculating workforce allocations...');
    try {
      const res = await API.submitTransferResponse(State.currentEmployeeId, offerId, 'accept');
      showToast(res.message || '✓ Project accepted! Database records updated.', 'success');
      await this.loadDashboard();
      await App.loadNotifications();
    } catch (err) {
      console.error(err);
      showToast(err.message || 'Failed to accept project', 'error');
    } finally {
      CalculationLockManager.unlock(true);
    }
  },

  openDeclineModal(offerId, projectName) {
    document.getElementById('decline-modal-project-name').textContent = projectName;
    document.getElementById('decline-reason-input').value = '';

    document.getElementById('btn-confirm-decline-submit').onclick = async () => {
      const reason = document.getElementById('decline-reason-input').value.trim();
      if (!reason) {
        alert('Please provide a valid reason for declining the assignment.');
        return;
      }

      try {
        const res = await API.submitTransferResponse(State.currentEmployeeId, offerId, 'decline', reason);
        document.getElementById('decline-reason-modal').classList.remove('active');
        showToast('✓ You chose to stick with your current project. Reason sent to manager.', 'info');
        await Employee.loadDashboard();
        await App.loadNotifications();
      } catch (err) {
        console.error(err);
        showToast(err.message || 'Failed to submit decline reason', 'error');
      }
    };

    document.getElementById('decline-reason-modal').classList.add('active');
  },

  bindEvents() {
    const empSelect = document.getElementById('employee-picker-select');
    if (empSelect) {
      empSelect.onchange = (e) => {
        State.setRole('employee', e.target.value);
        this.loadDashboard();
      };
    }
  }
};
