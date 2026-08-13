"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { DialogFooter } from "@/components/ui/dialog";
import {
  buildingCreateSchema,
  buildingUpdateSchema,
  type BuildingCreateForm,
  type BuildingUpdateForm,
} from "@/schemas/building";
import type { Building } from "@/types/building";
import { getErrorMessage } from "@/lib/errors";

interface BuildingFormProps {
  building?: Building;
  onSubmit: (values: { name?: string; address?: string | null }) => Promise<unknown>;
  onCancel: () => void;
}

export function BuildingForm({ building, onSubmit, onCancel }: BuildingFormProps) {
  const isEdit = Boolean(building);
  const [submitting, setSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<any>({
    resolver: zodResolver(isEdit ? buildingUpdateSchema : buildingCreateSchema),
    defaultValues: {
      name: building?.name ?? "",
      address: building?.address ?? "",
    },
  });

  const submit = handleSubmit(async (values) => {
    setSubmitting(true);
    try {
      await onSubmit({
        name: values.name,
        address: values.address === "" ? null : values.address,
      });
      onCancel();
    } catch (err) {
      toast.error(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  });

  return (
    <form onSubmit={submit} className="space-y-4">
      <div>
        <Label htmlFor="name">Building Name</Label>
        <Input id="name" placeholder="e.g. Riverside Tower" {...register("name")} />
        {errors.name && <p className="mt-1 text-xs text-destructive">{String(errors.name.message)}</p>}
      </div>
      <div>
        <Label htmlFor="address">Address</Label>
        <Input id="address" placeholder="e.g. 123 Main St" {...register("address")} />
        {errors.address && <p className="mt-1 text-xs text-destructive">{String(errors.address.message)}</p>}
      </div>
      <DialogFooter>
        <Button type="button" variant="outline" onClick={onCancel} disabled={submitting}>
          Cancel
        </Button>
        <Button type="submit" disabled={submitting}>
          {submitting ? "Saving…" : isEdit ? "Save Changes" : "Create Building"}
        </Button>
      </DialogFooter>
    </form>
  );
}
