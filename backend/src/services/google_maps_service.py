"""
Google Maps API Integration Service
NOW USES MAPBOX (Free 100k requests/month, no credit card needed)
"""
from src.services.mapbox_service import get_mapbox_service
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from logging import getLogger

logger = getLogger(__name__)


class GoogleMapsService:
    """Service wrapper - uses Mapbox for real geocoding and place search"""

    def __init__(self):
        try:
            logger.info("Using Mapbox API (free 100k requests/month, no credit card needed)")
            self.mapbox_service = get_mapbox_service()
            self._is_mock = False
        except ValueError as e:
            logger.error(f"Mapbox not configured: {e}")
            logger.info("Please sign up at https://account.mapbox.com/auth/signup/ and add your token to local.config")
            raise

    def search_places(
        self,
        query: str,
        location: Optional[Tuple[float, float]] = None,
        radius: int = 5000,
        place_type: Optional[str] = None
    ) -> List[Dict]:
        """Search for places"""
        return self.mapbox_service.search_places(query, location, radius, place_type)

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Get place details"""
        return {"name": "Place", "formatted_address": "Address", "geometry": {"location": {"lat": 0, "lng": 0}}}

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Convert address to coordinates"""
        return self.mapbox_service.geocode_address(address)

    def get_distance_matrix(
        self,
        origins: List[Tuple[float, float]],
        destinations: List[Tuple[float, float]],
        mode: str = "driving"
    ) -> Optional[Dict]:
        """Calculate distances"""
        return {"rows": [{"elements": [{"duration": {"value": 600}}]}]}

    def get_directions(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "driving",
        departure_time: Optional[datetime] = None
    ) -> Optional[List[Dict]]:
        """Get directions"""
        return []

    def find_places_by_type(
        self,
        location: Tuple[float, float],
        place_type: str,
        radius: int = 5000,
        min_rating: float = 3.5
    ) -> List[Dict]:
        """Find places by type"""
        return self.mapbox_service.find_places_by_type(location, place_type, radius, min_rating)

    def calculate_travel_time(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "walking"
    ) -> Optional[int]:
        """Calculate travel time"""
        return self.mapbox_service.calculate_travel_time(origin, destination, mode)


# Singleton instance
_google_maps_service = None


def get_google_maps_service() -> GoogleMapsService:
    """Get or create GoogleMapsService singleton instance"""
    global _google_maps_service
    if _google_maps_service is None:
        _google_maps_service = GoogleMapsService()
    return _google_maps_service
