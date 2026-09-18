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
      skills: ['Roadmapping', 'Agile/Scrum', 'Data Analytics', 'AI', 'Python'],
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
      skills: ['Go', 'Microservices', 'gRPC', 'Kafka', 'PostgreSQL', 'Redis'],
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
      skills: ['Flutter', 'React Native', 'iOS Swift', 'Android', 'GraphQL'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'TA',
      joinDate: 'Aug 2023',
      utilizationHistory: 'Ready for cross-platform app rollout',
      alert: 'Resource on bench for 10 days. Ready for staffing.'
    },
    {
      id: 'emp-8',
      name: 'Liam Chen',
      email: 'liam.chen@resalloc.io',
      role: 'Senior Frontend Developer',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['React', 'TypeScript', 'Next.js', 'Tailwind', 'GraphQL'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'LC',
      joinDate: 'Feb 2023',
      utilizationHistory: 'Completed Design System migration',
      alert: 'Resource ready for assignment.'
    },
    {
      id: 'emp-9',
      name: 'Sofia Rodriguez',
      email: 'sofia.r@resalloc.io',
      role: 'UI/UX Designer',
      department: 'Design',
      project: 'None (Bench)',
      skills: ['Figma', 'Design Systems', 'User Research', 'UI/UX'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'SR',
      joinDate: 'Apr 2023',
      utilizationHistory: 'Recently wrapped customer discovery audit',
      alert: 'Resource available immediately.'
    },
    {
      id: 'emp-10',
      name: 'Maya Lin',
      email: 'maya.lin@resalloc.io',
      role: 'AI / ML Specialist',
      department: 'Data & AI',
      project: 'None (Bench)',
      skills: ['Python', 'PyTorch', 'TensorFlow', 'Machine Learning', 'NLP', 'Data Science'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'ML',
      joinDate: 'Jun 2023',
      utilizationHistory: 'Model evaluation spike completed',
      alert: 'Available for AI/ML and Data Science initiatives.'
    },
    {
      id: 'emp-11',
      name: 'David Kim',
      email: 'david.kim@resalloc.io',
      role: 'Cloud & DevOps Architect',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['Kubernetes', 'Terraform', 'AWS', 'Docker', 'CI/CD'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'DK',
      joinDate: 'Nov 2022',
      utilizationHistory: 'Finalized Multi-Region EKS clusters',
      alert: 'Ready for Cloud/DevOps infrastructure setup.'
    },
    {
      id: 'emp-12',
      name: 'Sarah Jenkins',
      email: 'sarah.j@resalloc.io',
      role: 'Lead Full-Stack Engineer',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['React', 'Node.js', 'TypeScript', 'PostgreSQL', 'Full Stack', 'Backend'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'SJ',
      joinDate: 'Jan 2023',
      utilizationHistory: 'Delivered Payments API v3',
      alert: 'Bench available for full-stack delivery.'
    },
    {
      id: 'emp-13',
      name: 'Arthur Pendelton',
      email: 'arthur.p@resalloc.io',
      role: 'QA Automation Specialist',
      department: 'QA',
      project: 'None (Bench)',
      skills: ['Cypress', 'Playwright', 'Jest', 'CI/CD', 'QA Automation', 'Testing'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'AP',
      joinDate: 'Mar 2023',
      utilizationHistory: 'Automated 300+ end-to-end integration tests',
      alert: 'Ready for QA Automation assignments.'
    },
    {
      id: 'emp-14',
      name: 'Zoe Sterling',
      email: 'zoe.s@resalloc.io',
      role: 'AI Research Engineer',
      department: 'Data & AI',
      project: 'None (Bench)',
      skills: ['Python', 'Machine Learning', 'PyTorch', 'AI', 'NLP', 'LangChain'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'ZS',
      joinDate: 'May 2023',
      utilizationHistory: 'RAG LLM optimization spike completed',
      alert: 'Available for AI & LLM integration.'
    },
    {
      id: 'emp-15',
      name: 'Omar Farooq',
      email: 'omar.f@resalloc.io',
      role: 'Frontend Developer',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['React', 'Vue', 'JavaScript', 'CSS', 'HTML', 'Frontend', 'TypeScript'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'OF',
      joinDate: 'Sep 2023',
      utilizationHistory: 'Design token rollout completed',
      alert: 'Available for UI front-end development.'
    },
    {
      id: 'emp-16',
      name: 'Nina Patel',
      email: 'nina.p@resalloc.io',
      role: 'Data Scientist & ML Engineer',
      department: 'Data & AI',
      project: 'None (Bench)',
      skills: ['Python', 'Data Science', 'Pandas', 'SQL', 'Machine Learning', 'PyTorch'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'NP',
      joinDate: 'Jul 2023',
      utilizationHistory: 'Churn prediction pipeline in production',
      alert: 'Available for data science and predictive analytics.'
    },
    {
      id: 'emp-17',
      name: 'Ethan Hunt',
      email: 'ethan.h@resalloc.io',
      role: 'Cybersecurity & SecOps Engineer',
      department: 'Security',
      project: 'None (Bench)',
      skills: ['Security', 'Cybersecurity', 'OAuth', 'Penetration Testing', 'SIEM'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'EH',
      joinDate: 'Oct 2022',
      utilizationHistory: 'SOC2 Type II compliance audit wrapped',
      alert: 'Available for security architecture review and hardening.'
    },
    {
      id: 'emp-18',
      name: 'Carlos Mendoza',
      email: 'carlos.m@resalloc.io',
      role: 'Database Administrator & Backend',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['PostgreSQL', 'MySQL', 'Database Administration', 'Redis', 'SQL', 'Backend', 'Go'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'CM',
      joinDate: 'Dec 2022',
      utilizationHistory: 'Postgres 16 cluster sharding completed',
      alert: 'Available for database design and backend scaling.'
    },
    {
      id: 'emp-19',
      name: 'Chloe Dupont',
      email: 'chloe.d@resalloc.io',
      role: 'Full-Stack Developer',
      department: 'Engineering',
      project: 'FinTech Platform 2.0',
      skills: ['React', 'TypeScript', 'Node.js', 'PostgreSQL', 'Frontend'],
      allocationPercent: 50,
      hours: '20/40 hrs',
      status: 'partial',
      statusLabel: 'Partial (50%)',
      avatarText: 'CD',
      joinDate: 'Jan 2024',
      utilizationHistory: 'Available 20h/wk for new projects',
      alert: null
    },
    {
      id: 'emp-20',
      name: 'Kenji Sato',
      email: 'kenji.s@resalloc.io',
      role: 'Mobile & iOS Developer',
      department: 'Engineering',
      project: 'Omnichannel Banking App',
      skills: ['iOS Swift', 'Flutter', 'Mobile', 'Kotlin'],
      allocationPercent: 50,
      hours: '20/40 hrs',
      status: 'partial',
      statusLabel: 'Partial (50%)',
      avatarText: 'KS',
      joinDate: 'Feb 2024',
      utilizationHistory: 'Available 20h/wk for mobile work',
      alert: null
    },
    {
      id: 'emp-21',
      name: 'Rachel Green',
      email: 'rachel.g@resalloc.io',
      role: 'UI/UX Product Designer',
      department: 'Design',
      project: 'Design Systems',
      skills: ['Figma', 'UI Design', 'UX Research', 'Design Systems'],
      allocationPercent: 50,
      hours: '20/40 hrs',
      status: 'partial',
      statusLabel: 'Partial (50%)',
      avatarText: 'RG',
      joinDate: 'Mar 2024',
      utilizationHistory: 'Available 20h/wk for UI/UX projects',
      alert: null
    },
    {
      id: 'emp-22',
      name: 'Lucas Vance',
      email: 'lucas.v@resalloc.io',
      role: 'DevOps & Cloud Engineer',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['Kubernetes', 'Docker', 'GCP', 'Terraform', 'CI/CD', 'Cloud', 'AWS'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'LV',
      joinDate: 'Jun 2023',
      utilizationHistory: 'Completed staging infra overhaul',
      alert: 'Available for DevOps pipelines.'
    },
    {
      id: 'emp-23',
      name: 'Hannah Abbott',
      email: 'hannah.a@resalloc.io',
      role: 'SRE & Cloud Architect',
      department: 'Engineering',
      project: 'Infrastructure Modernization',
      skills: ['AWS', 'Cloud', 'Kubernetes', 'CI/CD', 'DevOps', 'Docker'],
      allocationPercent: 50,
      hours: '20/40 hrs',
      status: 'partial',
      statusLabel: 'Partial (50%)',
      avatarText: 'HA',
      joinDate: 'Apr 2023',
      utilizationHistory: 'Available 20h/wk for cloud architecture',
      alert: null
    },
    {
      id: 'emp-24',
      name: 'Vikram Seth',
      email: 'vikram.s@resalloc.io',
      role: 'Cloud & Infrastructure Engineer',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['AWS', 'Docker', 'DevOps', 'CI/CD', 'Terraform', 'Kubernetes'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'VS',
      joinDate: 'Aug 2023',
      utilizationHistory: 'Completed multi-tenant VPC build',
      alert: 'Available immediately for cloud infrastructure.'
    },
    {
      id: 'emp-25',
      name: 'Samira Khan',
      email: 'samira.k@resalloc.io',
      role: 'Full-Stack Engineer',
      department: 'Engineering',
      project: 'Cloud Native Migration',
      skills: ['React', 'Node.js', 'Full Stack', 'TypeScript'],
      allocationPercent: 50,
      hours: '20/40 hrs',
      status: 'partial',
      statusLabel: 'Partial (50%)',
      avatarText: 'SK',
      joinDate: 'Nov 2023',
      utilizationHistory: 'Available 20h/wk for full-stack apps',
      alert: null
    },
    {
      id: 'emp-26',
      name: 'Dev Patel',
      email: 'dev.patel@resalloc.io',
      role: 'Full-Stack & Mobile Developer',
      department: 'Engineering',
      project: 'None (Bench)',
      skills: ['React Native', 'Flutter', 'Full Stack', 'Node.js', 'Mobile', 'gRPC'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'DP',
      joinDate: 'Oct 2023',
      utilizationHistory: 'Delivered mobile checkout SDK',
      alert: 'Available for mobile and full-stack development.'
    },
    {
      id: 'emp-27',
      name: 'Megan Fox',
      email: 'megan.f@resalloc.io',
      role: 'Security Analyst & InfoSec',
      department: 'Security',
      project: 'None (Bench)',
      skills: ['Security', 'Cybersecurity', 'SIEM', 'Compliance', 'OAuth'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'MF',
      joinDate: 'Jan 2023',
      utilizationHistory: 'Completed vulnerability assessments',
      alert: 'Available for cybersecurity and compliance.'
    },
    {
      id: 'emp-28',
      name: 'Leo Zhang',
      email: 'leo.z@resalloc.io',
      role: 'QA & Test Automation Engineer',
      department: 'QA',
      project: 'None (Bench)',
      skills: ['Playwright', 'Selenium', 'QA Automation', 'Testing', 'Kafka'],
      allocationPercent: 0,
      hours: '0/40 hrs',
      status: 'bench',
      statusLabel: 'Bench Available',
      avatarText: 'LZ',
      joinDate: 'Feb 2023',
      utilizationHistory: 'Built end-to-end regression suite',
      alert: 'Available for QA and test automation.'
    },
    {
      id: 'emp-29',
      name: 'Jessica Miller',
      email: 'jessica.m@resalloc.io',
      role: 'QA Automation & Testing Engineer',
      department: 'QA',
      project: 'Omnichannel Banking App',
      skills: ['Cypress', 'Jest', 'Testing', 'CI/CD', 'QA'],
      allocationPercent: 50,
      hours: '20/40 hrs',
      status: 'partial',
      statusLabel: 'Partial (50%)',
      avatarText: 'JM',
      joinDate: 'Mar 2023',
      utilizationHistory: 'Available 20h/wk for testing and QA automation',
      alert: null
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

  const btnNewProjectModal = document.getElementById('btn-open-new-project-modal');
  if (btnNewProjectModal) {
    btnNewProjectModal.addEventListener('click', () => {
      openModal('new-project-modal');
      refreshNewProjectModal();
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
      // Match employee by name and attach row click listener
      const matchedEmp = AppState.employees.find(e => e.name && e.name.toLowerCase() === member.name.toLowerCase());

      // Row click opens details
      tr.addEventListener('click', (e) => {
        if (e.target.closest('.btn-table-action')) return;
        if (matchedEmp) {
          openEmployeeDrawer(matchedEmp.id);
        }
      });

      tableBody.appendChild(tr);
    });

    // Wire adjust/release buttons
    tableBody.querySelectorAll('.btn-table-action').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
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
// 5. MODAL SYSTEM & ADD EMPLOYEE POP-UP
// ==========================================
function initModals() {
  // Generic close buttons
  const closeButtons = document.querySelectorAll('.btn-modal-close, .btn-modal-cancel');
  closeButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
      const parentModal = e.target.closest('.modal-overlay');
      if (parentModal) {
        closeModal(parentModal.id);
      }
    });
  });

  // Close modals on overlay backdrop click
  const modals = document.querySelectorAll('.modal-overlay');
  modals.forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        closeModal(modal.id);
      }
    });
  });

  // PM Resource Request Form
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

  // HR Add Employee Modal setup
  initAddEmployeeModal();

  // PM New Project Modal setup
  initNewProjectModal();
}

function initAddEmployeeModal() {
  const addEmpBtn = document.getElementById('btn-add-employee');
  const closeBtn = document.getElementById('btn-close-add-emp-modal');
  const cancelBtn = document.getElementById('btn-cancel-add-emp');
  const addEmpForm = document.getElementById('add-employee-form');

  // Resume Upload Elements
  const resumeDropzone = document.getElementById('resume-dropzone');
  const resumeFileInput = document.getElementById('emp-resume-file');
  const resumeEmptyView = document.getElementById('resume-empty-view');
  const resumePreviewView = document.getElementById('resume-preview-view');
  const resumeFileName = document.getElementById('resume-file-name');
  const resumeFileSize = document.getElementById('resume-file-size');
  const resumeErrorMsg = document.getElementById('resume-error-msg');
  const btnReplaceResume = document.getElementById('btn-replace-resume');
  const btnRemoveResume = document.getElementById('btn-remove-resume');

  // Employee Type Elements
  const typeBtnExperienced = document.getElementById('type-btn-experienced');
  const typeBtnFresher = document.getElementById('type-btn-fresher');
  const typeHiddenInput = document.getElementById('emp-type-value');
  const experiencedGroup = document.getElementById('experienced-fields-group');
  const fresherGroup = document.getElementById('fresher-fields-group');

  let uploadedResume = null;

  // Open modal handler
  if (addEmpBtn) {
    addEmpBtn.addEventListener('click', () => {
      // Set today's date as default joining date
      const today = new Date().toISOString().split('T')[0];
      const joinDateInput = document.getElementById('emp-joining-date');
      if (joinDateInput && !joinDateInput.value) {
        joinDateInput.value = today;
      }
      
      // Suggest next employee ID
      const empIdInput = document.getElementById('emp-id');
      if (empIdInput && !empIdInput.value) {
        const nextNum = AppState.employees.length + 101;
        empIdInput.value = `EMP-${nextNum}`;
      }

      openModal('add-employee-modal');
    });
  }

  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('add-employee-modal'));
  if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('add-employee-modal'));

  // 1. Resume Upload Handlers
  function handlePdfFile(file) {
    if (!file) return;

    const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
    if (!isPdf) {
      if (resumeErrorMsg) {
        resumeErrorMsg.style.display = 'flex';
        resumeErrorMsg.querySelector('span').textContent = 'Invalid format! Please upload a PDF file.';
      }
      uploadedResume = null;
      resumeFileInput.value = '';
      if (resumeEmptyView) resumeEmptyView.style.display = 'flex';
      if (resumePreviewView) resumePreviewView.style.display = 'none';
      return;
    }

    // Valid PDF
    uploadedResume = file;
    if (resumeErrorMsg) resumeErrorMsg.style.display = 'none';

    // Format file size
    const sizeKB = file.size / 1024;
    const sizeStr = sizeKB > 1024 
      ? `${(sizeKB / 1024).toFixed(1)} MB` 
      : `${Math.round(sizeKB)} KB`;

    if (resumeFileName) resumeFileName.textContent = file.name;
    if (resumeFileSize) resumeFileSize.textContent = sizeStr;

    if (resumeEmptyView) resumeEmptyView.style.display = 'none';
    if (resumePreviewView) resumePreviewView.style.display = 'flex';
  }

  if (resumeDropzone) {
    resumeDropzone.addEventListener('click', (e) => {
      if (e.target.closest('#btn-remove-resume') || e.target.closest('#btn-replace-resume')) return;
      if (!uploadedResume) {
        resumeFileInput.click();
      }
    });

    resumeDropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      resumeDropzone.classList.add('drag-over');
    });

    resumeDropzone.addEventListener('dragleave', () => {
      resumeDropzone.classList.remove('drag-over');
    });

    resumeDropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      resumeDropzone.classList.remove('drag-over');
      if (e.dataTransfer.files && e.dataTransfer.files[0]) {
        handlePdfFile(e.dataTransfer.files[0]);
      }
    });
  }

  if (resumeFileInput) {
    resumeFileInput.addEventListener('change', (e) => {
      if (e.target.files && e.target.files[0]) {
        handlePdfFile(e.target.files[0]);
      }
    });
  }

  if (btnReplaceResume) {
    btnReplaceResume.addEventListener('click', (e) => {
      e.stopPropagation();
      resumeFileInput.click();
    });
  }

  if (btnRemoveResume) {
    btnRemoveResume.addEventListener('click', (e) => {
      e.stopPropagation();
      uploadedResume = null;
      resumeFileInput.value = '';
      if (resumeEmptyView) resumeEmptyView.style.display = 'flex';
      if (resumePreviewView) resumePreviewView.style.display = 'none';
      if (resumeErrorMsg) resumeErrorMsg.style.display = 'none';
    });
  }

  // 2. Employee Type Switcher
  function setEmployeeType(type) {
    typeHiddenInput.value = type;
    if (type === 'experienced') {
      typeBtnExperienced.classList.add('active');
      typeBtnFresher.classList.remove('active');
      experiencedGroup.style.display = 'block';
      fresherGroup.style.display = 'none';
    } else {
      typeBtnFresher.classList.add('active');
      typeBtnExperienced.classList.remove('active');
      fresherGroup.style.display = 'block';
      experiencedGroup.style.display = 'none';
    }
  }

  if (typeBtnExperienced) {
    typeBtnExperienced.addEventListener('click', () => setEmployeeType('experienced'));
  }
  if (typeBtnFresher) {
    typeBtnFresher.addEventListener('click', () => setEmployeeType('fresher'));
  }

  // 3. Form Validation & Submission
  if (addEmpForm) {
    addEmpForm.addEventListener('submit', (e) => {
      e.preventDefault();
      
      // Reset error states
      const allErrors = addEmpForm.querySelectorAll('.form-error-text');
      allErrors.forEach(err => err.style.display = 'none');

      let isValid = true;
      let firstInvalidEl = null;

      // Check Resume
      if (!uploadedResume) {
        if (resumeErrorMsg) {
          resumeErrorMsg.style.display = 'flex';
          const spanEl = resumeErrorMsg.querySelector('span');
          if (spanEl) spanEl.textContent = 'Please upload a valid employee resume in PDF format.';
        }
        isValid = false;
        firstInvalidEl = firstInvalidEl || resumeDropzone;
      }

      // Check Full Name
      const nameInput = document.getElementById('emp-fullname');
      const nameVal = nameInput?.value.trim();
      if (!nameVal || nameVal.length < 2) {
        const err = document.getElementById('error-fullname');
        if (err) err.style.display = 'flex';
        isValid = false;
        firstInvalidEl = firstInvalidEl || nameInput;
      }

      // Check Phone Number
      const phoneInput = document.getElementById('emp-phone');
      const phoneVal = phoneInput?.value.trim();
      const phoneRegex = /^[0-9+\-()\s]{7,20}$/;
      if (!phoneVal || !phoneRegex.test(phoneVal)) {
        const err = document.getElementById('error-phone');
        if (err) err.style.display = 'flex';
        isValid = false;
        firstInvalidEl = firstInvalidEl || phoneInput;
      }

      // Check Email
      const emailInput = document.getElementById('emp-email');
      const emailVal = emailInput?.value.trim();
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailVal || !emailRegex.test(emailVal)) {
        const err = document.getElementById('error-email');
        if (err) err.style.display = 'flex';
        isValid = false;
        firstInvalidEl = firstInvalidEl || emailInput;
      }

      // Check Employee ID
      const empIdInput = document.getElementById('emp-id');
      const empIdVal = empIdInput?.value.trim();
      if (!empIdVal) {
        const err = document.getElementById('error-id');
        if (err) err.style.display = 'flex';
        isValid = false;
        firstInvalidEl = firstInvalidEl || empIdInput;
      }

      // Check Role
      const roleInput = document.getElementById('emp-role');
      const roleVal = roleInput?.value.trim();
      if (!roleVal) {
        const err = document.getElementById('error-role');
        if (err) err.style.display = 'flex';
        isValid = false;
        firstInvalidEl = firstInvalidEl || roleInput;
      }

      // Check Department
      const deptInput = document.getElementById('emp-department');
      const deptVal = deptInput?.value;
      if (!deptVal) {
        const err = document.getElementById('error-department');
        if (err) err.style.display = 'flex';
        isValid = false;
        firstInvalidEl = firstInvalidEl || deptInput;
      }

      // Check Joining Date
      const joinDateInput = document.getElementById('emp-joining-date');
      const joinDateVal = joinDateInput?.value;
      if (!joinDateVal) {
        const err = document.getElementById('error-joining-date');
        if (err) err.style.display = 'flex';
        isValid = false;
        firstInvalidEl = firstInvalidEl || joinDateInput;
      }

      // Check Type-specific fields
      const empType = typeHiddenInput.value;
      let expDetails = {};

      if (empType === 'experienced') {
        const yearsInput = document.getElementById('emp-years-exp');
        const yearsVal = parseFloat(yearsInput?.value);
        if (isNaN(yearsVal) || yearsVal <= 0) {
          const err = document.getElementById('error-years-exp');
          if (err) err.style.display = 'flex';
          isValid = false;
          firstInvalidEl = firstInvalidEl || yearsInput;
        }

        const prevCoInput = document.getElementById('emp-prev-company');
        const prevCoVal = prevCoInput?.value.trim();
        if (!prevCoVal) {
          const err = document.getElementById('error-prev-company');
          if (err) err.style.display = 'flex';
          isValid = false;
          firstInvalidEl = firstInvalidEl || prevCoInput;
        }

        const ratingVal = document.getElementById('emp-rating')?.value || '4.5';

        expDetails = {
          type: 'experienced',
          years: yearsVal,
          previousCompany: prevCoVal,
          rating: ratingVal
        };
      } else {
        const salaryInput = document.getElementById('emp-expected-salary');
        const salaryVal = salaryInput?.value.trim();
        if (!salaryVal) {
          const err = document.getElementById('error-expected-salary');
          if (err) err.style.display = 'flex';
          isValid = false;
          firstInvalidEl = firstInvalidEl || salaryInput;
        }

        expDetails = {
          type: 'fresher',
          expectedSalary: salaryVal
        };
      }

      if (!isValid) {
        if (firstInvalidEl) {
          firstInvalidEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
          if (firstInvalidEl.focus) firstInvalidEl.focus();
        }
        showToast('Please complete all required fields correctly.', 'warning');
        return;
      }

      // Generate Avatar Initials
      const nameParts = nameVal.split(' ').filter(Boolean);
      const initials = nameParts.length >= 2 
        ? (nameParts[0][0] + nameParts[1][0]).toUpperCase()
        : nameVal.substring(0, 2).toUpperCase();

      // Format Joining Date (e.g. "Sep 2026")
      const dateObj = new Date(joinDateVal);
      const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
      const formattedJoin = isNaN(dateObj.getTime()) ? 'Recent' : `${monthNames[dateObj.getMonth()]} ${dateObj.getFullYear()}`;

      // Create New Employee Record
      const newEmployee = {
        id: empIdVal,
        name: nameVal,
        email: emailVal,
        phone: phoneVal,
        role: roleVal,
        department: deptVal,
        project: 'Available on Bench',
        skills: [roleVal.split(' ')[0], deptVal, 'PDF Resume Attached'],
        allocationPercent: 0,
        hours: '0/40 hrs',
        status: 'bench',
        statusLabel: 'Available on Bench (0%)',
        avatarText: initials,
        joinDate: formattedJoin,
        utilizationHistory: empType === 'experienced' 
          ? `Prior: ${expDetails.previousCompany} (${expDetails.years} yrs exp, Rating: ${expDetails.rating})` 
          : `Fresher / New Joiner (Target: ${expDetails.expectedSalary})`,
        alert: null,
        resumeName: uploadedResume ? uploadedResume.name : 'resume.pdf'
      };

      // Add to Talent Directory at the top
      AppState.employees.unshift(newEmployee);

      // Re-render HR Directory
      renderHRTable();

      // Reset form & states
      addEmpForm.reset();
      uploadedResume = null;
      resumeFileInput.value = '';
      if (resumeEmptyView) resumeEmptyView.style.display = 'flex';
      if (resumePreviewView) resumePreviewView.style.display = 'none';
      setEmployeeType('experienced');

      // Close modal
      closeModal('add-employee-modal');

      // Success Notification
      showToast(`🎉 Employee ${nameVal} onboarded successfully with verified PDF resume!`);
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

// ==========================================
// 6. PM NEW PROJECT & RESOURCE ESTIMATION
// ==========================================
const SUGGESTED_PROJECT_SKILLS = [
  'HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Angular', 'Vue.js', 'Next.js', 
  'Bootstrap', 'Tailwind CSS', 'Flutter', 'React Native', 'C', 'C++', 'Java', 'Python', 
  'C#', 'Go', 'PHP', 'Kotlin', 'Swift', 'Rust', 'Node.js', 'Express.js', 'Spring Boot', 
  'Django', 'Flask', '.NET', 'Laravel', 'MySQL', 'PostgreSQL', 'MongoDB', 'SQLite', 
  'Oracle', 'SQL Server', 'Firebase', 'Redis', 'Cassandra', 'Machine Learning', 
  'Deep Learning', 'Generative AI', 'LLM', 'NLP', 'Computer Vision', 'TensorFlow', 
  'PyTorch', 'Scikit-learn', 'OpenCV', 'Keras', 'Pandas', 'NumPy', 'Data Science', 
  'Data Analytics', 'Power BI', 'Tableau', 'Apache Spark', 'Hadoop', 'Apache Kafka', 
  'Databricks', 'Selenium', 'Playwright', 'Cypress', 'Jest', 'JUnit', 'PyTest', 
  'Git', 'GitHub', 'GitLab', 'Docker', 'Kubernetes', 'AWS', 'Terraform', 'CI/CD', 'gRPC', 'GraphQL',
  'Figma', 'VS Code', 'IntelliJ IDEA', 'Eclipse', 'Jenkins', 'Data Structures & Algorithms', 
  'Object-Oriented Programming', 'Operating Systems', 'Computer Networks', 'Database Management', 
  'Computer Architecture', 'Software Engineering', 'System Design', 'Cybersecurity', 
  'Network Security', 'Ethical Hacking', 'Penetration Testing', 'Web Security'
];

const PROJECT_DOMAINS = [
  { 
    id: 'frontend', 
    name: 'Frontend Development', 
    matchSkills: ['react', 'vue', 'angular', 'typescript', 'javascript', 'frontend', 'ui', 'css', 'html', 'next.js', 'tailwind'], 
    matchRoles: ['frontend', 'ui', 'full-stack'] 
  },
  { 
    id: 'backend', 
    name: 'Backend Development', 
    matchSkills: ['node.js', 'go', 'python', 'java', 'postgresql', 'backend', 'microservices', 'grpc', 'kafka', 'redis', 'sql'], 
    matchRoles: ['backend', 'full-stack'] 
  },
  { 
    id: 'fullstack', 
    name: 'Full Stack Development', 
    matchSkills: ['react', 'node.js', 'typescript', 'full stack', 'fullstack', 'full-stack'], 
    matchRoles: ['full-stack', 'full stack'] 
  },
  { 
    id: 'design', 
    name: 'UI/UX Design', 
    matchSkills: ['figma', 'design systems', 'user research', 'ui/ux', 'ux', 'ui design', 'prototyping'], 
    matchRoles: ['designer', 'ux', 'ui'] 
  },
  { 
    id: 'ai', 
    name: 'AI/ML', 
    matchSkills: ['python', 'pytorch', 'tensorflow', 'machine learning', 'ai', 'ml', 'nlp', 'llm', 'langchain'], 
    matchRoles: ['ai', 'ml', 'data'] 
  },
  { 
    id: 'datascience', 
    name: 'Data Science', 
    matchSkills: ['python', 'data analytics', 'data science', 'sql', 'pandas', 'r', 'bi'], 
    matchRoles: ['data', 'analytics', 'scientist'] 
  },
  { 
    id: 'mobile', 
    name: 'Mobile Development', 
    matchSkills: ['flutter', 'react native', 'ios swift', 'ios', 'android', 'swift', 'kotlin', 'mobile'], 
    matchRoles: ['mobile', 'ios', 'android'] 
  },
  { 
    id: 'cloud', 
    name: 'DevOps/Cloud', 
    matchSkills: ['kubernetes', 'docker', 'aws', 'gcp', 'terraform', 'ci/cd', 'devops', 'sre', 'cloud'], 
    matchRoles: ['devops', 'sre', 'cloud'] 
  },
  { 
    id: 'cybersecurity', 
    name: 'Cybersecurity', 
    matchSkills: ['security', 'cybersecurity', 'auth', 'oauth', 'penetration testing', 'siem', 'compliance'], 
    matchRoles: ['security', 'cybersecurity'] 
  },
  { 
    id: 'database', 
    name: 'Database', 
    matchSkills: ['postgresql', 'mysql', 'mongodb', 'redis', 'database', 'dba', 'sql'], 
    matchRoles: ['database', 'dba', 'backend'] 
  },
  { 
    id: 'qa', 
    name: 'Testing/QA', 
    matchSkills: ['cypress', 'playwright', 'jest', 'qa', 'testing', 'selenium', 'automation'], 
    matchRoles: ['qa', 'testing', 'quality'] 
  }
];

const PROJECT_TYPE_PRESETS = {
  frontend: ['React', 'TypeScript', 'Tailwind', 'Next.js', 'Figma'],
  backend: ['Node.js', 'Go', 'PostgreSQL', 'Kafka', 'Redis', 'gRPC'],
  fullstack: ['React', 'TypeScript', 'Node.js', 'PostgreSQL', 'Docker'],
  design: ['Figma', 'Design Systems', 'User Research', 'UI/UX'],
  ai: ['Python', 'PyTorch', 'Docker', 'AWS', 'Data Analytics'],
  datascience: ['Python', 'Data Analytics', 'PostgreSQL', 'Pandas'],
  mobile: ['Flutter', 'React Native', 'Node.js', 'iOS Swift'],
  cloud: ['Kubernetes', 'AWS', 'Terraform', 'Docker', 'CI/CD'],
  cybersecurity: ['Security', 'OAuth', 'PostgreSQL', 'Docker'],
  database: ['PostgreSQL', 'Redis', 'Node.js', 'Docker'],
  qa: ['Playwright', 'Cypress', 'Jest', 'CI/CD'],
  web: ['React', 'TypeScript', 'Node.js', 'PostgreSQL'],
  fintech: ['Go', 'PostgreSQL', 'Kafka', 'Docker', 'gRPC'],
  enterprise: ['Go', 'Kubernetes', 'Kafka', 'PostgreSQL', 'React']
};

function getDomainAvailableCount(domainDef) {
  if (!AppState.employees) return 0;
  return AppState.employees.filter(emp => {
    const isAvailable = emp.status === 'bench' || emp.status === 'partial' || (emp.allocationPercent !== undefined && emp.allocationPercent < 100);
    if (!isAvailable) return false;

    const roleLower = (emp.role || '').toLowerCase();
    const skillsLower = (emp.skills || []).map(s => s.toLowerCase());

    const roleMatch = domainDef.matchRoles.some(r => roleLower.includes(r));
    const skillMatch = domainDef.matchSkills.some(ms => skillsLower.some(s => s.includes(ms) || ms.includes(s)));

    return roleMatch || skillMatch;
  }).length;
}

function getSkillAvailableCount(skillName) {
  if (!AppState.employees) return 0;
  const target = skillName.toLowerCase();
  return AppState.employees.filter(emp => {
    const isAvailable = emp.status === 'bench' || emp.status === 'partial' || (emp.allocationPercent !== undefined && emp.allocationPercent < 100);
    if (!isAvailable) return false;

    const skills = (emp.skills || []).map(s => s.toLowerCase());
    const role = (emp.role || '').toLowerCase();
    
    return skills.some(s => s.includes(target) || target.includes(s)) || role.includes(target);
  }).length;
}

function updateDomainSelectOptions() {
  const typeSelect = document.getElementById('np-type-select');
  if (!typeSelect) return;

  const currentSelected = typeSelect.value || 'frontend';
  typeSelect.innerHTML = PROJECT_DOMAINS.map(domain => {
    const isSelected = domain.id === currentSelected;
    return `<option value="${domain.id}" ${isSelected ? 'selected' : ''}>${domain.name}</option>`;
  }).join('');
}

let currentNewProjectSkills = new Map([
  ['React', 2],
  ['TypeScript', 1],
  ['Node.js', 2],
  ['PostgreSQL', 1]
]);

function initNewProjectModal() {
  const form = document.getElementById('new-project-form');
  const typeSelect = document.getElementById('np-type-select');
  const workloadInput = document.getElementById('np-workload-input');
  const deadlineInput = document.getElementById('np-deadline-input');
  const customSkillsInput = document.getElementById('np-custom-skills-input');
  const presetChips = document.querySelectorAll('.workload-presets .btn-preset-chip');
  const domainHeadcountInput = document.getElementById('np-domain-headcount');
  const btnDomainMinus = document.getElementById('btn-domain-count-minus');
  const btnDomainPlus = document.getElementById('btn-domain-count-plus');

  // Update domain dropdown options with live counts
  updateDomainSelectOptions();

  // Set default deadline to 4 weeks (28 days) from today
  const defaultDeadline = new Date(Date.now() + 28 * 24 * 60 * 60 * 1000);
  if (deadlineInput && !deadlineInput.value) {
    deadlineInput.value = defaultDeadline.toISOString().split('T')[0];
    const minDate = new Date(Date.now() + 24 * 60 * 60 * 1000);
    deadlineInput.min = minDate.toISOString().split('T')[0];
  }

  // Domain Headcount Steppers
  if (btnDomainMinus && domainHeadcountInput) {
    btnDomainMinus.addEventListener('click', () => {
      const current = parseInt(domainHeadcountInput.value, 10) || 1;
      if (current > 1) {
        domainHeadcountInput.value = current - 1;
        updateProjectCalculations();
      }
    });
  }

  if (btnDomainPlus && domainHeadcountInput) {
    btnDomainPlus.addEventListener('click', () => {
      const current = parseInt(domainHeadcountInput.value, 10) || 1;
      if (current < 50) {
        domainHeadcountInput.value = current + 1;
        updateProjectCalculations();
      }
    });
  }

  if (domainHeadcountInput) {
    domainHeadcountInput.addEventListener('input', () => {
      updateProjectCalculations();
    });
  }

  // Workload Preset button clicks
  presetChips.forEach(chip => {
    chip.addEventListener('click', () => {
      presetChips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      if (workloadInput) {
        workloadInput.value = chip.dataset.hours;
        updateProjectCalculations();
      }
    });
  });

  // Workload input change
  if (workloadInput) {
    workloadInput.addEventListener('input', () => {
      const val = workloadInput.value;
      presetChips.forEach(chip => {
        if (chip.dataset.hours === val) {
          chip.classList.add('active');
        } else {
          chip.classList.remove('active');
        }
      });
      updateProjectCalculations();
    });
  }

  // Deadline input change
  if (deadlineInput) {
    deadlineInput.addEventListener('input', updateProjectCalculations);
    deadlineInput.addEventListener('change', updateProjectCalculations);
  }

  // Project Type change
  if (typeSelect) {
    typeSelect.addEventListener('change', () => {
      const selectedType = typeSelect.value;
      const domainDef = PROJECT_DOMAINS.find(d => d.id === selectedType);
      if (domainDef && domainHeadcountInput) {
        const availCount = getDomainAvailableCount(domainDef);
        domainHeadcountInput.value = availCount || 3;
      }
      if (PROJECT_TYPE_PRESETS[selectedType]) {
        currentNewProjectSkills = new Map();
        PROJECT_TYPE_PRESETS[selectedType].forEach(skill => {
          currentNewProjectSkills.set(skill, 1);
        });
        renderProjectSkills();
      }
      updateProjectCalculations();
    });
  }

  // Custom Skills input
  if (customSkillsInput) {
    const handleAddSkill = () => {
      const val = customSkillsInput.value.trim();
      if (!val) return;
      const tokens = val.split(',').map(s => s.trim()).filter(s => s.length > 0);
      tokens.forEach(t => {
        if (!currentNewProjectSkills.has(t)) {
          currentNewProjectSkills.set(t, 1);
        }
      });
      customSkillsInput.value = '';
      renderProjectSkills();
      updateProjectCalculations();
    };

    customSkillsInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ',') {
        e.preventDefault();
        handleAddSkill();
      }
    });

    customSkillsInput.addEventListener('blur', handleAddSkill);
  }

  // Form Submission -> Create Project and update dashboard
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      handleCreateNewProject();
    });
  }

  renderProjectSkills();
  updateProjectCalculations();
}

