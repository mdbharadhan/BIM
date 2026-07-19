"""
demo.py
-------
Run this directly to see the database module working end-to-end:

    cd database
    python3 demo.py

Exercises both storage backends and the search feature.
"""
from db_manager import DatabaseManager


def main():
    print("=== SQLite backend ===")
    db = DatabaseManager(backend="sqlite")
    project = db.load_sample_data()
    print(f"Created sample project: {project.name} ({project.id})")

    reloaded = db.load_project(project.id)
    print(f"Reloaded ok: {reloaded.name}, buildings={len(reloaded.buildings)}")

    print("All projects:", db.list_projects())

    fire_doors = db.search_objects(type="Door", fire_rating__not_null=True)
    print(f"Fire-rated doors ({len(fire_doors)}):")
    for d in fire_doors:
        print(f"  - {d['name']} [{d['fire_rating']}]")
    db.close()

    print("\n=== JSON backend ===")
    db_json = DatabaseManager(backend="json")
    project_json = db_json.load_sample_data()
    reloaded_json = db_json.load_project(project_json.id)
    print(f"Reloaded ok: {reloaded_json.name}, buildings={len(reloaded_json.buildings)}")
    print("All projects:", db_json.list_projects())


if __name__ == "__main__":
    main()
