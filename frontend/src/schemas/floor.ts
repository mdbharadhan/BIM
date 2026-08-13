import { z } from "zod";

export const floorCreateSchema = z.object({
  floor_name: z.string().min(1, "Floor name is required").max(255),
  floor_number: z.coerce.number().int("Must be a whole number"),
  building_id: z.coerce.number().int().positive("Select a building"),
});

export const floorUpdateSchema = z.object({
  floor_name: z.string().min(1, "Floor name is required").max(255).optional(),
  floor_number: z.coerce.number().int("Must be a whole number").optional(),
});

export type FloorCreateForm = z.infer<typeof floorCreateSchema>;
export type FloorUpdateForm = z.infer<typeof floorUpdateSchema>;