function refreshNewProjectModal() {
  updateDomainSelectOptions();
  const deadlineInput = document.getElementById('np-deadline-input');
  if (deadlineInput && !deadlineInput.value) {
    const defaultDeadline = new Date(Date.now() + 28 * 24 * 60 * 60 * 1000);
    deadlineInput.value = defaultDeadline.toISOString().split('T')[0];
  }
  renderProjectSkills();
  updateProjectCalculations();
}

function renderProjectSkills() {
  const suggestionsBox = document.getElementById('np-skill-suggestions');
  const selectedBox = document.getElementById('np-selected-skills-container');

  if (suggestionsBox) {
    suggestionsBox.innerHTML = SUGGESTED_PROJECT_SKILLS.map(skill => {
      const isSelected = currentNewProjectSkills.has(skill);
      return `
        <span class="skill-choice-chip ${isSelected ? 'selected' : ''}" data-skill="${skill}">
          ${skill}
        </span>
      `;
    }).join('');

    suggestionsBox.querySelectorAll('.skill-choice-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const skill = chip.dataset.skill;
        if (currentNewProjectSkills.has(skill)) {
          currentNewProjectSkills.delete(skill);
        } else {
          currentNewProjectSkills.set(skill, 1);
        }
        renderProjectSkills();
        updateProjectCalculations();
      });
    });
  }

  if (selectedBox) {
    selectedBox.innerHTML = Array.from(currentNewProjectSkills.entries()).map(([skill, reqCount]) => {
      return `
        <span class="selected-skill-tag">
          <span class="skill-name-text">${skill}</span>
          <span class="skill-stepper-wrap">
            <button type="button" class="btn-tag-stepper btn-skill-minus" data-skill="${skill}" aria-label="Decrease ${skill} count">−</button>
            <span class="tag-count-display" data-skill="${skill}">${reqCount}</span>
            <button type="button" class="btn-tag-stepper btn-skill-plus" data-skill="${skill}" aria-label="Increase ${skill} count">+</button>
          </span>
          <button type="button" class="btn-remove-tag" data-skill="${skill}" aria-label="Remove skill">✕</button>
        </span>
      `;
    }).join('');

    selectedBox.querySelectorAll('.btn-skill-minus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const skill = btn.dataset.skill;
        const count = currentNewProjectSkills.get(skill) || 1;
        if (count > 1) {
          currentNewProjectSkills.set(skill, count - 1);
        } else {
          currentNewProjectSkills.delete(skill);
        }
        renderProjectSkills();
        updateProjectCalculations();
      });
    });

    selectedBox.querySelectorAll('.btn-skill-plus').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const skill = btn.dataset.skill;
        const count = currentNewProjectSkills.get(skill) || 1;
        currentNewProjectSkills.set(skill, count + 1);
        renderProjectSkills();
        updateProjectCalculations();
      });
    });

    selectedBox.querySelectorAll('.btn-remove-tag').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const skill = btn.dataset.skill;
        currentNewProjectSkills.delete(skill);
        renderProjectSkills();
        updateProjectCalculations();
      });
    });
  }
}

