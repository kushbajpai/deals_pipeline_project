"""Script to create and manage admin users in the database."""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from deals_processor.core.database import get_database_instance
from deals_processor.core.auth import PasswordHasher
from deals_processor.models.user import UserModel, RoleModel


def create_admin_user(email: str, password: str, full_name: str = "") -> None:
    """Create an admin user in the database.
    
    Args:
        email: User email address.
        password: Plain text password (will be hashed).
        full_name: User's full name.
    """
    db_instance = get_database_instance()
    db_instance.init_db()
    
    session = next(db_instance.get_session_generator())
    
    try:
        # Check if user already exists
        existing = session.query(UserModel).filter(UserModel.email == email).first()
        if existing:
            print(f"⚠️  User {email} already exists")
            return
        
        # Get admin role
        admin_role = session.query(RoleModel).filter(
            RoleModel.name == "ADMIN"
        ).first()
        
        if not admin_role:
            print("❌ Admin role not found in database")
            return
        
        # Hash password
        hasher = PasswordHasher(rounds=12)
        hashed_password = hasher.hash_password(password)
        
        # Create admin user
        admin_user = UserModel(
            email=email,
            password_hash=hashed_password,
            full_name=full_name,
            role_id=admin_role.id,
            is_active=True,
            email_verified=True,
        )
        
        session.add(admin_user)
        session.commit()
        
        print(f"✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Name: {full_name or '(not set)'}")
        print(f"\n   Login with:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error creating admin user: {e}")
    finally:
        session.close()


def list_admins() -> None:
    """List all admin users in the database."""
    db_instance = get_database_instance()
    db_instance.init_db()
    
    session = next(db_instance.get_session_generator())
    
    try:
        # Get admin role
        admin_role = session.query(RoleModel).filter(
            RoleModel.name == "ADMIN"
        ).first()
        
        if not admin_role:
            print("❌ Admin role not found in database")
            return
        
        # Get all admin users
        admins = session.query(UserModel).filter(
            UserModel.role_id == admin_role.id
        ).all()
        
        if not admins:
            print("ℹ️  No admin users found")
            return
        
        print(f"\n📋 Admin Users ({len(admins)} total)\n")
        for admin in admins:
            status = "✓ Active" if admin.is_active else "✗ Inactive"
            print(f"  • {admin.email}")
            print(f"    Name: {admin.full_name or 'N/A'}")
            print(f"    Status: {status}\n")
        
    except Exception as e:
        print(f"❌ Error listing admins: {e}")
    finally:
        session.close()


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manage admin users in the Deal Pipeline application"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create subcommand
    create_parser = subparsers.add_parser("create", help="Create a new admin user")
    create_parser.add_argument("email", help="Admin email address")
    create_parser.add_argument("password", help="Admin password")
    create_parser.add_argument("--name", default="", help="Admin full name")
    
    # List subcommand
    subparsers.add_parser("list", help="List all admin users")
    
    args = parser.parse_args()
    
    if args.command == "create":
        print("🔐 Creating Admin User\n")
        create_admin_user(args.email, args.password, args.name)
    elif args.command == "list":
        list_admins()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
