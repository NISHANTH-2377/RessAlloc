/**
 * API Service for Resource Allocation Engine
 */

const isDirectFlask = window.location.port === '5000' || (window.location.port === '' && window.location.protocol.startsWith('http') && !window.location.host.includes(':'));
const API_BASE = isDirectFlask ? '' : 'http://127.0.0.1:5000';

const API = {
  // Projects
  async getProjects() {
    const res = await fetch(`${API_BASE}/api/projects`);
    if (!res.ok) throw new Error('Failed to fetch projects');
    return res.json();
  },

  async getProject(id) {
    const res = await fetch(`${API_BASE}/api/projects/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch project ${id}`);
    return res.json();
  },

  async createProject(projectData) {
    const res = await fetch(`${API_BASE}/api/projects`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(projectData)
    });
    return res.json();
  },

  async updateProject(id, projectData) {
    const res = await fetch(`${API_BASE}/api/projects/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(projectData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to update project');
    }
    return res.json();
  },

  async deleteProject(id) {
    const res = await fetch(`${API_BASE}/api/projects/${id}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to delete project');
    }
    return res.json();
  },

  async getRecommendations(projectId) {
    const res = await fetch(`${API_BASE}/api/projects/${projectId}/recommendations`);
    if (!res.ok) throw new Error(`Failed to get recommendations for ${projectId}`);
    return res.json();
  },

  async refreshProject(projectId) {
    const res = await fetch(`${API_BASE}/api/projects/${projectId}/refresh`, {
      method: 'POST'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Failed to refresh allocations for project ${projectId}`);
    }
    return res.json();
  },

  async refreshAllProjects() {
    const res = await fetch(`${API_BASE}/api/projects/refresh-all`, {
      method: 'POST'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to refresh all project allocations');
    }
    return res.json();
  },

  async getProjectRankedCsv(projectId) {
    const res = await fetch(`${API_BASE}/api/projects/${projectId}/ranked-csv`);
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Failed to fetch ranked CSV for project ${projectId}`);
    }
    return res.json();
  },

  getProjectCsvDownloadUrl(projectId) {
    return `${API_BASE}/api/projects/${projectId}/download-csv`;
  },

  async assignEmployee(projectId, employeeId) {
    const res = await fetch(`${API_BASE}/api/projects/${projectId}/assign`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employee_id: employeeId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to assign employee');
    }
    return res.json();
  },

  async removeEmployeeFromProject(projectId, employeeId) {
    const res = await fetch(`${API_BASE}/api/projects/${projectId}/remove-employee`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ employee_id: employeeId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to remove employee from project');
    }
    return res.json();
  },

  // HR Requisitions
  async getHrRequests(status = null) {
    const url = status ? `${API_BASE}/api/hr/requests?status=${encodeURIComponent(status)}` : `${API_BASE}/api/hr/requests`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch HR requests');
    return res.json();
  },

  async createHrRequest(requestData) {
    const res = await fetch(`${API_BASE}/api/hr/requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to submit HR request');
    }
    return res.json();
  },

  async updateHrRequestStatus(requestId, status = 'fulfilled') {
    const res = await fetch(`${API_BASE}/api/hr/requests/${requestId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to update HR request status');
    }
    return res.json();
  },

  async deleteHrRequest(requestId) {
    const res = await fetch(`${API_BASE}/api/hr/requests/${requestId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to delete HR request');
    }
    return res.json();
  },

  // Employees (HR Directory)
  async getEmployees() {
    const res = await fetch(`${API_BASE}/api/employees`);
    if (!res.ok) throw new Error('Failed to fetch employees');
    return res.json();
  },

  async getEmployee(id) {
    const res = await fetch(`${API_BASE}/api/employees/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch employee ${id}`);
    return res.json();
  },

  async addEmployee(formData) {
    // If formData is FormData object, omit Content-Type header to let browser set boundary
    const isFormData = formData instanceof FormData;
    const res = await fetch(`${API_BASE}/api/employees`, {
      method: 'POST',
      headers: isFormData ? {} : { 'Content-Type': 'application/json' },
      body: isFormData ? formData : JSON.stringify(formData)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to add employee');
    }
    return res.json();
  },

  async updateEmployee(employeeId, data) {
    const isFormData = data instanceof FormData;
    const cleanId = encodeURIComponent((employeeId || '').trim());
    const res = await fetch(`${API_BASE}/api/employees/${cleanId}`, {
      method: 'PUT',
      headers: isFormData ? {} : { 'Content-Type': 'application/json' },
      body: isFormData ? data : JSON.stringify(data)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Failed to update employee (${res.status})`);
    }
    return res.json();
  },

  async deleteEmployee(employeeId) {
    const cleanId = encodeURIComponent((employeeId || '').trim());
    const res = await fetch(`${API_BASE}/api/employees/${cleanId}`, {
      method: 'DELETE'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || `Failed to delete employee (${res.status})`);
    }
    return res.json();
  },

  // Employee Portal
  async getEmployeeDashboard(employeeId) {
    const res = await fetch(`${API_BASE}/api/employees/${employeeId}/dashboard`);
    if (!res.ok) throw new Error(`Failed to load employee dashboard for ${employeeId}`);
    return res.json();
  },

  async submitTransferResponse(employeeId, offerId, action, reason = '') {
    const res = await fetch(`${API_BASE}/api/employees/${employeeId}/transfer-response`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ offer_id: offerId, action, reason })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Failed to submit response');
    }
    return res.json();
  },

  // Notifications
  async getNotifications(role, employeeId = null) {
    let url = `${API_BASE}/api/notifications?role=${role}`;
    if (employeeId) url += `&employee_id=${employeeId}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error('Failed to fetch notifications');
    return res.json();
  },

  async markNotificationsRead(role) {
    const res = await fetch(`${API_BASE}/api/notifications/mark-read`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ role })
    });
    return res.json();
  },

  async dismissNotification(notifId) {
    const res = await fetch(`${API_BASE}/api/notifications/${notifId}/dismiss`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    });
    if (!res.ok) throw new Error('Failed to dismiss notification');
    return res.json();
  },

  // Authentication
  async login(username, password, role = null) {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password, role })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.error || 'Authentication failed');
    }
    return res.json();
  },

  async logout() {
    try {
      await fetch(`${API_BASE}/api/auth/logout`, { method: 'POST' });
    } catch (e) {
      console.warn('Logout request error:', e);
    }
    return { success: true };
  },

  // System Calculation Status
  async getCalculationStatus() {
    try {
      const res = await fetch(`${API_BASE}/api/system/calculation-status`);
      if (!res.ok) return { is_calculating: false };
      return res.json();
    } catch (e) {
      return { is_calculating: false };
    }
  }
};
