"""
Configuration management for OptiBot scraper.
Centralizes all environment variables and validation.
"""

import os
import sys
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

class Config:
    """Application configuration from environment variables."""

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    VECTOR_STORE_ID = os.getenv("VECTOR_STORE_ID")

    # Zendesk Configuration
    ZENDESK_ARTICLES_URL = os.getenv(
        "ZENDESK_ARTICLES_URL",
        "https://support.optisigns.com/api/v2/help_center/en-us/articles.json"
    )

    # AWS S3 Configuration (for cache persistence)
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY")
    S3_SECRET_KEY = os.getenv("S3_SECRET_KEY")
    S3_REGION = os.getenv("S3_REGION", "us-east-1")
    S3_CACHE_KEY = os.getenv("S3_CACHE_KEY", "cache/articles.json")
    S3_MARKDOWN_PREFIX = os.getenv("S3_MARKDOWN_PREFIX", "markdown/")

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is required")

        if not cls.VECTOR_STORE_ID:
            errors.append("VECTOR_STORE_ID is required")

        if not cls.ZENDESK_ARTICLES_URL:
            errors.append("ZENDESK_ARTICLES_URL is required")

        if not cls.S3_BUCKET_NAME:
            errors.append("S3_BUCKET_NAME is required for cache persistence")

        if not cls.S3_ACCESS_KEY:
            errors.append("S3_ACCESS_KEY is required")

        if not cls.S3_SECRET_KEY:
            errors.append("S3_SECRET_KEY is required")

        if errors:
            logger.error("Configuration validation failed:")
            for error in errors:
                logger.error(f"  - {error}")
            logger.error("\nPlease check your .env file and ensure all required variables are set.")
            sys.exit(1)

        logger.info("Configuration validated successfully")

    @classmethod
    def display(cls):
        """Display configuration (masked sensitive values)."""
        logger.info("Current configuration:")
        logger.info(f"  OPENAI_API_KEY: {'*' * 20}...{cls.OPENAI_API_KEY[-4:] if cls.OPENAI_API_KEY else 'NOT SET'}")
        logger.info(f"  VECTOR_STORE_ID: {cls.VECTOR_STORE_ID}")
        logger.info(f"  ZENDESK_ARTICLES_URL: {cls.ZENDESK_ARTICLES_URL}")
        logger.info(f"  S3_BUCKET_NAME: {cls.S3_BUCKET_NAME}")
        logger.info(f"  S3_REGION: {cls.S3_REGION}")
        logger.info(f"  S3_CACHE_KEY: {cls.S3_CACHE_KEY}")
