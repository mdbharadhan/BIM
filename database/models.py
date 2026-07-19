"""
models.py
---------
Data models for the BIM Project's Database module.

Mirrors the object-based hierarchy described in the BIM R&D report:

    Project -> Building -> Floor -> Room -> Objects -> Properties

Each level is a plain dataclass with to_dict()/from_dict() so it can be
serialized to JSON or flattened into SQLite rows by storage.py.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
import uuid


def _new_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


@dataclass
class BIMObject:
    """A single BIM object: Wall, Door, Window, Column, Beam, etc.

    Field names follow the 'Wall Object' info card in the report
    (Object ID, Material, Length, Height, Thickness, Fire Rating,
    Thermal/Structural Properties, Cost, Manufacturer, Installation Date,
    Maintenance Schedule, Coordinates, Relationships).
    """
    id: str = field(default_factory=lambda: _new_id("obj"))
    type: str = "Generic"                      # Wall, Door, Window, Column...
    name: str = ""
    material: Optional[str] = None
    length: Optional[float] = None              # meters
    height: Optional[float] = None              # meters
    thickness: Optional[float] = None           # meters
    fire_rating: Optional[str] = None
    thermal_properties: Optional[str] = None
    structural_properties: Optional[str] = None
    cost: Optional[float] = None
    manufacturer: Optional[str] = None
    installation_date: Optional[str] = None
    maintenance_schedule: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None   # {"x":.., "y":.., "z":..}
    relationships: List[str] = field(default_factory=list)  # related object ids
    extra_properties: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BIMObject":
        known = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
        return cls(**known)


@dataclass
class Room:
    id: str = field(default_factory=lambda: _new_id("room"))
    name: str = ""
    area: Optional[float] = None  # sq meters
    objects: List[BIMObject] = field(default_factory=list)

    def add_object(self, obj: BIMObject) -> None:
        self.objects.append(obj)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "area": self.area,
            "objects": [o.to_dict() for o in self.objects],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Room":
        objs = [BIMObject.from_dict(o) for o in data.get("objects", [])]
        return cls(id=data["id"], name=data.get("name", ""), area=data.get("area"), objects=objs)


@dataclass
class Floor:
    id: str = field(default_factory=lambda: _new_id("floor"))
    name: str = ""
    level: int = 0
    rooms: List[Room] = field(default_factory=list)

    def add_room(self, room: Room) -> None:
        self.rooms.append(room)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "rooms": [r.to_dict() for r in self.rooms],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Floor":
        rooms = [Room.from_dict(r) for r in data.get("rooms", [])]
        return cls(id=data["id"], name=data.get("name", ""), level=data.get("level", 0), rooms=rooms)


@dataclass
class Building:
    id: str = field(default_factory=lambda: _new_id("bldg"))
    name: str = ""
    address: Optional[str] = None
    floors: List[Floor] = field(default_factory=list)

    def add_floor(self, floor: Floor) -> None:
        self.floors.append(floor)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "floors": [f.to_dict() for f in self.floors],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Building":
        floors = [Floor.from_dict(f) for f in data.get("floors", [])]
        return cls(id=data["id"], name=data.get("name", ""), address=data.get("address"), floors=floors)


@dataclass
class Project:
    id: str = field(default_factory=lambda: _new_id("proj"))
    name: str = ""
    description: Optional[str] = None
    buildings: List[Building] = field(default_factory=list)

    def add_building(self, building: Building) -> None:
        self.buildings.append(building)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "buildings": [b.to_dict() for b in self.buildings],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Project":
        buildings = [Building.from_dict(b) for b in data.get("buildings", [])]
        return cls(
            id=data["id"],
            name=data.get("name", ""),
            description=data.get("description"),
            buildings=buildings,
        )
