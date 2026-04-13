"""Main API router aggregating all module routers."""

from fastapi import APIRouter

from app.modules.admin.router import router as admin_router
from app.modules.auth.router import router as auth_router
from app.modules.logs.router import router as logs_router
from app.modules.monitor.alerts.router import router as alert_channels_router
from app.modules.monitor.router import router as monitor_router
from app.modules.settings.router import router as settings_router
from app.modules.users.router import router as users_router

# Main API router
api_router = APIRouter()


# Health check endpoint
@api_router.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Status message
    """
    return {"status": "healthy"}


# Register module routers
api_router.include_router(admin_router)
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(logs_router, prefix="/logs", tags=["Logs"])
api_router.include_router(users_router, prefix="/users", tags=["Users"])
api_router.include_router(settings_router, prefix="/me/settings", tags=["Settings"])
api_router.include_router(monitor_router, prefix="/monitor", tags=["Monitor"])
api_router.include_router(
    alert_channels_router, prefix="/monitor", tags=["Alert Channels"]
)

# Register Two-Factor module (optional, added during development)
try:
    from app.modules.two_factor.router import router as two_factor_router

    api_router.include_router(
        two_factor_router,
        prefix="/two-factor",
        tags=["Two-Factor Authentication", "Security", "WebAuthn", "TOTP"],
    )
except ImportError:
    # Module may be absent in some builds; ignore if not present
    pass
