/**
 * ResAlloc - Resource Allocation & Workforce Management Platform
 * Faithful recreation of Figma Prototype interactions & data flow
 */

// ==========================================
// Mock Database State
// ==========================================
const AppState = {
  activeView: 'login', // 'login' | 'employee' | 'hr' | 'pm'
  currentUser: {
    id: 'emp-101',
    name: 'Alex Rivera',
    email: 'alex.rivera@resalloc.io',
    role: 'Senior Full-Stack Engineer',
    department: 'Engineering',
    allocatedHours: 36,
    maxHours: 40,
    avatarText: 'AR'
  },
  
  // HR Talent Directory Data
  employees: [
    {
      id: 'emp-1',
      name: 'Alex Rivera',
      email: 'alex.rivera@resalloc.io',
      role: 'Senior Full-Stack Engineer',
      department: 'Engineering',
      project: 'Cloud Native Migration',
      skills: ['React', 'Node.js', 'PostgreSQL', 'AWS'],
      allocationPercent: 90,
      hours: '36/40 hrs',
      status: 'allocated', // allocated | bench | overloaded | partial
      statusLabel: 'Allocated (90%)',
      avatarText: 'AR',
      joinDate: 'Mar 2023',
      utilizationHistory: 'Consistently 90-100% over last 4 quarters',
      alert: null
    },
    {
      id: 'emp-2',
      name: 'Elena Rostova',
      email: 'elena.rostova@resalloc.io',
      role: 'Lead UX/UI Designer',
      department: 'Design',
      project: 'FinTech Platform 2.0',
      skills: ['Figma', 'Design Systems', 'User Research'],
      allocationPercent: 100,
      hours: '40/40 hrs',
      status: 'allocated',
      statusLabel: 'Allocated (100%)',
      avatarText: 'ER',
      joinDate: 'Jan 2022',
      utilizationHistory: 'High demand across multi-product squads',
      alert: null
    },
    {
      id: 'emp-3',
      name: 'Devon Vance',
      email: 'devon.vance@resalloc.io',
      role: 'DevOps & SRE Engineer',
      department: 'Engineering',
      project: 'Infrastructure Modernization',
      skills: ['Kubernetes', 'Terraform', 'Docker', 'GCP'],
      allocationPercent: 125,
      hours: '50/40 hrs',
      status: 'overloaded',
      statusLabel: 'Over-allocated (125%)',
      avatarText: 'DV',
      joinDate: 'Jul 2021',
      utilizationHistory: 'Assigned to 3 overlapping critical pipelines',
      alert: 'Warning: Resource is over capacity (+10 hrs overtime). High burnout risk.'
    },
    {
      id: 'emp-4',
      name: 'Priya Sharma',
      email: 'priya.sharma@resalloc.io',
      role: 'Staff Product Manager',
      department: 'Product',
      project: 'AI Analytics Copilot',
      skills: ['Roadmapping', 'Agile/Scrum', 'Data Analytics'],
      allocationPercent: 50,
      hours: '20/40 hrs',
      status: 'partial',
      statusLabel: 'Partial (50%)',
      avatarText: 'PS',
      joinDate: 'Sep 2023',
      utilizationHistory: 'Concluding current discovery phase',
      alert: null
    },
    {
      id: 'emp-5',
      name: 'Marcus Brody',
      email: 'marcus.brody@resalloc.io',
      role: 'Senior Backend Engineer',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['Go', 'Microservices', 'gRPC', 'Kafka'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'MB',
      joinDate: 'Nov 2023',
      utilizationHistory: 'Finished FinTech core API migration 1 week ago',
      alert: 'Resource is currently unallocated. Available for immediate project onboarding.'
    },
    {
      id: 'emp-6',
      name: 'Sophie Martin',
      email: 'sophie.m@resalloc.io',
      role: 'QA Automation Lead',
      department: 'QA',
      project: 'Omnichannel Banking App',
      skills: ['Cypress', 'Playwright', 'Jest', 'CI/CD'],
      allocationPercent: 85,
      hours: '34/40 hrs',
      status: 'allocated',
      statusLabel: 'Allocated (85%)',
      avatarText: 'SM',
      joinDate: 'May 2022',
      utilizationHistory: 'Stable sprint commitment',
      alert: null
    },
    {
      id: 'emp-7',
      name: 'Tariq Al-Mansoor',
      email: 'tariq.m@resalloc.io',
      role: 'Mobile Architect',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['Flutter', 'React Native', 'iOS Swift'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'TA',
      joinDate: 'Aug 2023',
      utilizationHistory: 'Ready for cross-platform app rollout',
      alert: 'Resource on bench for 10 days. Ready for staffing.'
    }
  ],

  // Employee Tasks & Timesheet
  employeeTasks: [
    { id: 1, title: 'Finalize Architecture Spike for Auth Service', project: 'Cloud Migration', priority: 'high', due: 'Today, 5:00 PM', completed: false },
    { id: 2, title: 'Code Review PR #412: Terraform VPC peering', project: 'Cloud Migration', priority: 'medium', due: 'Tomorrow', completed: false },
    { id: 3, title: 'Sprint 24 Retrospective & Capacity Planning', project: 'FinTech Platform', priority: 'low', due: 'Sep 21, 2026', completed: true },
    { id: 4, title: 'Resolve Redis connection timeout in staging', project: 'Cloud Migration', priority: 'high', due: 'Sep 22, 2026', completed: false }
  ],

  timesheetHours: {
    mon: 8,
    tue: 8,
    wed: 8,
    thu: 8,
    fri: 4
  },

  // PM Projects Data
  pmProjects: {
    'proj-1': {
      name: 'Cloud Native Migration',
      code: 'CNM-2026',
      health: 'On Track',
      teamSize: 8,
      allocatedHours: 290,
      budgetHours: 320,
      openGaps: 2,
      teamMembers: [
        { name: 'Alex Rivera', role: 'Frontend Lead', hours: '36 hrs/wk', percent: 90, status: 'Active' },
        { name: 'Devon Vance', role: 'DevOps Lead', hours: '40 hrs/wk', percent: 100, status: 'Active' },
        { name: 'Sophie Martin', role: 'QA Automation', hours: '34 hrs/wk', percent: 85, status: 'Active' },
        { name: 'Kavita Rao', role: 'Backend Dev', hours: '40 hrs/wk', percent: 100, status: 'Active' }
      ]
    },
    'proj-2': {
      name: 'FinTech Platform 2.0',
      code: 'FTP-902',
      health: 'Needs Resources',
      teamSize: 6,
      allocatedHours: 210,
      budgetHours: 280,
      openGaps: 3,
      teamMembers: [
        { name: 'Elena Rostova', role: 'Lead UX/UI Designer', hours: '40 hrs/wk', percent: 100, status: 'Active' },
        { name: 'Priya Sharma', role: 'Product Manager', hours: '20 hrs/wk', percent: 50, status: 'Active' },
        { name: 'Jordan Hayes', role: 'Full Stack Dev', hours: '40 hrs/wk', percent: 100, status: 'Active' }
      ]
    }
  },

  // Resource Requests Pipeline
  resourceRequests: [
    {
      id: 'req-101',
      role: 'Senior Go Engineer',
      project: 'Cloud Native Migration',
      experience: '5+ Years',
      priority: 'high',
      status: 'Pending HR Review',
      date: 'Requested 2 days ago'
    },
    {
      id: 'req-102',
      role: 'DevOps Platform Specialist',
      project: 'FinTech Platform 2.0',
      experience: '3+ Years',
      priority: 'medium',
      status: 'Candidate Matching',
      date: 'Requested yesterday'
    },
    {
      id: 'req-103',
      role: 'Mobile UI/UX Designer',
      project: 'Omnichannel Banking',
      experience: '4+ Years',
      priority: 'low',
      status: 'Approved & Assigned',
      date: 'Completed Sep 15'
    }
  ]
};

// ==========================================
// Initialization & Routing
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  initRouting();
  initLoginForm();
  initHRDirectory();
  initEmployeeDashboard();
  initPMDashboard();
  initModals();
});

