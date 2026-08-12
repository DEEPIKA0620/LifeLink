// Leaflet + OpenStreetMap Interactive Map Module

let mapInstance = null;
let markersGroup = null;

function initLeafletMap(containerId, centerLat = 12.9716, centerLon = 77.5946, zoom = 12) {
  const container = document.getElementById(containerId);
  if (!container) return null;

  if (mapInstance) {
    mapInstance.remove();
  }

  // Initialize Leaflet Map
  mapInstance = L.map(containerId).setView([centerLat, centerLon], zoom);

  // Add OpenStreetMap tile layer
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mapInstance);

  markersGroup = L.layerGroup().addTo(mapInstance);

  // Add user center pin
  const userIcon = L.divIcon({
    className: 'custom-div-icon',
    html: `<div style="background-color: #0284C7; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 0 10px rgba(2,132,199,0.8);"></div>`,
    iconSize: [16, 16]
  });
  L.marker([centerLat, centerLon], { icon: userIcon }).addTo(mapInstance).bindPopup("<b>Your Search Location</b>");

  return mapInstance;
}

function renderMapPins(pinsData) {
  if (!mapInstance || !markersGroup) return;

  markersGroup.clearLayers();

  pinsData.forEach(pin => {
    const lat = pin.latitude || pin.lat;
    const lon = pin.longitude || pin.lon;
    if (!lat || !lon) return;

    let markerColor = '#DC2626'; // Default Red for Donors/Requests
    if (pin.type === 'hospital') markerColor = '#0284C7'; // Blue
    if (pin.type === 'pharmacy') markerColor = '#059669'; // Green

    const iconHtml = `<div style="background-color: ${markerColor}; width: 22px; height: 22px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 6px rgba(0,0,0,0.3); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 10px;">✚</div>`;
    
    const customIcon = L.divIcon({
      className: 'map-pin-icon',
      html: iconHtml,
      iconSize: [22, 22]
    });

    const popupContent = `
      <div style="font-family: sans-serif; padding: 4px; max-width: 200px;">
        <h4 style="margin: 0 0 4px 0; color: #0F172A; font-weight: 700; font-size: 14px;">${pin.name || pin.full_name || 'Location'}</h4>
        <p style="margin: 0; font-size: 12px; color: #64748B;"><b>Type:</b> ${pin.type || 'Entity'}</p>
        ${pin.blood_group ? `<p style="margin: 0; font-size: 12px; color: #DC2626;"><b>Blood Group:</b> ${pin.blood_group}</p>` : ''}
        ${pin.distance_km ? `<p style="margin: 0; font-size: 12px; color: #0284C7;"><b>Distance:</b> ${pin.distance_km} km (~${pin.estimated_minutes || Math.ceil(pin.distance_km*3)} mins)</p>` : ''}
        ${pin.match_score ? `<p style="margin: 4px 0 0 0; font-size: 12px; font-weight: bold; color: #059669;">Match Score: ${pin.match_score}/100</p>` : ''}
      </div>
    `;

    L.marker([lat, lon], { icon: customIcon }).addTo(markersGroup).bindPopup(popupContent);
  });
}
