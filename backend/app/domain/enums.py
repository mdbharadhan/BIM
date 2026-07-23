import enum


class ElementType(enum.StrEnum):
    WALL = "wall"
    BEAM = "beam"
    COLUMN = "column"
    SLAB = "slab"
    DOOR = "door"
    WINDOW = "window"
    STAIR = "stair"
