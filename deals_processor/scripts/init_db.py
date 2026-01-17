"""Database initialization script for seeding default roles.

This script initializes the database with default roles required
for the application. It's safe to run multiple times (idempotent).
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from deals_processor.core.config import get_settings
from deals_processor.core.database import get_database_instance, get_db_session
from deals_processor.models.user import RoleModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_default_roles(db: Session) -> None:
    """Seed default roles into the database.

    Creates three default roles:
    - Admin: Full access (level 100)
    - Analyst: Deal creation and editing (level 50)
    - Partner: Deal approval and decline (level 10)

    Args:
        db: Database session.
    """
    default_roles = [
        {
            "name": "admin",
            "description": "Administrator with full access",
            "level": 100,
        },
        {
            "name": "analyst",
            "description": "Analyst who can create and edit deals",
            "level": 50,
        },
        {
            "name": "partner",
            "description": "Partner who can approve/decline deals",
            "level": 10,
        },
    ]

    for role_data in default_roles:
        # Check if role already exists
        existing_role = (
            db.query(RoleModel).filter(RoleModel.name == role_data["name"]).first()
        )

        if existing_role:
            logger.info(f"Role '{role_data['name']}' already exists, skipping")
            continue

        # Create new role
        role = RoleModel(
            name=role_data["name"],
            description=role_data["description"],
            level=role_data["level"],
            is_active=True,
        )

        try:
            db.add(role)
            db.commit()
            logger.info(
                f"Created role: {role_data['name']} "
                f"(level: {role_data['level']})"
            )
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create role '{role_data['name']}': {e}")
            raise


def main() -> None:
    """Main entry point for database initialization."""
    try:
        logger.info("Starting database initialization...")

        # Get database instance and initialize
        db_instance = get_database_instance()
        db_instance.init_db()
        logger.info("Database tables created")

        # Seed default roles
        db = db_instance.get_session()
        try:
            seed_default_roles(db)
            logger.info("Default roles seeded successfully")
        finally:
            db.close()

        logger.info("Database initialization complete")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
