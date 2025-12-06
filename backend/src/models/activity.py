from sqlalchemy import Column, Integer, String, Time, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.db_config import Base
import enum


class TransportMode(enum.Enum):
    WALK = "walk"
    DRIVE = "drive"
    TRANSIT = "transit"
    BIKE = "bike"
    TAXI = "taxi"
    NONE = "none"  # For first activity or staying at same location


class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False, index=True)
    place_id = Column(Integer, ForeignKey("places.id"), nullable=False)
    start_time = Column(Time, nullable=False)
    duration_minutes = Column(Integer, nullable=False)  # Expected duration at the place
    transport_mode = Column(SQLEnum(TransportMode), default=TransportMode.WALK)
    transport_duration_minutes = Column(Integer, default=0)  # Time to get here from previous activity
    order_index = Column(Integer, nullable=False)  # Order within the day
    notes = Column(String(500))
    is_custom = Column(Integer, default=0)  # 1 if user added manually, 0 if auto-generated
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    itinerary = relationship("Itinerary", back_populates="activities")
    place = relationship("Place")

    def __repr__(self):
        return f"<Activity(id={self.id}, place_id={self.place_id}, time={self.start_time})>"
