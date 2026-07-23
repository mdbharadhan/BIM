import { z } from "zod";

export const buildingCreateSchema = z.object({
  name: z.string().min(1, "Name is required").max(255),
  address: z.string().max(500).optional().or(z.literal("")),
});

export const buildingUpdateSchema = z.object({
  name: z.string().min(1, "Name is required").max(255).optional(),
  address: z.string().max(500).optional().or(z.literal("")),
});

export type BuildingCreateForm = z.infer<typeof buildingCreateSchema>;
export type BuildingUpdateForm = z.infer<typeof buildingUpdateSchema>;
