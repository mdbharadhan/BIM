"use client";

import { useCallback, useEffect, useState } from "react";
import { toast } from "sonner";
import { roomService } from "@/services/room";
import type { Room, RoomCreateInput, RoomUpdateInput } from "@/types/room";
import { getErrorMessage } from "@/lib/errors";

export function useRooms(floorId?: number) {
  const [rooms, setRooms] = useState<Room[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = floorId ? await roomService.listByFloor(floorId) : await roomService.list();
      setRooms(data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  }, [floorId]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const createRoom = useCallback(async (payload: RoomCreateInput) => {
    const created = await roomService.create(payload);
    setRooms((prev) => [...prev, created]);
    toast.success(`Room "${created.room_name}" created`);
    return created;
  }, []);

  const updateRoom = useCallback(async (id: number, payload: RoomUpdateInput) => {
    const updated = await roomService.update(id, payload);
    setRooms((prev) => prev.map((r) => (r.id === id ? updated : r)));
    toast.success(`Room "${updated.room_name}" updated`);
    return updated;
  }, []);

  const deleteRoom = useCallback(async (id: number) => {
    await roomService.remove(id);
    setRooms((prev) => prev.filter((r) => r.id !== id));
    toast.success("Room deleted");
  }, []);

  return { rooms, loading, error, refresh, createRoom, updateRoom, deleteRoom };
}
