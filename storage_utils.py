"""
Storage utilities for persistent cache using AWS S3 and local filesystem
"""

import os
import json
import logging
import boto3
from pathlib import Path
from config import Config

logger = logging.getLogger(__name__)

class CacheStorage:
    """
    Dual storage: AWS S3 (cloud) + Local filesystem (backup/development)
    """

    def __init__(self):
        # Local storage paths
        self.local_base = Path("storage")
        self.local_cache_dir = self.local_base / "cache"
        self.local_markdown_dir = self.local_base / "markdown"
        self.local_cache_file = self.local_cache_dir / "articles.json"

        # Create local directories
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)
        self.local_markdown_dir.mkdir(parents=True, exist_ok=True)

        # S3 client
        if not Config.S3_BUCKET_NAME:
            raise ValueError("S3_BUCKET_NAME must be set in environment variables")

        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=Config.S3_ACCESS_KEY,
            aws_secret_access_key=Config.S3_SECRET_KEY,
            region_name=Config.S3_REGION
        )
        logger.info(f"Using AWS S3: {Config.S3_BUCKET_NAME}/{Config.S3_CACHE_KEY}")
        logger.info(f"Using Local: {self.local_cache_file}")

    def save_markdown(self, filename, content):
        """Save markdown file to both local and S3."""
        # Save to local
        try:
            local_path = self.local_markdown_dir / filename
            local_path.write_text(content, encoding='utf-8')
            logger.debug(f"Saved markdown locally: {local_path}")
        except Exception as e:
            logger.warning(f"Failed to save markdown {filename} locally: {e}")

        # Save to S3
        try:
            key = f"{Config.S3_MARKDOWN_PREFIX}{filename}"
            self.s3_client.put_object(
                Bucket=Config.S3_BUCKET_NAME,
                Key=key,
                Body=content.encode('utf-8'),
                ContentType='text/markdown'
            )
            logger.debug(f"Saved markdown to S3: {key}")
        except Exception as e:
            logger.warning(f"Failed to save markdown {filename} to S3: {e}")

    def load(self):
        """Load cache from S3, fallback to local."""
        # Try S3 first
        try:
            response = self.s3_client.get_object(
                Bucket=Config.S3_BUCKET_NAME,
                Key=Config.S3_CACHE_KEY
            )
            content = response['Body'].read().decode('utf-8')
            cache = json.loads(content) if content else {}
            logger.info(f"Loaded cache with {len(cache)} articles from S3")
            return cache
        except self.s3_client.exceptions.NoSuchKey:
            logger.info("No cache found in S3. Trying local...")
        except Exception as e:
            logger.warning(f"Failed to load cache from S3: {e}. Trying local...")

        # Fallback to local
        try:
            if self.local_cache_file.exists():
                cache = json.loads(self.local_cache_file.read_text(encoding='utf-8'))
                logger.info(f"Loaded cache with {len(cache)} articles from local")
                return cache
        except Exception as e:
            logger.warning(f"Failed to load cache from local: {e}")

        logger.info("Starting with empty cache.")
        return {}

    def save(self, cache):
        """Save cache to both local and S3."""
        cache_json = json.dumps(cache, indent=2)

        # Save to local
        try:
            self.local_cache_file.write_text(cache_json, encoding='utf-8')
            logger.info(f"Saved cache with {len(cache)} articles locally")
        except Exception as e:
            logger.error(f"Failed to save cache locally: {e}")

        # Save to S3
        try:
            self.s3_client.put_object(
                Bucket=Config.S3_BUCKET_NAME,
                Key=Config.S3_CACHE_KEY,
                Body=cache_json.encode('utf-8'),
                ContentType='application/json'
            )
            logger.info(f"Saved cache with {len(cache)} articles to S3")
        except Exception as e:
            logger.error(f"Failed to save cache to S3: {e}")
            raise
