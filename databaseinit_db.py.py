import sqlite3
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from config import DB_PATH

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Core Schema Definitions
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            role TEXT
        );

        CREATE TABLE IF NOT EXISTS buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            campus TEXT,
            manager TEXT,
            status TEXT
        );

        CREATE TABLE IF NOT EXISTS floors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_id INTEGER,
            floor_number TEXT,
            name TEXT,
            area_sqm REAL,
            FOREIGN KEY (building_id) REFERENCES buildings (id)
        );

        CREATE TABLE IF NOT EXISTS rooms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            floor_id INTEGER,
            room_number TEXT,
            purpose TEXT,
            capacity INTEGER,
            FOREIGN KEY (floor_id) REFERENCES floors (id)
        );

        CREATE TABLE IF NOT EXISTS bim_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT NOT NULL,
            format TEXT,
            file_size_mb REAL,
            building_id INTEGER,
            uploaded_by TEXT,
            version TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            FOREIGN KEY (building_id) REFERENCES buildings (id)
        );

        CREATE TABLE IF NOT EXISTS structural_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            element_tag TEXT UNIQUE NOT NULL,
            building_id INTEGER,
            category TEXT,
            material TEXT,
            health_index INTEGER,
            status TEXT,
            last_inspection_date TEXT,
            FOREIGN KEY (building_id) REFERENCES buildings (id)
        );

        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            action TEXT,
            details TEXT
        );
    """)

    # Seed Baseline Data
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, full_name, email, role) VALUES ('admin', 'admin123', 'Alex Mercer', 'alex.mercer@nexusbim.io', 'Lead BIM Architect')")
        cursor.execute("INSERT INTO buildings (code, name, campus, manager, status) VALUES ('BLD-01', 'AeroTech HQ', 'Main Campus', 'Sarah Jenkins', 'Active')")
        cursor.execute("INSERT INTO buildings (code, name, campus, manager, status) VALUES ('BLD-02', 'Nexus Tower Alpha', 'North Tech Park', 'David Miller', 'Under Inspection')")
        cursor.execute("INSERT INTO floors (building_id, floor_number, name, area_sqm) VALUES (1, 'L1', 'Ground Concourse', 1200.5)")
        cursor.execute("INSERT INTO floors (building_id, floor_number, name, area_sqm) VALUES (1, 'L2', 'Executive Suites', 1150.0)")
        cursor.execute("INSERT INTO structural_elements (element_tag, building_id, category, material, health_index, status, last_inspection_date) VALUES ('COL-A12', 1, 'Column', 'Reinforced Concrete', 94, 'Nominal', '2026-06-15')")
        cursor.execute("INSERT INTO structural_elements (element_tag, building_id, category, material, health_index, status, last_inspection_date) VALUES ('BEAM-B04', 2, 'Beam', 'Structural Steel', 78, 'Monitor Required', '2026-07-01')")
        cursor.execute("INSERT INTO bim_models (file_name, format, file_size_mb, building_id, uploaded_by, version, status) VALUES ('Aerotech_Arch_v2.ifc', 'IFC', 142.5, 1, 'admin', 'v2.1', 'Verified')")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")