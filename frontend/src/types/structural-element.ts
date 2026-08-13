// Mirrors app/schemas/structural_element.py exactly.
import type { ElementType } from "@/lib/constants";

export interface StructuralElement {
  id: number;
  element_name: string;
  element_type: ElementType;
  material: string | null;
  floor_id: number;
  room_id: number | null;
  dim_width: number | null;
  dim_height: number | null;
  dim_depth: number | null;
}

export interface StructuralElementCreateInput {
  element_name: string;
  element_type: ElementType;
  material?: string | null;
  floor_id: number;
  room_id?: number | null;
  dim_width?: number | null;
  dim_height?: number | null;
  dim_depth?: number | null;
}

// StructuralElementUpdate has no floor_id/room_id — reassignment isn't supported by this API.
export interface StructuralElementUpdateInput {
  element_name?: string;
  element_type?: ElementType;
  material?: string | null;
  dim_width?: number | null;
  dim_height?: number | null;
  dim_depth?: number | null;
}
