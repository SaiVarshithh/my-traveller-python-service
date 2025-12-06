import strawberry
from typing import Optional, List
from datetime import timedelta, date, time
from enum import Enum
from src.models.user import User
from src.models.trip import Trip, TripStatus, BudgetLevel
from src.models.place import PlaceCategory
from src.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token
)
from src.services.trip_service import TripService
from src.services.itinerary_service import ItineraryService
from src.services.place_service import PlaceService
from src.utils.auth_utils import require_auth
from src.configs.app_config import get_app_config
from src.db.db_config import thread_safe_session_factory


def get_db_session():
    """Get database session with proper error handling"""
    if thread_safe_session_factory is None:
        raise ValueError("Database not initialized. Call init_db() first.")
    return thread_safe_session_factory()


# ============================================================================
# ENUMS
# ============================================================================

@strawberry.enum
class TripStatusEnum(Enum):
    PLANNING = "planning"
    CONFIRMED = "confirmed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@strawberry.enum
class BudgetLevelEnum(Enum):
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"


@strawberry.enum
class TransportModeEnum(Enum):
    WALK = "walk"
    DRIVE = "drive"
    TRANSIT = "transit"
    BIKE = "bike"
    TAXI = "taxi"
    NONE = "none"


@strawberry.enum
class PlaceCategoryEnum(Enum):
    ATTRACTION = "attraction"
    RESTAURANT = "restaurant"
    HOTEL = "hotel"
    MUSEUM = "museum"
    PARK = "park"
    SHOPPING = "shopping"
    ENTERTAINMENT = "entertainment"
    HISTORICAL = "historical"
    RELIGIOUS = "religious"
    NIGHTLIFE = "nightlife"
    CAFE = "cafe"
    OTHER = "other"


# ============================================================================
# TYPES
# ============================================================================

@strawberry.type
class UserType:
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: str


@strawberry.type
class PlaceType:
    id: int
    google_place_id: str
    name: str
    address: Optional[str]
    latitude: float
    longitude: float
    category: PlaceCategoryEnum
    rating: Optional[float]
    price_level: Optional[int]
    phone_number: Optional[str]
    website: Optional[str]
    photo_reference: Optional[str]


@strawberry.type
class ActivityType:
    id: int
    place: PlaceType
    start_time: str
    duration_minutes: int
    transport_mode: TransportModeEnum
    transport_duration_minutes: int
    order_index: int
    notes: Optional[str]
    is_custom: bool


@strawberry.type
class ItineraryType:
    id: int
    day_number: int
    date: str
    theme: Optional[str]
    notes: Optional[str]
    activities: List[ActivityType]


@strawberry.type
class TripType:
    id: int
    destination: str
    start_date: str
    end_date: str
    status: TripStatusEnum
    budget_level: BudgetLevelEnum
    notes: Optional[str]
    created_at: str
    itineraries: List[ItineraryType]


@strawberry.type
class AuthPayload:
    token: str
    user: UserType
    message: str


@strawberry.type
class TripPayload:
    trip: TripType
    message: str


@strawberry.type
class DeletePayload:
    success: bool
    message: str


# ============================================================================
# INPUTS
# ============================================================================

@strawberry.input
class RegisterInput:
    email: str
    username: str
    password: str
    full_name: Optional[str] = None


@strawberry.input
class LoginInput:
    username: str
    password: str


@strawberry.input
class CreateTripInput:
    destination: str
    start_date: str  # ISO format: YYYY-MM-DD
    end_date: str    # ISO format: YYYY-MM-DD
    budget_level: Optional[BudgetLevelEnum] = BudgetLevelEnum.MODERATE
    notes: Optional[str] = None


@strawberry.input
class UpdateTripInput:
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget_level: Optional[BudgetLevelEnum] = None
    status: Optional[TripStatusEnum] = None
    notes: Optional[str] = None


@strawberry.input
class SearchPlacesInput:
    query: str
    location: Optional[str] = None
    category: Optional[PlaceCategoryEnum] = None
    radius: Optional[int] = 5000


