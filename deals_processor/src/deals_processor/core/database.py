"""Database configuration and management using OOP principles."""

import logging
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, declarative_base, sessionmaker

logger = logging.getLogger(__name__)

# Declarative base for all models
Base = declarative_base()


class DatabaseConfig:
    """Database configuration manager.
    
    Manages SQLite database connection, session creation, and initialization.
    Follows Single Responsibility Principle.
    """

    def __init__(self, database_url: str = "sqlite:///./deals_processor.db") -> None:
        """Initialize database configuration.
        
        Args:
            database_url: SQLite database URL. Defaults to local file.
        """
        self.database_url = database_url
        self.engine = self._create_engine()
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        logger.info(f"Database initialized: {database_url}")

    def _create_engine(self):
        """Create SQLAlchemy engine with SQLite-specific configuration.
        
        Returns:
            Engine: SQLAlchemy engine instance.
        """
        engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False},
            echo=False,
        )
        
        # Enable foreign key support for SQLite
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            """Enable foreign key constraints in SQLite."""
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        return engine

    def get_session(self) -> Session:
        """Create a new database session.
        
        Returns:
            Session: SQLAlchemy session instance.
        """
        return self.session_factory()

    def get_session_generator(self) -> Generator[Session, None, None]:
        """Provide session as dependency injection generator.
        
        Yields:
            Session: SQLAlchemy session instance.
        """
        db = self.get_session()
        try:
            yield db
        finally:
            db.close()

    def init_db(self) -> None:
        """Initialize all database tables.
        
        Creates tables for all models. Should be called on application startup.
        """
        logger.info("Initializing database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def drop_db(self) -> None:
        """Drop all database tables.
        
        WARNING: This is destructive and should only be used for testing.
        """
        logger.warning("Dropping all database tables!")
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")

    def close(self) -> None:
        """Close database connection and cleanup resources."""
        self.engine.dispose()
        logger.info("Database connection closed")


# Global database instance
_db_instance: DatabaseConfig | None = None


def get_database_instance() -> DatabaseConfig:
    """Get or create the global database instance.
    
    Implements singleton pattern for database management.
    
    Returns:
        DatabaseConfig: Global database configuration instance.
    """
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConfig()
    return _db_instance


def get_db_session() -> Generator[Session, None, None]:
    """Dependency injection function for FastAPI to provide database sessions.
    
    Yields:
        Session: SQLAlchemy session for use in route handlers.
    """
    db_config = get_database_instance()
    yield from db_config.get_session_generator()
