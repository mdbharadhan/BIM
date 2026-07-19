"""
sample_data.py
--------------
Generates a small but realistic sample Project so Team 2 (frontend) and
Team 1 (backend) have real data to build against before real project data
exists. Mirrors the report's example: a mix of walls, doors (some fire
rated), and windows across a couple of floors.
"""
from __future__ import annotations
try:
    from .models import Project, Building, Floor, Room, BIMObject
    from .constants import SAMPLE_PROJECT_ID
except ImportError:  # allows running this file directly from inside database/
    from models import Project, Building, Floor, Room, BIMObject
    from constants import SAMPLE_PROJECT_ID


def build_sample_project() -> Project:
    # Fixed ID (not a random uuid) so every team member who calls this
    # gets the SAME project id every time — re-saving just overwrites the
    # same record instead of piling up duplicate "Riverside Office Tower"
    # projects in the database.
    project = Project(
        id=SAMPLE_PROJECT_ID,
        name="Riverside Office Tower",
        description="Sample BIM project used for development and testing.",
    )

    building = Building(name="Riverside Tower - Block A", address="12 Riverside Ave")

    ground_floor = Floor(name="Ground Floor", level=0)
    lobby = Room(name="Lobby", area=120.0)
    lobby.add_object(BIMObject(
        type="Door", name="Main Entrance Door", material="Glass/Aluminum",
        length=1.2, height=2.4, thickness=0.05, fire_rating="FD30",
        cost=2500.0, manufacturer="Acme Doors Inc.",
        installation_date="2025-03-10", maintenance_schedule="Annual",
        coordinates={"x": 0.0, "y": 0.0, "z": 0.0},
    ))
    lobby.add_object(BIMObject(
        type="Wall", name="Lobby Reception Wall", material="Gypsum Board",
        length=6.0, height=3.0, thickness=0.15, fire_rating="FD60",
        thermal_properties="U=0.35", structural_properties="Non-load-bearing",
        cost=1800.0,
    ))
    ground_floor.add_room(lobby)

    corridor = Room(name="Ground Floor Corridor", area=45.0)
    corridor.add_object(BIMObject(
        type="Door", name="Fire Exit Door 1", material="Steel",
        length=1.0, height=2.1, thickness=0.05, fire_rating="FD60",
        cost=1200.0, manufacturer="SafeExit Co.",
        installation_date="2025-03-12", maintenance_schedule="Semi-annual",
    ))
    ground_floor.add_room(corridor)
    building.add_floor(ground_floor)

    first_floor = Floor(name="1st Floor - Offices", level=1)
    office_101 = Room(name="Office 101", area=30.0)
    office_101.add_object(BIMObject(
        type="Window", name="Office 101 Window", material="Double Glazed Glass",
        length=1.5, height=1.2, thickness=0.03,
        thermal_properties="U=1.1", cost=650.0,
    ))
    office_101.add_object(BIMObject(
        type="Door", name="Office 101 Door", material="Wood",
        length=0.9, height=2.1, thickness=0.04, fire_rating=None,
        cost=400.0,
    ))
    first_floor.add_room(office_101)

    server_room = Room(name="Server Room", area=18.0)
    server_room.add_object(BIMObject(
        type="Door", name="Server Room Door", material="Steel",
        length=1.0, height=2.1, thickness=0.06, fire_rating="FD90",
        cost=1500.0, manufacturer="SafeExit Co.",
        installation_date="2025-04-01", maintenance_schedule="Quarterly",
    ))
    server_room.add_object(BIMObject(
        type="Wall", name="Server Room Fire Wall", material="Concrete Block",
        length=8.0, height=3.0, thickness=0.2, fire_rating="FD120",
        structural_properties="Load-bearing", cost=3200.0,
    ))
    first_floor.add_room(server_room)

    building.add_floor(first_floor)
    project.add_building(building)
    return project


if __name__ == "__main__":
    # Quick manual check: print a summary of the generated sample data.
    p = build_sample_project()
    print(f"Project: {p.name} ({p.id})")
    for b in p.buildings:
        print(f"  Building: {b.name}")
        for f in b.floors:
            print(f"    Floor: {f.name}")
            for r in f.rooms:
                print(f"      Room: {r.name} ({len(r.objects)} objects)")
                for o in r.objects:
                    print(f"        - {o.type}: {o.name} (fire_rating={o.fire_rating})")
