import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
DB_DIR = BASE_DIR / "database"

# Ensure directories exist
for path in [UPLOADS_DIR, EXPORTS_DIR, LOGS_DIR, DB_DIR]:
    os.makedirs(path, exist_ok=True)

# Database Configuration
DB_PATH = DB_DIR / "bim.db"

# Application Settings
APP_NAME = "Nexus BIM Automation Hub"
APP_VERSION = "2.4.0"
COMPANY_NAME = "Nexus Systems"

# Upload Constraints
MAX_UPLOAD_SIZE_MB = 500
ALLOWED_EXTENSIONS = ["ifc", "rvt", "dwg", "nwd", "pdf"]