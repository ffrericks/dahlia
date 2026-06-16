"""Seasonal dahlia care tips.

Derived from Dahlia_Verzorgingsgids_Bak.md and DAHLIA_VERZORGING_PER_MAAND.md.
Each tip lists the months (1-12) in which it is relevant, so the app can show
"what to do now" for the current month.
"""

_TIPS = [
    # --- basics (most of the year) ---
    {
        "id": "basis-zon",
        "title": "Zon",
        "text": "Zet de bak of plek waar minstens 6 uur zon per dag valt. Dahlia's zijn echte zonaanbidders.",
        "category": "basis",
        "months": list(range(1, 13)),
    },
    {
        "id": "basis-water",
        "title": "Water geven",
        "text": "Houd de grond licht vochtig en geef water aan de basis van de plant, niet op het blad (voorkomt schimmels). Doe de vingertest: voelt de grond dieper nog donker en vochtig, dan is extra water niet nodig. Potgrond in een bak droogt sneller uit — op warme dagen dagelijks controleren.",
        "category": "basis",
        "months": [5, 6, 7, 8, 9],
    },
    # --- winter: storage & checks ---
    {
        "id": "winter-controle",
        "title": "Winterberging controleren",
        "text": "Controleer de bewaarde knollen. Voel of ze stevig aanvoelen; gooi zachte, beschimmelde of rottende knollen weg. Bewaar de rest ondersteboven in kratten met houtkrullen of zaagsel, op een vorstvrije, koele en droge plek.",
        "category": "winter",
        "months": [1, 2],
    },
    # --- spring: wake, propagate, raise, plant ---
    {
        "id": "wekken",
        "title": "Knollen wekken",
        "text": "Haal de knollen uit de opslag om ze te laten ontwaken. Soorten lopen op verschillende momenten uit: sommige tonen snel 'ogen' of scheuten, andere hebben meer tijd nodig.",
        "category": "voorjaar",
        "months": [3],
    },
    {
        "id": "splitsen",
        "title": "Splitsen / vermeerderen",
        "text": "Grote, compacte knollen kun je delen om de plant te verjongen. Gebruik een schoon, scherp mes en zorg dat elk deel minstens één stevige knol én een zichtbaar oog heeft. Snijd losse knollen en knollen met een gebroken 'nek' weg — die gaan snel rotten.",
        "category": "voorjaar",
        "months": [3, 4],
    },
    {
        "id": "voortrekken",
        "title": "Voortrekken in pot",
        "text": "Trek knollen vroeg binnen voor in een pot (±2 liter, lichte compost, knol licht bedekt). Houd ze vorstvrij rond 7-8 °C en licht vochtig (niet nat — dat geeft rot). Zodra groene scheuten komen hebben ze direct daglicht nodig, anders worden ze wit en slap. Voortrekken beschermt jonge planten later tegen vroege slakkenvraat.",
        "category": "voorjaar",
        "months": [3, 4],
    },
    {
        "id": "afharden",
        "title": "Afharden",
        "text": "Zijn de scheuten ~4 cm? Hard de planten af: overdag naar buiten, vóór de nacht weer naar binnen. Zo wennen ze aan buiten en zijn ze minder kwetsbaar voor nachtvorst en slakken.",
        "category": "voorjaar",
        "months": [4],
    },
    {
        "id": "uitplanten",
        "title": "Uitplanten",
        "text": "Plant de dahlia's definitief in de tuin of bak zodra alle kans op nachtvorst voorbij is en de nachttemperatuur stabiel blijft. Geen voorgetrokken planten? Dan kan de droge knol nu direct de grond in.",
        "category": "voorjaar",
        "months": [5],
    },
    {
        "id": "opstart-slakken",
        "title": "Slakkenbescherming",
        "text": "Nu de eerste groene puntjes boven komen, zijn ze het kwetsbaarst voor slakken. Bescherm ze met koperstape of koperen ringen, een barrière van vaseline met zout, aaltjes (nematoden), of raap ze 's avonds handmatig.",
        "category": "opstart",
        "months": [4, 5, 6],
    },
    {
        "id": "opstart-vocht",
        "title": "Niet te nat",
        "text": "Houd de grond matig vochtig. Te natte grond kan de startende knol laten rotten.",
        "category": "opstart",
        "months": [4, 5, 6],
    },
    # --- growth: pinch, thin, feed, support ---
    {
        "id": "toppen",
        "title": "Toppen / pinceren",
        "text": "Zodra een scheut flink hoog is (~20-45 cm) en voldoende setjes echte bladeren heeft: knijp de bovenste groeitop eruit. De plant vertakt dan en wordt voller met veel meer bloemknoppen. Niet te vroeg toppen — de plant heeft eerst bladeren nodig om energie op te nemen.",
        "category": "groei",
        "months": [5, 6, 7],
    },
    {
        "id": "uitdunnen",
        "title": "Scheuten uitdunnen",
        "text": "Heeft een knol heel veel scheuten (bijv. 9-10)? Dun uit tot 5-7 sterke stengels. Dat voorkomt dat de knol uitgeput raakt en geeft grotere bloemen. Overtollige scheuten kun je eventueel stekken.",
        "category": "groei",
        "months": [6, 7],
    },
    {
        "id": "voeding",
        "title": "Voeding",
        "text": "Vanaf ~30 cm hoogte: geef elke twee weken vloeibare plantenvoeding (bijv. biologische tomaten- of terrasplantenvoeding).",
        "category": "groei",
        "months": [6, 7, 8],
    },
    {
        "id": "opbinden",
        "title": "Opbinden & ondersteunen",
        "text": "De planten schieten omhoog. Bind de hoofdstengels losjes vast met zacht binddraad of jute aan stokken, ringen of een trellis, zodat ze niet insnoeren en niet omwaaien.",
        "category": "groei",
        "months": [7, 8, 9],
    },
    # --- bloom ---
    {
        "id": "deadheaden",
        "title": "Deadheaden",
        "text": "Knip uitgebloeide bloemen consequent weg, vlak boven de eerste lagere zijtak met bladeren. Zo blijft de plant nieuwe knoppen maken in plaats van zaad. Knop = rond en hard; uitgebloeid = spitser en zacht. Bloemen voor in een vaas knippen bevordert óók nieuwe bloei.",
        "category": "bloei",
        "months": [8, 9, 10],
    },
    # --- end of season: lift, label, store ---
    {
        "id": "winter-vorst",
        "title": "Wachten op nachtvorst",
        "text": "Doe niets tot de eerste echte nachtvorst. Het loof wordt zwart; de plant trekt dan de laatste suikers terug in de knol.",
        "category": "winter",
        "months": [10, 11],
    },
    {
        "id": "rooien",
        "title": "Afknippen & rooien",
        "text": "Knip dode stengels tot 10-15 cm boven de grond. Graaf de knollen voorzichtig op; trek nooit aan de stengels — de nekjes breken snel en een afgebroken knol loopt niet meer uit.",
        "category": "winter",
        "months": [11],
    },
    {
        "id": "labelen",
        "title": "Labelen",
        "text": "Label de knollen meteen bij het rooien met de juiste soort. In deze tool kun je het QR-label van een plant printen en erbij bewaren, zodat je volgend jaar precies weet wat wat is.",
        "category": "winter",
        "months": [11],
    },
    {
        "id": "opslag",
        "title": "Winteropslag",
        "text": "Maak de knollen voorzichtig schoon en laat ze een paar dagen ondersteboven drogen op een vorstvrije plek. Leg ze ondersteboven in kratten of dozen met droge potgrond, zaagsel, houtkrullen of kranten. Bewaar donker, koel en vorstvrij (5-10 °C).",
        "category": "winter",
        "months": [11, 12],
    },
]


def tips_for_month(month: int) -> list[dict]:
    return [tip for tip in _TIPS if month in tip["months"]]
