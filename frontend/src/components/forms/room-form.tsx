"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { DialogFooter } from "@/components/ui/dialog";
import {
  roomCreateSchema,
  roomUpdateSchema,
  type RoomCreateForm,
  type RoomUpdateForm,
} from "@/schemas/room";
import type { Room } from "@/types/room";
import type { Floor } from "@/types/floor";
import { getErrorMessage } from "@/lib/errors";

interface RoomFormProps {
  room?: Room;
  floors: Floor[];
  defaultFloorId?: number;
  onSubmit: (values: any) => Promise<unknown>;
  onCancel: () => void;
}

export function RoomForm({ room, floors, defaultFloorId, onSubmit, onCancel }: RoomFormProps) {
  const isEdit = Boolean(room);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(isEdit ? roomUpdateSchema : roomCreateSchema),
    defaultValues: {
      room_name: room?.room_name ?? "",
      room_number: room?.room_number ?? "",
      room_type: room?.room_type ?? "",
      area: room?.area ?? "",
      occupancy: room?.occupancy ?? "",
      ...(isEdit ? {} : { floor_id: room?.floor_id ?? defaultFloorId ?? undefined }),
    } as RoomCreateForm,
  });

  const submit = handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      const payload = {
        ...values,
        room_number: values.room_number === "" ? null : values.room_number,
        room_type: values.room_type === "" ? null : values.room_type,
        area: values.area === "" ? null : values.area,
        occupancy: values.occupancy === "" ? null : values.occupancy,
      };
      await onSubmit(payload);
      onCancel();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  });

  return (
    <form onSubmit={submit} className="space-y-4">
      {!isEdit && (
        <div>
          <Label htmlFor="floor_id">Floor</Label>
          <Select id="floor_id" {...register("floor_id")}>
            <option value="">Select a floor…</option>
            {floors.map((f) => (
              <option key={f.id} value={f.id}>
                {f.floor_name} (#{f.floor_number})
              </option>
            ))}
          </Select>
          {"floor_id" in errors && errors.floor_id && (
            <p className="mt-1 text-xs text-destructive">{String(errors.floor_id.message)}</p>
          )}
        </div>
      )}
      <div>
        <Label htmlFor="room_name">Room Name</Label>
        <Input id="room_name" placeholder="e.g. Conference Room A" {...register("room_name")} />
        {errors.room_name && <p className="mt-1 text-xs text-destructive">{String(errors.room_name.message)}</p>}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="room_number">Room Number</Label>
          <Input id="room_number" placeholder="e.g. 101" {...register("room_number")} />
        </div>
        <div>
          <Label htmlFor="room_type">Room Type</Label>
          <Input id="room_type" placeholder="e.g. Office" {...register("room_type")} />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="area">Area (m²)</Label>
          <Input id="area" type="number" step="any" placeholder="e.g. 24.5" {...register("area")} />
          {errors.area && <p className="mt-1 text-xs text-destructive">{String(errors.area.message)}</p>}
        </div>
        <div>
          <Label htmlFor="occupancy">Occupancy</Label>
          <Input id="occupancy" type="number" placeholder="e.g. 8" {...register("occupancy")} />
          {errors.occupancy && (
            <p className="mt-1 text-xs text-destructive">{String(errors.occupancy.message)}</p>
          )}
        </div>
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : isEdit ? "Save Changes" : "Create Room"}
        </Button>
      </DialogFooter>
    </form>
  );
}
