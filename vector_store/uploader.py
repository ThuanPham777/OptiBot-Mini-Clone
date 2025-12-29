from openai import OpenAI
import os
import io

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def upload_chunks(chunks, base_filename, vector_store_id):
    """
    Upload markdown chunks to OpenAI Vector Store.

    Args:
        chunks: List of markdown text chunks
        base_filename: Base name for the chunk files
        vector_store_id: OpenAI Vector Store ID

    Returns:
        Number of chunks uploaded
    """
    count = 0

    for i, chunk in enumerate(chunks):
        filename = f"{base_filename}_chunk_{i}.md"

        # Create a file-like object from the chunk text
        file_obj = io.BytesIO(chunk.encode("utf-8"))
        file_obj.name = filename

        # Upload file to OpenAI
        file = client.files.create(
            file=file_obj,
            purpose="assistants"
        )

        # Attach file to Vector Store
        client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file.id
        )

        count += 1

    return count
