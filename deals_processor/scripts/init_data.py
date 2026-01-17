"""Initialize default data for the application on startup."""

import logging
from sqlalchemy.orm import Session

from deals_processor.models.user import UserModel
from deals_processor.core.auth import PasswordHasher
from deals_processor.core.config import get_settings

logger = logging.getLogger(__name__)


def init_default_admin(db: Session) -> None:
    """Create default admin user if it doesn't exist.
    
    Creates a default admin user with email 'admin@default.com' and password 'admin123'
    This allows initial access to the application for setup.
    
    Args:
        db: Database session.
    """
    try:
        # Check if default admin already exists
        existing_admin = db.query(UserModel).filter(
            UserModel.email == "admin@default.com"
        ).first()
        
        if existing_admin:
            logger.info("Default admin user already exists")
            return
        
        # Create default admin user
        settings = get_settings()
        password_hasher = PasswordHasher(rounds=settings.bcrypt_rounds)
        hashed_password = password_hasher.hash_password("admin123")
        
        default_admin = UserModel(
            email="admin@default.com",
            full_name="Default Admin",
            password_hash=hashed_password,
            role="admin",
            is_active=True,
        )
        
        db.add(default_admin)
        db.commit()
        db.refresh(default_admin)
        
        logger.info(
            f"Default admin user created successfully\n"
            f"Email: admin@default.com\n"
            f"Password: admin123\n"
            f"⚠️  IMPORTANT: Change this password immediately after first login!"
        )
        
    except Exception as e:
        logger.error(f"Failed to initialize default admin user: {e}")
        db.rollback()
        raise
