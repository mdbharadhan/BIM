import { api } from "@/services/api";
import type {
  StructuralElement,
  StructuralElementCreateInput,
  StructuralElementUpdateInput,
} from "@/types/structural-element";

export const structuralElementService = {
  list: async (): Promise<StructuralElement[]> => {
    const { data } = await api.get<StructuralElement[]>("/structural-elements");
    return data;
  },

  get: async (id: number): Promise<StructuralElement> => {
    const { data } = await api.get<StructuralElement>(`/structural-elements/${id}`);
    return data;
  },

  // NOTE: backend only exposes /rooms/{room_id}/elements — there is no
  // /floors/{floor_id}/elements route. Unassigned (room_id = null) elements
  // for a floor must be derived client-side by filtering the full list.
  listByRoom: async (roomId: number): Promise<StructuralElement[]> => {
    const { data } = await api.get<StructuralElement[]>(`/rooms/${roomId}/elements`);
    return data;
  },

  create: async (payload: StructuralElementCreateInput): Promise<StructuralElement> => {
    const { data } = await api.post<StructuralElement>("/structural-elements", payload);
    return data;
  },

  update: async (
    id: number,
    payload: StructuralElementUpdateInput
  ): Promise<StructuralElement> => {
    const { data } = await api.put<StructuralElement>(`/structural-elements/${id}`, payload);
    return data;
  },

  remove: async (id: number): Promise<void> => {
    await api.delete(`/structural-elements/${id}`);
  },
};
