import { gql } from '@apollo/client';
import { TRIP_WITH_ITINERARY_FRAGMENT, TRIP_FRAGMENT } from './queries';

export const REGISTER_MUTATION = gql`
  mutation Register($input: RegisterInput!) {
    register(input: $input) {
      token
      user {
        id
        email
        username
        fullName
      }
      message
    }
  }
`;

export const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      token
      user {
        id
        email
        username
        fullName
      }
      message
    }
  }
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

// ============================================================================
// TRIP MUTATIONS
// ============================================================================

export const CREATE_TRIP = gql`
  mutation CreateTrip($token: String!, $input: CreateTripInput!) {
    createTrip(token: $token, input: $input) {
      message
      trip {
        ...TripWithItineraryFields
      }
    }
  }
  ${TRIP_WITH_ITINERARY_FRAGMENT}
`;

export const UPDATE_TRIP = gql`
  mutation UpdateTrip($token: String!, $tripId: Int!, $input: UpdateTripInput!) {
    updateTrip(token: $token, tripId: $tripId, input: $input) {
      message
      trip {
        ...TripFields
      }
    }
  }
  ${TRIP_FRAGMENT}
`;

export const DELETE_TRIP = gql`
  mutation DeleteTrip($token: String!, $tripId: Int!) {
    deleteTrip(token: $token, tripId: $tripId) {
      success
      message
    }
  }
`;

export const REGENERATE_ITINERARY = gql`
  mutation RegenerateItinerary($token: String!, $tripId: Int!) {
    regenerateItinerary(token: $token, tripId: $tripId) {
      message
      trip {
        ...TripWithItineraryFields
      }
    }
  }
  ${TRIP_WITH_ITINERARY_FRAGMENT}
`;

export const ADD_ACTIVITY = gql`
  mutation AddActivity($token: String!, $itineraryId: Int!, $input: AddActivityInput!) {
    addActivity(token: $token, itineraryId: $itineraryId, input: $input) {
      message
      trip {
        ...TripWithItineraryFields
      }
    }
  }
  ${TRIP_WITH_ITINERARY_FRAGMENT}
`;

export const REMOVE_ACTIVITY = gql`
  mutation RemoveActivity($token: String!, $activityId: Int!) {
    removeActivity(token: $token, activityId: $activityId) {
      success
      message
    }
  }
`;
