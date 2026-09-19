/**
 * Central State Management & Utilities
 */

const State = {
  currentRole: 'manager', // 'manager' | 'hr' | 'employee'
  currentEmployeeId: 'EMP-001', // Default employee for employee portal
  currentUser: null, // Logged in user info
  authToken: null,
  projects: [],
  employees: [],
  hrRequests: [],
  notifications: [],
  activeProjectForRec: null,
  activeRecData: null,

  isAuthenticated() {
    return Boolean(this.currentUser && this.currentUser.role);
  },

  setSession(user, token = null) {
    this.currentUser = user;
    this.currentRole = user.role;
    if (user.employee_id) {
      this.currentEmployeeId = user.employee_id;
    }
    this.authToken = token;

    sessionStorage.setItem('resalloc_session_user', JSON.stringify(user));
    if (token) sessionStorage.setItem('resalloc_session_token', token);
    localStorage.setItem('resalloc_role', user.role);
    if (user.employee_id) localStorage.setItem('resalloc_emp_id', user.employee_id);
  },

  clearSession() {
    this.currentUser = null;
    this.authToken = null;
    sessionStorage.removeItem('resalloc_session_user');
    sessionStorage.removeItem('resalloc_session_token');
    localStorage.removeItem('resalloc_role');
    localStorage.removeItem('resalloc_emp_id');
  },

  setRole(role, employeeId = null) {
    this.currentRole = role;
    if (employeeId) this.currentEmployeeId = employeeId;
    if (this.currentUser) {
      this.currentUser.role = role;
      if (employeeId) this.currentUser.employee_id = employeeId;
      sessionStorage.setItem('resalloc_session_user', JSON.stringify(this.currentUser));
    }
    localStorage.setItem('resalloc_role', role);
    if (employeeId) localStorage.setItem('resalloc_emp_id', employeeId);
  },

  loadSavedSession() {
    try {
      const rawUser = sessionStorage.getItem('resalloc_session_user');
      const token = sessionStorage.getItem('resalloc_session_token');
      if (rawUser) {
        const user = JSON.parse(rawUser);
        if (user && user.role) {
          this.currentUser = user;
          this.currentRole = user.role;
          if (user.employee_id) this.currentEmployeeId = user.employee_id;
          this.authToken = token;
          return true;
        }
      }
    } catch (e) {
      console.warn('Session parsing error:', e);
    }
    this.currentUser = null;
    this.authToken = null;
    return false;
  }
};

function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ')}</span>
    <div>${message}</div>
  `;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/**
 * Calculation Lock Manager (Mouse Unclickable Controller)
 * Blocks all mouse interactions across the entire document during backend/watcher data calculations.
 */
const CalculationLockManager = {
  isLocked: false,
  pollTimer: null,
  lockCount: 0,
  _initialized: false,

  init() {
    if (this._initialized) return;
    this._initialized = true;

    // Start background status polling
    this.startPolling();
  },

  lock(message = 'Database records modified. Recalculating allocations, SLA risks, and Qdrant vectors...') {
    this.lockCount++;
    this.isLocked = true;
    document.body.classList.add('data-calculating-active');

    const overlay = document.getElementById('calculation-lock-overlay');
    const msgEl = document.getElementById('calc-lock-message');
    if (msgEl && message) msgEl.textContent = message;
    if (overlay) overlay.classList.add('active');
  },

  unlock(triggerRefresh = false) {
    this.lockCount = Math.max(0, this.lockCount - 1);
    if (this.lockCount === 0) {
      this.isLocked = false;
      document.body.classList.remove('data-calculating-active');

      const overlay = document.getElementById('calculation-lock-overlay');
      if (overlay) overlay.classList.remove('active');

      if (triggerRefresh) {
        showToast('✓ Calculations finished. Workforce data & allocations synchronized.', 'success');
        this.refreshCurrentView();
      }
    }
  },

  forceUnlock(triggerRefresh = false) {
    this.lockCount = 0;
    this.isLocked = false;
    document.body.classList.remove('data-calculating-active');

    const overlay = document.getElementById('calculation-lock-overlay');
    if (overlay) overlay.classList.remove('active');

    if (triggerRefresh) {
      showToast('✓ Calculations finished. Workforce data & allocations synchronized.', 'success');
      this.refreshCurrentView();
    }
  },

  refreshCurrentView() {
    if (!State.isAuthenticated()) return;
    try {
      if (State.currentRole === 'manager' && window.Manager && typeof Manager.loadDashboard === 'function') {
        Manager.loadDashboard();
      } else if (State.currentRole === 'hr' && window.HR && typeof HR.loadData === 'function') {
        HR.loadData();
      } else if (State.currentRole === 'employee' && window.Employee && typeof Employee.loadDashboard === 'function') {
        Employee.loadDashboard();
      }
      if (window.App && typeof App.loadNotifications === 'function') {
        App.loadNotifications();
      }
    } catch (e) {
      console.warn('View refresh warning after calculation unlock:', e);
    }
  },

  startPolling() {
    if (this.pollTimer) clearInterval(this.pollTimer);
    this.pollTimer = setInterval(async () => {
      try {
        if (!window.API || typeof API.getCalculationStatus !== 'function') return;
        const data = await API.getCalculationStatus();
        if (data.is_calculating) {
          if (!this.isLocked) {
            this.lock(data.message || 'Database modified. Calculations in progress...');
          }
        } else {
          // If locked due to external watcher/backend calculation, unlock now
          if (this.isLocked && this.lockCount <= 1) {
            this.forceUnlock(true);
          }
        }
      } catch (err) {
        // Backend offline or starting up
      }
    }, 1000);
  }
};

window.CalculationLockManager = CalculationLockManager;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => CalculationLockManager.init());
} else {
  CalculationLockManager.init();
}
