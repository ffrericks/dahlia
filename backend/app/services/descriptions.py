from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from .wikipedia import fetch_first_paragraph as _wikipedia_extract

# Wikimedia and most sites reject requests without a descriptive User-Agent.
_USER_AGENT = "DahliaTool/0.1 (https://github.com/ffrericks/dahlia; self-hosted personal app)"


def extract_description(url: str) -> str:
    """Import a variety description from a supported page.

    Supported: Wikipedia, Studio May & June (Shopify), Nederlandse Dahlia
    Vereniging. Other sites fall back to their og:description / meta description.
    """
    host = urlparse(url.strip()).netloc.lower()
    if not host:
        raise ValueError("Geen geldige link.")

    if host.endswith("wikipedia.org"):
        return _wikipedia_extract(url)

    soup = BeautifulSoup(_fetch_html(url), "html.parser")
    if host.endswith("nederlandsedahliavereniging.nl"):
        return _extract_dahliavereniging(soup)
    if host.endswith("studiomayandjune.com"):
        return _extract_shopify(soup)
    return _extract_generic(soup)


def _fetch_html(url: str) -> str:
    response = httpx.get(
        url, timeout=15.0, follow_redirects=True, headers={"User-Agent": _USER_AGENT}
    )
    response.raise_for_status()
    return response.text


def _meta_description(soup: BeautifulSoup) -> str:
    og = soup.find("meta", attrs={"property": "og:description"})
    if og and og.get("content", "").strip():
        return og["content"].strip()
    md = soup.find("meta", attrs={"name": "description"})
    if md and md.get("content", "").strip():
        return md["content"].strip()
    return ""


def _extract_shopify(soup: BeautifulSoup) -> str:
    # Shopify product description block; fall back to the page's social description.
    node = soup.select_one("div.product__description") or soup.select_one(
        ".product-single__description"
    )
    text = node.get_text(" ", strip=True) if node else ""
    if not text:
        text = _meta_description(soup)
    if not text:
        raise ValueError("Geen omschrijving gevonden op deze pagina.")
    return text


def _extract_dahliavereniging(soup: BeautifulSoup) -> str:
    """The description sits between the variety <h1> and the first <h2>.

    It's an intro paragraph plus labeled sections (e.g. "Kleurbeschrijving").
    """
    lines: list[str] = []
    pending_label: str | None = None
    started = False

    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        text = tag.get_text(" ", strip=True)
        if tag.name == "h1":
            started = True  # the variety title; start collecting after it
            continue
        if not started:
            continue
        if tag.name == "h2":
            break  # next section ("Onder andere te koop bij") — stop
        if not text:
            continue
        if tag.name == "h3":
            pending_label = text  # label for the paragraph that follows
        elif pending_label:
            lines.append(f"{pending_label}: {text}")
            pending_label = None
        else:
            lines.append(text)

    if not lines:
        raise ValueError("Geen omschrijving gevonden op deze pagina.")
    return "\n".join(lines)


def _extract_generic(soup: BeautifulSoup) -> str:
    text = _meta_description(soup)
    if not text:
        raise ValueError(
            "Deze site wordt nog niet herkend. Vul de omschrijving handmatig in."
        )
    return text
