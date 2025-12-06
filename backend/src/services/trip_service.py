"""
Trip Service - Manages trip CRUD operations
"""
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session
from src.models.trip import Trip, TripStatus, BudgetLevel
from src.models.user import User
from logging import getLogger

logger = getLogger(__name__)


class TripService:
    """Service for managing trips"""

    def __init__(self, db: Session):
        self.db = db

    def create_trip(
        self,
        user_id: int,
        destination: str,
        start_date: date,
        end_date: date,
        budget_level: BudgetLevel = BudgetLevel.MODERATE,
        notes: Optional[str] = None
    ) -> Trip:
        """
        Create a new trip
        
        Args:
            user_id: ID of the user creating the trip
            destination: Destination name
            start_date: Trip start date
            end_date: Trip end date
            budget_level: Budget preference
            notes: Optional notes
        
        Returns:
            Created Trip object
        """
        # Validate dates
        if end_date < start_date:
            raise ValueError("End date must be after start date")

        trip = Trip(
            user_id=user_id,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget_level=budget_level,
            notes=notes,
            status=TripStatus.PLANNING
        )

        self.db.add(trip)
        self.db.commit()
        self.db.refresh(trip)

        return trip

    def get_trip(self, trip_id: int, user_id: int) -> Optional[Trip]:
        """
        Get a trip by ID with authorization check
        
        Args:
            trip_id: Trip ID
            user_id: User ID for authorization
        
        Returns:
            Trip object or None if not found or unauthorized
        """
        trip = self.db.query(Trip).filter(
            Trip.id == trip_id,
            Trip.user_id == user_id
        ).first()

        return trip

    def get_user_trips(self, user_id: int) -> List[Trip]:
        """
        Get all trips for a user
        
        Args:
            user_id: User ID
        
        Returns:
            List of Trip objects
        """
        trips = self.db.query(Trip).filter(
            Trip.user_id == user_id
        ).order_by(Trip.start_date.desc()).all()

        return trips

    def update_trip(
        self,
        trip_id: int,
        user_id: int,
        destination: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        budget_level: Optional[BudgetLevel] = None,
        status: Optional[TripStatus] = None,
        notes: Optional[str] = None
    ) -> Optional[Trip]:
        """
        Update a trip
        
        Args:
            trip_id: Trip ID
            user_id: User ID for authorization
            destination: Optional new destination
            start_date: Optional new start date
            end_date: Optional new end date
            budget_level: Optional new budget level
            status: Optional new status
            notes: Optional new notes
        
        Returns:
            Updated Trip object or None if not found/unauthorized
        """
        trip = self.get_trip(trip_id, user_id)
        if not trip:
            return None

        if destination is not None:
            trip.destination = destination
        if start_date is not None:
            trip.start_date = start_date
        if end_date is not None:
            trip.end_date = end_date
        if budget_level is not None:
            trip.budget_level = budget_level
        if status is not None:
            trip.status = status
        if notes is not None:
            trip.notes = notes

        # Validate dates
        if trip.end_date < trip.start_date:
            raise ValueError("End date must be after start date")

        self.db.commit()
        self.db.refresh(trip)

        return trip

    def delete_trip(self, trip_id: int, user_id: int) -> bool:
        """
        Delete a trip
        
        Args:
            trip_id: Trip ID
            user_id: User ID for authorization
        
        Returns:
            True if deleted, False if not found/unauthorized
        """
        trip = self.get_trip(trip_id, user_id)
        if not trip:
            return False

        self.db.delete(trip)
        self.db.commit()

        return True
