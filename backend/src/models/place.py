from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from src.db.db_config import Base
import enum


class PlaceCategory(enum.Enum):
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


class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    google_place_id = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(String(500))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    category = Column(SQLEnum(PlaceCategory), default=PlaceCategory.OTHER)
    rating = Column(Float)
    price_level = Column(Integer)  # 0-4 scale from Google
    phone_number = Column(String(50))
    website = Column(String(500))
    photo_reference = Column(String(500))  # Google Photos API reference
    opening_hours = Column(String(1000))  # JSON string of opening hours
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Place(id={self.id}, name='{self.name}', category='{self.category}')>"
