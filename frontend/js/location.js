// Browser Geolocation Helper

const DEFAULT_COORDS = { latitude: 12.9716, longitude: 77.5946, city: "Bengaluru" }; // Default center

function getUserLocation(callback) {
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        callback({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          city: "Detected Location"
        });
      },
      (error) => {
        console.warn("Geolocation permission denied or failed. Using fallback location.", error);
        callback(DEFAULT_COORDS);
      },
      { timeout: 8000, enableHighAccuracy: true }
    );
  } else {
    callback(DEFAULT_COORDS);
  }
}
