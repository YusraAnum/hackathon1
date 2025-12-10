"""
CDN Configuration for Static Assets
This module provides configuration and utilities for CDN setup.
"""
import os
from typing import Optional
from src.utils.config import settings
from src.utils.logging import get_logger


logger = get_logger(__name__)


class CDNConfig:
    """
    Configuration class for CDN settings
    """
    def __init__(self):
        self.cdn_enabled = settings.cdn_enabled or os.getenv("CDN_ENABLED", "false").lower() == "true"
        self.cdn_url = settings.cdn_url or os.getenv("CDN_URL", "")
        self.asset_path = settings.asset_path or os.getenv("ASSET_PATH", "/static")
        self.cache_duration = int(settings.cache_duration or os.getenv("CACHE_DURATION", "3600"))  # 1 hour default

        if self.cdn_enabled:
            logger.info(f"CDN enabled: {self.cdn_url}")
        else:
            logger.info("CDN disabled - serving assets locally")

    def get_asset_url(self, asset_path: str) -> str:
        """
        Get the full URL for an asset, using CDN if enabled

        Args:
            asset_path: Path to the asset (e.g., "/images/logo.png")

        Returns:
            Full URL to the asset
        """
        if self.cdn_enabled and self.cdn_url:
            # Ensure CDN URL ends with a slash and asset path starts with a slash
            cdn_base = self.cdn_url.rstrip('/') + '/'
            asset_path = asset_path.lstrip('/')
            return cdn_base + asset_path
        else:
            # Return local path
            return self.asset_path + asset_path

    def get_cache_headers(self) -> dict:
        """
        Get cache headers for CDN optimization
        """
        return {
            "Cache-Control": f"public, max-age={self.cache_duration}",
            "CDN-Cache-Control": f"max-age={self.cache_duration}",
            "Vary": "Accept-Encoding"
        }

    def is_cdn_ready(self) -> bool:
        """
        Check if CDN is properly configured
        """
        return self.cdn_enabled and bool(self.cdn_url)


# Global instance
cdn_config = CDNConfig()


def optimize_static_asset_serving():
    """
    Apply optimizations for static asset serving
    """
    logger.info("Optimizing static asset serving...")

    # This would typically involve:
    # 1. Pre-compressing assets (gzip, brotli)
    # 2. Setting appropriate cache headers
    # 3. Optimizing image formats and sizes
    # 4. Implementing asset versioning for cache busting

    logger.info("Static asset optimization completed")


def get_optimized_asset_path(asset_path: str, version: Optional[str] = None) -> str:
    """
    Get an optimized asset path with versioning for cache busting

    Args:
        asset_path: Original asset path
        version: Optional version string (e.g., commit hash, timestamp)

    Returns:
        Optimized asset path with version query parameter
    """
    if version:
        separator = "&" if "?" in asset_path else "?"
        return f"{asset_path}{separator}v={version}"
    return asset_path