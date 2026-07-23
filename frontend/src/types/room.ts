// Mirrors app/schemas/room.py exactly.

export interface Room {
  id: number;
  room_name: string;
  room_number: string | null;
  room_type: string | null;
  floor_id: number;
  area: number | null;
  occupancy: number | null;
}

export interface RoomCreateInput {
  room_name: string;
  room_number?: string | null;
  room_type?: string | null;
  floor_id: number;
  area?: number | null;
  occupancy?: number | null;
}

// RoomUpdate has no floor_id — a room cannot be moved between floors via this API.
export interface RoomUpdateInput {
  room_name?: string;
  room_number?: string | null;
  room_type?: string | null;
  area?: number | null;
  occupancy?: number | null;
}
