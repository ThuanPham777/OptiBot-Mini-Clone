import tiktoken
import re

encoder = tiktoken.get_encoding("cl100k_base")

def split_by_headings(markdown: str, max_tokens=800, overlap=100):
    """
    Chunk markdown by semantic headings for support documentation.

    Strategy:
    - Each chunk MUST include Title and "Article URL:" for citations
    - Splits at ## or ### headings for semantic coherence
    - If no headings, keeps entire article as single chunk
    - Large chunks are split with overlap while preserving header
    """
    lines = markdown.split("\n")
    title = ""
    article_url = ""

    # Extract title and URL from header
    for line in lines:
        if line.startswith("# "):
            title = line
        elif line.startswith("Article URL: "):
            article_url = line
            break

    # Create header to prepend to each chunk
    # Format ensures OpenAI can find "Article URL:" for citations
    header = f"{title}\n\n{article_url}\n\n---\n\n" if title and article_url else ""

    sections = []
    current = []
    content_started = False

    for line in lines:
        # Skip initial header section
        if not content_started:
            if line.startswith("Article URL: "):
                content_started = True
            continue

        # Split at ## or ### headings
        if (line.startswith("## ") or line.startswith("### ")) and current:
            sections.append("\n".join(current))
            current = [line]
        else:
            current.append(line)

    if current:
        sections.append("\n".join(current))

    # If no sections found (no headings), use entire content
    if not sections:
        content_lines = []
        content_started = False
        for line in lines:
            if not content_started:
                if line.startswith("Article URL: "):
                    content_started = True
                continue
            content_lines.append(line)
        if content_lines:
            sections = ["\n".join(content_lines)]

    chunks = []
    for section in sections:
        # Add header to section
        section_with_header = header + section.strip()
        tokens = encoder.encode(section_with_header)

        if len(tokens) <= max_tokens:
            chunks.append(section_with_header)
        else:
            # Split large sections while keeping header
            section_tokens = encoder.encode(section.strip())
            header_tokens = encoder.encode(header)
            available_tokens = max_tokens - len(header_tokens)

            start = 0
            while start < len(section_tokens):
                end = start + available_tokens
                chunk_tokens = section_tokens[start:end]
                chunk_text = header + encoder.decode(chunk_tokens)
                chunks.append(chunk_text)
                start += available_tokens - overlap

    return chunks
