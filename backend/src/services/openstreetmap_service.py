"""
OpenStreetMap/Nominatim Service using geopy
Completely free, no API key required, no billing needed
"""
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from typing import List, Dict, Optional, Tuple
from logging import getLogger
import time

logger = getLogger(__name__)


class OpenStreetMapService:
    """Service for interacting with OpenStreetMap via Nominatim (geopy)"""

    def __init__(self):
        # Create geolocator with a custom user agent
        self.geolocator = Nominatim(user_agent="mytraveller_app_v1.0")
        self.last_request_time = 0
        self.min_request_interval = 1.0  # Nominatim requires 1 second between requests

    def _rate_limit(self):
        """Ensure we don't exceed Nominatim's rate limit (1 request/second)"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last_request)
        self.last_request_time = time.time()

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        Convert address to coordinates using Nominatim
        
        Args:
            address: Address string (e.g., "Paris, France")
        
        Returns:
            (latitude, longitude) tuple or None if not found
        """
        try:
            self._rate_limit()
            location = self.geolocator.geocode(address, timeout=10)
            if location:
                logger.info(f"Geocoded '{address}' to ({location.latitude}, {location.longitude})")
                return (location.latitude, location.longitude)
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
        """
        Search for places near a location
        Note: Nominatim doesn't have as rich place search as Google Maps
        We'll search for the query and return results
        """
        try:
            self._rate_limit()
            
            # Build search query
            search_query = query
            if location:
                # Search near the location
                search_query = f"{query} near {location[0]},{location[1]}"
            
            # Search for multiple results
            results = self.geolocator.geocode(
                search_query,
                exactly_one=False,
                limit=10,
                timeout=10
            )
            
            if not results:
                return []
            
            # Convert to our format
            places = []
            for result in results:
                places.append({
                    "place_id": f"osm_{result.raw.get('place_id', '')}",
                    "name": result.address.split(',')[0],  # First part of address
                    "geometry": {
                        "location": {
                            "lat": result.latitude,
                            "lng": result.longitude
                        }
                    },
                    "types": [result.raw.get('type', 'point_of_interest')],
                    "rating": 4.0,  # OSM doesn't have ratings
                })
            
            return places
        except Exception as e:
            logger.error(f"Error searching places: {e}")
            return []

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get details about a place
        Note: Limited compared to Google Maps
        """
        try:
            # OSM place IDs are different, we'll do a reverse geocode if needed
            # For now, return basic structure
            return {
                "name": "Place",
                "formatted_address": "Address not available",
                "geometry": {"location": {"lat": 0, "lng": 0}},
                "rating": 4.0,
                "types": ["point_of_interest"],
            }
        except Exception as e:
            logger.error(f"Error getting place details: {e}")
            return None

    def find_places_by_type(
        self,
        location: Tuple[float, float],
        place_type: str,
        radius: int = 5000,
        min_rating: float = 3.5
    ) -> List[Dict]:
        """
        Find places of a specific type near a location
        """
        try:
            self._rate_limit()
            
            # Map our place types to OSM amenity types
            type_mapping = {
                "restaurant": "restaurant",
                "cafe": "cafe",
                "museum": "museum",
                "tourist_attraction": "attraction",
                "park": "park",
                "shopping_mall": "mall",
                "church": "place_of_worship",
            }
            
            osm_type = type_mapping.get(place_type, place_type)
            
            # Search for places of this type near the location
            search_query = f"{osm_type} near {location[0]},{location[1]}"
            results = self.geolocator.geocode(
                search_query,
                exactly_one=False,
                limit=10,
                timeout=10
            )
            
            if not results:
                return []
            
            # Convert and filter by distance
            places = []
            for result in results:
                result_location = (result.latitude, result.longitude)
                distance_km = geodesic(location, result_location).kilometers
                
                # Only include if within radius
                if distance_km <= (radius / 1000):
                    places.append({
                        "place_id": f"osm_{result.raw.get('place_id', '')}",
                        "name": result.address.split(',')[0],
                        "geometry": {
                            "location": {
                                "lat": result.latitude,
                                "lng": result.longitude
                            }
                        },
                        "types": [osm_type],
                        "rating": 4.0,  # Default rating since OSM doesn't have ratings
                    })
            
            return places
        except Exception as e:
            logger.error(f"Error finding places by type '{place_type}': {e}")
            return []

    def calculate_travel_time(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "walking"
    ) -> Optional[int]:
        """
        Calculate travel time between two points
        Uses simple distance-based calculation since OSM doesn't have routing in geopy
        """
        try:
            # Calculate distance
            distance_km = geodesic(origin, destination).kilometers
            
            # Estimate time based on mode and average speeds
            speed_mapping = {
                "walking": 5,      # 5 km/h
                "bicycling": 15,   # 15 km/h
                "transit": 30,     # 30 km/h
                "driving": 50,     # 50 km/h in city
            }
            
            speed_kmh = speed_mapping.get(mode, 5)
            time_hours = distance_km / speed_kmh
            time_minutes = int(time_hours * 60)
            
            # Minimum 5 minutes
            return max(5, time_minutes)
        except Exception as e:
            logger.error(f"Error calculating travel time: {e}")
            return None


# Singleton instance
_osm_service = None


def get_openstreetmap_service() -> OpenStreetMapService:
    """Get or create OpenStreetMapService singleton instance"""
    global _osm_service
    if _osm_service is None:
        _osm_service = OpenStreetMapService()
    return _osm_service
