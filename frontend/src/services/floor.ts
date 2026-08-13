import { api } from "@/services/api";
import type { Floor, FloorCreateInput, FloorUpdateInput } from "@/types/floor";

export const floorService = {
  list: async (): Promise<Floor[]> => {
    const { data } = await api.get<Floor[]>("/floors");
    return data;
  },

  get: async (id: number): Promise<Floor> => {
    const { data } = await api.get<Floor>(`/floors/${id}`);
    return data;
  },

  listByBuilding: async (buildingId: number): Promise<Floor[]> => {
    const { data } = await api.get<Floor[]>(`/buildings/${buildingId}/floors`);
    return data;
  },

  create: async (payload: FloorCreateInput): Promise<Floor> => {
    const { data } = await api.post<Floor>("/floors", payload);
    return data;
  },

  update: async (id: number, payload: FloorUpdateInput): Promise<Floor> => {
    const { data } = await api.put<Floor>(`/floors/${id}`, payload);
    return data;
  },

  remove: async (id: number): Promise<void> => {
    await api.delete(`/floors/${id}`);
  },
};
