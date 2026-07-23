"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Plus, Pencil, Trash2, Search } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Select } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DataTable, type Column } from "@/components/tables/data-table";
import { DeleteConfirmDialog } from "@/components/tables/delete-confirm-dialog";
import { StructuralElementForm } from "@/components/forms/structural-element-form";
import { useStructuralElements } from "@/hooks/use-structural-elements";
import { useFloors } from "@/hooks/use-floors";
import { useRooms } from "@/hooks/use-rooms";
import { useDebounce } from "@/hooks/use-debounce";
import { ELEMENT_TYPES, ELEMENT_TYPE_LABELS } from "@/lib/constants";
import type { StructuralElement } from "@/types/structural-element";

export default function StructuralElementsPage() {
  const { elements, loading, createElement, updateElement, deleteElement } = useStructuralElements();
  const { floors } = useFloors();
  const { rooms } = useRooms();
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const debouncedSearch = useDebounce(search);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<StructuralElement | undefined>();
  const [deleteTarget, setDeleteTarget] = useState<StructuralElement | null>(null);

  const floorName = (id: number) => floors.find((f) => f.id === id)?.floor_name ?? `#${id}`;
  const roomName = (id: number | null) => (id ? rooms.find((r) => r.id === id)?.room_name ?? `#${id}` : "—");

  const filtered = useMemo(() => {
    const q = debouncedSearch.trim().toLowerCase();
    return elements.filter((e) => {
      const matchesSearch = !q || e.element_name.toLowerCase().includes(q) || (e.material ?? "").toLowerCase().includes(q);
      const matchesType = !typeFilter || e.element_type === typeFilter;
      return matchesSearch && matchesType;
    });
  }, [elements, debouncedSearch, typeFilter]);

  const columns: Column<StructuralElement>[] = [
    { key: "element_name", header: "Name", accessor: (e) => e.element_name, sortValue: (e) => e.element_name.toLowerCase() },
    {
      key: "element_type",
      header: "Type",
      accessor: (e) => <Badge variant="accent">{ELEMENT_TYPE_LABELS[e.element_type]}</Badge>,
      sortValue: (e) => e.element_type,
    },
    { key: "material", header: "Material", accessor: (e) => e.material ?? "—", sortValue: (e) => e.material ?? "" },
    {
      key: "floor",
      header: "Floor",
      accessor: (e) => <Link href={`/floors/${e.floor_id}`} className="hover:underline">{floorName(e.floor_id)}</Link>,
      sortValue: (e) => floorName(e.floor_id).toLowerCase(),
    },
    {
      key: "room",
      header: "Room",
      accessor: (e) => (e.room_id ? <Link href={`/rooms/${e.room_id}`} className="hover:underline">{roomName(e.room_id)}</Link> : "—"),
      sortValue: (e) => roomName(e.room_id).toLowerCase(),
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      accessor: (e) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => { setEditing(e); setFormOpen(true); }} aria-label="Edit">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(e)} aria-label="Delete">
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Structural Elements"
        description="Manage walls, beams, columns, and other structural components"
        actions={
          <Button onClick={() => { setEditing(undefined); setFormOpen(true); }}>
            <Plus className="h-4 w-4" /> New Element
          </Button>
        }
      />

      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative max-w-sm flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input placeholder="Search elements…" className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <Select className="sm:w-48" value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
          <option value="">All types</option>
          {ELEMENT_TYPES.map((t) => (
            <option key={t} value={t}>{ELEMENT_TYPE_LABELS[t]}</option>
          ))}
        </Select>
      </div>

      <Card>
        <DataTable
          columns={columns}
          data={filtered}
          loading={loading}
          rowKey={(e) => e.id}
          emptyTitle="No structural elements found"
          emptyDescription="Create your first structural element to get started."
        />
      </Card>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editing ? "Edit Structural Element" : "Create Structural Element"}</DialogTitle></DialogHeader>
          <StructuralElementForm
            element={editing}
            floors={floors}
            rooms={rooms}
            onCancel={() => setFormOpen(false)}
            onSubmit={(values) =>
              editing
                ? updateElement(editing.id, values)
                : createElement({
                    element_name: values.element_name!,
                    element_type: values.element_type!,
                    material: values.material,
                    floor_id: values.floor_id!,
                    room_id: values.room_id ? Number(values.room_id) : null,
                    dim_width: values.dim_width,
                    dim_height: values.dim_height,
                    dim_depth: values.dim_depth,
                  })
            }
          />
        </DialogContent>
      </Dialog>

      <DeleteConfirmDialog
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete structural element?"
        description={`This will permanently delete "${deleteTarget?.element_name}".`}
        onConfirm={() => deleteElement(deleteTarget!.id)}
      />
    </div>
  );
}
