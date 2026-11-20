from bs4 import BeautifulSoup


def normalize_hubspot_note(html_content: str) -> str:
    """
    Convert HubSpot note HTML into readable text.

    Preserve paragraph boundaries while removing HTML tags.
    """

    if not html_content:
        return ""

    soup = BeautifulSoup(html_content, "html.parser")

    for element in soup(["script", "style"]):
        element.decompose()

    for br in soup.find_all("br"):
        br.replace_with("\n")

    text = soup.get_text(separator="\n")

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)