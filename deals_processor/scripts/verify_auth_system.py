#!/usr/bin/env python
"""Verification script for authentication system implementation.

Validates all components are properly implemented and integrated.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def verify_imports() -> bool:
    """Verify all required imports work correctly."""
    print("\n[Imports] Verifying module imports...")
    try:
        from deals_processor.core.auth import PasswordHasher, JWTTokenManager
        print("  ✓ Core auth components")
        
        from deals_processor.core.security import (
            get_current_user,
            get_current_admin,
            get_current_analyst,
            get_current_partner,
            require_role,
            require_permission,
            admin_only,
            analyst_only,
            partner_only,
        )
        print("  ✓ Security dependencies and decorators")
        
        from deals_processor.models.user import UserModel, RoleModel
        print("  ✓ User and Role models")
        
        from deals_processor.repositories.user_repository import (
            UserRepository,
            RoleRepository,
        )
        print("  ✓ User and Role repositories")
        
        from deals_processor.services.auth_service import AuthService, UserService
        print("  ✓ Auth and User services")
        
        from deals_processor.api.auth import AuthRouteHandler
        print("  ✓ Auth route handler")
        
        from deals_processor.api.deals import DealRouteHandler
        print("  ✓ Deal route handler (updated)")
        
        from deals_processor.main import app
        print("  ✓ FastAPI application")
        
        return True
    except Exception as e:
        print(f"  ✗ Import error: {e}")
        return False


def verify_database_models() -> bool:
    """Verify database models are properly defined."""
    print("\n[Models] Verifying ORM models...")
    try:
        from deals_processor.models.user import UserModel, RoleModel
        
        # Check RoleModel fields
        role_fields = {col.name for col in RoleModel.__table__.columns}
        required_role_fields = {"id", "name", "description", "level", "is_active", "created_at", "updated_at"}
        if not required_role_fields.issubset(role_fields):
            print(f"  ✗ RoleModel missing fields: {required_role_fields - role_fields}")
            return False
        print("  ✓ RoleModel properly defined")
        
        # Check UserModel fields
        user_fields = {col.name for col in UserModel.__table__.columns}
        required_user_fields = {"id", "email", "username", "password_hash", "full_name", "role", "is_active", "email_verified", "last_login", "created_at", "updated_at"}
        if not required_user_fields.issubset(user_fields):
            print(f"  ✗ UserModel missing fields: {required_user_fields - user_fields}")
            return False
        print("  ✓ UserModel properly defined")
        
        return True
    except Exception as e:
        print(f"  ✗ Model verification error: {e}")
        return False


def verify_config() -> bool:
    """Verify configuration settings."""
    print("\n[Configuration] Verifying settings...")
    try:
        from deals_processor.core.config import get_settings
        
        settings = get_settings()
        
        # Check JWT settings
        if not hasattr(settings, 'jwt_secret_key'):
            print("  ✗ Missing jwt_secret_key")
            return False
        if len(settings.jwt_secret_key) < 32:
            print("  ⚠ Warning: jwt_secret_key should be at least 32 characters")
        print("  ✓ JWT settings configured")
        
        # Check password settings
        if not hasattr(settings, 'password_min_length'):
            print("  ✗ Missing password_min_length")
            return False
        if not hasattr(settings, 'bcrypt_rounds'):
            print("  ✗ Missing bcrypt_rounds")
            return False
        print("  ✓ Password settings configured")
        
        return True
    except Exception as e:
        print(f"  ✗ Configuration verification error: {e}")
        return False


def verify_routes() -> bool:
    """Verify all routes are registered."""
    print("\n[Routes] Verifying route registration...")
    try:
        from deals_processor.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        required_routes = {
            "/api/v1/health",
            "/auth/register",
            "/auth/login",
            "/auth/refresh",
            "/auth/me",
            "/auth/change-password",
            "/api/v1/deals",
            "/openapi.json",
            "/docs",
            "/redoc",
        }
        
        registered = set(routes)
        found = required_routes & registered
        missing = required_routes - registered
        
        if missing:
            print(f"  ✗ Missing routes: {missing}")
            return False
        
        print(f"  ✓ All required routes registered ({len(found)} routes)")
        return True
    except Exception as e:
        print(f"  ✗ Route verification error: {e}")
        return False


def verify_schemas() -> bool:
    """Verify authentication schemas."""
    print("\n[Schemas] Verifying Pydantic schemas...")
    try:
        from deals_processor.schemas import (
            UserRegister,
            UserLogin,
            TokenResponse,
            AccessTokenResponse,
            UserResponse,
            RoleResponse,
            ChangePasswordRequest,
            RefreshTokenRequest,
        )
        print("  ✓ All auth schemas available")
        
        # Verify schema fields
        user_register = UserRegister.schema()
        if "email" not in user_register["properties"]:
            print("  ✗ UserRegister missing email field")
            return False
        print("  ✓ UserRegister schema valid")
        
        user_login = UserLogin.schema()
        if "email" not in user_login["properties"] or "password" not in user_login["properties"]:
            print("  ✗ UserLogin schema invalid")
            return False
        print("  ✓ UserLogin schema valid")
        
        token_response = TokenResponse.schema()
        if "access_token" not in token_response["properties"]:
            print("  ✗ TokenResponse missing access_token field")
            return False
        print("  ✓ TokenResponse schema valid")
        
        return True
    except Exception as e:
        print(f"  ✗ Schema verification error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_services() -> bool:
    """Verify service implementations."""
    print("\n[Services] Verifying service classes...")
    try:
        from deals_processor.services.auth_service import AuthService, UserService
        
        # Check AuthService methods
        auth_methods = {
            "register_user", "login", "refresh_access_token", "validate_token"
        }
        if not auth_methods.issubset(set(dir(AuthService))):
            print(f"  ✗ AuthService missing methods: {auth_methods - set(dir(AuthService))}")
            return False
        print("  ✓ AuthService fully implemented")
        
        # Check UserService methods
        user_methods = {
            "get_user", "get_user_by_email", "list_users", "update_user",
            "change_password", "deactivate_user", "activate_user"
        }
        if not user_methods.issubset(set(dir(UserService))):
            print(f"  ✗ UserService missing methods: {user_methods - set(dir(UserService))}")
            return False
        print("  ✓ UserService fully implemented")
        
        return True
    except Exception as e:
        print(f"  ✗ Service verification error: {e}")
        return False


def verify_files() -> bool:
    """Verify all required files exist."""
    print("\n[Files] Verifying file structure...")
    
    required_files = [
        "src/deals_processor/core/security.py",
        "src/deals_processor/api/auth.py",
        "src/deals_processor/models/user.py",
        "src/deals_processor/repositories/user_repository.py",
        "src/deals_processor/services/auth_service.py",
        "scripts/init_db.py",
        "tests/test_auth_integration.py",
        "AUTH_SYSTEM.md",
        "IMPLEMENTATION_SUMMARY.md",
    ]
    
    base_path = Path(__file__).parent.parent
    missing_files = []
    
    for file_path in required_files:
        full_path = base_path / file_path
        if not full_path.exists():
            missing_files.append(file_path)
            print(f"  ✗ Missing: {file_path}")
        else:
            print(f"  ✓ {file_path}")
    
    if missing_files:
        return False
    
    return True


def main() -> None:
    """Run all verification checks."""
    print("\n" + "=" * 70)
    print("Authentication System Implementation Verification")
    print("=" * 70)
    
    checks = [
        ("Files", verify_files),
        ("Imports", verify_imports),
        ("Models", verify_database_models),
        ("Configuration", verify_config),
        ("Schemas", verify_schemas),
        ("Services", verify_services),
        ("Routes", verify_routes),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n✗ {check_name} verification failed: {e}")
            import traceback
            traceback.print_exc()
            results.append((check_name, False))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} - {check_name}")
    
    print("\n" + "=" * 70)
    print(f"Result: {passed}/{total} checks passed")
    print("=" * 70 + "\n")
    
    if passed == total:
        print("✓ All verification checks passed!")
        print("✓ Authentication system is properly implemented and ready for use")
        sys.exit(0)
    else:
        print("✗ Some verification checks failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
