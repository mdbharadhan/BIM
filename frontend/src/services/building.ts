import { api } from "@/services/api";
import type { Building, BuildingCreateInput, BuildingUpdateInput } from "@/types/building";

export const buildingService = {
  list: async (): Promise<Building[]> => {
    const { data } = await api.get<Building[]>("/buildings");
    return data;
  },

  get: async (id: number): Promise<Building> => {
    const { data } = await api.get<Building>(`/buildings/${id}`);
    return data;
  },

  create: async (payload: BuildingCreateInput): Promise<Building> => {
    const { data } = await api.post<Building>("/buildings", payload);
    return data;
  },

  update: async (id: number, payload: BuildingUpdateInput): Promise<Building> => {
    const { data } = await api.put<Building>(`/buildings/${id}`, payload);
    return data;
  },

  remove: async (id: number): Promise<void> => {
    await api.delete(`/buildings/${id}`);
  },
};
