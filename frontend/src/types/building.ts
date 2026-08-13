// Mirrors app/schemas/building.py exactly.

export interface Building {
  id: number;
  name: string;
  address: string | null;
}

export interface BuildingCreateInput {
  name: string;
  address?: string | null;
}

export interface BuildingUpdateInput {
  name?: string;
  address?: string | null;
}
