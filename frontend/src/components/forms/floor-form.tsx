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
  floorCreateSchema,
  floorUpdateSchema,
  type FloorCreateForm,
  type FloorUpdateForm,
} from "@/schemas/floor";
import type { Floor } from "@/types/floor";
import type { Building } from "@/types/building";
import { getErrorMessage } from "@/lib/errors";

interface FloorFormProps {
  floor?: Floor;
  buildings: Building[];
  defaultBuildingId?: number;
  onSubmit: (values: any) => Promise<unknown>;
  onCancel: () => void;
}

export function FloorForm({ floor, buildings, defaultBuildingId, onSubmit, onCancel }: FloorFormProps) {
  const isEdit = Boolean(floor);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(isEdit ? floorUpdateSchema : floorCreateSchema),
    defaultValues: {
      floor_name: floor?.floor_name ?? "",
      floor_number: floor?.floor_number ?? 0,
      ...(isEdit ? {} : { building_id: floor?.building_id ?? defaultBuildingId ?? undefined }),
    } as FloorCreateForm,
  });

  const submit = handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      await onSubmit(values);
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
          <Label htmlFor="building_id">Building</Label>
          <Select id="building_id" {...register("building_id")}>
            <option value="">Select a building…</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>
                {b.name}
              </option>
            ))}
          </Select>
          {"building_id" in errors && errors.building_id && (
            <p className="mt-1 text-xs text-destructive">{String(errors.building_id.message)}</p>
          )}
        </div>
      )}
      <div>
        <Label htmlFor="floor_name">Floor Name</Label>
        <Input id="floor_name" placeholder="e.g. Ground Floor" {...register("floor_name")} />
        {errors.floor_name && <p className="mt-1 text-xs text-destructive">{String(errors.floor_name.message)}</p>}
      </div>
      <div>
        <Label htmlFor="floor_number">Floor Number</Label>
        <Input id="floor_number" type="number" placeholder="e.g. 0" {...register("floor_number")} />
        {errors.floor_number && (
          <p className="mt-1 text-xs text-destructive">{String(errors.floor_number.message)}</p>
        )}
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : isEdit ? "Save Changes" : "Create Floor"}
        </Button>
      </DialogFooter>
    </form>
  );
}
