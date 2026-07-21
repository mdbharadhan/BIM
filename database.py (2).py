import sqlite3
import os

DB_NAME = "nexus_bim.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # Create Tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            full_name TEXT,
            email TEXT,
            role TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS buildings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            name TEXT,
            campus TEXT,
            manager TEXT,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS floors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            building_id INTEGER,
            floor_number TEXT,
            name TEXT,
            area_sqm REAL,
            FOREIGN KEY (building_id) REFERENCES buildings (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS structural_elements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            element_tag TEXT UNIQUE,
            building_id INTEGER,
            category TEXT,
            material TEXT,
            health_index INTEGER,
            status TEXT,
            last_inspection_date TEXT,
            FOREIGN KEY (building_id) REFERENCES buildings (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bim_models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            format TEXT,
            file_size_mb REAL,
            building_id INTEGER,
            uploaded_by TEXT,
            version TEXT,
            upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT,
            FOREIGN KEY (building_id) REFERENCES buildings (id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            username TEXT,
            action TEXT,
            details TEXT
        )
    """)

    # Seed Default Records
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