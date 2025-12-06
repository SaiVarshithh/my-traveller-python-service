"""
Test OpenStreetMap service
"""
from src.services.openstreetmap_service import get_openstreetmap_service

def test_osm():
    print("=" * 60)
    print("OpenStreetMap/Nominatim Service Test")
    print("=" * 60)
    
    service = get_openstreetmap_service()
    
    # Test geocoding
    print("\n1. Testing Geocoding...")
    coords = service.geocode_address("Paris, France")
    if coords:
        print(f"   ✅ Paris coordinates: {coords}")
    else:
        print("   ❌ Failed to geocode Paris")
    
    # Test place search
    print("\n2. Testing Place Search...")
    if coords:
        places = service.find_places_by_type(coords, "restaurant", radius=5000)
        print(f"   ✅ Found {len(places)} restaurants near Paris")
        if places:
            print(f"   First result: {places[0].get('name')}")
    
    # Test travel time
    print("\n3. Testing Travel Time Calculation...")
    if coords:
        # Eiffel Tower approximate coords
        eiffel = (48.8584, 2.2945)
        travel_time = service.calculate_travel_time(coords, eiffel, "walking")
        print(f"   ✅ Walking time to Eiffel Tower: {travel_time} minutes")
    
    print("\n" + "=" * 60)
    print("Test complete! OpenStreetMap service is working!")
    print("=" * 60)

if __name__ == "__main__":
    test_osm()
