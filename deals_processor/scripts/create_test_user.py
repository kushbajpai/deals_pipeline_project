#!/usr/bin/env python
"""Create test user for development."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deals_processor.core.database import get_database_instance
from deals_processor.core.security import hash_password
from deals_processor.models.user import UserModel, RoleModel

def create_test_user():
    """Create a test user in the database."""
    db_instance = get_database_instance()
    engine = db_instance.engine
    
    with db_instance.SessionLocal() as db:
        # Check if user exists
        existing = db.query(UserModel).filter_by(email="testuser@example.com").first()
        if existing:
            print(f"User {existing.email} already exists")
            return
        
        # Get or create role
        analyst_role = db.query(RoleModel).filter_by(name="analyst").first()
        if not analyst_role:
            print("Role 'analyst' not found. Please run init_db.py first.")
            return
        
        # Create user
        user = UserModel(
            email="testuser@example.com",
            username="testuser",
            password_hash=hash_password("SecurePassword123!"),
            full_name="Test User",
            role_id=analyst_role.id,
            is_active=True,
            email_verified=True,
        )
        
        db.add(user)
        db.commit()
        
        print(f"✓ Test user created: {user.email}")
        print(f"  Username: testuser")
        print(f"  Password: SecurePassword123!")
        print(f"  Role: analyst")

if __name__ == "__main__":
    create_test_user()
