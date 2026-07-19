"""
storage.py
----------
Two interchangeable storage backends for BIM project data:

  * JSONStorage   - one .json file per project. Simple, human-readable,
                    good for early development / small models.
  * SQLiteStorage - normalized tables (projects, buildings, floors, rooms,
                    objects) so Team 1 (backend) can run real SQL search
                    queries, e.g. "all fire-rated doors" from the report's
                    AI query example.

Both expose the same basic methods so db_manager.py can swap between them
without changing calling code:

    save_project(project) -> None
    load_project(project_id) -> Project | None
    list_projects() -> list[dict]   # id + name summaries
    delete_project(project_id) -> bool
"""
from __future__ import annotations
import json
import os
import sqlite3
from typing import List, Dict, Any, Optional

try:
    from .models import Project, Building, Floor, Room, BIMObject
    from .constants import JSON_STORE_DIR, SQLITE_PATH
except ImportError:  # allows running this file directly from inside database/
    from models import Project, Building, Floor, Room, BIMObject
    from constants import JSON_STORE_DIR, SQLITE_PATH


# ---------------------------------------------------------------------------
# JSON storage
# ---------------------------------------------------------------------------
class JSONStorage:
    def __init__(self, directory: str = JSON_STORE_DIR):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def _path(self, project_id: str) -> str:
        return os.path.join(self.directory, f"{project_id}.json")

    def save_project(self, project: Project) -> None:
        with open(self._path(project.id), "w", encoding="utf-8") as f:
            json.dump(project.to_dict(), f, indent=2)

    def load_project(self, project_id: str) -> Optional[Project]:
        path = self._path(project_id)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return Project.from_dict(json.load(f))

    def list_projects(self) -> List[Dict[str, Any]]:
        summaries = []
        for fname in os.listdir(self.directory):
            if fname.endswith(".json"):
                with open(os.path.join(self.directory, fname), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    summaries.append({"id": data.get("id"), "name": data.get("name")})
        return summaries

    def delete_project(self, project_id: str) -> bool:
        path = self._path(project_id)
        if os.path.exists(path):
            os.remove(path)
            return True
        return False


# ---------------------------------------------------------------------------
# SQLite storage
# ---------------------------------------------------------------------------
_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT,
    description TEXT
);

