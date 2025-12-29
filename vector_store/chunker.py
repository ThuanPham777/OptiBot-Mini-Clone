import tiktoken

encoder = tiktoken.get_encoding("cl100k_base")

def split_by_headings(markdown: str, max_tokens=500, overlap=50):
    """
    Chunk markdown by semantic headings (##),
    optimized for support documentation.
    """
    sections = []
    current = []

    lines = markdown.split("\n")

    for line in lines:
        if line.startswith("## ") and current:
            sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append("\n".join(current))

    chunks = []
    for section in sections:
        tokens = encoder.encode(section)

        if len(tokens) <= max_tokens:
            chunks.append(section)
        else:
            start = 0
            while start < len(tokens):
                end = start + max_tokens
                chunk_tokens = tokens[start:end]
                chunks.append(encoder.decode(chunk_tokens))
                start += max_tokens - overlap

    return chunks
