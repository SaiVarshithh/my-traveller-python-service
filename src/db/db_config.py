import urllib.parse
import yoyo
from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.schema import CreateSchema
from sqlalchemy.ext.declarative import declarative_base
from src.configs.app_config import AppConfig

# Global variables
engine: Engine = None
thread_safe_session_factory: scoped_session = None
Base = declarative_base()


def init_db(app_config: AppConfig, logger=None, create_schema_only=True, run_migrations=True):
    """Initialize database connection and create schema"""
    print("Initializing DB Connection")
    full_db_connection_string = get_db_connection_string(app_config)
    init_engine(full_db_connection_string, app_config.db_schema, pool_pre_ping=True)
    init_session_factory()

    if create_schema_only:
        create_schema(app_config, logger)

    if run_migrations:
        yoyo_db_connection_string = get_db_connection_string(app_config, for_yoyo=True)
        apply_db_migrations(yoyo_db_connection_string, app_config, logger)

    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete")


def get_db_connection_string(app_config: AppConfig, for_yoyo: bool = False):
    """Generate database connection string"""
    scheme = "postgresql" if for_yoyo else "postgresql+psycopg2"

    # Remove duplicate scheme if present
    db_url = app_config.db_url
    for prefix in ["postgresql+psycopg2://", "postgresql://"]:
        if db_url.startswith(prefix):
            db_url = db_url[len(prefix):]

    return (
        f"{scheme}://"
        f"{urllib.parse.quote_plus(app_config.db_username)}:"
        f"{urllib.parse.quote_plus(app_config.db_password)}@"
        f"{db_url}"
    )


def init_engine(uri, db_schema, **kwargs):
    """Initialize SQLAlchemy engine"""
    global engine
    if engine is None:
        engine = create_engine(uri, **kwargs).execution_options(
            schema_translate_map={None: db_schema}
        )
    return engine


def init_session_factory():
    """Initialize session factory"""
    global engine, thread_safe_session_factory
    if engine is None:
        raise ValueError("Initialize engine by calling init_engine first")

    if thread_safe_session_factory is None:
        thread_safe_session_factory = scoped_session(
            sessionmaker(bind=engine, expire_on_commit=False)
        )
    return thread_safe_session_factory


def create_schema(app_config: AppConfig, logger):
    """Create database schema if it doesn't exist"""
    global engine
    if engine is None:
        raise ValueError("Initialize engine first")

    if not inspect(engine).has_schema(app_config.db_schema):
        try:
            print(f"Creating schema {app_config.db_schema}")
            with engine.begin() as connection:
                connection.execute(CreateSchema(app_config.db_schema))
        except Exception as e:
            print(f"Error creating schema '{app_config.db_schema}': {e}")
    else:
        print(f'Schema {app_config.db_schema} exists.')


def apply_db_migrations(full_db_connection_string, app_config: AppConfig, logger):
    """Apply database migrations using yoyo"""
    print("Running DB Migrations")

    try:
        backend = yoyo.get_backend(full_db_connection_string)
        backend.schema = app_config.db_schema  # Set schema for yoyo

        migrations = yoyo.read_migrations('./migrations')

        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

        print("Migrations applied successfully")
    except Exception as e:
        print(f"Error applying migrations: {e}")
        if logger:
            logger.error(f"Migration error: {e}")


def get_db() -> Session:
    """Dependency for getting database session"""
    global thread_safe_session_factory
    if thread_safe_session_factory is None:
        raise ValueError("Session factory not initialized")

    db = thread_safe_session_factory()
    try:
        yield db
    finally:
        db.close()