CREATE TABLE IF NOT EXISTS buildings (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    name TEXT,
    address TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS floors (
    id TEXT PRIMARY KEY,
    building_id TEXT,
    name TEXT,
    level INTEGER,
    FOREIGN KEY(building_id) REFERENCES buildings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rooms (
    id TEXT PRIMARY KEY,
    floor_id TEXT,
    name TEXT,
    area REAL,
    FOREIGN KEY(floor_id) REFERENCES floors(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS objects (
    id TEXT PRIMARY KEY,
    room_id TEXT,
    type TEXT,
    name TEXT,
    material TEXT,
    length REAL,
    height REAL,
    thickness REAL,
    fire_rating TEXT,
    thermal_properties TEXT,
    structural_properties TEXT,
    cost REAL,
    manufacturer TEXT,
    installation_date TEXT,
    maintenance_schedule TEXT,
    coord_x REAL,
    coord_y REAL,
    coord_z REAL,
    relationships_json TEXT,
    extra_json TEXT,
    FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE
);
"""


class SQLiteStorage:
    def __init__(self, db_path: str = SQLITE_PATH):
        os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
        self.db_path = db_path
        # check_same_thread=False: Streamlit can hand session state (and
        # anything stored on it, like a DatabaseManager) to a different
        # thread than the one that created it. Safe here because our
        # writes are short, single-statement-block transactions — not
        # meant for real concurrent multi-user writes (see README).
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()

    # -- save (full replace of a project's tree) --------------------------
    def save_project(self, project: Project) -> None:
        cur = self.conn.cursor()
        # Wipe out any existing rows for this project, then re-insert.
        cur.execute("DELETE FROM projects WHERE id = ?", (project.id,))
        cur.execute(
            "INSERT INTO projects (id, name, description) VALUES (?, ?, ?)",
            (project.id, project.name, project.description),
        )
        for building in project.buildings:
            cur.execute(
                "INSERT INTO buildings (id, project_id, name, address) VALUES (?, ?, ?, ?)",
                (building.id, project.id, building.name, building.address),
            )
            for floor in building.floors:
                cur.execute(
                    "INSERT INTO floors (id, building_id, name, level) VALUES (?, ?, ?, ?)",
                    (floor.id, building.id, floor.name, floor.level),
                )
                for room in floor.rooms:
                    cur.execute(
                        "INSERT INTO rooms (id, floor_id, name, area) VALUES (?, ?, ?, ?)",
                        (room.id, floor.id, room.name, room.area),
                    )
                    for obj in room.objects:
                        coords = obj.coordinates or {}
                        cur.execute(
                            """INSERT INTO objects (
                                id, room_id, type, name, material, length, height,
                                thickness, fire_rating, thermal_properties,
                                structural_properties, cost, manufacturer,
                                installation_date, maintenance_schedule,
                                coord_x, coord_y, coord_z, relationships_json, extra_json
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (
                                obj.id, room.id, obj.type, obj.name, obj.material,
                                obj.length, obj.height, obj.thickness, obj.fire_rating,
                                obj.thermal_properties, obj.structural_properties,
                                obj.cost, obj.manufacturer, obj.installation_date,
                                obj.maintenance_schedule, coords.get("x"), coords.get("y"),
                                coords.get("z"), json.dumps(obj.relationships),
                                json.dumps(obj.extra_properties),
                            ),
                        )
        self.conn.commit()

    # -- load (rebuild the full tree) --------------------------------------
    def load_project(self, project_id: str) -> Optional[Project]:
        cur = self.conn.cursor()
        prow = cur.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        if prow is None:
            return None
        project = Project(id=prow["id"], name=prow["name"], description=prow["description"])

        for brow in cur.execute("SELECT * FROM buildings WHERE project_id = ?", (project_id,)):
            building = Building(id=brow["id"], name=brow["name"], address=brow["address"])
            for frow in cur.execute("SELECT * FROM floors WHERE building_id = ?", (brow["id"],)):
                floor = Floor(id=frow["id"], name=frow["name"], level=frow["level"])
                for rrow in cur.execute("SELECT * FROM rooms WHERE floor_id = ?", (frow["id"],)):
                    room = Room(id=rrow["id"], name=rrow["name"], area=rrow["area"])
                    for orow in cur.execute("SELECT * FROM objects WHERE room_id = ?", (rrow["id"],)):
                        coords = None
                        if orow["coord_x"] is not None or orow["coord_y"] is not None or orow["coord_z"] is not None:
                            coords = {"x": orow["coord_x"], "y": orow["coord_y"], "z": orow["coord_z"]}
                        obj = BIMObject(
                            id=orow["id"], type=orow["type"], name=orow["name"],
                            material=orow["material"], length=orow["length"],
                            height=orow["height"], thickness=orow["thickness"],
                            fire_rating=orow["fire_rating"],
                            thermal_properties=orow["thermal_properties"],
                            structural_properties=orow["structural_properties"],
                            cost=orow["cost"], manufacturer=orow["manufacturer"],
                            installation_date=orow["installation_date"],
                            maintenance_schedule=orow["maintenance_schedule"],
                            coordinates=coords,
                            relationships=json.loads(orow["relationships_json"] or "[]"),
                            extra_properties=json.loads(orow["extra_json"] or "{}"),
                        )
                        room.add_object(obj)
                    floor.add_room(room)
                building.add_floor(floor)
            project.add_building(building)
        return project

    def list_projects(self) -> List[Dict[str, Any]]:
        cur = self.conn.cursor()
        rows = cur.execute("SELECT id, name FROM projects").fetchall()
        return [{"id": r["id"], "name": r["name"]} for r in rows]

    def delete_project(self, project_id: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        self.conn.commit()
        return cur.rowcount > 0

    # -- search: direct SQL access for Team 1's search/report features ----
    def search_objects(self, **filters) -> List[Dict[str, Any]]:
        """Simple equality/NOT-NULL search over the `objects` table.

        Example:
            storage.search_objects(type="Door", fire_rating__not_null=True)
            storage.search_objects(material="Concrete")
        """
        clauses = []
        params: List[Any] = []
        for key, value in filters.items():
            if key.endswith("__not_null"):
                col = key[: -len("__not_null")]
                clauses.append(f"{col} IS NOT NULL")
            else:
                clauses.append(f"{key} = ?")
                params.append(value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        query = f"SELECT * FROM objects {where}"
        rows = self.conn.execute(query, params).fetchall()
        return [dict(r) for r in rows]
