"use client";

import { useMemo, useState } from "react";
import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select } from "@/components/ui/select";
import { DialogFooter } from "@/components/ui/dialog";
import {
  structuralElementCreateSchema,
  structuralElementUpdateSchema,
  type StructuralElementCreateForm,
  type StructuralElementUpdateForm,
} from "@/schemas/structural-element";
import { ELEMENT_TYPES, ELEMENT_TYPE_LABELS } from "@/lib/constants";
import type { StructuralElement } from "@/types/structural-element";
import type { Floor } from "@/types/floor";
import type { Room } from "@/types/room";
import { getErrorMessage } from "@/lib/errors";

interface StructuralElementFormProps {
  element?: StructuralElement;
  floors: Floor[];
  rooms: Room[]; // full room list; filtered client-side by selected floor
  defaultFloorId?: number;
  onSubmit: (values: any) => Promise<unknown>;
  onCancel: () => void;
}

export function StructuralElementForm({
  element,
  floors,
  rooms,
  defaultFloorId,
  onSubmit,
  onCancel,
}: StructuralElementFormProps) {
  const isEdit = Boolean(element);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(isEdit ? structuralElementUpdateSchema : structuralElementCreateSchema),
    defaultValues: {
      element_name: element?.element_name ?? "",
      element_type: element?.element_type ?? undefined,
      material: element?.material ?? "",
      dim_width: element?.dim_width ?? "",
      dim_height: element?.dim_height ?? "",
      dim_depth: element?.dim_depth ?? "",
      ...(isEdit
        ? {}
        : {
            floor_id: element?.floor_id ?? defaultFloorId ?? undefined,
            room_id: element?.room_id ?? "",
          }),
    } as StructuralElementCreateForm,
  });

  // Only relevant pre-edit (create mode): filter rooms to the selected floor,
  // since the backend 400s if room_id doesn't belong to floor_id.
  const selectedFloorId = useWatch({ control, name: "floor_id" as const }) as number | string | undefined;
  const filteredRooms = useMemo(() => {
    if (isEdit) return rooms.filter((r) => r.floor_id === element?.floor_id);
    if (!selectedFloorId) return [];
    return rooms.filter((r) => r.floor_id === Number(selectedFloorId));
  }, [rooms, selectedFloorId, isEdit, element]);

  const submit = handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      const payload = {
        ...values,
        material: values.material === "" ? null : values.material,
        dim_width: values.dim_width === "" ? null : values.dim_width,
        dim_height: values.dim_height === "" ? null : values.dim_height,
        dim_depth: values.dim_depth === "" ? null : values.dim_depth,
        ...(isEdit
          ? {}
          : { room_id: (values as StructuralElementCreateForm).room_id === "" ? null : (values as StructuralElementCreateForm).room_id }),
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
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="floor_id">Floor</Label>
            <Select id="floor_id" {...register("floor_id")}>
              <option value="">Select a floor…</option>
              {floors.map((f) => (
                <option key={f.id} value={f.id}>
                  {f.floor_name}
                </option>
              ))}
            </Select>
            {"floor_id" in errors && errors.floor_id && (
              <p className="mt-1 text-xs text-destructive">{String(errors.floor_id.message)}</p>
            )}
          </div>
          <div>
            <Label htmlFor="room_id">Room (optional)</Label>
            <Select id="room_id" disabled={!selectedFloorId} {...register("room_id")}>
              <option value="">None</option>
              {filteredRooms.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.room_name}
                </option>
              ))}
            </Select>
          </div>
        </div>
      )}
      <div>
        <Label htmlFor="element_name">Element Name</Label>
        <Input id="element_name" placeholder="e.g. North Wall" {...register("element_name")} />
        {errors.element_name && (
          <p className="mt-1 text-xs text-destructive">{String(errors.element_name.message)}</p>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="element_type">Element Type</Label>
          <Select id="element_type" {...register("element_type")}>
            <option value="">Select type…</option>
            {ELEMENT_TYPES.map((t) => (
              <option key={t} value={t}>
                {ELEMENT_TYPE_LABELS[t]}
              </option>
            ))}
          </Select>
          {errors.element_type && (
            <p className="mt-1 text-xs text-destructive">{String(errors.element_type.message)}</p>
          )}
        </div>
        <div>
          <Label htmlFor="material">Material</Label>
          <Input id="material" placeholder="e.g. Concrete" {...register("material")} />
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <div>
          <Label htmlFor="dim_width">Width</Label>
          <Input id="dim_width" type="number" step="any" {...register("dim_width")} />
        </div>
        <div>
          <Label htmlFor="dim_height">Height</Label>
          <Input id="dim_height" type="number" step="any" {...register("dim_height")} />
        </div>
        <div>
          <Label htmlFor="dim_depth">Depth</Label>
          <Input id="dim_depth" type="number" step="any" {...register("dim_depth")} />
        </div>
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : isEdit ? "Save Changes" : "Create Element"}
        </Button>
      </DialogFooter>
    </form>
  );
}
