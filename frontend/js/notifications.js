// Notifications Handler Module

async function updateUnreadBadge() {
  if (!isAuthenticated()) return;
  try {
    const res = await api.get('/notifications/unread');
    if (res && res.success) {
      const badge = document.getElementById('unread-badge');
      if (badge) {
        if (res.data.unread_count > 0) {
          badge.textContent = res.data.unread_count;
          badge.classList.remove('hidden');
        } else {
          badge.classList.add('hidden');
        }
      }
    }
  } catch (e) {
    // Ignore silent failures
  }
}

document.addEventListener('DOMContentLoaded', () => {
  updateUnreadBadge();
  setInterval(updateUnreadBadge, 15000); // Check every 15s
});
