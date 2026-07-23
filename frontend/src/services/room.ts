import { api } from "@/services/api";
import type { Room, RoomCreateInput, RoomUpdateInput } from "@/types/room";

export const roomService = {
  list: async (): Promise<Room[]> => {
    const { data } = await api.get<Room[]>("/rooms");
    return data;
  },

  get: async (id: number): Promise<Room> => {
    const { data } = await api.get<Room>(`/rooms/${id}`);
    return data;
  },

  listByFloor: async (floorId: number): Promise<Room[]> => {
    const { data } = await api.get<Room[]>(`/floors/${floorId}/rooms`);
    return data;
  },

  create: async (payload: RoomCreateInput): Promise<Room> => {
    const { data } = await api.post<Room>("/rooms", payload);
    return data;
  },

  update: async (id: number, payload: RoomUpdateInput): Promise<Room> => {
    const { data } = await api.put<Room>(`/rooms/${id}`, payload);
    return data;
  },

  remove: async (id: number): Promise<void> => {
    await api.delete(`/rooms/${id}`);
  },
};
