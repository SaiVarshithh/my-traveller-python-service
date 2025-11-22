from src.db.db_config import thread_safe_session_factory


def get_db_session():
    """Get database session"""
    global thread_safe_session_factory

    if thread_safe_session_factory is None:
        # Import here to avoid circular imports
        from src.db.db_config import init_session_factory
        init_session_factory()

    db = thread_safe_session_factory()
    try:
        return db
    except Exception as e:
        print(f"Error getting database session: {e}")
        raise