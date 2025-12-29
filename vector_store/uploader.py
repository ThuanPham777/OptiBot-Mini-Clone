from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def upload_chunks(chunks, base_filename, vector_store_id):
    count = 0

    for i, chunk in enumerate(chunks):
        filename = f"{base_filename}_chunk_{i}.md"

        file = client.files.create(
            file=chunk.encode("utf-8"),
            purpose="assistants",
            filename=filename
        )

        client.vector_stores.files.create(
            vector_store_id=vector_store_id,
            file_id=file.id
        )

        count += 1

    return count
