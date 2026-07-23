// Mirrors app/schemas/floor.py exactly.

export interface Floor {
  id: number;
  floor_name: string;
  floor_number: number;
  building_id: number;
}

export interface FloorCreateInput {
  floor_name: string;
  floor_number: number;
  building_id: number;
}

// FloorUpdate has no building_id — a floor cannot be moved between buildings via this API.
export interface FloorUpdateInput {
  floor_name?: string;
  floor_number?: number;
}
