// LifeLink Authentication & Session Management Module

function getAppPath(path) {
  const isFrontendDir = window.location.pathname.startsWith('/frontend');
  const prefix = isFrontendDir ? '/frontend' : '';
  const cleanPath = path.startsWith('/') ? path : '/' + path;
  return `${prefix}${cleanPath}`;
}

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
    window.location.href = getAppPath('/pages/login.html');
  }
}

function requireRole(allowedRoles) {
  requireAuth();
  const role = getUserRole();
  if (!allowedRoles.includes(role)) {
    showToast('Access denied: Unauthorized role', 'error');
    window.location.href = getAppPath('/index.html');
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
          case 'patient': window.location.href = getAppPath('/pages/patient/dashboard.html'); break;
          case 'donor': window.location.href = getAppPath('/pages/donor/dashboard.html'); break;
          case 'hospital': window.location.href = getAppPath('/pages/hospital/dashboard.html'); break;
          case 'pharmacy': window.location.href = getAppPath('/pages/pharmacy/dashboard.html'); break;
          case 'admin': window.location.href = getAppPath('/pages/admin/dashboard.html'); break;
          default: window.location.href = getAppPath('/index.html');
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
        window.location.href = getAppPath('/pages/login.html');
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
    window.location.href = getAppPath('/index.html');
  }, 800);
}
