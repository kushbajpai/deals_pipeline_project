"""Exception classes for the application.

Defines custom exceptions following the Single Responsibility Principle,
with each exception class responsible for a specific error condition.
"""


class DealsProcessorException(Exception):
    """Base exception for all deals processor errors."""

    def __init__(self, message: str, code: str | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Exception message.
            code: Optional error code for API responses.
        """
        super().__init__(message)
        self.message = message
        self.code = code or "INTERNAL_ERROR"


class ValidationError(DealsProcessorException):
    """Raised when data validation fails."""

    def __init__(self, message: str) -> None:
        """Initialize validation error."""
        super().__init__(message, code="VALIDATION_ERROR")


class NotFoundError(DealsProcessorException):
    """Raised when a requested resource is not found."""

    def __init__(self, resource: str, identifier: str) -> None:
        """Initialize not found error.

        Args:
            resource: Name of the resource that was not found.
            identifier: Identifier of the resource.
        """
        message = f"{resource} with id '{identifier}' not found"
        super().__init__(message, code="NOT_FOUND")


class DuplicateError(DealsProcessorException):
    """Raised when attempting to create a duplicate resource."""

    def __init__(self, resource: str, identifier: str) -> None:
        """Initialize duplicate error.

        Args:
            resource: Name of the resource that already exists.
            identifier: Identifier of the resource.
        """
        message = f"{resource} with id '{identifier}' already exists"
        super().__init__(message, code="DUPLICATE_RESOURCE")


class UnauthorizedError(DealsProcessorException):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Unauthorized access") -> None:
        """Initialize unauthorized error."""
        super().__init__(message, code="UNAUTHORIZED")


class ForbiddenError(DealsProcessorException):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Access forbidden") -> None:
        """Initialize forbidden error."""
        super().__init__(message, code="FORBIDDEN")
