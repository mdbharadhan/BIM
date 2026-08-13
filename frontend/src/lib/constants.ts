// Mirrors app/domain/enums.py::ElementType exactly. Do not add values the backend doesn't have.
export const ELEMENT_TYPES = [
  "wall",
  "beam",
  "column",
  "slab",
  "door",
  "window",
  "stair",
] as const;

export type ElementType = (typeof ELEMENT_TYPES)[number];

export const ELEMENT_TYPE_LABELS: Record<ElementType, string> = {
  wall: "Wall",
  beam: "Beam",
  column: "Column",
  slab: "Slab",
  door: "Door",
  window: "Window",
  stair: "Stair",
};