function initRouting() {
  // Handle URL hash routing
  const handleHashChange = () => {
    const hash = window.location.hash.replace('#', '') || 'login';
    switchView(hash);
  };

  window.addEventListener('hashchange', handleHashChange);
  
  // Initial check
  const initialHash = window.location.hash.replace('#', '') || 'login';
  switchView(initialHash);

  // Demo bar switcher buttons
  const demoButtons = document.querySelectorAll('.demo-tab-btn');
  demoButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const target = e.currentTarget.dataset.view;
      window.location.hash = target;
    });
  });

  // Mobile menu sidebar toggle
  const mobileToggles = document.querySelectorAll('.mobile-menu-toggle');
  mobileToggles.forEach(toggle => {
    toggle.addEventListener('click', () => {
      const activeSidebar = document.querySelector('.page-view.active .dashboard-sidebar');
      if (activeSidebar) {
        activeSidebar.classList.toggle('mobile-open');
      }
    });
  });
}

function switchView(viewName) {
  const validViews = ['login', 'employee', 'hr', 'pm'];
  if (!validViews.includes(viewName)) {
    viewName = 'login';
  }

  AppState.activeView = viewName;

  // Toggle active class on pages
  const pages = document.querySelectorAll('.page-view');
  pages.forEach(p => p.classList.remove('active'));

  const activePage = document.getElementById(`view-${viewName}`);
  if (activePage) {
    activePage.classList.add('active');
  }

  // Update top switcher tabs
  const demoButtons = document.querySelectorAll('.demo-tab-btn');
  demoButtons.forEach(btn => {
    if (btn.dataset.view === viewName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Close any open drawers or modals
  closeEmployeeDrawer();
  closeModal('request-resource-modal');

  // Re-render views if needed
  if (viewName === 'hr') {
    renderHRTable();
  } else if (viewName === 'pm') {
    renderPMView();
  } else if (viewName === 'employee') {
    renderEmployeeTimesheet();
  }
}

// ==========================================
// Toast Notification Utility
// ==========================================
function showToast(message, type = 'info') {
  let toast = document.querySelector('.toast-msg');
  if (!toast) {
    toast = document.createElement('div');
    toast.className = 'toast-msg';
    document.body.appendChild(toast);
  }

  let icon = '✓';
  if (type === 'warning') icon = '⚠️';
  if (type === 'error') icon = '✕';

  toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
  toast.classList.add('show');

  setTimeout(() => {
    toast.classList.remove('show');
  }, 3500);
}

// ==========================================
// 1. LOGIN SCREEN LOGIC
// ==========================================
function initLoginForm() {
  const roleButtons = document.querySelectorAll('.role-preset-buttons .role-btn');
  const emailInput = document.getElementById('login-email');
  const passwordInput = document.getElementById('login-password');
  const loginForm = document.getElementById('auth-form');
  const togglePassBtn = document.getElementById('toggle-password-btn');

  // Role quick select presets
  const roleCredentials = {
    employee: {
      email: 'alex.rivera@resalloc.io',
      role: 'Employee'
    },
    hr: {
      email: 'claire.lin@resalloc.io',
      role: 'HR Administrator'
    },
    pm: {
      email: 'marcus.chen@resalloc.io',
      role: 'Project Manager'
    }
  };

  roleButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      roleButtons.forEach(b => b.classList.remove('active'));
      e.currentTarget.classList.add('active');
      const role = e.currentTarget.dataset.role;
      if (roleCredentials[role]) {
        emailInput.value = roleCredentials[role].email;
        passwordInput.value = '••••••••••••';
      }
    });
  });

  // Password visibility reveal toggle
  if (togglePassBtn) {
    togglePassBtn.addEventListener('click', () => {
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
      } else {
        passwordInput.type = 'password';
      }
    });
  }

  // Handle Form Submission
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const activeRoleBtn = document.querySelector('.role-preset-buttons .role-btn.active');
      const selectedRole = activeRoleBtn ? activeRoleBtn.dataset.role : 'employee';

      showToast(`Signed in successfully as ${selectedRole.toUpperCase()}`);

      // Route to destination
      setTimeout(() => {
        window.location.hash = selectedRole;
      }, 300);
    });
  }

  // Social SSO buttons
  const ssoButtons = document.querySelectorAll('.btn-sso');
  ssoButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      showToast('Single Sign-On provider authenticated. Redirecting...');
      setTimeout(() => {
        window.location.hash = 'employee';
      }, 500);
    });
  });
}

