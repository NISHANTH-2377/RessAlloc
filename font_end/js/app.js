/**
 * Main Application Orchestrator, Router & Authentication Guard
 */

const App = {
  activeLoginRole: 'employee',

  async init() {
    this.setupGlobalEvents();
    this.setupAuthGuard();
    await this.populateEmployeeSelector();

    const hasSession = State.loadSavedSession();
    if (hasSession && State.isAuthenticated()) {
      this.switchRoleView(State.currentRole, State.currentEmployeeId);
    } else {
      this.showLoginView();
    }

    // Background notifications poll (only active when logged in)
    setInterval(() => {
      if (State.isAuthenticated()) {
        this.loadNotifications();
      }
    }, 8000);
  },

  setupAuthGuard() {
    // Intercept browser back/forward navigation
    window.addEventListener('popstate', () => {
      if (!State.isAuthenticated()) {
        this.showLoginView();
      } else if (window.location.hash === '#login') {
        // Logged-in user pressing back to login -> redirect to their active role
        this.switchRoleView(State.currentRole, State.currentEmployeeId);
      }
    });

    window.addEventListener('hashchange', () => {
      if (!State.isAuthenticated()) {
        this.showLoginView();
      }
    });
  },

  showLoginView() {
    // Hide all view sections
    document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

    // Show login section
    const loginSection = document.getElementById('login-view');
    if (loginSection) {
      loginSection.classList.add('active');
    }

    // Hide authenticated header actions
    const headerActions = document.getElementById('header-authenticated-actions');
    if (headerActions) {
      headerActions.style.display = 'none';
    }

    // Update history so back button cannot restore previous dashboard
    if (window.location.hash !== '#login') {
      history.replaceState(null, '', '#login');
    }

    this.selectLoginRole(this.activeLoginRole);
  },

  selectLoginRole(role) {
    this.activeLoginRole = role;

    // Update active tab button
    document.querySelectorAll('.role-tab').forEach(tab => {
      if (tab.dataset.loginRole === role) {
        tab.classList.add('active');
      } else {
        tab.classList.remove('active');
      }
    });

    const hint = document.getElementById('login-role-hint');
    const empSelectGroup = document.getElementById('login-emp-select-group');
    const usernameInput = document.getElementById('login-username');
    const empSelect = document.getElementById('login-emp-select');
    const errorAlert = document.getElementById('login-error-alert');
    if (errorAlert) errorAlert.style.display = 'none';

    if (role === 'employee') {
      if (hint) hint.textContent = 'Access your assigned tasks, review project scope, and respond to allocation invitations.';
      if (empSelectGroup) empSelectGroup.style.display = 'block';
      if (usernameInput) {
        usernameInput.placeholder = 'e.g. EMP-001 or alex';
        if (empSelect && empSelect.value) {
          usernameInput.value = empSelect.value;
        } else {
          usernameInput.value = 'EMP-001';
        }
      }
    } else if (role === 'manager') {
      if (hint) hint.textContent = 'Track ongoing projects, monitor SLA delivery risks, and allocate talent with the engine.';
      if (empSelectGroup) empSelectGroup.style.display = 'none';
      if (usernameInput) {
        usernameInput.placeholder = 'manager';
        usernameInput.value = 'manager';
      }
    } else if (role === 'hr') {
      if (hint) hint.textContent = 'Maintain corporate workforce records, review hiring requisitions, and onboard new talent.';
      if (empSelectGroup) empSelectGroup.style.display = 'none';
      if (usernameInput) {
        usernameInput.placeholder = 'hr';
        usernameInput.value = 'hr';
      }
    }
  },

  async handleLoginSubmit(e) {
    if (e) e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();
    const errorAlert = document.getElementById('login-error-alert');
    const submitBtn = document.getElementById('btn-login-submit');

    if (!username || !password) {
      if (errorAlert) {
        errorAlert.textContent = 'Please enter both username and password.';
        errorAlert.style.display = 'flex';
      }
      return;
    }

    if (errorAlert) errorAlert.style.display = 'none';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Authenticating...';
    }

    try {
      const res = await API.login(username, password, this.activeLoginRole);
      if (res.success && res.user) {
        State.setSession(res.user, res.token);
        showToast(`✓ Welcome, ${res.user.full_name}!`, 'success');
        this.switchRoleView(res.user.role, res.user.employee_id);
      } else {
        throw new Error(res.error || 'Authentication failed');
      }
    } catch (err) {
      console.error('Login error:', err);
      if (errorAlert) {
        errorAlert.textContent = err.message || 'Invalid credentials. Please verify your login details.';
        errorAlert.style.display = 'flex';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Sign In to Portal';
      }
    }
  },

  async quickLogin(role, employeeId = null) {
    this.selectLoginRole(role);
    let username = role;
    if (role === 'employee') {
      username = employeeId || 'EMP-001';
      const empSelect = document.getElementById('login-emp-select');
      if (empSelect && employeeId) empSelect.value = employeeId;
    }

    const usernameInput = document.getElementById('login-username');
    const passwordInput = document.getElementById('login-password');
    if (usernameInput) usernameInput.value = username;
    if (passwordInput) passwordInput.value = 'password123';

    await this.handleLoginSubmit(null);
  },

  async handleSignOut() {
    try {
      await API.logout();
    } catch (e) {
      console.warn('Logout API error:', e);
    }

    State.clearSession();
    this.showLoginView();
    showToast('Signed out of session successfully.', 'info');
  },

  switchRoleView(role, employeeId = null) {
    if (!State.isAuthenticated()) {
      this.showLoginView();
      return;
    }

    State.setRole(role, employeeId);

    // Hide all view sections
    document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));

    // Show authenticated header controls
    const headerActions = document.getElementById('header-authenticated-actions');
    if (headerActions) {
      headerActions.style.display = 'flex';
    }

    // Update active nav / role badge
    const badge = document.getElementById('active-role-badge');
    if (badge) {
      badge.className = `role-badge ${role}`;
      badge.textContent = role.toUpperCase();
    }

    // Update user profile display in header
    const userNameDisplay = document.getElementById('header-user-name');
    if (userNameDisplay && State.currentUser) {
      userNameDisplay.textContent = State.currentUser.full_name || State.currentUser.username;
    }

    const roleSelect = document.getElementById('header-role-switcher');
    if (roleSelect) roleSelect.value = role;

    // Show target section
    const targetSection = document.getElementById(`${role}-view`);
    if (targetSection) targetSection.classList.add('active');

    // Toggle employee picker visibility in header
    const empPickerWrap = document.getElementById('header-emp-picker-wrap');
    if (empPickerWrap) {
      empPickerWrap.style.display = (role === 'employee') ? 'block' : 'none';
    }

    // Replace history entry to record active dashboard
    history.replaceState(null, '', `#${role}`);

    // Initialize role module
    if (role === 'manager') {
      Manager.init();
    } else if (role === 'hr') {
      HR.init();
    } else if (role === 'employee') {
      Employee.init(State.currentEmployeeId);
    }

    this.loadNotifications();
  },

  async populateEmployeeSelector() {
    try {
      const emps = await API.getEmployees();
      State.employees = emps;

      // Populate header employee switcher & login screen employee list
      const selectors = [
        document.getElementById('header-emp-select'),
        document.getElementById('login-emp-select')
      ];

      selectors.forEach(sel => {
        if (!sel) return;
        sel.innerHTML = emps.map(e => `
          <option value="${e.employee_id}" ${e.employee_id === State.currentEmployeeId ? 'selected' : ''}>
            ${e.full_name} (${e.job_title} - ${e.current_project ? 'On ' + e.current_project : 'Bench'})
          </option>
        `).join('');
      });
    } catch (err) {
      console.warn('Could not populate employee selectors:', err);
    }
  },

  async loadNotifications() {
    if (!State.isAuthenticated()) return;

    try {
      const notifs = await API.getNotifications(State.currentRole, State.currentEmployeeId);
      State.notifications = notifs;

      const unreadCount = notifs.filter(n => !n.read_status).length;
      const badge = document.getElementById('notif-badge-count');
      if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
      }

      this.renderNotificationDrawer(notifs);

      // If employee view is currently active, also refresh the employee dashboard notifications list
      if (State.currentRole === 'employee' && Employee.renderNotificationsList) {
        Employee.renderNotificationsList();
      }
    } catch (err) {
      console.warn('Notification poll error:', err);
    }
  },

  renderNotificationDrawer(notifs) {
    const container = document.getElementById('notif-drawer-list');
    if (!container) return;

    if (notifs.length === 0) {
      container.innerHTML = `<div style="text-align:center; padding:2rem; color:var(--text-muted); font-size:0.85rem;">No notifications at this time.</div>`;
      return;
    }

    container.innerHTML = notifs.map(n => {
      const isUnread = !n.read_status;
      const timeStr = new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      return `
        <div class="notif-item ${isUnread ? 'unread' : ''} ${n.type}" id="drawer-notif-${n.id}">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.25rem;">
            <div class="notif-item-title">${n.title}</div>
            <span style="font-size:0.7rem; color:var(--text-muted);">${timeStr}</span>
          </div>
          <div class="notif-item-msg" style="margin-bottom:0.5rem;">${n.message}</div>
          <div style="display:flex; justify-content:flex-end;">
            <button class="notif-dismiss-btn" onclick="App.dismissNotification(${n.id}, event)" title="Dismiss notification without affecting tasks">
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
      // Remove from state
      State.notifications = State.notifications.filter(n => n.id !== notifId);

      // Remove from drawer
      const drawerItem = document.getElementById(`drawer-notif-${notifId}`);
      if (drawerItem) drawerItem.remove();

      // Update badge
      const unreadCount = State.notifications.filter(n => !n.read_status).length;
      const badge = document.getElementById('notif-badge-count');
      if (badge) {
        badge.textContent = unreadCount;
        badge.style.display = unreadCount > 0 ? 'flex' : 'none';
      }

      // If employee view is active, update employee dashboard notifications list too
      if (State.currentRole === 'employee' && Employee.renderNotificationsList) {
        Employee.renderNotificationsList();
      }

      showToast('Notification dismissed. Task and project assignment remain unchanged.', 'info');
    } catch (err) {
      console.error(err);
      showToast('Failed to dismiss notification', 'error');
    }
  },

  toggleNotifDrawer(forceOpen = null) {
    const drawer = document.getElementById('notif-drawer');
    if (!drawer) return;

    if (forceOpen !== null) {
      if (forceOpen) drawer.classList.add('open');
      else drawer.classList.remove('open');
    } else {
      drawer.classList.toggle('open');
    }
  },

  async markAllNotificationsRead() {
    await API.markNotificationsRead(State.currentRole);
    await this.loadNotifications();
    showToast('Notifications marked as read', 'info');
  },

  setupGlobalEvents() {
    // Login form submission
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
      loginForm.onsubmit = (e) => this.handleLoginSubmit(e);
    }

    // Login role tabs
    document.querySelectorAll('.role-tab').forEach(tab => {
      tab.onclick = () => {
        const role = tab.dataset.loginRole;
        if (role) this.selectLoginRole(role);
      };
    });

    // Login employee dropdown change
    const loginEmpSelect = document.getElementById('login-emp-select');
    if (loginEmpSelect) {
      loginEmpSelect.onchange = (e) => {
        const usernameInput = document.getElementById('login-username');
        if (usernameInput && this.activeLoginRole === 'employee') {
          usernameInput.value = e.target.value;
        }
      };
    }

    // Sign out button in header and on all dashboards
    const headerSignout = document.getElementById('btn-header-signout');
    if (headerSignout) {
      headerSignout.onclick = () => this.handleSignOut();
    }

    document.querySelectorAll('.btn-signout-action').forEach(btn => {
      btn.onclick = () => this.handleSignOut();
    });

    // Role switcher dropdown in header
    const roleSelect = document.getElementById('header-role-switcher');
    if (roleSelect) {
      roleSelect.onchange = (e) => {
        this.switchRoleView(e.target.value);
      };
    }

    // Employee picker in header
    const empSelect = document.getElementById('header-emp-select');
    if (empSelect) {
      empSelect.onchange = (e) => {
        this.switchRoleView('employee', e.target.value);
      };
    }

    // Notification button
    const notifBtn = document.getElementById('btn-toggle-notifs');
    if (notifBtn) {
      notifBtn.onclick = () => this.toggleNotifDrawer();
    }

    const notifClose = document.getElementById('btn-close-notifs');
    if (notifClose) {
      notifClose.onclick = () => this.toggleNotifDrawer(false);
    }

    const notifMarkRead = document.getElementById('btn-mark-all-read');
    if (notifMarkRead) {
      notifMarkRead.onclick = () => this.markAllNotificationsRead();
    }

    // Close modal triggers
    document.querySelectorAll('.modal-close, [data-modal-close]').forEach(btn => {
      btn.onclick = (e) => {
        const modal = e.target.closest('.modal-overlay');
        if (modal) modal.classList.remove('active');
      };
    });

    // Close on overlay background click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
      overlay.onclick = (e) => {
        if (e.target === overlay) overlay.classList.remove('active');
      };
    });

    // Bind Manager and HR action events early so buttons work immediately
    if (typeof Manager !== 'undefined' && Manager.bindEvents) {
      Manager.bindEvents();
    }
    if (typeof HR !== 'undefined' && HR.bindEvents) {
      HR.bindEvents();
    }
  }
};

// Boot app on DOM ready
document.addEventListener('DOMContentLoaded', () => {
  App.init();
});
