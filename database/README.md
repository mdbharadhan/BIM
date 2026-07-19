# Database Module (Team 3)

Stores and manages BIM project data as JSON or SQLite. This is what Team 1
(Backend) should import — nobody else needs to touch `storage.py` directly.

## Structure

```
database/
├── __init__.py      # public API — import from here
├── models.py         # Project > Building > Floor > Room > BIMObject dataclasses
├── storage.py         # JSONStorage + SQLiteStorage (internal, same interface)
├── db_manager.py      # DatabaseManager — the facade everyone else calls
├── sample_data.py     # build_sample_project() — fake data for dev/demo
└── data/               # created at runtime, holds the .json / .db files (gitignored)
```

## Data hierarchy

Matches the BIM report's object model:

```
Project → Building → Floor → Room → BIMObject (Wall/Door/Window/...) → properties
```

Each `BIMObject` carries the fields from the report's "Wall Object" info card:
`material, length, height, thickness, fire_rating, thermal_properties,
structural_properties, cost, manufacturer, installation_date,
maintenance_schedule, coordinates, relationships`, plus a free-form
`extra_properties` dict for anything discipline-specific.

## Integration notes for other teams

- **Everyone gets the same database automatically.** Paths default to
  `BIM_Project/data/`, anchored to this package's location — not to
  whatever folder you happened to launch a script from. So Team 1's
  backend code, Team 2's Streamlit app, and Team 4's tests all read/write
  the same `data/bim_project.db` without any path configuration.
- **`db.get_sample_project()`** is the easiest way for frontend/backend to
  get *something* to render on day one — no need to call
  `list_projects()` first to find an ID. It creates the sample project on
  first call and just re-loads it after that.
- **Sample data is safe to regenerate.** `load_sample_data()` always
  writes to the same fixed id (`sample-project-001`), so calling it
  repeatedly (e.g. every time the Streamlit app starts) overwrites the
  same record instead of piling up duplicates.

## Quick start

```python
from database import DatabaseManager

# Pick a backend. Use "sqlite" if you want to run search queries,
# use "json" if you just want simple human-readable files.
db = DatabaseManager(backend="sqlite")

# Get some data to work with immediately:
project = db.load_sample_data()

# Save / load a project:
db.save_project(project)
same_project = db.load_project(project.id)

# List all saved projects (id + name only):
db.list_projects()

# Search (SQLite backend only) — powers things like the report's
# "show all fire-rated doors" AI query example:
doors = db.search_objects(type="Door")
fire_rated_doors = db.search_objects(type="Door", fire_rating__not_null=True)
```

## Building your own project data

```python
from database import Project, Building, Floor, Room, BIMObject

project = Project(name="My Building")
building = Building(name="Tower A")
floor = Floor(name="Ground Floor", level=0)
room = Room(name="Lobby", area=100.0)
room.add_object(BIMObject(type="Door", name="Main Door", fire_rating="FD30"))
floor.add_room(room)
building.add_floor(floor)
project.add_building(building)
```

## Notes / edge cases to keep in mind (see BIM_edge_cases.pdf)

- **Data quality is on us, not the tool.** Nothing here validates that a
  contractor entered the right fire rating — garbage in, garbage out. If
  Team 1 wants validation (e.g. required fields, valid fire-rating codes),
  that logic belongs in the backend layer before it hits `save_project()`.
- **SQLite backend does a full delete-and-reinsert on `save_project()`.**
  Fine for a single-editor student project; not safe for concurrent
  multi-user edits (that's the "version conflicts" problem the edge-cases
  doc calls out — not solved here, just flagged).
- **`search_objects()` only works on the SQLite backend.** If you're on
  JSON storage, load the `Project` and filter its `.buildings/.floors/.rooms.objects`
  in plain Python instead.
- No external dependencies — everything uses Python's standard library
  (`json`, `sqlite3`, `dataclasses`), so there's nothing to `pip install`.

## Running the demo yourself

```bash
cd database
python3 demo.py
```

This creates a sample project, saves/reloads it through both backends,
and runs a search for fire-rated doors — a quick sanity check that
everything is wired up correctly.
