import { z } from "zod";

export const roomCreateSchema = z.object({
  room_name: z.string().min(1, "Room name is required").max(255),
  room_number: z.string().max(100).optional().or(z.literal("")),
  room_type: z.string().max(100).optional().or(z.literal("")),
  floor_id: z.coerce.number().int().positive("Select a floor"),
  area: z.coerce.number().nonnegative().optional().or(z.literal("")),
  occupancy: z.coerce.number().int().nonnegative().optional().or(z.literal("")),
});

export const roomUpdateSchema = z.object({
  room_name: z.string().min(1, "Room name is required").max(255).optional(),
  room_number: z.string().max(100).optional().or(z.literal("")),
  room_type: z.string().max(100).optional().or(z.literal("")),
  area: z.coerce.number().nonnegative().optional().or(z.literal("")),
  occupancy: z.coerce.number().int().nonnegative().optional().or(z.literal("")),
});

export type RoomCreateForm = z.infer<typeof roomCreateSchema>;
export type RoomUpdateForm = z.infer<typeof roomUpdateSchema>;