function updateProjectCalculations() {
  const workloadInput = document.getElementById('np-workload-input');
  const deadlineInput = document.getElementById('np-deadline-input');
  const typeSelect = document.getElementById('np-type-select');

  const workloadHours = parseFloat(workloadInput?.value) || 480;
  const deadlineVal = deadlineInput?.value;
  const projectType = typeSelect ? typeSelect.value : 'web';

  // Calculate timeline
  const now = new Date();
  const deadline = deadlineVal ? new Date(deadlineVal) : new Date(now.getTime() + 28 * 24 * 60 * 60 * 1000);
  const diffTime = deadline.getTime() - now.getTime();
  const diffDays = Math.max(2, Math.round(diffTime / (1000 * 60 * 60 * 24)));
  const diffWeeks = Math.max(0.5, +(diffDays / 7).toFixed(1));
  const workingDays = Math.max(2, Math.round(diffDays * 5 / 7));

  const previewEl = document.getElementById('np-deadline-preview');
  if (previewEl) {
    previewEl.textContent = `Delivery Horizon: ~${diffWeeks} weeks (${workingDays} working days)`;
  }

  // Headcount calculation:
  // Standard productive sprint load = ~32 committed hrs/wk per dev
  const weeklyHoursNeeded = workloadHours / diffWeeks;
  const productiveHoursPerDev = 32;
  let rawHeadcount = weeklyHoursNeeded / productiveHoursPerDev;

  // Pod coordination overhead scaling (Brook's law factor)
  if (rawHeadcount > 4) {
    rawHeadcount *= 1.08;
  }
  const recommendedHeadcount = Math.max(1, Math.min(30, Math.ceil(rawHeadcount)));
  const avgHoursPerMember = Math.min(40, Math.round(weeklyHoursNeeded / recommendedHeadcount));
  const capacityPercent = Math.min(100, Math.round((avgHoursPerMember / 40) * 100));

  // Feasibility status badge
  const feasibilityPill = document.getElementById('np-feasibility-pill');
  if (feasibilityPill) {
    feasibilityPill.className = 'rec-feasibility-pill';
    if (avgHoursPerMember <= 34) {
      feasibilityPill.classList.add('optimal');
      feasibilityPill.textContent = '🟢 Optimal Velocity';
    } else if (avgHoursPerMember <= 40) {
      feasibilityPill.classList.add('aggressive');
      feasibilityPill.textContent = '🟡 Intensive Pace';
    } else {
      feasibilityPill.classList.add('critical');
      feasibilityPill.textContent = '🔴 High Overtime Risk';
    }
  }

  // Update KPI summaries
  const headcountEl = document.getElementById('np-rec-headcount');
  const hoursRateEl = document.getElementById('np-rec-hours-rate');
  const timelineEl = document.getElementById('np-rec-timeline');
  const sprintsEl = document.getElementById('np-rec-sprints');
  const avgHoursEl = document.getElementById('np-rec-avg-hours');

  if (headcountEl) headcountEl.textContent = `${recommendedHeadcount} ${recommendedHeadcount === 1 ? 'Member' : 'Members'}`;
  if (hoursRateEl) hoursRateEl.textContent = `~${Math.round(weeklyHoursNeeded)} hrs/week pod velocity`;
  if (timelineEl) timelineEl.textContent = `${diffWeeks} Weeks`;
  if (sprintsEl) sprintsEl.textContent = `~${Math.max(1, Math.round(diffWeeks / 2))} Agile Sprints`;
  if (avgHoursEl) avgHoursEl.textContent = `${avgHoursPerMember} hrs/wk (${capacityPercent}% load)`;

  // Role Breakdown
  const skillsArray = Array.from(currentNewProjectSkills.keys());
  renderRecommendedRoles(recommendedHeadcount, skillsArray, projectType, avgHoursPerMember);

  // Bench Talent Matching
  renderMatchedBenchTalent(skillsArray);
}

