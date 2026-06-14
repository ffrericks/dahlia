# ARCHITECT.md — Dahlia Tool

## Project overview

A self-hosted web app for tracking the care and propagation of dahlias. It manages varieties, photos, tuber splits and seedlings (with a full lineage/family tree), planting locations (garden spots, pots, and multi-plant "bakken"), inventory (planted vs. stored vs. discarded/given away), and per-plant logs (height, buds, flowers, harvest). All data is browsable per plant, variety, and location so you can see at season's end which spot grew best. Ships as a single Docker container via GitHub.

## Build vs. buy

| Option | Verdict |
|--------|---------|
| Generic plant tracker (e.g. Planta, garden journal apps) | **Rejected.** None model tuber splitting, seedling lineage, or pot/bak identity. The whole point is dahlia-specific propagation tracking. |
| Spreadsheet | **Rejected.** Can't do photos-per-lineage, location grouping, or genealogy cleanly. |
| Headless CMS (Directus/Strapi) | **Rejected.** Generic data admin, no domain logic for lineage rules or season comparisons. Heavier to self-host than a focused app. |
| **Custom build** | **Chosen.** The domain model (lineage, splits, pot/bak, inventory states) is the product. Small enough for one person to own. |

**Decision: build.** The domain rules are the value; off-the-shelf tools can't express them.

## Tech stack decision + rationale

| Layer | Choice | Why |
|-------|--------|-----|
| Backend | **Python + FastAPI** | Fast to build, great for a clear domain model, easy SQLite + image handling. |
| Database | **SQLite** (single file) | Personal use, home network. One file = trivial manual back-up (copy the file). No DB server to run. |
| ORM/migrations | **SQLModel + Alembic** | Type-safe models, versioned schema changes as the model grows. |
| Frontend | **React + Vite + TypeScript** | Responsive UI that works equally well on phone and desktop (your answer: both). |
| UI styling | **Tailwind CSS** | Fast, mobile-first responsive layout. |
| Photos | **Filesystem on a mounted volume** | Multiple photos per plant; one is marked the "profile" photo that also represents the variety. Images are **downscaled on upload** to save space, plus a thumbnail. Simple back-up = copy the folder. |
| Packaging | **Single Docker image** (FastAPI serves the built React app + API) | One container, one volume. Matches "Docker via GitHub". |
| CI/Distribution | **GitHub Actions → GitHub Container Registry (ghcr.io)** | Push builds the image automatically; you pull and run it at home. |
| Auth | **None** | Home-network only (your answer). Keeps setup minimal. |

**Why this shape:** one container, one data volume (SQLite file + photo folder). Personal scale means no need for Postgres, object storage, or accounts. Manual back-up is "copy one folder" — which matches your back-up preference.

## Key constraints

- **Single container, single volume.** Everything (DB + photos) lives under one mounted directory for easy back-up.
- **Home network only, no login.** Do not expose to the internet without adding auth first.
- **Responsive-first.** Every screen must be usable one-handed on a phone in the garden *and* comfortable on desktop.
- **Manual back-up model.** No automated back-up in scope; data layout must make a manual copy trivial.
- **Lineage is core.** Splits, seedlings, and the full family tree are first-class — not an afterthought.
- **Errors visible.** No silent fallbacks or swallowed errors (per project rules).

## Domain model (core entities)

- **Variety (Soort)** — a named dahlia type with a unique **3-letter code** (e.g. `WIT`), chosen at registration. Must be registered before any plant. Its display photo is the **profile photo** of one of its plants.
- **Photo** — belongs to a Plant; many photos per plant. One photo per plant can be flagged `is_profile`; that profile photo also serves as the variety's representative image. Stored downscaled + a thumbnail.
- **Plant** — a concrete plant/tuber instance belonging to a Variety, with a 5-digit `SSDDD` number (see Identifiers) that it keeps for life. Has an optional `parent_plant_id` (lineage) and an `origin` type:
  - `split` — same variety, next `DDD` within the parent's stam, inherits/shares the parent's profile photo.
  - `seedling` — becomes a *new* Variety (possibly unnamed) with its own photos and its own `01000`, still linked to the parent plant.
  - `purchased` / `gifted` — bought from a grower or received from someone. **No `parent_plant_id`**; starts a fresh stam (`SS`) in its variety (or a new variety). The UI must not ask for a mother plant in this case.
  - State: `stored`, `planted`, `discarded`, `given_away`, `survived_winter`.
  - `eye_status` (relevant while `stored`/early spring): `awaiting_eye`, `has_eye`, or `blind`. A blind tuber (no growth point) is flagged as a likely discard candidate; "has eye" = woken up and ready to plant.
  - `disease_warning` — optional flag set when discarding for disease (see Disease handling).
