import pytest

from app.services.wikipedia import parse_wikipedia_target


def test_parse_dutch_article():
    lang, title = parse_wikipedia_target("https://nl.wikipedia.org/wiki/Dahlia")
    assert lang == "nl"
    assert title == "Dahlia"


def test_parse_handles_url_encoding():
    lang, title = parse_wikipedia_target("https://en.wikipedia.org/wiki/Dahlia_(genus)")
    assert lang == "en"
    assert title == "Dahlia_(genus)"


def test_parse_rejects_non_wikipedia_url():
    with pytest.raises(ValueError):
        parse_wikipedia_target("https://example.com/wiki/Dahlia")


def test_parse_rejects_non_article_url():
    with pytest.raises(ValueError):
        parse_wikipedia_target("https://nl.wikipedia.org/")
