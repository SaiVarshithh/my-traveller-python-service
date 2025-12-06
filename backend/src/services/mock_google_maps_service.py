"""
Mock Google Maps Service - For testing without API key
Uses predefined data for popular destinations
"""
from typing import List, Dict, Optional, Tuple
from logging import getLogger

logger = getLogger(__name__)


class MockGoogleMapsService:
    """Mock service with predefined destination data"""

    def __init__(self):
        # Predefined coordinates for popular destinations
        self.destinations = {
            "paris, france": (48.8566, 2.3522),
            "tokyo, japan": (35.6762, 139.6503),
            "new york, usa": (40.7128, -74.0060),
            "london, uk": (51.5074, -0.1278),
            "dubai, uae": (25.2048, 55.2708),
            "bangkok, thailand": (13.7563, 100.5018),
            "rome, italy": (41.9028, 12.4964),
            "barcelona, spain": (41.3851, 2.1734),
            "amsterdam, netherlands": (52.3676, 4.9041),
            "singapore": (1.3521, 103.8198),
        }

        # Mock places for each destination
        self.mock_places = {
            "paris, france": [
                {"place_id": "mock_eiffel", "name": "Eiffel Tower", "types": ["tourist_attraction"], "rating": 4.6, "lat": 48.8584, "lng": 2.2945},
                {"place_id": "mock_louvre", "name": "Louvre Museum", "types": ["museum"], "rating": 4.7, "lat": 48.8606, "lng": 2.3376},
                {"place_id": "mock_notre", "name": "Notre-Dame", "types": ["church"], "rating": 4.6, "lat": 48.8530, "lng": 2.3499},
                {"place_id": "mock_sacre", "name": "Sacré-Cœur", "types": ["church"], "rating": 4.7, "lat": 48.8867, "lng": 2.3431},
                {"place_id": "mock_rest1", "name": "Le Jules Verne", "types": ["restaurant"], "rating": 4.5, "lat": 48.8584, "lng": 2.2945},
                {"place_id": "mock_rest2", "name": "L'Ami Jean", "types": ["restaurant"], "rating": 4.6, "lat": 48.8566, "lng": 2.3522},
                {"place_id": "mock_cafe1", "name": "Café de Flore", "types": ["cafe"], "rating": 4.3, "lat": 48.8542, "lng": 2.3320},
                {"place_id": "mock_shop1", "name": "Galeries Lafayette", "types": ["shopping_mall"], "rating": 4.5, "lat": 48.8738, "lng": 2.3320},
            ],
            "tokyo, japan": [
                {"place_id": "mock_tower", "name": "Tokyo Tower", "types": ["tourist_attraction"], "rating": 4.5, "lat": 35.6586, "lng": 139.7454},
                {"place_id": "mock_senso", "name": "Senso-ji Temple", "types": ["church"], "rating": 4.6, "lat": 35.7148, "lng": 139.7967},
                {"place_id": "mock_palace", "name": "Imperial Palace", "types": ["tourist_attraction"], "rating": 4.4, "lat": 35.6852, "lng": 139.7528},
                {"place_id": "mock_sushi", "name": "Sukiyabashi Jiro", "types": ["restaurant"], "rating": 4.8, "lat": 35.6684, "lng": 139.7638},
                {"place_id": "mock_ramen", "name": "Ichiran Ramen", "types": ["restaurant"], "rating": 4.5, "lat": 35.6762, "lng": 139.6503},
            ],
        }

    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Mock geocoding - returns predefined coordinates"""
        address_lower = address.lower().strip()
        coords = self.destinations.get(address_lower)
        if coords:
            logger.info(f"Mock geocoding: {address} -> {coords}")
            return coords
        
        # Default fallback
        logger.warning(f"Mock geocoding: Unknown destination '{address}', using Paris as fallback")
        return (48.8566, 2.3522)

    def search_places(
        self,
        query: str,
        location: Optional[Tuple[float, float]] = None,
        radius: int = 5000,
        place_type: Optional[str] = None
    ) -> List[Dict]:
        """Mock place search"""
        # Find destination by coordinates
        destination_key = None
        if location:
            for dest, coords in self.destinations.items():
                if abs(coords[0] - location[0]) < 0.1 and abs(coords[1] - location[1]) < 0.1:
                    destination_key = dest
                    break
        
        if not destination_key:
            destination_key = "paris, france"
        
        places = self.mock_places.get(destination_key, self.mock_places["paris, france"])
        
        # Filter by type if specified
        if place_type:
            places = [p for p in places if place_type in p.get("types", [])]
        
        # Convert to Google Maps format
        results = []
        for p in places:
            results.append({
                "place_id": p["place_id"],
                "name": p["name"],
                "geometry": {"location": {"lat": p["lat"], "lng": p["lng"]}},
                "types": p["types"],
                "rating": p.get("rating", 4.0),
            })
        
        return results

    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """Mock place details"""
        # Find place in mock data
        for dest_places in self.mock_places.values():
            for place in dest_places:
                if place["place_id"] == place_id:
                    return {
                        "name": place["name"],
                        "formatted_address": f"{place['name']}, Mock Address",
                        "geometry": {"location": {"lat": place["lat"], "lng": place["lng"]}},
                        "rating": place.get("rating", 4.0),
                        "types": place.get("types", []),
                    }
        return None

    def find_places_by_type(
        self,
        location: Tuple[float, float],
        place_type: str,
        radius: int = 5000,
        min_rating: float = 3.5
    ) -> List[Dict]:
        """Mock find places by type"""
        # Find destination
        destination_key = None
        for dest, coords in self.destinations.items():
            if abs(coords[0] - location[0]) < 0.1 and abs(coords[1] - location[1]) < 0.1:
                destination_key = dest
                break
        
        if not destination_key:
            destination_key = "paris, france"
        
        places = self.mock_places.get(destination_key, self.mock_places["paris, france"])
        
        # Filter by type and rating
        filtered = [
            p for p in places 
            if place_type in p.get("types", []) and p.get("rating", 0) >= min_rating
        ]
        
        # Convert to Google Maps format
        results = []
        for p in filtered:
            results.append({
                "place_id": p["place_id"],
                "name": p["name"],
                "geometry": {"location": {"lat": p["lat"], "lng": p["lng"]}},
                "types": p["types"],
                "rating": p.get("rating", 4.0),
            })
        
        return results

    def calculate_travel_time(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        mode: str = "walking"
    ) -> Optional[int]:
        """Mock travel time calculation"""
        # Simple distance-based calculation
        import math
        
        lat1, lon1 = origin
        lat2, lon2 = destination
        
        # Haversine formula for distance
        R = 6371  # Earth radius in km
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        distance_km = R * c
        
        # Estimate time based on mode
        if mode == "walking":
            speed_kmh = 5
        elif mode == "bicycling":
            speed_kmh = 15
        elif mode == "transit":
            speed_kmh = 30
        else:  # driving
            speed_kmh = 40
        
        time_hours = distance_km / speed_kmh
        time_minutes = int(time_hours * 60)
        
        return max(5, time_minutes)  # Minimum 5 minutes


# Singleton instance
_mock_service = None


def get_mock_google_maps_service() -> MockGoogleMapsService:
    """Get or create mock service singleton"""
    global _mock_service
    if _mock_service is None:
        _mock_service = MockGoogleMapsService()
    return _mock_service
