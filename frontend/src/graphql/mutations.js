import { gql } from '@apollo/client';

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