function renderRecommendedRoles(totalHeadcount, skills, projectType, avgHours) {
  const container = document.getElementById('np-rec-roles-list');
  if (!container) return;

  const roleDefinitions = [
    {
      title: 'Senior Backend Engineer',
      domain: 'backend',
      matchSkills: ['go', 'node.js', 'python', 'java', 'postgresql', 'sql', 'microservices', 'grpc', 'kafka', 'redis', 'graphql'],
      weight: (projectType === 'fintech' || projectType === 'enterprise') ? 3 : 2
    },
    {
      title: 'Frontend / UI Engineer',
      domain: 'frontend',
      matchSkills: ['react', 'vue', 'angular', 'typescript', 'figma', 'ui', 'ux', 'html', 'css', 'next.js', 'tailwind'],
      weight: (projectType === 'web') ? 3 : 1
    },
    {
      title: 'DevOps & Cloud Architect',
      domain: 'cloud',
      matchSkills: ['kubernetes', 'docker', 'aws', 'gcp', 'terraform', 'ci/cd', 'cloud'],
      weight: (projectType === 'cloud') ? 3 : 1
    },
    {
      title: 'QA Automation Engineer',
      domain: 'qa',
      matchSkills: ['playwright', 'cypress', 'jest', 'qa', 'testing', 'automation'],
      weight: 1
    },
    {
      title: 'Mobile App Developer',
      domain: 'mobile',
      matchSkills: ['flutter', 'react native', 'ios', 'android', 'swift', 'kotlin'],
      weight: (projectType === 'mobile') ? 3 : 0
    },
    {
      title: 'AI / Data Engineer',
      domain: 'ai',
      matchSkills: ['pytorch', 'ai', 'ml', 'machine learning', 'langchain', 'analytics', 'data'],
      weight: (projectType === 'ai') ? 3 : 0
    }
  ];

  // Identify roles with skill matches or high relevance to project type
  const activeRoles = [];
  roleDefinitions.forEach(def => {
    const matched = skills.filter(s => def.matchSkills.some(ms => s.toLowerCase().includes(ms) || ms.includes(s.toLowerCase())));
    if (matched.length > 0 || def.weight >= 2) {
      activeRoles.push({
        title: def.title,
        skills: matched.length > 0 ? matched : skills.slice(0, 3),
        weight: def.weight + (matched.length * 1.5)
      });
    }
  });

  if (activeRoles.length === 0) {
    activeRoles.push({
      title: 'Full-Stack Developer',
      skills: skills.length ? skills : ['General Engineering'],
      weight: 2
    });
  }

  // Allocate headcount across active roles proportionally
  const totalWeight = activeRoles.reduce((acc, r) => acc + r.weight, 0);
  let allocations = activeRoles.map(r => {
    const count = Math.max(1, Math.round((r.weight / totalWeight) * totalHeadcount));
    return { ...r, count };
  });

  // Balance sum exactly to totalHeadcount
  let sum = allocations.reduce((acc, a) => acc + a.count, 0);
  while (sum > totalHeadcount && allocations.length > 1) {
    const maxItem = allocations.reduce((max, a) => a.count > max.count ? a : max, allocations[0]);
    if (maxItem.count > 1) {
      maxItem.count--;
      sum--;
    } else {
      break;
    }
  }
  while (sum < totalHeadcount) {
    allocations[0].count++;
    sum++;
  }

  container.innerHTML = allocations.map(item => `
    <div class="rec-role-card">
      <div class="rec-role-card-top">
        <span class="rec-role-name">${item.title}</span>
        <span class="rec-role-badge">${item.count} ${item.count === 1 ? 'Engineer' : 'Engineers'}</span>
      </div>
      <div class="rec-role-skills">
        ${item.skills.map(s => `<span class="rec-role-skill-tag">${s}</span>`).join('')}
      </div>
      <div class="rec-role-alloc">
        <span>Target: <strong>${avgHours} hrs/wk</strong></span>
        <span>${item.count} Required</span>
      </div>
    </div>
  `).join('');
}

