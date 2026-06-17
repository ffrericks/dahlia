from collections import defaultdict

from sqlmodel import Session, select

from ..models import LogEntry, Plant, Planting, Variety
from .care_tips import tips_for_month
from .insights import planting_metrics
from .numbering import format_number

_ORIGIN_ACQUIRED = {
    "purchased": "gekocht",
    "gifted": "gekregen",
    "unknown": "verkregen (herkomst onbekend)",
}
_MONTHS_NL = [
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]


def _label(session: Session, plant: Plant) -> str:
    variety = session.get(Variety, plant.variety_id) if plant.variety_id else None
    if variety and plant.ss is not None and plant.ddd is not None:
        return f"{variety.code}{format_number(plant.ss, plant.ddd)}"
    return plant.nickname or "Onbekend"


def _root_and_generation(session: Session, plant: Plant) -> tuple[Plant, int]:
    """Walk up the lineage to the founder; return (root, generations from root)."""
    generation = 0
    current = plant
    while current.parent_plant_id is not None:
        parent = session.get(Plant, current.parent_plant_id)
        if parent is None:
            break
        current = parent
        generation += 1
    return current, generation


def _line_plant_ids(session: Session, root_id: int) -> list[int]:
    """The whole family line: the root and all its (transitive) descendants."""
    children: dict[int, list[int]] = defaultdict(list)
    for pid, parent_id in session.exec(select(Plant.id, Plant.parent_plant_id)).all():
        if parent_id is not None:
            children[parent_id].append(pid)
    ids = [root_id]
    stack = [root_id]
    while stack:
        for child in children[stack.pop()]:
            ids.append(child)
            stack.append(child)
    return ids


def _earliest_year(session: Session, plant_id: int) -> int | None:
    planted = session.exec(
        select(Planting.planted_on).where(Planting.plant_id == plant_id)
    ).all()
    logged = session.exec(
        select(LogEntry.entry_date).where(LogEntry.plant_id == plant_id)
    ).all()
    dates = list(planted) + list(logged)
    return min(d.year for d in dates) if dates else None


def _chain(session: Session, plant: Plant) -> list[str]:
    """Labels from the root down to this plant."""
    labels = [_label(session, plant)]
    current = plant
    while current.parent_plant_id is not None:
        parent = session.get(Plant, current.parent_plant_id)
        if parent is None:
            break
        labels.append(_label(session, parent))
        current = parent
    return list(reversed(labels))


def build_plant_summary(session: Session, plant_id: int) -> tuple[str, str]:
    """Build a hand-over text: lineage, line averages and care tips. Returns (filename, text)."""
    plant = session.get(Plant, plant_id)
    if plant is None:
        raise ValueError("Plant niet gevonden.")

    label = _label(session, plant)
    variety = session.get(Variety, plant.variety_id) if plant.variety_id else None
    root, generation = _root_and_generation(session, plant)

    # Stats across the whole line.
    line_ids = _line_plant_ids(session, root.id)
    heights: list[int] = []
    flowers: list[int] = []
    harvested_total = 0
    seasons = 0
    for pid in line_ids:
        for planting in session.exec(
            select(Planting).where(Planting.plant_id == pid)
        ).all():
            metrics = planting_metrics(session, planting)
            if metrics["height_max"] is not None:
                heights.append(metrics["height_max"])
            if metrics["flowers_max"] is not None:
                flowers.append(metrics["flowers_max"])
            harvested_total += metrics["harvested_total"]
            seasons += 1

    year = _earliest_year(session, root.id)
    acquired = _ORIGIN_ACQUIRED.get(root.origin, "verkregen")

    lines: list[str] = []
    title = f"Stamboom & geschiedenis — {label}"
    if variety and variety.name:
        title += f" ({variety.name})"
    lines.append(title)
    lines.append("=" * len(title))
    lines.append("")

    if variety and variety.description:
        lines.append("Over de soort:")
        lines.append(variety.description)
        lines.append("")

    if year:
        lines.append(
            f"Herkomst: deze lijn begon met een knol die rond {year} is {acquired}."
        )
    else:
        lines.append(f"Herkomst: de oorspronkelijke knol is {acquired}.")

    if generation == 0:
        lines.append("Dit is de oorspronkelijke plant/knol van deze lijn.")
    else:
        lines.append(f"Dit is de {generation}e generatie afstammeling in deze lijn.")
    lines.append(f"Afstammingslijn: {' -> '.join(_chain(session, plant))}")
    lines.append("")

    plural = "plant" if len(line_ids) == 1 else "planten"
    lines.append(
        f"Over deze lijn ({len(line_ids)} {plural}, {seasons} seizoen(en) met metingen):"
    )
    if heights:
        lines.append(f"- Gemiddelde hoogte: {round(sum(heights) / len(heights))} cm")
    if flowers:
        lines.append(
            f"- Gemiddeld aantal bloemen (piek): {round(sum(flowers) / len(flowers))} per seizoen"
        )
    if harvested_total:
        lines.append(f"- Totaal geoogste bloemen in deze lijn: {harvested_total}")
    if not (heights or flowers or harvested_total):
        lines.append("- Nog geen metingen vastgelegd.")
    lines.append("")

    # Care across the growing season (planting -> lifting) plus winter storage.
    # Progressive dedup: each tip is listed only the first time it becomes relevant.
    lines.append("Verzorging door het seizoen:")
    seen: set[str] = set()

    def take_new(tips: list[dict]) -> list[str]:
        fresh: list[str] = []
        for tip in tips:
            if tip["title"] not in seen:
                seen.add(tip["title"])
                fresh.append(tip["title"])
        return fresh

    basics = take_new(
        [t for m in range(5, 11) for t in tips_for_month(m) if t["category"] == "basis"]
    )
    if basics:
        lines.append(f"- Hele seizoen: {', '.join(basics)}")

    for m in range(5, 11):  # mei (planten) t/m oktober (rooien)
        titles = take_new([t for t in tips_for_month(m) if t["category"] != "basis"])
        if titles:
            lines.append(f"- {_MONTHS_NL[m - 1].capitalize()}: {', '.join(titles)}")

    winter = take_new([t for m in (11, 12, 1, 2) for t in tips_for_month(m)])
    if winter:
        lines.append(f"- Winterberging: {', '.join(winter)}")

    lines.append("")
    lines.append("Gemaakt met Dahlia Tool.")

    filename = f"dahlia-{label}-samenvatting.txt"
    return filename, "\n".join(lines) + "\n"
