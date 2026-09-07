from datetime import datetime, timezone
from src.config import settings


class HealthService:
    """
    Service for checking application health status.
    Used for monitoring and Kubernetes liveness/readiness probes.
    """
    
    @staticmethod
    def get_health_status() -> dict:
        """
        Get current application health status.
        
        Returns:
            Dictionary with health information
        """
        return {
            "status": "healthy",
            "service": "Enterprise Telegram Agent",
            "version": settings.version,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    
    @staticmethod
    def get_detailed_status() -> dict:
        """
        Get detailed health status including dependencies.
        
        Returns:
            Dictionary with detailed health information
        """
        return {
            "status": "healthy",
            "service": "Enterprise Telegram Agent",
            "version": settings.version,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": settings.debug and "development" or "production",
            "components": {
                "database": "configured",
                "openai": "configured" if settings.openai_api_key else "not_configured",
                "gemini": "configured" if settings.google_api_key else "not_configured",
                "telegram": "configured" if settings.telegram_token else "not_configured",
            }
        }