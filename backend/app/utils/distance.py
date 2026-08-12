import math

def calculate_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculates the great-circle distance between two points on the Earth's surface
    using the Haversine formula in kilometers (km).
    """
    if lat1 == 0.0 or lon1 == 0.0 or lat2 == 0.0 or lon2 == 0.0:
        return 5.0 # Default reasonable distance if coordinates missing

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

def estimate_travel_time_minutes(distance_km: float) -> int:
    """
    Estimates travel time in minutes based on distance.
    Prototype estimation rule: estimated_minutes = distance_km * 3
    """
    minutes = int(math.ceil(distance_km * 3))
    return max(3, minutes) # Minimum 3 minutes