function renderMatchedBenchTalent(skills) {
  const container = document.getElementById('np-bench-list');
  const countEl = document.getElementById('np-bench-count');
  if (!container) return;

  const skillLower = skills.map(s => s.toLowerCase());

  // Score available or bench candidates from AppState.employees
  const scored = AppState.employees.map(emp => {
    const matchedSkills = (emp.skills || []).filter(s => skillLower.some(req => req.includes(s.toLowerCase()) || s.toLowerCase().includes(req)));
    const isBench = emp.status === 'bench';
    const isPartial = emp.status === 'partial';
    let score = matchedSkills.length * 15;
    if (isBench) score += 30;
    if (isPartial) score += 15;
    return {
      emp,
      matchedSkills,
      score,
      isBench,
      isPartial
    };
  }).filter(item => item.matchedSkills.length > 0 || item.isBench)
    .sort((a, b) => b.score - a.score);

  const topMatches = scored.slice(0, 3);

  if (countEl) {
    countEl.textContent = `${topMatches.length} Bench Candidate${topMatches.length === 1 ? '' : 's'} Matched`;
  }

  if (topMatches.length === 0) {
    container.innerHTML = `<span style="font-size: 12px; color: var(--text-muted); padding: 4px 0;">No bench candidates match exact skills. Ready for recruitment request.</span>`;
    return;
  }

  container.innerHTML = topMatches.map(m => `
    <div class="rec-bench-card">
      <div class="rec-bench-avatar">${m.emp.avatarText || m.emp.name.split(' ').map(n=>n[0]).join('')}</div>
      <div class="rec-bench-info">
        <span class="rec-bench-name">${m.emp.name}</span>
        <span class="rec-bench-role">${m.emp.role} • ${m.matchedSkills.slice(0, 2).join(', ') || 'Ready for Staffing'}</span>
      </div>
      <span class="rec-bench-status">${m.emp.status === 'bench' ? '🟢 Bench' : '🟡 Partial'}</span>
    </div>
  `).join('');
}

