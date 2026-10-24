from fastapi import APIRouter
from app.utils.locations import SUPPORTED_LOCATIONS
from app.schemas.auth import ApiResponse

router = APIRouter(prefix="/api/locations", tags=["Locations"])

@router.get("", response_model=ApiResponse)
def get_supported_locations():
    """
    Returns full catalog of supported cities and localities with coordinates.
    Allows frontend location selector to dynamically set search origin coordinates.
    """
    cities = []
    for city_name, data in SUPPORTED_LOCATIONS.items():
        cities.append({
            "city": city_name,
            "state": data["state"],
            "center": data["center"],
            "localities": [
                {"name": loc_name, "lat": loc_data["lat"], "lon": loc_data["lon"]}
                for loc_name, loc_data in data["localities"].items()
            ]
        })
    return ApiResponse(
        success=True,
        message=f"Loaded {len(cities)} supported cities",
        data={"cities": cities, "locations": cities}
    )
