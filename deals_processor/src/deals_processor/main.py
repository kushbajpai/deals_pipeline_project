"""FastAPI application factory and configuration.

Creates and configures the FastAPI application with middleware,
exception handlers, and route registration.
"""

import logging
import logging.config

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware

from deals_processor.api import auth, deals, health, users, ic_memo
from deals_processor.core.config import LogConfig, get_settings
from deals_processor.core.database import get_database_instance
from deals_processor.core.exceptions import DealsProcessorException
# Import all models to ensure they're registered with SQLAlchemy Base before init_db()
from deals_processor.models.user import UserModel  # noqa: F401
from deals_processor.models.deal import DealModel, ActivityModel  # noqa: F401
from deals_processor.models.ic_memo import ICMemoModel, ICMemoVersionModel  # noqa: F401

# Configure logging
logging_config = LogConfig()
logging.config.dictConfig(logging_config.config)
logger = logging.getLogger(__name__)


def custom_openapi(app: FastAPI):
    """Add custom OpenAPI configuration with JWT Bearer authentication.
    
    Adds security scheme for JWT Bearer tokens so Swagger UI can authenticate requests.
    
    Args:
        app: FastAPI application instance.
    """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # Add JWT Bearer security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT Bearer token. Get one from /auth/login endpoint.",
        }
    }
    
    # Add security requirement to all endpoints (except /auth/login and /auth/register)
    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            if isinstance(operation, dict) and "security" not in operation:
                # Don't require auth for login/register endpoints
                if "/auth/login" not in str(operation) and "/auth/register" not in str(operation):
                    operation["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def register_exception_handlers(app: FastAPI) -> None:
    """Register custom exception handlers.

    Args:
        app: FastAPI application instance.
    """

    @app.exception_handler(DealsProcessorException)
    async def deals_processor_exception_handler(
        request: Request, exc: DealsProcessorException
    ) -> JSONResponse:
        """Handle application-specific exceptions.

        Args:
            request: Request object.
            exc: Exception instance.

        Returns:
            JSONResponse: Error response.
        """
        logger.error(f"DealsProcessorException: {exc.message}")
        return JSONResponse(
            status_code=400,
            content={
                "code": exc.code,
                "message": exc.message,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors.

        Args:
            request: Request object.
            exc: Exception instance.

        Returns:
            JSONResponse: Error response with validation details.
        """
        logger.warning(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": str(exc),
            },
        )


def include_routers(app: FastAPI) -> None:
    """Include API routers.

    Args:
        app: FastAPI application instance.
    """
    app.include_router(health.router)
    app.include_router(auth.auth_handler.router)
    app.include_router(deals.router)
    app.include_router(users.router)
    app.include_router(ic_memo.router)
    logger.info("API routers registered")


def add_middleware(app: FastAPI) -> None:
    """Add middleware to the application.

    Args:
        app: FastAPI application instance.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://localhost:5177",
            "http://localhost:3000",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def add_events(app: FastAPI) -> None:
    """Add startup and shutdown events.

    Args:
        app: FastAPI application instance.
    """

    @app.on_event("startup")
    async def startup_event() -> None:
        """Execute on application startup."""
        try:
            db_instance = get_database_instance()
            db_instance.init_db()
            logger.info("Database initialized successfully")
            
            # Initialize default admin user
            db = db_instance.get_session()
            try:
                init_default_admin(db)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise
        logger.info("Application startup complete")

    @app.on_event("shutdown")
    async def shutdown_event() -> None:
        """Execute on application shutdown."""
        try:
            db_instance = get_database_instance()
            db_instance.engine.dispose()
            logger.info("Database connection pool disposed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        logger.info("Application shutdown")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Follows the Application Factory pattern for testability and modularity.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    settings = get_settings()

    # Create FastAPI instance with Swagger/OpenAPI documentation
    app = FastAPI(
        title=settings.app_name,
        description="A FastAPI application for processing deals",
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",  # Swagger UI at /docs
        redoc_url="/redoc",  # ReDoc at /redoc
        openapi_url="/openapi.json",  # OpenAPI schema at /openapi.json
    )

    # Register exception handlers
    register_exception_handlers(app)

    # Include routers
    include_routers(app)

    # Add middleware
    add_middleware(app)

    # Add startup/shutdown events
    add_events(app)

    # Configure custom OpenAPI schema with JWT Bearer authentication
    app.openapi = lambda: custom_openapi(app)

    logger.info(f"FastAPI application created: {settings.app_name} v{settings.app_version}")

    return app


# Create the app instance
app = create_app()


def main() -> None:
    """Run the FastAPI application using Uvicorn."""
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "deals_processor.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    main()
