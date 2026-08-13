"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { floorService } from "@/services/floor";
import type { Floor, FloorCreateInput, FloorUpdateInput } from "@/types/floor";
import { getErrorMessage } from "@/lib/errors";

export function useFloors(buildingId?: number) {
  const [floors, setFloors] = useState<Floor[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = buildingId ? await floorService.listByBuilding(buildingId) : await floorService.list();
      setFloors(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [buildingId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createFloor = useCallback(async (payload: FloorCreateInput) => {
    const created = await floorService.create(payload);
    setFloors((prev) => [...prev, created]);
    toast.success(`Floor "${created.floor_name}" created`);
    return created;
  }, []);

  const updateFloor = useCallback(async (id: number, payload: FloorUpdateInput) => {
    const updated = await floorService.update(id, payload);
    setFloors((prev) => prev.map((f) => (f.id === id ? updated : f)));
    toast.success(`Floor "${updated.floor_name}" updated`);
    return updated;
  }, []);

  const deleteFloor = useCallback(async (id: number) => {
    await floorService.remove(id);
    setFloors((prev) => prev.filter((f) => f.id !== id));
    toast.success("Floor deleted");
  }, []);

  return { floors, loading, error, refresh, createFloor, updateFloor, deleteFloor };
}
