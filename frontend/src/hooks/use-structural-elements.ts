"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { structuralElementService } from "@/services/structural-element";
import type {
  StructuralElement,
  StructuralElementCreateInput,
  StructuralElementUpdateInput,
} from "@/types/structural-element";
import { getErrorMessage } from "@/lib/errors";

export function useStructuralElements(roomId?: number) {
  const [elements, setElements] = useState<StructuralElement[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = roomId
        ? await structuralElementService.listByRoom(roomId)
        : await structuralElementService.list();
      setElements(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [roomId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createElement = useCallback(async (payload: StructuralElementCreateInput) => {
    const created = await structuralElementService.create(payload);
    setElements((prev) => [...prev, created]);
    toast.success(`Element "${created.element_name}" created`);
    return created;
  }, []);

  const updateElement = useCallback(async (id: number, payload: StructuralElementUpdateInput) => {
    const updated = await structuralElementService.update(id, payload);
    setElements((prev) => prev.map((e) => (e.id === id ? updated : e)));
    toast.success(`Element "${updated.element_name}" updated`);
    return updated;
  }, []);

  const deleteElement = useCallback(async (id: number) => {
    await structuralElementService.remove(id);
    setElements((prev) => prev.filter((e) => e.id !== id));
    toast.success("Element deleted");
  }, []);

  return { elements, loading, error, refresh, createElement, updateElement, deleteElement };
}
