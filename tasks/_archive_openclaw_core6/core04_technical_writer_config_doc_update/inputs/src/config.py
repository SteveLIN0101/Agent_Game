"""Application configuration."""

import os

# Server settings
HOST = os.getenv("APP_HOST", "0.0.0.0")
PORT = int(os.getenv("APP_PORT", "8080"))

# Cache settings
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
CACHE_BACKEND = os.getenv("CACHE_BACKEND", "redis")

# Retry settings
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = os.getenv("LOG_FORMAT", "json")

# Feature flags
ENABLE_METRICS = os.getenv("ENABLE_METRICS", "true").lower() == "true"
ENABLE_RATE_LIMIT = os.getenv("ENABLE_RATE_LIMIT", "true").lower() == "true"