@strawberry.input
class AddActivityInput:
    place_id: int
    start_time: str  # HH:MM format
    duration_minutes: int
    notes: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def trip_to_graphql(trip: Trip) -> TripType:
    """Convert Trip model to GraphQL TripType"""
    return TripType(
        id=trip.id,
        destination=trip.destination,
        start_date=str(trip.start_date),
        end_date=str(trip.end_date),
        status=TripStatusEnum[trip.status.name],
        budget_level=BudgetLevelEnum[trip.budget_level.name],
        notes=trip.notes,
        created_at=str(trip.created_at),
        itineraries=[
            ItineraryType(
                id=itin.id,
                day_number=itin.day_number,
                date=str(itin.date),
                theme=itin.theme,
                notes=itin.notes,
                activities=[
                    ActivityType(
                        id=act.id,
                        place=PlaceType(
                            id=act.place.id,
                            google_place_id=act.place.google_place_id,
                            name=act.place.name,
                            address=act.place.address,
                            latitude=act.place.latitude,
                            longitude=act.place.longitude,
                            category=PlaceCategoryEnum[act.place.category.name],
                            rating=act.place.rating,
                            price_level=act.place.price_level,
                            phone_number=act.place.phone_number,
                            website=act.place.website,
                            photo_reference=act.place.photo_reference
                        ),
                        start_time=str(act.start_time),
                        duration_minutes=act.duration_minutes,
                        transport_mode=TransportModeEnum[act.transport_mode.name],
                        transport_duration_minutes=act.transport_duration_minutes,
                        order_index=act.order_index,
                        notes=act.notes,
                        is_custom=bool(act.is_custom)
                    )
                    for act in itin.activities
                ]
            )
            for itin in trip.itineraries
        ]
    )


def place_to_graphql(place) -> PlaceType:
    """Convert Place model to GraphQL PlaceType"""
    return PlaceType(
        id=place.id,
        google_place_id=place.google_place_id,
        name=place.name,
        address=place.address,
        latitude=place.latitude,
        longitude=place.longitude,
        category=PlaceCategoryEnum[place.category.name],
        rating=place.rating,
        price_level=place.price_level,
        phone_number=place.phone_number,
        website=place.website,
        photo_reference=place.photo_reference
    )


# ============================================================================
# QUERIES
# ============================================================================

@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        """Health check endpoint"""
        return "🌍 MyTraveller GraphQL API is running!"

    @strawberry.field
    def me(self, token: str) -> Optional[UserType]:
        """Get current user from token"""
        payload = verify_token(token)
        if not payload:
            return None

        db = get_db_session()
        try:
            username = payload.get("sub")
            user = db.query(User).filter(User.username == username).first()

            if user:
                return UserType(
                    id=user.id,
                    email=user.email,
                    username=user.username,
                    full_name=user.full_name,
                    created_at=str(user.created_at)
                )
            return None
        finally:
            db.close()

    @strawberry.field
    def my_trips(self, token: str) -> List[TripType]:
        """Get all trips for the authenticated user"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            trip_service = TripService(db)
            trips = trip_service.get_user_trips(user.id)
            return [trip_to_graphql(trip) for trip in trips]
        finally:
            db.close()

    @strawberry.field
    def trip(self, token: str, trip_id: int) -> Optional[TripType]:
        """Get a specific trip with full itinerary"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            trip_service = TripService(db)
            trip = trip_service.get_trip(trip_id, user.id)
            if trip:
                return trip_to_graphql(trip)
            return None
        finally:
            db.close()

    @strawberry.field
    def search_places(self, input: SearchPlacesInput) -> List[PlaceType]:
        """Search for places using Google Maps"""
        db = get_db_session()
        try:
            place_service = PlaceService(db)
            category = PlaceCategory[input.category.name] if input.category else None
            places = place_service.search_places(
                query=input.query,
                location=input.location,
                category=category,
                radius=input.radius
            )
            return [place_to_graphql(place) for place in places]
        finally:
            db.close()

    @strawberry.field
    def place_details(self, place_id: int) -> Optional[PlaceType]:
        """Get details of a specific place"""
        db = get_db_session()
        try:
            from src.models.place import Place
            place = db.query(Place).filter(Place.id == place_id).first()
            if place:
                return place_to_graphql(place)
            return None
        finally:
            db.close()


