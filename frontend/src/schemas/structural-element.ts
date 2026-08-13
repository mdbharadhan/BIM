import { z } from "zod";
import { ELEMENT_TYPES } from "@/lib/constants";

export const structuralElementCreateSchema = z.object({
  element_name: z.string().min(1, "Element name is required").max(255),
  element_type: z.enum(ELEMENT_TYPES, { message: "Select an element type" }),
  material: z.string().max(255).optional().or(z.literal("")),
  floor_id: z.coerce.number().int().positive("Select a floor"),
  room_id: z.coerce.number().int().positive().optional().or(z.literal("")),
  dim_width: z.coerce.number().nonnegative().optional().or(z.literal("")),
  dim_height: z.coerce.number().nonnegative().optional().or(z.literal("")),
  dim_depth: z.coerce.number().nonnegative().optional().or(z.literal("")),
});

export const structuralElementUpdateSchema = z.object({
  element_name: z.string().min(1, "Element name is required").max(255).optional(),
  element_type: z.enum(ELEMENT_TYPES).optional(),
  material: z.string().max(255).optional().or(z.literal("")),
  dim_width: z.coerce.number().nonnegative().optional().or(z.literal("")),
  dim_height: z.coerce.number().nonnegative().optional().or(z.literal("")),
  dim_depth: z.coerce.number().nonnegative().optional().or(z.literal("")),
});

export type StructuralElementCreateForm = z.infer<typeof structuralElementCreateSchema>;
export type StructuralElementUpdateForm = z.infer<typeof structuralElementUpdateSchema>;
