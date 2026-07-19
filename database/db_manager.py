"""
db_manager.py
-------------
Single entry point for the rest of the app (mainly Team 1 - Backend).
Wraps whichever storage backend is configured so callers never touch
JSONStorage / SQLiteStorage directly.

Usage:
    from database.db_manager import DatabaseManager

    db = DatabaseManager(backend="sqlite")       # or backend="json"
    db.load_sample_data()                        # populate with sample data
    project = db.load_project(project_id)
    db.save_project(project)
    doors = db.search_objects(type="Door")
    fire_rated_doors = db.search_objects(type="Door", fire_rating__not_null=True)
"""
from __future__ import annotations
from typing import List, Dict, Any, Optional

try:
    from .models import Project
    from .storage import JSONStorage, SQLiteStorage
    from .sample_data import build_sample_project
    from .constants import JSON_STORE_DIR, SQLITE_PATH, SAMPLE_PROJECT_ID
except ImportError:  # allows running this file directly from inside database/
    from models import Project
    from storage import JSONStorage, SQLiteStorage
    from sample_data import build_sample_project
    from constants import JSON_STORE_DIR, SQLITE_PATH, SAMPLE_PROJECT_ID


class DatabaseManager:
    def __init__(self, backend: str = "sqlite", json_dir: str = JSON_STORE_DIR,
                 sqlite_path: str = SQLITE_PATH):
        backend = backend.lower()
        if backend == "json":
            self._backend_name = "json"
            self._store = JSONStorage(directory=json_dir)
        elif backend == "sqlite":
            self._backend_name = "sqlite"
            self._store = SQLiteStorage(db_path=sqlite_path)
        else:
            raise ValueError(f"Unknown backend '{backend}'. Use 'json' or 'sqlite'.")

    # -- core CRUD ----------------------------------------------------------
    def save_project(self, project: Project) -> None:
        self._store.save_project(project)

    def load_project(self, project_id: str) -> Optional[Project]:
        return self._store.load_project(project_id)

    def list_projects(self) -> List[Dict[str, Any]]:
        return self._store.list_projects()

    def delete_project(self, project_id: str) -> bool:
        return self._store.delete_project(project_id)

    # -- search (only available on the SQLite backend) -----------------------
    def search_objects(self, **filters) -> List[Dict[str, Any]]:
        if self._backend_name != "sqlite":
            raise NotImplementedError(
                "search_objects() requires backend='sqlite'. "
                "Switch backends or filter the JSON-loaded Project in Python instead."
            )
        return self._store.search_objects(**filters)

    # -- convenience ----------------------------------------------------------
    def load_sample_data(self) -> Project:
        """Generate and persist the sample project, return it.

        Safe to call repeatedly — the sample project has a fixed id, so
        this overwrites the same record rather than creating duplicates.
        """
        project = build_sample_project()
        self.save_project(project)
        return project

    def get_sample_project(self) -> Project:
        """Load the sample project by its known fixed id, creating it
        first if it doesn't exist yet. Handy for frontend/backend code
        that just wants *a* project to render without calling
        list_projects() first to find one."""
        existing = self.load_project(SAMPLE_PROJECT_ID)
        if existing is not None:
            return existing
        return self.load_sample_data()

    def close(self) -> None:
        if hasattr(self._store, "close"):
            self._store.close()