# ============================================================================
# MUTATIONS
# ============================================================================

@strawberry.type
class Mutation:
    @strawberry.mutation
    def register(self, input: RegisterInput) -> AuthPayload:
        """Register a new user"""
        db = get_db_session()

        try:
            # Validate input
            if len(input.password) < 6:
                raise Exception("Password must be at least 6 characters long")

            if len(input.username) < 3:
                raise Exception("Username must be at least 3 characters long")

            # Check if user exists
            existing_user = db.query(User).filter(
                (User.email == input.email) | (User.username == input.username)
            ).first()

            if existing_user:
                if existing_user.email == input.email:
                    raise Exception("Email already registered")
                if existing_user.username == input.username:
                    raise Exception("Username already taken")

            # Create new user
            hashed_password = get_password_hash(input.password)
            new_user = User(
                email=input.email,
                username=input.username,
                hashed_password=hashed_password,
                full_name=input.full_name
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            # Create token
            app_config = get_app_config()
            access_token_expires = timedelta(minutes=app_config.access_token_expire_min)
            access_token = create_access_token(
                data={"sub": new_user.username},
                expires_delta=access_token_expires
            )

            user_type = UserType(
                id=new_user.id,
                email=new_user.email,
                username=new_user.username,
                full_name=new_user.full_name,
                created_at=str(new_user.created_at)
            )

            return AuthPayload(
                token=access_token,
                user=user_type,
                message="Welcome to MyTraveller! Registration successful 🎉"
            )

        except Exception as e:
            db.rollback()
            raise Exception(str(e))
        finally:
            db.close()

    @strawberry.mutation
    def login(self, input: LoginInput) -> AuthPayload:
        """Login user"""
        db = get_db_session()

        try:
            # Find user
            user = db.query(User).filter(User.username == input.username).first()

            if not user:
                raise Exception("Invalid username or password")

            if not verify_password(input.password, user.hashed_password):
                raise Exception("Invalid username or password")

            # Create token
            app_config = get_app_config()
            access_token_expires = timedelta(minutes=app_config.access_token_expire_min)
            access_token = create_access_token(
                data={"sub": user.username},
                expires_delta=access_token_expires
            )

            user_type = UserType(
                id=user.id,
                email=user.email,
                username=user.username,
                full_name=user.full_name,
                created_at=str(user.created_at)
            )

            return AuthPayload(
                token=access_token,
                user=user_type,
                message=f"Welcome back, {user.username}! 🌍"
            )

        except Exception as e:
            raise Exception(str(e))
        finally:
            db.close()

    @strawberry.mutation
    def create_trip(self, token: str, input: CreateTripInput) -> TripPayload:
        """Create a new trip and generate itinerary"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            
            # Parse dates
            start_date = date.fromisoformat(input.start_date)
            end_date = date.fromisoformat(input.end_date)
            
            # Create trip
            trip_service = TripService(db)
            budget_level = BudgetLevel[input.budget_level.name] if input.budget_level else BudgetLevel.MODERATE
            trip = trip_service.create_trip(
                user_id=user.id,
                destination=input.destination,
                start_date=start_date,
                end_date=end_date,
                budget_level=budget_level,
                notes=input.notes
            )
            
            # Generate itinerary
            itinerary_service = ItineraryService(db)
            itinerary_service.generate_itinerary(trip)
            
            # Refresh to get itineraries
            db.refresh(trip)
            
            return TripPayload(
                trip=trip_to_graphql(trip),
                message=f"🎉 Trip to {trip.destination} created with {len(trip.itineraries)} days planned!"
            )
        except Exception as e:
            db.rollback()
            raise Exception(str(e))
        finally:
            db.close()

    @strawberry.mutation
    def update_trip(self, token: str, trip_id: int, input: UpdateTripInput) -> TripPayload:
        """Update an existing trip"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            trip_service = TripService(db)
            
            # Parse optional dates
            start_date = date.fromisoformat(input.start_date) if input.start_date else None
            end_date = date.fromisoformat(input.end_date) if input.end_date else None
            budget_level = BudgetLevel[input.budget_level.name] if input.budget_level else None
            status = TripStatus[input.status.name] if input.status else None
            
            trip = trip_service.update_trip(
                trip_id=trip_id,
                user_id=user.id,
                destination=input.destination,
                start_date=start_date,
                end_date=end_date,
                budget_level=budget_level,
                status=status,
                notes=input.notes
            )
            
            if not trip:
                raise Exception("Trip not found or unauthorized")
            
            return TripPayload(
                trip=trip_to_graphql(trip),
                message="Trip updated successfully!"
            )
        except Exception as e:
            db.rollback()
            raise Exception(str(e))
        finally:
            db.close()

    @strawberry.mutation
    def delete_trip(self, token: str, trip_id: int) -> DeletePayload:
        """Delete a trip"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            trip_service = TripService(db)
            success = trip_service.delete_trip(trip_id, user.id)
            
            if success:
                return DeletePayload(
                    success=True,
                    message="Trip deleted successfully"
                )
            else:
                return DeletePayload(
                    success=False,
                    message="Trip not found or unauthorized"
                )
        except Exception as e:
            db.rollback()
            raise Exception(str(e))
        finally:
            db.close()

    @strawberry.mutation
    def regenerate_itinerary(self, token: str, trip_id: int) -> TripPayload:
        """Regenerate itinerary for an existing trip"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            trip_service = TripService(db)
            trip = trip_service.get_trip(trip_id, user.id)
            
            if not trip:
                raise Exception("Trip not found or unauthorized")
            
            itinerary_service = ItineraryService(db)
            itinerary_service.generate_itinerary(trip)
            
            db.refresh(trip)
            
            return TripPayload(
                trip=trip_to_graphql(trip),
                message="Itinerary regenerated successfully!"
            )
        except Exception as e:
            db.rollback()
            raise Exception(str(e))
        finally:
            db.close()

    @strawberry.mutation
    def add_activity(self, token: str, itinerary_id: int, input: AddActivityInput) -> TripPayload:
        """Add a custom activity to an itinerary"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            
            # Parse time
            time_parts = input.start_time.split(":")
            start_time = time(int(time_parts[0]), int(time_parts[1]))
            
            itinerary_service = ItineraryService(db)
            activity = itinerary_service.add_custom_activity(
                itinerary_id=itinerary_id,
                place_id=input.place_id,
                start_time=start_time,
                duration_minutes=input.duration_minutes,
                notes=input.notes
            )
            
            # Get the trip to return
            from src.models.itinerary import Itinerary
            itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
            trip = itinerary.trip
            
            # Verify user owns this trip
            if trip.user_id != user.id:
                raise Exception("Unauthorized")
            
            db.refresh(trip)
            
            return TripPayload(
                trip=trip_to_graphql(trip),
                message="Activity added successfully!"
            )
        except Exception as e:
            db.rollback()
            raise Exception(str(e))
        finally:
            db.close()

    @strawberry.mutation
    def remove_activity(self, token: str, activity_id: int) -> DeletePayload:
        """Remove an activity from an itinerary"""
        db = get_db_session()
        try:
            user = require_auth(token, db)
            itinerary_service = ItineraryService(db)
            success = itinerary_service.remove_activity(activity_id, user.id)
            
            if success:
                return DeletePayload(
                    success=True,
                    message="Activity removed successfully"
                )
            else:
                return DeletePayload(
                    success=False,
                    message="Activity not found or unauthorized"
                )
        except Exception as e:
            db.rollback()
            raise Exception(str(e))
        finally:
            db.close()


schema = strawberry.Schema(query=Query, mutation=Mutation)