// ==========================================
// 2. EMPLOYEE DASHBOARD LOGIC
// ==========================================
function initEmployeeDashboard() {
  // Task checkboxes
  const taskChecks = document.querySelectorAll('.task-check');
  taskChecks.forEach(check => {
    check.addEventListener('change', (e) => {
      const taskId = parseInt(e.target.dataset.taskId);
      const task = AppState.employeeTasks.find(t => t.id === taskId);
      if (task) {
        task.completed = e.target.checked;
        const textSpan = e.target.closest('.checklist-item').querySelector('.task-title-text');
        if (task.completed) {
          textSpan.classList.add('completed');
          showToast('Task marked as completed!');
        } else {
          textSpan.classList.remove('completed');
        }
        updatePendingTaskCount();
      }
    });
  });

  // Timesheet hour inputs
  const hourInputs = document.querySelectorAll('.timesheet-input');
  hourInputs.forEach(input => {
    input.addEventListener('change', (e) => {
      const day = e.target.dataset.day;
      const val = parseFloat(e.target.value) || 0;
      AppState.timesheetHours[day] = val;
      renderEmployeeTimesheet();
      showToast('Timesheet hours updated!');
    });
  });
}

function renderEmployeeTimesheet() {
  const total = Object.values(AppState.timesheetHours).reduce((a, b) => a + b, 0);
  const totalEl = document.getElementById('emp-total-hours-display');
  const kpiEl = document.getElementById('emp-kpi-allocated');
  const kpiFill = document.getElementById('emp-kpi-fill');

  if (totalEl) totalEl.textContent = `${total} hrs`;
  if (kpiEl) kpiEl.textContent = `${total} / 40 hrs`;

  const percent = Math.min(100, Math.round((total / 40) * 100));
  if (kpiFill) {
    kpiFill.style.width = `${percent}%`;
    if (percent > 100) {
      kpiFill.style.background = 'var(--status-danger-bar)';
    } else {
      kpiFill.style.background = 'var(--primary)';
    }
  }
}

