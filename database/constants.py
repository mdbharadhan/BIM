"""
constants.py
------------
Central location for shared paths/IDs so every team member gets the same
database regardless of which directory they launch their script from
(app.py at project root, a Streamlit app inside frontend/, a test inside
tests/, etc. all resolve to the same place).
"""
import os

# database/constants.py -> parent is database/ -> parent of that is project root
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(_THIS_DIR)

DATA_DIR = os.path.join(PROJECT_ROOT, "data")
JSON_STORE_DIR = os.path.join(DATA_DIR, "json_store")
SQLITE_PATH = os.path.join(DATA_DIR, "bim_project.db")

# Fixed ID for the generated sample project so calling load_sample_data()
# repeatedly updates the same record instead of creating duplicates, and
# so other teams can hardcode this ID during early development without
# first having to call list_projects() to find it.
SAMPLE_PROJECT_ID = "sample-project-001"
