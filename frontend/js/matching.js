// Smart Emergency Donor Matching UI Module

function renderMatchCard(match) {
  const reasons = Array.isArray(match.match_reasons) 
    ? match.match_reasons 
    : (match.reasons || (match.match_reasons ? match.match_reasons.split(' | ') : []));

  const scoreClass = match.match_score >= 90 ? 'text-green-600 border-green-600 bg-green-50' : (match.match_score >= 75 ? 'text-blue-600 border-blue-600 bg-blue-50' : 'text-amber-600 border-amber-600 bg-amber-50');

  return `
    <div class="glass-card p-6 border-l-4 border-l-red-600 relative">
      <div class="flex items-start justify-between">
        <div>
          <div class="flex items-center gap-3">
            <h3 class="text-xl font-bold text-slate-900">${match.donor_name || match.full_name || 'Donor Candidate'}</h3>
            <span class="badge bg-red-100 text-red-700 border-red-300 font-extrabold">${match.blood_group}</span>
            <span class="badge ${match.availability_status === 'available' ? 'badge-available' : 'badge-unavailable'}">${match.availability_status || 'available'}</span>
          </div>
          
          <div class="flex items-center gap-6 mt-3 text-sm text-slate-600">
            <span>📍 <b>Distance:</b> ${match.distance_km} km</span>
            <span>⏱️ <b>Est. Travel Time:</b> ~${match.estimated_minutes} minutes</span>
            ${match.contact_revealed && match.donor_phone ? `<span class="text-green-700 font-bold">📞 Phone: ${match.donor_phone}</span>` : ''}
          </div>
        </div>

        <!-- Match Score Pill -->
        <div class="text-center">
          <div class="w-16 h-16 rounded-full border-4 ${scoreClass} flex items-center justify-center font-extrabold text-xl shadow-sm">
            ${match.match_score}
          </div>
          <span class="block text-xs text-slate-500 font-semibold mt-1">/ 100 Match</span>
        </div>
      </div>

      <!-- Recommendation Breakdown -->
      <div class="mt-4 pt-4 border-t border-slate-100">
        <h4 class="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Why Recommended:</h4>
        <ul class="space-y-1 text-sm text-slate-700">
          ${reasons.map(r => `<li class="flex items-center gap-2"><span class="text-green-600 font-bold">✓</span> ${r}</li>`).join('')}
        </ul>
      </div>

      <!-- Action Button -->
      <div class="mt-4 flex items-center justify-between">
        <p class="text-xs text-slate-400 italic">Scores are generated strictly for emergency donor prioritization.</p>
        ${match.status === 'accepted' ? `
          <span class="badge badge-completed text-sm py-1.5 px-3">Donor Accepted & Contact Revealed</span>
        ` : `
          <button onclick="requestDonorNotification(${match.request_id || 0}, ${match.donor_id || 0})" class="btn-emergency text-xs py-2 px-4">
            Request Donor
          </button>
        `}
      </div>
    </div>
  `;
}

function renderMedicalDisclaimer() {
  return `
    <div class="p-4 bg-amber-50 border border-amber-200 rounded-xl text-amber-900 text-xs leading-relaxed mt-6">
      <span class="font-bold text-amber-800">⚠️ IMPORTANT MEDICAL SAFETY NOTICE:</span>
      LifeLink is an emergency donor discovery and prioritization platform. Matching scores do NOT guarantee medical compatibility. Final blood compatibility, cross-matching, and transfusion decisions must always be confirmed by qualified healthcare professionals or blood banks.
    </div>
  `;
}
