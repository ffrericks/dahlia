from urllib.parse import unquote, urlparse

import httpx


def parse_wikipedia_target(url: str) -> tuple[str, str]:
    """Extract (language, article title) from a Wikipedia URL.

    e.g. https://nl.wikipedia.org/wiki/Dahlia -> ("nl", "Dahlia")
    """
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower()
    if not host.endswith("wikipedia.org"):
        raise ValueError("Dit is geen Wikipedia-link.")

    # Language is the subdomain (nl, en, ...); fall back to English if absent.
    lang = host.split(".")[0]
    if lang in ("wikipedia", ""):
        lang = "en"

    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2 or parts[0] != "wiki":
        raise ValueError("Dit is geen Wikipedia-artikel.")

    return lang, unquote(parts[1])


# Wikimedia's User-Agent policy requires a descriptive UA with a contact URL,
# otherwise requests are rejected with HTTP 403.
_USER_AGENT = (
    "DahliaTool/0.1 (https://github.com/dahlia-tool; self-hosted personal app)"
)


def fetch_first_paragraph(url: str) -> str:
    """Return the lead paragraph of a Wikipedia article as plain text."""
    lang, title = parse_wikipedia_target(url)
    # MediaWiki Action API: prop=extracts with exintro+explaintext gives the
    # intro section as plain text; redirects=1 follows article redirects.
    response = httpx.get(
        f"https://{lang}.wikipedia.org/w/api.php",
        params={
            "action": "query",
            "prop": "extracts",
            "exintro": 1,
            "explaintext": 1,
            "redirects": 1,
            "titles": title,
            "format": "json",
        },
        timeout=10.0,
        follow_redirects=True,
        headers={"User-Agent": _USER_AGENT},
    )
    response.raise_for_status()

    pages = response.json().get("query", {}).get("pages", {})
    # A missing article comes back as a page with id "-1" and no extract.
    extract = next(iter(pages.values()), {}).get("extract", "").strip()
    if not extract:
        raise ValueError("Geen omschrijving gevonden op Wikipedia.")
    return extract
