from sqlalchemy import Column, Integer, String, DateTime, Date, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.db_config import Base
import enum


class TripStatus(enum.Enum):
    PLANNING = "planning"
    CONFIRMED = "confirmed"
    ONGOING = "ongoing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class BudgetLevel(enum.Enum):
    BUDGET = "budget"
    MODERATE = "moderate"
    LUXURY = "luxury"


class Trip(Base):
    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    destination = Column(String(255), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(SQLEnum(TripStatus), default=TripStatus.PLANNING, nullable=False)
    budget_level = Column(SQLEnum(BudgetLevel), default=BudgetLevel.MODERATE)
    notes = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", backref="trips")
    itineraries = relationship("Itinerary", back_populates="trip", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Trip(id={self.id}, destination='{self.destination}', user_id={self.user_id})>"
