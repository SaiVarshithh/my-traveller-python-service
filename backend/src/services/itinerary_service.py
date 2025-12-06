"""
Itinerary Service - AI-powered itinerary generation and optimization
"""
from typing import List, Dict, Optional, Tuple
from datetime import date, time, timedelta, datetime
from sqlalchemy.orm import Session
from src.models.trip import Trip
from src.models.itinerary import Itinerary
from src.models.activity import Activity, TransportMode
from src.models.place import Place, PlaceCategory
from src.services.place_service import PlaceService
from src.services.google_maps_service import get_google_maps_service
from logging import getLogger
import random

logger = getLogger(__name__)


class ItineraryService:
    """Service for generating and managing itineraries"""

    def __init__(self, db: Session):
        self.db = db
        self.place_service = PlaceService(db)
        self.maps_service = get_google_maps_service()

    def generate_itinerary(self, trip: Trip) -> List[Itinerary]:
        """
        Generate complete itinerary for a trip
        
        Args:
            trip: Trip object
        
        Returns:
            List of Itinerary objects with activities
        """
        # Delete existing itineraries if regenerating
        self.db.query(Itinerary).filter(Itinerary.trip_id == trip.id).delete()
        self.db.commit()

        # Calculate number of days
        num_days = (trip.end_date - trip.start_date).days + 1

        # Get destination coordinates
        destination_coords = self.maps_service.geocode_address(trip.destination)
        if not destination_coords:
            raise ValueError(f"Could not geocode destination: {trip.destination}")

        itineraries = []

        for day_num in range(1, num_days + 1):
            current_date = trip.start_date + timedelta(days=day_num - 1)
            
            # Create itinerary for the day
            itinerary = Itinerary(
                trip_id=trip.id,
                day_number=day_num,
                date=current_date,
                theme=self._get_day_theme(day_num, num_days)
            )
            self.db.add(itinerary)
            self.db.flush()  # Get the ID

            # Generate activities for the day
            activities = self._generate_daily_activities(
                itinerary=itinerary,
                destination=trip.destination,
                destination_coords=destination_coords,
                day_number=day_num,
                total_days=num_days,
                budget_level=trip.budget_level
            )

            itinerary.activities = activities
            itineraries.append(itinerary)

        self.db.commit()

        # Refresh to get all relationships
        for itinerary in itineraries:
            self.db.refresh(itinerary)

        return itineraries

    def _generate_daily_activities(
        self,
        itinerary: Itinerary,
        destination: str,
        destination_coords: Tuple[float, float],
        day_number: int,
        total_days: int,
        budget_level
    ) -> List[Activity]:
        """Generate activities for a single day"""
        
        # Define activity schedule
        morning_start = time(9, 0)
        lunch_time = time(12, 30)
        afternoon_start = time(14, 30)
        dinner_time = time(19, 0)
        evening_start = time(20, 30)

        activities = []
        
        # Morning activity (attraction/museum)
        morning_places = self._get_places_for_time_slot(
            destination, destination_coords, "morning", day_number, total_days
        )
        if morning_places:
            activities.append(self._create_activity(
                itinerary=itinerary,
                place=morning_places[0],
                start_time=morning_start,
                duration_minutes=150,  # 2.5 hours
                order_index=1,
                previous_location=None
            ))

        # Lunch
        lunch_places = self.place_service.get_popular_places(
            destination, PlaceCategory.RESTAURANT, limit=10
        )
        if lunch_places:
            lunch_place = random.choice(lunch_places[:5])  # Pick from top 5
            prev_location = (activities[-1].place.latitude, activities[-1].place.longitude) if activities else None
            activities.append(self._create_activity(
                itinerary=itinerary,
                place=lunch_place,
                start_time=lunch_time,
                duration_minutes=90,
                order_index=2,
                previous_location=prev_location
            ))

        # Afternoon activity
        afternoon_places = self._get_places_for_time_slot(
            destination, destination_coords, "afternoon", day_number, total_days
        )
        if afternoon_places:
            prev_location = (activities[-1].place.latitude, activities[-1].place.longitude) if activities else None
            activities.append(self._create_activity(
                itinerary=itinerary,
                place=afternoon_places[0],
                start_time=afternoon_start,
                duration_minutes=150,
                order_index=3,
                previous_location=prev_location
            ))

        # Dinner
        dinner_places = self.place_service.get_popular_places(
            destination, PlaceCategory.RESTAURANT, limit=10
        )
        # Make sure it's different from lunch
        dinner_places = [p for p in dinner_places if p.id != (lunch_places[0].id if lunch_places else -1)]
        if dinner_places:
            dinner_place = random.choice(dinner_places[:5])
            prev_location = (activities[-1].place.latitude, activities[-1].place.longitude) if activities else None
            activities.append(self._create_activity(
                itinerary=itinerary,
                place=dinner_place,
                start_time=dinner_time,
                duration_minutes=90,
                order_index=4,
                previous_location=prev_location
            ))

        # Evening activity (optional - entertainment/nightlife)
        if day_number % 2 == 0:  # Every other day
            evening_places = self.place_service.get_popular_places(
                destination, PlaceCategory.ENTERTAINMENT, limit=5
            )
            if evening_places:
                prev_location = (activities[-1].place.latitude, activities[-1].place.longitude) if activities else None
                activities.append(self._create_activity(
                    itinerary=itinerary,
                    place=evening_places[0],
                    start_time=evening_start,
                    duration_minutes=120,
                    order_index=5,
                    previous_location=prev_location
                ))

        return activities

    def _get_places_for_time_slot(
        self,
        destination: str,
        destination_coords: Tuple[float, float],
        time_slot: str,
        day_number: int,
        total_days: int
    ) -> List[Place]:
        """Get appropriate places for a time slot"""
        
        # Vary activities based on day number
        if time_slot == "morning":
            categories = [PlaceCategory.ATTRACTION, PlaceCategory.MUSEUM, PlaceCategory.PARK]
            category = categories[(day_number - 1) % len(categories)]
        elif time_slot == "afternoon":
            categories = [PlaceCategory.ATTRACTION, PlaceCategory.HISTORICAL, PlaceCategory.SHOPPING]
            category = categories[(day_number - 1) % len(categories)]
        else:
            category = PlaceCategory.ATTRACTION

        places = self.place_service.get_popular_places(
            destination, category, limit=10
        )

        return places

    def _create_activity(
        self,
        itinerary: Itinerary,
        place: Place,
        start_time: time,
        duration_minutes: int,
        order_index: int,
        previous_location: Optional[Tuple[float, float]]
    ) -> Activity:
        """Create an activity with transport calculation"""
        
        current_location = (place.latitude, place.longitude)
        transport_mode = TransportMode.NONE
        transport_duration = 0

        if previous_location:
            # Calculate distance and determine transport mode
            transport_mode, transport_duration = self._determine_transport(
                previous_location, current_location
            )

        activity = Activity(
            itinerary_id=itinerary.id,
            place_id=place.id,
            start_time=start_time,
            duration_minutes=duration_minutes,
            transport_mode=transport_mode,
            transport_duration_minutes=transport_duration,
            order_index=order_index,
            is_custom=0
        )

        return activity

    def _determine_transport(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> Tuple[TransportMode, int]:
        """
        Determine best transport mode and duration between two points
        
        Returns:
            (TransportMode, duration_in_minutes)
        """
        # Calculate walking time
        walking_time = self.maps_service.calculate_travel_time(
            origin, destination, mode="walking"
        )

        if walking_time is None:
            return (TransportMode.WALK, 15)  # Default fallback

        # If walkable in under 20 minutes, suggest walking
        if walking_time <= 20:
            return (TransportMode.WALK, walking_time)

        # If 20-40 minutes walking, check transit
        if walking_time <= 40:
            transit_time = self.maps_service.calculate_travel_time(
                origin, destination, mode="transit"
            )
            if transit_time and transit_time < walking_time * 0.7:
                return (TransportMode.TRANSIT, transit_time)
            return (TransportMode.WALK, walking_time)

        # For longer distances, prefer transit
        transit_time = self.maps_service.calculate_travel_time(
            origin, destination, mode="transit"
        )
        if transit_time:
            return (TransportMode.TRANSIT, transit_time)

        # Fallback to taxi for very long distances
        driving_time = self.maps_service.calculate_travel_time(
            origin, destination, mode="driving"
        )
        if driving_time:
            return (TransportMode.TAXI, driving_time)

        return (TransportMode.TRANSIT, 30)  # Default fallback

    def _get_day_theme(self, day_number: int, total_days: int) -> str:
        """Generate a theme for the day"""
        themes = [
            "Cultural Exploration",
            "Historical Journey",
            "Food & Culinary Tour",
            "Nature & Parks",
            "Shopping & Entertainment",
            "Local Experience",
            "Architectural Wonders",
            "Art & Museums"
        ]
        
        return themes[(day_number - 1) % len(themes)]

    def add_custom_activity(
        self,
        itinerary_id: int,
        place_id: int,
        start_time: time,
        duration_minutes: int,
        notes: Optional[str] = None
    ) -> Activity:
        """Add a custom activity to an itinerary"""
        
        itinerary = self.db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
        if not itinerary:
            raise ValueError("Itinerary not found")

        place = self.db.query(Place).filter(Place.id == place_id).first()
        if not place:
            raise ValueError("Place not found")

        # Get the last activity to calculate order and transport
        last_activity = self.db.query(Activity).filter(
            Activity.itinerary_id == itinerary_id
        ).order_by(Activity.order_index.desc()).first()

        order_index = (last_activity.order_index + 1) if last_activity else 1
        previous_location = (last_activity.place.latitude, last_activity.place.longitude) if last_activity else None

        activity = self._create_activity(
            itinerary=itinerary,
            place=place,
            start_time=start_time,
            duration_minutes=duration_minutes,
            order_index=order_index,
            previous_location=previous_location
        )
        activity.is_custom = 1
        activity.notes = notes

        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)

        return activity

    def remove_activity(self, activity_id: int, user_id: int) -> bool:
        """Remove an activity from an itinerary"""
        
        activity = self.db.query(Activity).join(Itinerary).join(Trip).filter(
            Activity.id == activity_id,
            Trip.user_id == user_id
        ).first()

        if not activity:
            return False

        self.db.delete(activity)
        self.db.commit()

        return True
