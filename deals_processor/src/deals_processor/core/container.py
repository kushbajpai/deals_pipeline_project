"""Dependency injection container for the application.

Follows the Dependency Injection pattern to manage application dependencies
and provide them to various components.
"""

from typing import Dict, Any

from deals_processor.core.config import Settings, get_settings


class Container:
    """IoC container for managing application dependencies.

    This container manages all application dependencies and provides
    them to services and routes following the Dependency Injection pattern.
    """

    def __init__(self) -> None:
        """Initialize the dependency container."""
        self._dependencies: Dict[str, Any] = {}
        self._init_dependencies()

    def _init_dependencies(self) -> None:
        """Initialize all dependencies."""
        # Register settings
        self._dependencies["settings"] = get_settings()

    def get(self, key: str) -> Any:
        """Get a dependency by key.

        Args:
            key: Dependency identifier.

        Returns:
            The requested dependency.

        Raises:
            KeyError: If dependency is not found.
        """
        if key not in self._dependencies:
            raise KeyError(f"Dependency '{key}' not found in container")
        return self._dependencies[key]

    def register(self, key: str, dependency: Any) -> None:
        """Register a dependency in the container.

        Args:
            key: Dependency identifier.
            dependency: The dependency instance.
        """
        self._dependencies[key] = dependency

    def get_settings(self) -> Settings:
        """Get application settings.

        Returns:
            Settings: Application settings instance.
        """
        return self.get("settings")


# Global container instance
_container: Container | None = None


def get_container() -> Container:
    """Get the global dependency container instance.

    Returns:
        Container: The global container instance.
    """
    global _container
    if _container is None:
        _container = Container()
    return _container
