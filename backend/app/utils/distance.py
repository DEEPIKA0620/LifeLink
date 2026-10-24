import math

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth's surface
    using the Haversine formula in kilometers (km).
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 9999.0

    # Radius of Earth in kilometers
    R = 6371.0

    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return round(distance, 2)

def estimate_travel_time_minutes(distance_km: float, assumed_speed_kmh: float = 30.0) -> int:
    """
    Estimates travel time in minutes based on straight-line distance and an assumed average speed of 30 km/h.
    - 5 km ≈ 10 mins
    - 10 km ≈ 20 mins
    - 25 km ≈ 50 mins
    """
    if distance_km <= 0:
        return 2
    minutes = int(math.ceil((distance_km / assumed_speed_kmh) * 60.0))
    return max(2, minutes)

def format_travel_time_label(minutes: int) -> str:
    """Transparently labels the travel time estimate without faking live traffic accuracy"""
    if minutes < 60:
        return f"~{minutes} mins (approx. 30 km/h estimate)"
    hours = minutes // 60
    rem_mins = minutes % 60
    return f"~{hours}h {rem_mins}m (approx. 30 km/h estimate)"
