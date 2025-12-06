from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from src.db.db_config import Base


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    day_number = Column(Integer, nullable=False)  # 1, 2, 3, etc.
    date = Column(Date, nullable=False)
    theme = Column(String(255))  # e.g., "Cultural Exploration", "Food Tour", etc.
    notes = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    trip = relationship("Trip", back_populates="itineraries")
    activities = relationship("Activity", back_populates="itinerary", cascade="all, delete-orphan", order_by="Activity.start_time")

    def __repr__(self):
        return f"<Itinerary(id={self.id}, trip_id={self.trip_id}, day={self.day_number})>"