- **Lineage** — the parent/child links across Plants form the full family tree (your answer: full tree).
- **Location** — a `garden_spot` (`T##`), a `pot`/`bak` (`B##`). For a **bak, the position of each plant inside it is recorded** (e.g. front/back, slot). A pot becomes an item when first used; reused-or-new is chosen at planting time. Garden spots and bakken/pots **persist as empty locations** when emptied.
- **StorageBox (Doos)** — a winter-storage box coded `D` + number + 2-digit year (e.g. `D0126`). A `stored` plant/tuber records its box. A box **disappears once all its tubers are planted out**.
- **Season** — a plant's season starts at planting and ends at lifting (rooien). A **global "new season" rollover is an explicit, gated action**: it is blocked while any plant is still `planted`; each must be discarded or marked `survived_winter` (becoming the first plant of the new season).
- **Planting** — links a Plant to a Location, from planting date to lifting date (preserves per-season location history; with bak position when applicable). Plantings are never deleted, so each plant has a **full multi-year history**: every location it has stood and how it performed each year (see Insights).
- **LogEntry** — per planted Plant: text + optional height, bud count, flower count, harvested-flower count, date. "Did not come up" = a log event that sets state to `discarded`.
- **Disposal record** — discard or give-away; give-away stores a recipient name, feeding the "how many descendants total / how many still owned" log. A discard can carry a **`disease_warning`** with a reason (e.g. dahlia mosaic virus, leafy gall / crown gall). Disease discards are flagged as "bin, not compost" and prompt tool-hygiene (don't reuse the same shears on other dahlias).

## Identifiers & numbering scheme

Every plant has a unique, human-readable code that also encodes its full placement, so any plant is traceable from its label.

**Variety code** — 3 letters, chosen at registration. Example: `WIT` (a white dahlia). A variety must be registered before any plant.

**Plant number** — 5 digits, `SSDDD`:
- `SS` = the stam (founder) index within the variety: `01`, `02`, `03`, …
- `DDD` = descendant counter within that stam: `000` = the stam plant itself, `001`–`999` = its descendants (max 999).
- The first plant registered on a variety is `01000`; its descendants run `01001`–`01999` (the `01` stays fixed). The next registered plant is `02000`, descendants `02001`–`02999`, and so on.
- Full plant code = variety + plant number, e.g. **`WIT01000`**.
- A plant **keeps its own number for life** — including when it survives the winter into a new season.

**Location codes** (suffix appended to the plant code while the plant lives there):
- `T` + 2 digits = a garden spot (tuin), e.g. `T01`.
- `B` + 2 digits = a pot or bak, e.g. `B01`.
- `D` + box-number + last 2 digits of the year = a winter storage box (doos), e.g. `D0126` = box 01 in 2026.

**Composite tracking code** — plant code + current placement code. Example: `WIT01000` stored in box 01 at the end of 2026 → **`WIT01000D0126`**. The same applies for garden/pot placement (e.g. `WIT01000B01`). This composite is the label you can always trace back to one plant.

## Lifecycle rules

- **Eye check in storage / early spring.** A stored tuber tracks its `eye_status` (`awaiting_eye` → `has_eye` or `blind`). In spring you can see at a glance which tubers have woken up and which blind ones can be thrown away.
- **Taking a plant out of the box** offers two paths:
  - **Replant as a complete clump (tros)** — survives winter, keeps its *same* number; it simply grew larger underground, no new `DDD` is created.
  - **Split into new numbers** — create one or more new `split` plants (next `DDD`) from the clump.
- **Disease handling.** When a plant is discarded for disease, set `disease_warning` with the reason. The family tree then **highlights its siblings in red** (e.g. discarding `WIT01002` for gall flags `WIT01001` and `WIT01003`) so you watch them for symptoms. Such discards are marked "bin, not compost".
- A **storage box (doos) disappears** from the system once all its tubers have been planted out.
- **Garden spots and bakken/pots never disappear** — when emptied they remain as empty locations, reusable next season.
- **Starting a new season is gated:** you cannot start a new season while any plant is still `planted`. Each such plant must first be resolved:
  - discarded, **or**
  - marked as "survived the winter" — it then becomes the first plant of the new season.

## Development phases

## Phase 1: Foundation
Repo, Dockerfile, FastAPI + SQLite + React skeleton, single-container build, GitHub Actions publishing to ghcr.io. App runs and serves an empty UI.

## Phase 2: Varieties & photos
Register varieties with a unique 3-letter code, upload multiple photos per plant with downscaling + thumbnails, mark a profile photo (used as the variety image), browse the variety list.

## Phase 3: Plants, numbering, inventory & lineage
Create plants with auto-assigned `SSDDD` numbers via any origin — split (next `DDD`, share profile photo), seedling (new, possibly unnamed variety + new photos), or purchased/gifted (no mother plant, fresh stam). View the full family tree and inventory counts.

## Phase 4: Locations & plantings
Garden spots, pots, and bakken with per-plant position inside the bak. Plant a plant into a location (starts its season); new-vs-existing pot choice; per-season planting history.

## Phase 5: Winter rest, storage & season rollover
Lifting tubers (ends the season), eye-status tracking (awaiting/has-eye/blind), splitting during winter, assigning stored tubers to year-coded boxes (`D####`). Taking a plant out offers "replant as complete clump (same number)" or "split into new numbers". Gated "new season" rollover (resolve every still-planted plant first). Boxes vanish when emptied.

## Phase 6: Logbook, disposal & disease
Per-plant log entries (height, buds, flowers, harvest). "Did not come up" → discarded. Discard/give-away with recipient name and descendant tallies. A plant that dies or leaves is **never hard-deleted** — even a stam plant with descendants is marked via status, so it **disappears from the active plant list but stays in the family tree** (lineage stays intact). Disease discards set a warning (reason + "bin, not compost") that highlights siblings in red in the family tree.

## Phase 7: Insights & season comparison
Browse all data per plant / variety / location. **Per-plant multi-year history**: every location it has stood and how it performed each year. End-of-season view ranking which spot/bak grew best, by a combined score (height + flowers + harvested flowers) with **user-adjustable selection/weighting** of which metrics count.

## Folder structure

```
dahlia/
├── ARCHITECT.md
├── README.md
├── docker-compose.yml          # one service, one volume
├── Dockerfile                  # builds frontend, packages with backend
├── .github/workflows/
│   └── build.yml               # build + push image to ghcr.io
├── backend/
│   ├── app/
│   │   ├── main.py             # FastAPI app, serves API + static frontend
│   │   ├── models/             # SQLModel entities (variety, plant, location, log…)
│   │   ├── schemas/            # request/response models
│   │   ├── routers/            # variety, plant, photo, location, planting, storage, log, insights
│   │   ├── services/           # lineage rules, inventory, photo handling, season stats
│   │   └── db.py               # SQLite connection
│   ├── migrations/             # Alembic
│   ├── tests/                  # pytest — unit tests for lineage & stats logic
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── pages/              # varieties, plants, tree, locations, logbook, insights
│   │   ├── components/
│   │   ├── api/                # typed API client
│   │   └── main.tsx
│   ├── index.html
│   └── package.json
└── data/                       # MOUNTED VOLUME (gitignored)
    ├── dahlia.db               # SQLite file
    └── photos/                 # originals + thumbnails
```

## Resolved decisions

- **Devices:** equally important on phone and desktop → responsive-first.
- **Access:** home network only, no login. Not designing for future internet access (kept simple).
- **Back-up:** manual (copy one folder); no automated back-up in scope.
- **Lineage:** full family tree, first-class.
- **Photos:** multiple per plant, one profile photo per plant doubles as the variety image; images downscaled on upload.
- **Season:** starts at planting, ends at lifting (rooien); the "new season" rollover is gated on resolving all planted plants.
- **Storage:** year-coded boxes (`D` + number + 2-digit year); a box disappears when emptied. Garden/bak locations persist when emptied.
- **Seedlings:** new variety may stay unnamed until it proves itself; gets its own `0100`.
- **Bak:** record each plant's position inside the bak.
- **Identifiers:** variety = 3-letter code; plant = `SSDDD` (2-digit stam + 3-digit descendant, up to 999 descendants); full traceable code = variety + plant number + placement code (e.g. `WIT01000D0126`).
- **Plant numbers are permanent:** a plant keeps its number for life, including after surviving the winter.
- **Lifting (rooien):** done per individual plant (no bulk lift).
- **Boxes:** registered fresh each winter (year-coded, not reused across years).
- **"Best spot" ranking:** combined score across height + total flowers + harvested flowers, with a user-adjustable metric selection.
- **History:** every plant has a full multi-year record of where it stood and how it performed each year.
- **Origins:** plants can also be `purchased` or `gifted` — no mother plant, starts a fresh stam; the UI skips the parent prompt.
- **Blind tubers:** stored tubers track `eye_status` (awaiting / has-eye / blind) so spring shows what woke up vs. what to discard.
- **Clump vs. split:** out of the box, a plant can be replanted whole (same number, no new code) or split into new `DDD` numbers.
- **Disease:** disease discards flag the reason, mark "bin, not compost", and highlight siblings in red in the family tree.
- **Death / leaving (Phase 6):** a dead or removed plant is taken out of the system by a **status change, not deletion** — it drops out of the active plant list (no longer counted) but remains in the family tree for history. This applies even to a stam plant that still has descendants. The active plant list = plants not in a "gone" state.

## Open questions

None — all design decisions are settled (see Resolved decisions). Numbering capacity (99 stams × 999 descendants per variety) is years away and treated as a hard limit; revisit only if ever approached.
```
