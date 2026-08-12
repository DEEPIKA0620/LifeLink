// LifeLink Authentication & Session Management Module

function getCurrentUser() {
  const userStr = localStorage.getItem('lifelink_user');
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch (e) {
    return null;
  }
}

function isAuthenticated() {
  return !!localStorage.getItem('lifelink_token');
}

function getUserRole() {
  const user = getCurrentUser();
  return user ? user.role : null;
}

function requireAuth() {
  if (!isAuthenticated()) {
    showToast('Please login to access this page', 'warning');
    window.location.href = 'pages/login.html';
  }
}

function requireRole(allowedRoles) {
  requireAuth();
  const role = getUserRole();
  if (!allowedRoles.includes(role)) {
    showToast('Access denied: Unauthorized role', 'error');
    window.location.href = '/index.html';
  }
}

async function loginUser(email, password) {
  try {
    const res = await api.post('/auth/login', { email, password }, false);
    if (res && res.success) {
      localStorage.setItem('lifelink_token', res.data.access_token);
      localStorage.setItem('lifelink_user', JSON.stringify({
        id: res.data.user_id,
        role: res.data.role,
        full_name: res.data.full_name,
        email: res.data.email
      }));

      showToast('Welcome back! Login successful.', 'success');

      // Redirect to appropriate role dashboard
      setTimeout(() => {
        switch (res.data.role) {
          case 'patient': window.location.href = 'pages/patient/dashboard.html'; break;
          case 'donor': window.location.href = 'pages/donor/dashboard.html'; break;
          case 'hospital': window.location.href = 'pages/hospital/dashboard.html'; break;
          case 'pharmacy': window.location.href = 'pages/pharmacy/dashboard.html'; break;
          case 'admin': window.location.href = 'pages/admin/dashboard.html'; break;
          default: window.location.href = '/index.html';
        }
      }, 1000);
    }
  } catch (e) {
    console.error('Login error', e);
  }
}

async function registerUser(formData) {
  try {
    const res = await api.post('/auth/register', formData, false);
    if (res && res.success) {
      showToast('Registration successful! Please login.', 'success');
      setTimeout(() => {
        window.location.href = 'pages/login.html';
      }, 1500);
    }
  } catch (e) {
    console.error('Registration error', e);
  }
}

function logoutUser() {
  localStorage.removeItem('lifelink_token');
  localStorage.removeItem('lifelink_user');
  showToast('Logged out successfully', 'success');
  setTimeout(() => {
    window.location.href = '/index.html';
  }, 800);
}