function updatePendingTaskCount() {
  const pending = AppState.employeeTasks.filter(t => !t.completed).length;
  const el = document.getElementById('emp-pending-tasks-kpi');
  if (el) el.textContent = `${pending} Tasks`;
}

// ==========================================
// 3. HR DASHBOARD & TALENT DIRECTORY LOGIC
// ==========================================
function initHRDirectory() {
  const searchInput = document.getElementById('hr-search-input');
  const deptFilter = document.getElementById('hr-dept-filter');
  const statusFilter = document.getElementById('hr-status-filter');
  const drawerCloseBtn = document.getElementById('drawer-close-btn');
  const drawerBackdrop = document.getElementById('drawer-backdrop');

  if (searchInput) {
    searchInput.addEventListener('input', () => renderHRTable());
  }

  if (deptFilter) {
    deptFilter.addEventListener('change', () => renderHRTable());
  }

  if (statusFilter) {
    statusFilter.addEventListener('change', () => renderHRTable());
  }

  if (drawerCloseBtn) {
    drawerCloseBtn.addEventListener('click', closeEmployeeDrawer);
  }

  if (drawerBackdrop) {
    drawerBackdrop.addEventListener('click', closeEmployeeDrawer);
  }

  renderHRTable();
}

function renderHRTable() {
  const tableBody = document.getElementById('hr-employee-table-body');
  if (!tableBody) return;

  const searchVal = (document.getElementById('hr-search-input')?.value || '').toLowerCase().trim();
  const deptVal = document.getElementById('hr-dept-filter')?.value || 'all';
  const statusVal = document.getElementById('hr-status-filter')?.value || 'all';

  const filtered = AppState.employees.filter(emp => {
    const matchesSearch = 
      emp.name.toLowerCase().includes(searchVal) ||
      emp.role.toLowerCase().includes(searchVal) ||
      emp.email.toLowerCase().includes(searchVal) ||
      emp.skills.some(s => s.toLowerCase().includes(searchVal));

    const matchesDept = deptVal === 'all' || emp.department.toLowerCase() === deptVal.toLowerCase();
    const matchesStatus = statusVal === 'all' || emp.status === statusVal;

    return matchesSearch && matchesDept && matchesStatus;
  });

  tableBody.innerHTML = '';

  if (filtered.length === 0) {
    tableBody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align:center; padding: 40px; color: var(--text-muted);">
          No employees matched the search filters.
        </td>
      </tr>
    `;
    return;
  }

  filtered.forEach(emp => {
    const tr = document.createElement('tr');
    tr.style.cursor = 'pointer';

    // Status Pill Class
    let statusClass = 'status-allocated';
    if (emp.status === 'bench') statusClass = 'status-bench';
    if (emp.status === 'overloaded') statusClass = 'status-overloaded';
    if (emp.status === 'partial') statusClass = 'status-partial';

    // Allocation Fill Color
    let barColor = 'var(--primary)';
    if (emp.allocationPercent > 100) barColor = 'var(--status-danger-bar)';
    else if (emp.allocationPercent === 0) barColor = 'var(--status-warning-bar)';
    else if (emp.allocationPercent < 80) barColor = 'var(--status-info-bar)';

    // Skill Tags HTML
    const skillHtml = emp.skills.map(s => `<span class="skill-tag">${s}</span>`).join('');

    tr.innerHTML = `
      <td>
        <div class="user-cell">
          <div class="table-avatar">${emp.avatarText}</div>
          <div class="user-name-box">
            <span class="user-full-name">${emp.name}</span>
            <span class="user-email-text">${emp.email}</span>
          </div>
        </div>
      </td>
      <td>
        <div style="font-weight: 500;">${emp.role}</div>
        <div style="font-size: 11px; color: var(--text-muted);">${emp.department}</div>
      </td>
      <td>
        <span style="font-weight: 500; color: ${emp.project.includes('Bench') ? '#d97706' : 'var(--text-main)'};">
          ${emp.project}
        </span>
      </td>
      <td>
        <div class="skill-tags-row">
          ${skillHtml}
        </div>
      </td>
      <td>
        <div class="allocation-cell">
          <div class="alloc-meta-row">
            <span>${emp.hours}</span>
            <span style="color: ${barColor}">${emp.allocationPercent}%</span>
          </div>
          <div class="alloc-progress-track">
            <div class="alloc-progress-fill" style="width: ${Math.min(100, emp.allocationPercent)}%; background: ${barColor}"></div>
          </div>
        </div>
      </td>
      <td>
        <span class="status-pill ${statusClass}">
          <span class="dot"></span>
          ${emp.statusLabel}
        </span>
      </td>
      <td>
        <button class="btn-table-action primary" data-id="${emp.id}">View Details</button>
      </td>
    `;

    // Row click opens details
    tr.addEventListener('click', (e) => {
      openEmployeeDrawer(emp.id);
    });

    tableBody.appendChild(tr);
  });
}

function openEmployeeDrawer(empId) {
  const emp = AppState.employees.find(e => e.id === empId);
  if (!emp) return;

  const drawer = document.getElementById('employee-slide-drawer');
  const backdrop = document.getElementById('drawer-backdrop');

  // Populate drawer
  document.getElementById('drawer-avatar').textContent = emp.avatarText;
  document.getElementById('drawer-name').textContent = emp.name;
  document.getElementById('drawer-role').textContent = emp.role;
  document.getElementById('drawer-dept').textContent = emp.department;
  document.getElementById('drawer-email').textContent = emp.email;
  document.getElementById('drawer-joined').textContent = emp.joinDate;
  document.getElementById('drawer-project').textContent = emp.project;
  document.getElementById('drawer-alloc-val').textContent = `${emp.hours} (${emp.allocationPercent}%)`;

  // Skills
  const skillsContainer = document.getElementById('drawer-skills-list');
  if (skillsContainer) {
    skillsContainer.innerHTML = emp.skills.map(s => `<span class="skill-tag" style="padding: 4px 10px; font-size: 12px;">${s}</span>`).join('');
  }

  // Alert Box in Drawer
  const alertContainer = document.getElementById('drawer-alert-wrapper');
  if (alertContainer) {
    if (emp.alert) {
      const isRed = emp.status === 'overloaded';
      alertContainer.innerHTML = `
        <div class="drawer-alert-card ${isRed ? 'alert-red' : 'alert-yellow'}">
          <strong>${isRed ? 'Over-allocation Alert' : 'Resource Notice'}</strong>
          <span>${emp.alert}</span>
        </div>
      `;
      alertContainer.style.display = 'block';
    } else {
      alertContainer.style.display = 'none';
    }
  }

  drawer.classList.add('open');
  backdrop.classList.add('open');
}

function closeEmployeeDrawer() {
  const drawer = document.getElementById('employee-slide-drawer');
  const backdrop = document.getElementById('drawer-backdrop');
  if (drawer) drawer.classList.remove('open');
  if (backdrop) backdrop.classList.remove('open');
}

// ==========================================
// 4. PROJECT MANAGER DASHBOARD LOGIC
// ==========================================
function initPMDashboard() {
  const projectSelect = document.getElementById('pm-project-select');
  if (projectSelect) {
    projectSelect.addEventListener('change', () => {
      renderPMView();
    });
  }

  const btnRequestModal = document.getElementById('btn-open-request-modal');
  if (btnRequestModal) {
    btnRequestModal.addEventListener('click', () => {
      openModal('request-resource-modal');
    });
  }

  renderPMView();
}

function renderPMView() {
  const select = document.getElementById('pm-project-select');
  const projKey = select ? select.value : 'proj-1';
  const project = AppState.pmProjects[projKey] || AppState.pmProjects['proj-1'];

  // Update Metrics
  const teamSizeEl = document.getElementById('pm-team-size-kpi');
  const budgetHoursEl = document.getElementById('pm-budget-hours-kpi');
  const gapsEl = document.getElementById('pm-open-gaps-kpi');
  const healthEl = document.getElementById('pm-health-indicator');

  if (teamSizeEl) teamSizeEl.textContent = `${project.teamMembers.length} Members`;
  if (budgetHoursEl) budgetHoursEl.textContent = `${project.allocatedHours} / ${project.budgetHours} hrs`;
  if (gapsEl) gapsEl.textContent = `${project.openGaps} Open Roles`;
  if (healthEl) {
    healthEl.textContent = `🟢 ${project.health}`;
  }

  // Render PM Team Table
  const tableBody = document.getElementById('pm-team-table-body');
  if (tableBody) {
    tableBody.innerHTML = '';
    project.teamMembers.forEach(member => {
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td>
          <div class="user-cell">
            <div class="table-avatar" style="background: #e0e7ff; color: var(--primary);">${member.name.split(' ').map(n=>n[0]).join('')}</div>
            <div class="user-name-box">
              <span class="user-full-name">${member.name}</span>
              <span class="user-email-text">${member.role}</span>
            </div>
          </div>
        </td>
        <td><strong>${member.hours}</strong></td>
        <td>
          <div class="allocation-cell">
            <div class="alloc-meta-row">
              <span>Load</span>
              <span>${member.percent}%</span>
            </div>
            <div class="alloc-progress-track">
              <div class="alloc-progress-fill" style="width: ${member.percent}%; background: var(--primary);"></div>
            </div>
          </div>
        </td>
        <td>
          <span class="status-pill status-allocated">
            <span class="dot"></span>
            ${member.status}
          </span>
        </td>
        <td>
          <div style="display: flex; gap: 8px;">
            <button class="btn-table-action adjust-hrs-btn" data-name="${member.name}">Adjust Hours</button>
            <button class="btn-table-action" style="color: var(--status-danger-text);" data-name="${member.name}">Release</button>
          </div>
        </td>
      `;
      tableBody.appendChild(tr);
    });

    // Wire adjust/release buttons
    tableBody.querySelectorAll('.btn-table-action').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const action = e.target.textContent;
        const name = e.target.dataset.name;
        showToast(`${action} request submitted for ${name}`);
      });
    });
  }

  // Render Pipeline Requests
  renderPMPipeline();

  // Render Recommended Talent
  renderPMTalentRecommendations();
}

