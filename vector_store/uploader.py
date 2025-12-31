from openai import OpenAI
import os
import io
import logging
from config import Config

logger = logging.getLogger(__name__)

def delete_old_files(client, vector_store_id, old_file_ids):
    """Delete old files from Vector Store to prevent duplicates."""
    if not old_file_ids:
        return

    for file_id in old_file_ids:
        try:
            client.vector_stores.files.delete(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            client.files.delete(file_id)
        except Exception as e:
            logger.warning(f"Failed to delete file {file_id}: {e}")

def upload_chunks(chunks, base_filename, vector_store_id, old_file_ids=None):
    """
    Upload markdown chunks to OpenAI Vector Store.

    Args:
        chunks: List of markdown text chunks
        base_filename: Base name for the chunk files
        vector_store_id: OpenAI Vector Store ID
        old_file_ids: List of old file IDs to delete (prevents duplicates)

    Returns:
        Tuple of (count, list of new file_ids)
    """
    client = OpenAI(api_key=Config.OPENAI_API_KEY)

    if old_file_ids:
        delete_old_files(client, vector_store_id, old_file_ids)
        logger.info(f"  Deleted {len(old_file_ids)} old files")

    count = 0
    new_file_ids = []

    for i, chunk in enumerate(chunks):
        filename = f"{base_filename}_chunk_{i}.md"

        file_obj = io.BytesIO(chunk.encode("utf-8"))
        file_obj.name = filename

        file = client.files.create(
            file=file_obj,
            purpose="assistants"
        )

        client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file.id
        )

        new_file_ids.append(file.id)
        count += 1

    return count, new_file_ids
