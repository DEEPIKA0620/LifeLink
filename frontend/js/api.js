// LifeLink Reusable API Client Client Module
const API_BASE_URL = 'http://localhost:8000/api';

/**
 * Universal Toast Notification Helper
 */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icon = type === 'success' ? '✓' : (type === 'error' ? '✕' : 'ℹ');
  toast.innerHTML = `<span style="font-weight: bold; font-size: 1.1rem;">${icon}</span> <span>${message}</span>`;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/**
 * Core HTTP Request Wrapper
 */
async function apiRequest(endpoint, method = 'GET', body = null, authRequired = true) {
  const url = endpoint.startswith && endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  
  const headers = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  };

  if (authRequired) {
    const token = localStorage.getItem('lifelink_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  const options = {
    method: method.toUpperCase(),
    headers: headers
  };

  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(url, options);

    if (response.status === 401 && authRequired) {
      localStorage.removeItem('lifelink_token');
      localStorage.removeItem('lifelink_user');
      showToast('Session expired. Please login again.', 'error');
      setTimeout(() => {
        window.location.href = 'pages/login.html';
      }, 1500);
      return null;
    }

    const data = await response.json();

    if (!response.ok) {
      const errorMsg = data.detail || data.message || 'API operation failed';
      throw new Error(errorMsg);
    }

    return data;
  } catch (error) {
    console.error(`API Error [${method} ${endpoint}]:`, error);
    showToast(error.message || 'Network error occurred', 'error');
    throw error;
  }
}

// Shortcuts
const api = {
  get: (endpoint, auth = true) => apiRequest(endpoint, 'GET', null, auth),
  post: (endpoint, body, auth = true) => apiRequest(endpoint, 'POST', body, auth),
  put: (endpoint, body, auth = true) => apiRequest(endpoint, 'PUT', body, auth),
  delete: (endpoint, auth = true) => apiRequest(endpoint, 'DELETE', null, auth)
};