function renderPMPipeline() {
  const container = document.getElementById('pm-pipeline-container');
  if (!container) return;

  container.innerHTML = AppState.resourceRequests.map(req => {
    let tagColor = '#d97706';
    let tagBg = '#fffbeb';
    if (req.status.includes('Approved')) {
      tagColor = '#059669';
      tagBg = '#ecfdf5';
    } else if (req.status.includes('Review')) {
      tagColor = '#4f46e5';
      tagBg = '#eef2ff';
    }

    return `
      <div class="pipeline-card">
        <div class="pipeline-card-header">
          <span class="pipeline-role-title">${req.role}</span>
          <span style="font-size: 11px; font-weight: 700; color: ${tagColor}; background: ${tagBg}; padding: 3px 8px; border-radius: 4px;">
            ${req.status}
          </span>
        </div>
        <div class="pipeline-detail-row">
          <span>Project:</span>
          <strong>${req.project}</strong>
        </div>
        <div class="pipeline-detail-row">
          <span>Experience:</span>
          <span>${req.experience}</span>
        </div>
        <div class="pipeline-detail-row" style="font-size: 11px; color: var(--text-subtle);">
          <span>${req.date}</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderPMTalentRecommendations() {
  const container = document.getElementById('pm-recommendations-container');
  if (!container) return;

  const benchTalent = AppState.employees.filter(e => e.status === 'bench');

  container.innerHTML = benchTalent.map(talent => `
    <div class="rec-card">
      <div class="rec-user-row">
        <div class="rec-avatar">${talent.avatarText}</div>
        <div class="rec-info-col">
          <span class="rec-name">${talent.name}</span>
          <span class="rec-role">${talent.role}</span>
          <span class="rec-match-badge">96% Skill Match</span>
        </div>
      </div>
      <div class="skill-tags-row">
        ${talent.skills.map(s => `<span class="skill-tag">${s}</span>`).join('')}
      </div>
      <div style="font-size: 12px; color: var(--text-muted);">
        Status: <strong style="color: #059669;">Immediate Availability</strong>
      </div>
      <button class="btn-action-primary req-alloc-btn" data-name="${talent.name}" data-id="${talent.id}" style="width: 100%; justify-content: center;">
        Request Allocation
      </button>
    </div>
  `).join('');

  container.querySelectorAll('.req-alloc-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      const name = e.target.dataset.name;
      showToast(`Allocation request sent to HR for ${name}!`);
      e.target.textContent = 'Requested ✓';
      e.target.disabled = true;
      e.target.style.background = '#059669';
    });
  });
}

// ==========================================
// 5. MODAL SYSTEM
// ==========================================
function initModals() {
  const closeButtons = document.querySelectorAll('.btn-modal-close, .btn-modal-cancel');
  closeButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      closeModal('request-resource-modal');
    });
  });

  const requestForm = document.getElementById('resource-request-form');
  if (requestForm) {
    requestForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const role = document.getElementById('req-role-input').value;
      const experience = document.getElementById('req-exp-select').value;
      const hours = document.getElementById('req-hours-input').value;

      AppState.resourceRequests.unshift({
        id: `req-${Date.now()}`,
        role: role,
        project: 'Cloud Native Migration',
        experience: `${experience} Years`,
        priority: 'high',
        status: 'Pending HR Review',
        date: 'Just now'
      });

      closeModal('request-resource-modal');
      requestForm.reset();
      renderPMPipeline();
      showToast('New resource request submitted to HR team!');
    });
  }
}

function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.add('open');
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) modal.classList.remove('open');
}
