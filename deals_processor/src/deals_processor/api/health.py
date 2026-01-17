"""Health check route handler for the application."""

from typing import Dict

from fastapi import APIRouter, status

from deals_processor.core.config import get_settings
from deals_processor.schemas import HealthCheck


class HealthRouteHandler:
    """Handler for health check routes.

    Organizes all health-related endpoints as methods within a single
    class for better organization and testability.
    """

    def __init__(self) -> None:
        """Initialize the health route handler and setup routes."""
        self.router = APIRouter(prefix="/api/v1/health", tags=["health"])
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Register all health check routes."""
        self.router.add_api_route(
            "",
            self.health_check,
            methods=["GET"],
            response_model=HealthCheck,
            status_code=status.HTTP_200_OK,
            summary="Health Check",
            description="Returns the health status of the application",
        )

    async def health_check(self) -> Dict[str, str]:
        """Perform a health check.

        Returns:
            dict: Health status and version information.
        """
        settings = get_settings()
        return {
            "status": "healthy",
            "version": settings.app_version,
        }


# Create router instance
_handler = HealthRouteHandler()
router = _handler.router
