from bs4 import BeautifulSoup

from app.services.descriptions import (
    _extract_dahliavereniging,
    _extract_generic,
    _extract_shopify,
)

# Trimmed structure mirroring the real Nederlandse Dahlia Vereniging variety page.
DAHLIAVERENIGING_HTML = """
<html><body>
  <header><h2>Menu</h2></header>
  <main>
    <h1>Bumble Rumble</h1>
    <p>Bijzondere collerette-dahlia met dieproze buitenste bloemblaadjes.</p>
    <h3>Kleurbeschrijving</h3>
    <p>Dieproze met frambooskleurige adering, witte kraagblaadjes, geel centrum</p>
    <h3>Bijzondere kenmerken</h3>
    <p>Collerette-vorm, bijvriendelijk, uitstekende snijbloem</p>
  </main>
  <h2>Onder andere te koop bij</h2>
  <p>Deze tekst hoort er niet bij.</p>
</body></html>
"""

SHOPIFY_HTML = """
<html><head>
  <meta property="og:description" content="Korte social omschrijving.">
</head><body>
  <div class="product__description rte"><p>Halskraag dahlia met een dubbele laag binnenste blaadjes.</p></div>
</body></html>
"""

GENERIC_HTML = """
<html><head><meta name="description" content="Een generieke omschrijving."></head>
<body><p>iets</p></body></html>
"""


def test_dahliavereniging_combines_intro_and_labeled_sections():
    text = _extract_dahliavereniging(BeautifulSoup(DAHLIAVERENIGING_HTML, "html.parser"))
    assert "Bijzondere collerette-dahlia" in text
    assert "Kleurbeschrijving: Dieproze" in text
    assert "Bijzondere kenmerken: Collerette-vorm" in text
    # Content after the first <h2> is excluded.
    assert "hoort er niet bij" not in text


def test_shopify_uses_product_description():
    text = _extract_shopify(BeautifulSoup(SHOPIFY_HTML, "html.parser"))
    assert "dubbele laag binnenste blaadjes" in text


def test_generic_falls_back_to_meta_description():
    text = _extract_generic(BeautifulSoup(GENERIC_HTML, "html.parser"))
    assert text == "Een generieke omschrijving."
