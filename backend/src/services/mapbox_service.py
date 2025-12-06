"""
Mapbox Service - Free geocoding and place search (100k requests/month)
Sign up at https://account.mapbox.com/auth/signup/ (no credit card required)
"""
import requests
from typing import List, Dict, Optional, Tuple
from logging import getLogger
from src.configs.app_config import get_app_config

logger = getLogger(__name__)


class MapboxService:
    """Service for Mapbox API - completely free tier, no credit card needed"""

    def __init__(self):
        config = get_app_config()
        self.access_token = config.google_maps_api_key  # Reuse same config field
        if not self.access_token:
            raise ValueError(
                "Mapbox access token not configured. "
                "Sign up at https://account.mapbox.com/auth/signup/ and add token to GOOGLE_MAPS_API_KEY in local.config"
            )
        self.base_url = "https://api.mapbox.com"

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using Mapbox Geocoding API
        
        Args:
            address: Address string (e.g., "Paris, France")
        
        Returns:
            (latitude, longitude) tuple or None if not found
        """
        try:
            url = f"{self.base_url}/geocoding/v5/mapbox.places/{address}.json"
            params = {"access_token": self.access_token, "limit": 1}
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                # Mapbox returns [lng, lat], we need (lat, lng)
                return (coords[1], coords[0])
            
            logger.warning(f"Could not geocode address: {address}")
            return None
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None

    def search_places(
        self,
        query: str,
        location: Optional[Tuple[float, float]] = None,
        radius: int = 5000,
        place_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for places near a location"""
        try:
            # Build search query
            search_query = query
            if location:
                # Proximity bias
                search_query = f"{query}"
            
            url = f"{self.base_url}/geocoding/v5/mapbox.places/{search_query}.json"
            params = {
                "access_token": self.access_token,
                "limit": 10,
                "types": "poi"  # Points of interest
            }
            
            if location:
                # Add proximity for better results
                params["proximity"] = f"{location[1]},{location[0]}"  # lng,lat
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            places = []
            
            for feature in data.get("features", []):
                coords = feature["geometry"]["coordinates"]
                places.append({
                    "place_id": feature.get("id", ""),
                    "name": feature.get("text", "Unknown"),
                    "geometry": {
                        "location": {
                            "lat": coords[1],
                            "lng": coords[0]
                        }
                    },
                    "types": [feature.get("properties", {}).get("category", "point_of_interest")],
                    "rating": 4.0,  # Mapbox doesn't have ratings
                })
            
            return places
        except Exception as e:
            logger.error(f"Error searching places: {e}")
            return []

    def find_places_by_type(
        self,
        location: Tuple[float, float],
        place_type: str,
        radius: int = 5000,
        min_rating: float = 3.5
    ) -> List[Dict]:
        """Find places of a specific type near a location"""
        # Map our types to Mapbox categories
        type_mapping = {
            "restaurant": "restaurant",
            "cafe": "cafe",
            "museum": "museum",
            "tourist_attraction": "landmark",
            "park": "park",
            "shopping_mall": "shopping",
            "church": "place_of_worship",
        }
        
        mapbox_type = type_mapping.get(place_type, "landmark")
        return self.search_places(mapbox_type, location, radius, place_type)

    def calculate_travel_time(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "walking"
    ) -> Optional[int]:
        """
        Calculate travel time using simple distance calculation
        Mapbox Directions API requires paid plan for accurate routing
        """
        try:
            from geopy.distance import geodesic
            
            distance_km = geodesic(origin, destination).kilometers
            
            # Estimate time based on mode
            speed_mapping = {
                "walking": 5,
                "bicycling": 15,
                "transit": 30,
                "driving": 50,
            }
            
            speed_kmh = speed_mapping.get(mode, 5)
            time_hours = distance_km / speed_kmh
            time_minutes = int(time_hours * 60)
            
            return max(5, time_minutes)
        except Exception as e:
            logger.error(f"Error calculating travel time: {e}")
            return 15  # Default fallback


# Singleton
_mapbox_service = None


def get_mapbox_service() -> MapboxService:
    """Get or create Mapbox service singleton"""
    global _mapbox_service
    if _mapbox_service is None:
        _mapbox_service = MapboxService()
    return _mapbox_service
