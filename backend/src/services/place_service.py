"""
Place Service - Manages place data with Google Maps integration and caching
"""
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from src.models.place import Place, PlaceCategory
from src.services.google_maps_service import get_google_maps_service
from logging import getLogger

logger = getLogger(__name__)


class PlaceService:
    """Service for managing places with Google Maps integration"""

    def __init__(self, db: Session):
        self.db = db
        self.maps_service = get_google_maps_service()

    def get_or_create_place(self, google_place_id: str) -> Optional[Place]:
        """
        Get place from database or fetch from Google Maps and cache it
        
        Args:
            google_place_id: Google Place ID
        
        Returns:
            Place object or None if not found
        """
        # Check if place exists in database
        place = self.db.query(Place).filter(
            Place.google_place_id == google_place_id
        ).first()

        if place:
            return place

        # Fetch from Google Maps
        place_details = self.maps_service.get_place_details(google_place_id)
        if not place_details:
            return None

        # Create new place in database
        location = place_details['geometry']['location']
        
        # Determine category from types
        category = self._determine_category(place_details.get('types', []))
        
        # Get first photo reference if available
        photo_ref = None
        if place_details.get('photos'):
            photo_ref = place_details['photos'][0].get('photo_reference')

        place = Place(
            google_place_id=google_place_id,
            name=place_details.get('name', 'Unknown'),
            address=place_details.get('formatted_address', ''),
            latitude=location['lat'],
            longitude=location['lng'],
            category=category,
            rating=place_details.get('rating'),
            price_level=place_details.get('price_level'),
            phone_number=place_details.get('formatted_phone_number'),
            website=place_details.get('website'),
            photo_reference=photo_ref,
            opening_hours=str(place_details.get('opening_hours', {}))
        )

        self.db.add(place)
        self.db.commit()
        self.db.refresh(place)

        return place

    def search_places(
        self,
        query: str,
        location: Optional[str] = None,
        category: Optional[PlaceCategory] = None,
        radius: int = 5000
    ) -> List[Place]:
        """
        Search for places and cache results
        
        Args:
            query: Search query
            location: Location string (e.g., "Paris, France") or None
            category: Optional category filter
            radius: Search radius in meters
        
        Returns:
            List of Place objects
        """
        # Geocode location if provided
        location_coords = None
        if location:
            location_coords = self.maps_service.geocode_address(location)

        # Search Google Maps
        place_type = self._category_to_google_type(category) if category else None
        results = self.maps_service.search_places(
            query=query,
            location=location_coords,
            radius=radius,
            place_type=place_type
        )

        # Create places directly from results
        places = []
        for result in results[:20]:  # Limit to 20 results
            place = self._create_place_from_result(result, category)
            if place:
                places.append(place)

        return places

    def get_popular_places(
        self,
        destination: str,
        category: PlaceCategory,
        limit: int = 10
    ) -> List[Place]:
        """
        Get popular places in a destination by category
        
        Args:
            destination: Destination name (e.g., "Paris, France")
            category: Place category
            limit: Maximum number of results
        
        Returns:
            List of highly-rated Place objects
        """
        location_coords = self.maps_service.geocode_address(destination)
        if not location_coords:
            logger.warning(f"Could not geocode destination: {destination}")
            return []

        place_type = self._category_to_google_type(category)
        results = self.maps_service.find_places_by_type(
            location=location_coords,
            place_type=place_type,
            radius=10000,  # 10km radius
            min_rating=4.0
        )

        places = []
        for result in results[:limit]:
            place = self._create_place_from_result(result, category)
            if place:
                places.append(place)

        return places

    def _create_place_from_result(self, result: Dict, category: Optional[PlaceCategory] = None) -> Optional[Place]:
        """Create a Place object from API search result"""
        try:
            place_id = result.get('place_id')
            if not place_id:
                return None

            # Check if place already exists
            existing_place = self.db.query(Place).filter(
                Place.google_place_id == place_id
            ).first()

            if existing_place:
                return existing_place

            # Extract location
            location = result.get('geometry', {}).get('location', {})
            lat = location.get('lat')
            lng = location.get('lng')

            if lat is None or lng is None:
                logger.warning(f"Missing coordinates for place: {result.get('name')}")
                return None

            # Determine category
            if category:
                place_category = category
            else:
                types = result.get('types', [])
                place_category = self._determine_category(types)

            # Create new place
            place = Place(
                google_place_id=place_id,
                name=result.get('name', 'Unknown Place'),
                address=result.get('formatted_address', f"{lat}, {lng}"),
                latitude=lat,
                longitude=lng,
                category=place_category,
                rating=result.get('rating', 4.0),
                price_level=result.get('price_level'),
            )

            self.db.add(place)
            self.db.commit()
            self.db.refresh(place)

            logger.info(f"Created place: {place.name} ({place.category.value})")
            return place

        except Exception as e:
            logger.error(f"Error creating place from result: {e}")
            self.db.rollback()
            return None

    def _determine_category(self, types: List[str]) -> PlaceCategory:
        """Determine PlaceCategory from Google place types"""
        type_mapping = {
            'tourist_attraction': PlaceCategory.ATTRACTION,
            'museum': PlaceCategory.MUSEUM,
            'restaurant': PlaceCategory.RESTAURANT,
            'cafe': PlaceCategory.CAFE,
            'lodging': PlaceCategory.HOTEL,
            'park': PlaceCategory.PARK,
            'shopping_mall': PlaceCategory.SHOPPING,
            'church': PlaceCategory.RELIGIOUS,
            'mosque': PlaceCategory.RELIGIOUS,
            'temple': PlaceCategory.RELIGIOUS,
            'synagogue': PlaceCategory.RELIGIOUS,
            'night_club': PlaceCategory.NIGHTLIFE,
            'bar': PlaceCategory.NIGHTLIFE,
            'movie_theater': PlaceCategory.ENTERTAINMENT,
            'amusement_park': PlaceCategory.ENTERTAINMENT,
        }

        for place_type in types:
            if place_type in type_mapping:
                return type_mapping[place_type]

        return PlaceCategory.OTHER

    def _category_to_google_type(self, category: PlaceCategory) -> str:
        """Convert PlaceCategory to Google place type"""
        category_mapping = {
            PlaceCategory.ATTRACTION: 'tourist_attraction',
            PlaceCategory.MUSEUM: 'museum',
            PlaceCategory.RESTAURANT: 'restaurant',
            PlaceCategory.CAFE: 'cafe',
            PlaceCategory.HOTEL: 'lodging',
            PlaceCategory.PARK: 'park',
            PlaceCategory.SHOPPING: 'shopping_mall',
            PlaceCategory.RELIGIOUS: 'church',
            PlaceCategory.NIGHTLIFE: 'night_club',
            PlaceCategory.ENTERTAINMENT: 'movie_theater',
            PlaceCategory.HISTORICAL: 'museum',
        }

        return category_mapping.get(category, 'point_of_interest')
