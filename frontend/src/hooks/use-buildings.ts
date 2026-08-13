"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { buildingService } from "@/services/building";
import type { Building, BuildingCreateInput, BuildingUpdateInput } from "@/types/building";
import { getErrorMessage } from "@/lib/errors";

export function useBuildings() {
  const [buildings, setBuildings] = useState<Building[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await buildingService.list();
      setBuildings(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createBuilding = useCallback(async (payload: BuildingCreateInput) => {
    const created = await buildingService.create(payload);
    setBuildings((prev) => [...prev, created]);
    toast.success(`Building "${created.name}" created`);
    return created;
  }, []);

  const updateBuilding = useCallback(async (id: number, payload: BuildingUpdateInput) => {
    const updated = await buildingService.update(id, payload);
    setBuildings((prev) => prev.map((b) => (b.id === id ? updated : b)));
    toast.success(`Building "${updated.name}" updated`);
    return updated;
  }, []);

  const deleteBuilding = useCallback(async (id: number) => {
    await buildingService.remove(id);
    setBuildings((prev) => prev.filter((b) => b.id !== id));
    toast.success("Building deleted");
  }, []);

  return { buildings, loading, error, refresh, createBuilding, updateBuilding, deleteBuilding };
}
