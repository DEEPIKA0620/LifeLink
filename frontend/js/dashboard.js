// LifeLink Dashboard Helper Module

/**
 * Renders a stat card for dashboard pages
 */
function renderStatCard(label, value, icon, colorClass = 'text-slate-900') {
  return `
    <div class="stat-card">
      <div>
        <div class="stat-label">${label}</div>
        <div class="stat-value ${colorClass}">${value}</div>
      </div>
      <div class="stat-icon ${colorClass.replace('text-', 'bg-').replace('600', '100')} ${colorClass}">${icon}</div>
    </div>
  `;
}

/**
 * Renders a priority badge
 */
function renderPriorityBadge(priority) {
  const p = (priority || 'normal').toLowerCase();
  const cls = p === 'critical' ? 'badge-critical' : (p === 'urgent' ? 'badge-urgent' : 'badge-normal');
  return `<span class="badge ${cls}">${p.toUpperCase()}</span>`;
}

/**
 * Renders a status badge
 */
function renderStatusBadge(status) {
  const s = (status || 'pending').toLowerCase();
  let cls = 'badge-normal';
  if (['completed', 'accepted', 'available', 'in_stock'].includes(s)) cls = 'badge-available';
  else if (['cancelled', 'rejected', 'out_of_stock', 'unavailable'].includes(s)) cls = 'badge-unavailable';
  else if (['low_stock', 'urgent'].includes(s)) cls = 'badge-low_stock';
  else if (['critical'].includes(s)) cls = 'badge-critical';
  return `<span class="badge ${cls}">${s.replace(/_/g, ' ')}</span>`;
}

/**
 * Renders a loading spinner
 */
function renderLoading(message = 'Loading...') {
  return `
    <div class="flex flex-col items-center justify-center py-12 text-slate-400">
      <div class="w-10 h-10 border-4 border-slate-200 border-t-sky-500 rounded-full animate-spin mb-4"></div>
      <p class="text-sm font-medium">${message}</p>
    </div>
  `;
}

/**
 * Renders an empty state placeholder
 */
function renderEmptyState(title, subtitle, actionHtml = '') {
  return `
    <div class="glass-card p-8 text-center">
      <div class="text-4xl mb-4">📋</div>
      <h3 class="text-lg font-bold text-slate-700">${title}</h3>
      <p class="text-sm text-slate-500 mt-1 mb-4">${subtitle}</p>
      ${actionHtml}
    </div>
  `;
}

/**
 * Renders an error state
 */
function renderErrorState(message) {
  return `
    <div class="p-6 bg-red-50 border border-red-200 rounded-xl text-center">
      <div class="text-3xl mb-2">⚠️</div>
      <p class="text-red-700 font-semibold">${message}</p>
      <button onclick="location.reload()" class="mt-3 btn-outline text-xs">Try Again</button>
    </div>
  `;
}

/**
 * Renders a request timeline
 */
function renderTimeline(timeline) {
  if (!timeline || timeline.length === 0) return '<p class="text-sm text-slate-500">No timeline events yet.</p>';
  
  return `
    <div class="space-y-4">
      ${timeline.map((t, i) => `
        <div class="flex gap-4">
          <div class="flex flex-col items-center">
            <div class="w-3 h-3 rounded-full ${i === 0 ? 'bg-sky-500' : 'bg-slate-300'}"></div>
            ${i < timeline.length - 1 ? '<div class="w-0.5 flex-1 bg-slate-200"></div>' : ''}
          </div>
          <div class="pb-4">
            <p class="text-sm font-bold text-slate-900">${(t.status || '').replace(/_/g, ' ').toUpperCase()}</p>
            <p class="text-xs text-slate-600">${t.notes || ''}</p>
            <p class="text-xs text-slate-400 mt-1">${formatDate(t.timestamp)}</p>
          </div>
        </div>
      `).join('')}
    </div>
  `;
}

/**
 * Simple confirmation modal
 */
function showConfirmModal(message, onConfirm) {
  const overlay = document.createElement('div');
  overlay.className = 'fixed inset-0 bg-black/50 flex items-center justify-center z-[9999]';
  overlay.innerHTML = `
    <div class="bg-white rounded-2xl p-6 max-w-sm mx-4 shadow-2xl">
      <h3 class="text-lg font-bold text-slate-900 mb-2">Confirm Action</h3>
      <p class="text-sm text-slate-600 mb-6">${message}</p>
      <div class="flex gap-3 justify-end">
        <button id="modal-cancel" class="btn-outline text-sm py-2 px-4">Cancel</button>
        <button id="modal-confirm" class="btn-emergency text-sm py-2 px-4">Confirm</button>
      </div>
    </div>
  `;
  document.body.appendChild(overlay);

  overlay.querySelector('#modal-cancel').addEventListener('click', () => overlay.remove());
  overlay.querySelector('#modal-confirm').addEventListener('click', () => {
    overlay.remove();
    onConfirm();
  });
  overlay.addEventListener('click', (e) => {
    if (e.target === overlay) overlay.remove();
  });
}
