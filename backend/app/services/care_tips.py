"""Seasonal dahlia care tips, derived from Dahlia_Verzorgingsgids_Bak.md.

Each tip lists the months (1-12) in which it is relevant, so the app can show
"what to do now" for the current month.
"""

_TIPS = [
    {
        "id": "basis-zon",
        "title": "Zon",
        "text": "Zet de bak op een plek met minstens 6 uur zon per dag. Dahlia's zijn echte zonaanbidders.",
        "category": "basis",
        "months": list(range(1, 13)),
    },
    {
        "id": "basis-water",
        "title": "Water geven",
        "text": "Houd de grond licht vochtig en geef water aan de basis van de plant, niet op het blad (voorkomt schimmels). Potgrond in een bak droogt sneller uit — op warme dagen dagelijks controleren.",
        "category": "basis",
        "months": [5, 6, 7, 8, 9],
    },
    {
        "id": "opstart-slakken",
        "title": "Slakkenbescherming",
        "text": "Nu de eerste groene puntjes boven komen zijn ze het kwetsbaarst. Breng koperstape aan rond de bovenrand van de bak, of een barrière van vaseline met zout.",
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
    {
        "id": "toppen",
        "title": "Toppen / pinceren",
        "text": "Zodra een scheut ~20 cm hoog is en 3-4 setjes bladeren heeft: knijp de bovenste groeitop eruit. De plant vertakt dan en wordt voller met veel meer bloemknoppen.",
        "category": "groei",
        "months": [5, 6],
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
        "title": "Opbinden aan trellis",
        "text": "De planten schieten omhoog. Bind de hoofdstengels losjes vast met zacht binddraad of jute, zodat ze niet insnoeren en niet omwaaien.",
        "category": "groei",
        "months": [7, 8],
    },
    {
        "id": "deadheaden",
        "title": "Deadheaden",
        "text": "Knip uitgebloeide bloemen consequent weg, vlak boven de eerste lagere zijtak met bladeren. Zo blijft de plant bloemen maken in plaats van zaad. Knop = rond en hard; uitgebloeid = spitser en zacht.",
        "category": "bloei",
        "months": [8, 9, 10],
    },
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
        "id": "opslag",
        "title": "Winteropslag",
        "text": "Laat de knollen een paar dagen ondersteboven drogen op een vorstvrije plek. Pak ze in een doos met droge potgrond, turf of kranten. Bewaar donker, koel en vorstvrij (5-10 °C).",
        "category": "winter",
        "months": [11, 12, 1, 2, 3],
    },
]


def tips_for_month(month: int) -> list[dict]:
    return [tip for tip in _TIPS if month in tip["months"]]
