import { gql } from '@apollo/client';

// ============================================================================
// FRAGMENTS
// ============================================================================

export const PLACE_FRAGMENT = gql`
  fragment PlaceFields on PlaceType {
    id
    googlePlaceId
    name
    address
    latitude
    longitude
    category
    rating
    priceLevel
    phoneNumber
    website
    photoReference
  }
`;

export const ACTIVITY_FRAGMENT = gql`
  fragment ActivityFields on ActivityType {
    id
    place {
      ...PlaceFields
    }
    startTime
    durationMinutes
    transportMode
    transportDurationMinutes
    orderIndex
    notes
    isCustom
  }
  ${PLACE_FRAGMENT}
`;

export const ITINERARY_FRAGMENT = gql`
  fragment ItineraryFields on ItineraryType {
    id
    dayNumber
    date
    theme
    notes
    activities {
      ...ActivityFields
    }
  }
  ${ACTIVITY_FRAGMENT}
`;

export const TRIP_FRAGMENT = gql`
  fragment TripFields on TripType {
    id
    destination
    startDate
    endDate
    status
    budgetLevel
    notes
    createdAt
  }
`;

export const TRIP_WITH_ITINERARY_FRAGMENT = gql`
  fragment TripWithItineraryFields on TripType {
    ...TripFields
    itineraries {
      ...ItineraryFields
    }
  }
  ${TRIP_FRAGMENT}
  ${ITINERARY_FRAGMENT}
`;

// ============================================================================
// QUERIES
// ============================================================================

export const GET_MY_TRIPS = gql`
  query GetMyTrips($token: String!) {
    myTrips(token: $token) {
      ...TripFields
    }
  }
  ${TRIP_FRAGMENT}
`;

export const GET_TRIP = gql`
  query GetTrip($token: String!, $tripId: Int!) {
    trip(token: $token, tripId: $tripId) {
      ...TripWithItineraryFields
    }
  }
  ${TRIP_WITH_ITINERARY_FRAGMENT}
`;

export const SEARCH_PLACES = gql`
  query SearchPlaces($input: SearchPlacesInput!) {
    searchPlaces(input: $input) {
      ...PlaceFields
    }
  }
  ${PLACE_FRAGMENT}
`;

export const GET_PLACE_DETAILS = gql`
  query GetPlaceDetails($placeId: Int!) {
    placeDetails(placeId: $placeId) {
      ...PlaceFields
    }
  }
  ${PLACE_FRAGMENT}
`;

export const ME_QUERY = gql`
  query Me($token: String!) {
    me(token: $token) {
      id
      email
      username
      fullName
      createdAt
    }
  }
`;
