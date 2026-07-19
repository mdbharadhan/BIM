"""
database package
-----------------
Team 3's deliverable: project data storage for the BIM module.

Public API (import from `database`):
    DatabaseManager   - unified load/save/search facade (use this)
    Project, Building, Floor, Room, BIMObject  - data models
    build_sample_project() - generates sample data for dev/testing
"""
from .db_manager import DatabaseManager
from .models import Project, Building, Floor, Room, BIMObject
from .sample_data import build_sample_project

__all__ = [
    "DatabaseManager",
    "Project",
    "Building",
    "Floor",
    "Room",
    "BIMObject",
    "build_sample_project",
]