function handleCreateNewProject() {
  const nameInput = document.getElementById('np-name-input');
  const codeInput = document.getElementById('np-code-input');
  const workloadInput = document.getElementById('np-workload-input');
  const deadlineInput = document.getElementById('np-deadline-input');
  const typeSelect = document.getElementById('np-type-select');

  const name = nameInput.value.trim();
  if (!name) return;

  let code = codeInput.value.trim();
  if (!code) {
    code = name.split(' ').map(w => w[0]).join('').toUpperCase() + '-' + Math.floor(100 + Math.random() * 900);
  }

  const workload = parseInt(workloadInput.value, 10) || 480;
  const deadlineVal = deadlineInput.value;
  const projectType = typeSelect ? typeSelect.value : 'web';

  const now = new Date();
  const deadline = deadlineVal ? new Date(deadlineVal) : new Date(now.getTime() + 28 * 24 * 60 * 60 * 1000);
  const domainHeadcountInput = document.getElementById('np-domain-headcount');
  const customHeadcount = domainHeadcountInput ? parseInt(domainHeadcountInput.value, 10) : 0;
  const recommendedCount = customHeadcount > 0 ? customHeadcount : Math.max(1, Math.min(30, Math.ceil(workload / (diffWeeks * 32))));

  const projKey = `proj-${Date.now()}`;

  // Assemble team members from bench talent where available
  const teamMembers = [];
  const benchTalent = AppState.employees.filter(e => e.status === 'bench');

  benchTalent.slice(0, Math.min(2, recommendedCount)).forEach(talent => {
    teamMembers.push({
      name: talent.name,
      role: talent.role,
      hours: '40 hrs/wk',
      percent: 100,
      status: 'Active'
    });
  });

  const genericTitles = ['Lead Backend Dev', 'Frontend Specialist', 'DevOps Engineer', 'QA Automation', 'Full Stack Dev'];
  while (teamMembers.length < recommendedCount) {
    const idx = teamMembers.length;
    teamMembers.push({
      name: `Engineer ${idx + 1} (Allocated)`,
      role: genericTitles[idx % genericTitles.length],
      hours: '35 hrs/wk',
      percent: 88,
      status: 'Active'
    });
  }

  // Register in AppState.pmProjects
  AppState.pmProjects[projKey] = {
    name: name,
    code: code,
    health: 'On Track',
    teamSize: recommendedCount,
    allocatedHours: recommendedCount * 35,
    budgetHours: Math.round(workload / diffWeeks),
    openGaps: Math.max(0, recommendedCount - benchTalent.length),
    teamMembers: teamMembers
  };

  // Add to active project select dropdown
  const select = document.getElementById('pm-project-select');
  if (select) {
    const opt = document.createElement('option');
    opt.value = projKey;
    opt.textContent = `${name} (${code})`;
    opt.selected = true;
    select.prepend(opt);
  }

  // Close modal and update view
  closeModal('new-project-modal');
  renderPMView();
  renderPMPipeline();
  renderPMTalentRecommendations();

  // Reset name and code inputs for next time
  nameInput.value = '';
  codeInput.value = '';

  showToast(`🎉 New project "${name}" created with ${recommendedCount} allocated roles!`, 'success');
}

