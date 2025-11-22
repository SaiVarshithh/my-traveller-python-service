import strawberry
from typing import Optional
from datetime import timedelta
from src.models.user import User
from src.services.auth_service import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token
)
from src.configs.app_config import get_app_config
from src.db.db_config import thread_safe_session_factory


def get_db_session():
    """Get database session with proper error handling"""
    if thread_safe_session_factory is None:
        raise ValueError("Database not initialized. Call init_db() first.")
    return thread_safe_session_factory()


@strawberry.type
class UserType:
    id: int
    email: str
    username: str
    full_name: Optional[str]
    created_at: str


@strawberry.type
class AuthPayload:
    token: str
    user: UserType
    message: str


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


schema = strawberry.Schema(query=Query, mutation=Mutation)