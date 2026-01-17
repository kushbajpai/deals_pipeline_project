"""Core authentication classes for password hashing and JWT management.

Implements industry-standard password hashing with bcrypt and JWT token
generation/validation following security best practices.
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
import bcrypt

logger = logging.getLogger(__name__)


class PasswordHasher:
    """Password hashing utility using bcrypt directly.

    Provides secure password hashing and verification using bcrypt
    with industry-standard security settings.
    """

    def __init__(self, rounds: int = 12) -> None:
        """Initialize password hasher.

        Args:
            rounds: Bcrypt cost factor (higher = more secure but slower).
                   Default 12 is recommended for production.
        """
        self.rounds = rounds
        self.logger = logging.getLogger(self.__class__.__name__)

    def hash_password(self, plain_password: str) -> str:
        """Hash a plaintext password using bcrypt.

        Args:
            plain_password: The plaintext password to hash.

        Returns:
            str: The hashed password (safe to store in database).

        Raises:
            ValueError: If password is empty.
        """
        if not plain_password:
            raise ValueError("Password cannot be empty")

        # Bcrypt has a 72-byte limit; truncate if necessary
        # UTF-8 encoding can use multiple bytes per character
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            # Truncate at 72 bytes (safe operation, bcrypt will handle it)
            password_bytes = password_bytes[:72]
            self.logger.warning("Password truncated to 72 bytes (bcrypt limit)")

        try:
            salt = bcrypt.gensalt(rounds=self.rounds)
            hashed = bcrypt.hashpw(password_bytes, salt)
            self.logger.debug("Password hashed successfully")
            return hashed.decode('utf-8')
        except Exception as e:
            self.logger.error(f"Password hashing failed: {e}")
            raise ValueError(f"Password hashing failed: {e}")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hash.

        Uses bcrypt for secure comparison.

        Args:
            plain_password: The plaintext password to verify.
            hashed_password: The stored password hash.

        Returns:
            bool: True if password matches, False otherwise.
        """
        try:
            # Apply same truncation as hashing for consistency
            password_bytes = plain_password.encode('utf-8')
            if len(password_bytes) > 72:
                password_bytes = password_bytes[:72]

            # Convert hash to bytes if needed
            if isinstance(hashed_password, str):
                hashed_password = hashed_password.encode('utf-8')

            is_valid = bcrypt.checkpw(password_bytes, hashed_password)
            if is_valid:
                self.logger.debug("Password verification successful")
            else:
                self.logger.warning("Password verification failed")
            return is_valid
        except Exception as e:
            self.logger.error(f"Password verification error: {e}")
            return False


class JWTTokenManager:
    """JWT token generation and validation.

    Handles creation and validation of JWT tokens for authentication,
    following OAuth2/JWT best practices.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 15,
        refresh_token_expire_days: int = 7,
    ) -> None:
        """Initialize JWT token manager.

        Args:
            secret_key: Secret key for signing tokens (min 32 chars).
            algorithm: JWT algorithm (default HS256 for symmetric).
            access_token_expire_minutes: Access token expiration in minutes.
            refresh_token_expire_days: Refresh token expiration in days.

        Raises:
            ValueError: If secret_key is too short or algorithm invalid.
        """
        if not secret_key or len(secret_key) < 32:
            raise ValueError("Secret key must be at least 32 characters")

        if algorithm not in ["HS256", "HS384", "HS512"]:
            raise ValueError(f"Algorithm {algorithm} not supported")

        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.logger = logging.getLogger(self.__class__.__name__)

    def create_access_token(
        self,
        user_id: int,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT access token.

        Args:
            user_id: User ID to include in token.
            email: User email to include in token.
            role: User role to include in token.
            expires_delta: Custom expiration time (uses default if None).

        Returns:
            str: Encoded JWT token.
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=self.access_token_expire_minutes)

        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "type": "access",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        encoded_jwt = jwt.encode(
            payload, self.secret_key, algorithm=self.algorithm
        )
        self.logger.debug(f"Created access token for user {user_id}")
        return encoded_jwt

    def create_refresh_token(
        self,
        user_id: int,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """Create a JWT refresh token.

        Args:
            user_id: User ID to include in token.
            expires_delta: Custom expiration time (uses default if None).

        Returns:
            str: Encoded JWT refresh token.
        """
        if expires_delta is None:
            expires_delta = timedelta(days=self.refresh_token_expire_days)

        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }

        encoded_jwt = jwt.encode(
            payload, self.secret_key, algorithm=self.algorithm
        )
        self.logger.debug(f"Created refresh token for user {user_id}")
        return encoded_jwt

    def decode_token(self, token: str) -> dict:
        """Decode and validate a JWT token.

        Args:
            token: The JWT token to decode.

        Returns:
            dict: Decoded token payload.

        Raises:
            jwt.ExpiredSignatureError: If token has expired.
            jwt.InvalidTokenError: If token is invalid or tampered with.
        """
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            self.logger.debug(f"Token decoded successfully for user {payload.get('sub')}")
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning("Expired token detected")
            raise
        except jwt.InvalidTokenError as e:
            self.logger.error(f"Invalid token: {e}")
            raise

    def get_token_data(self, token: str) -> dict:
        """Get decoded token data safely.

        Handles token validation errors gracefully.

        Args:
            token: The JWT token to decode.

        Returns:
            dict: Decoded token data or empty dict if invalid.
        """
        try:
            return self.decode_token(token)
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            return {}
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid token")
            return {}
