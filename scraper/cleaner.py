from bs4 import BeautifulSoup

def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["nav", "footer", "aside", "script", "style"]):
        tag.decompose()

    return str(soup.body or soup)