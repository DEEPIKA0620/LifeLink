// LifeLink Form Validation Module

const VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
const VALID_ROLES = ['patient', 'donor', 'hospital', 'pharmacy'];
const VALID_PRIORITIES = ['critical', 'urgent', 'normal'];

function validateEmail(email) {
  const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return re.test(email);
}

function validatePhone(phone) {
  const cleaned = phone.replace(/[\s\-\(\)]/g, '');
  return cleaned.length >= 10 && /^\+?\d+$/.test(cleaned);
}

function validatePassword(password) {
  return password && password.length >= 6;
}

function validateBloodGroup(bloodGroup) {
  return VALID_BLOOD_GROUPS.includes(bloodGroup.toUpperCase());
}

function validateRequired(value, fieldName) {
  if (!value || (typeof value === 'string' && value.trim() === '')) {
    showToast(`${fieldName} is required`, 'error');
    return false;
  }
  return true;
}

function validateRegistrationForm(data) {
  if (!validateRequired(data.full_name, 'Full Name')) return false;
  if (!validateRequired(data.email, 'Email')) return false;
  if (!validateEmail(data.email)) {
    showToast('Please enter a valid email address', 'error');
    return false;
  }
  if (!validateRequired(data.phone, 'Phone Number')) return false;
  if (!validatePhone(data.phone)) {
    showToast('Please enter a valid phone number', 'error');
    return false;
  }
  if (!validateRequired(data.password, 'Password')) return false;
  if (!validatePassword(data.password)) {
    showToast('Password must be at least 6 characters', 'error');
    return false;
  }
  if (data.password !== data.confirm_password) {
    showToast('Passwords do not match', 'error');
    return false;
  }
  if (!VALID_ROLES.includes(data.role)) {
    showToast('Please select a valid account type', 'error');
    return false;
  }
  if (data.role === 'donor') {
    if (!data.blood_group || !validateBloodGroup(data.blood_group)) {
      showToast('Please select a valid blood group', 'error');
      return false;
    }
    if (!data.date_of_birth) {
      showToast('Date of birth is required for donors', 'error');
      return false;
    }
  }
  return true;
}

function validateEmergencyRequest(data) {
  if (!data.blood_group || !validateBloodGroup(data.blood_group)) {
    showToast('Please select a valid blood group', 'error');
    return false;
  }
  if (!data.units_required || data.units_required <= 0) {
    showToast('Units required must be greater than 0', 'error');
    return false;
  }
  if (!data.priority || !VALID_PRIORITIES.includes(data.priority.toLowerCase())) {
    showToast('Please select a valid priority level', 'error');
    return false;
  }
  if (!data.hospital_name) {
    showToast('Hospital name is required', 'error');
    return false;
  }
  if (!data.required_by) {
    showToast('Required by date is required', 'error');
    return false;
  }
  return true;
}

function validateMedicine(data) {
  if (!validateRequired(data.medicine_name, 'Medicine Name')) return false;
  if (!validateRequired(data.generic_name, 'Generic Name')) return false;
  if (data.quantity === undefined || data.quantity < 0) {
    showToast('Quantity cannot be negative', 'error');
    return false;
  }
  if (data.price === undefined || data.price < 0) {
    showToast('Price cannot be negative', 'error');
    return false;
  }
  return true;
}

function validateBloodStock(data) {
  if (!data.blood_group || !validateBloodGroup(data.blood_group)) {
    showToast('Please select a valid blood group', 'error');
    return false;
  }
  if (data.units_available === undefined || data.units_available < 0) {
    showToast('Units available cannot be negative', 'error');
    return false;
  }
  return true;
}
