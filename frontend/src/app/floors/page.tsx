"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Plus, Pencil, Trash2, Search } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DataTable, type Column } from "@/components/tables/data-table";
import { DeleteConfirmDialog } from "@/components/tables/delete-confirm-dialog";
import { FloorForm } from "@/components/forms/floor-form";
import { useFloors } from "@/hooks/use-floors";
import { useBuildings } from "@/hooks/use-buildings";
import { useDebounce } from "@/hooks/use-debounce";
import type { Floor } from "@/types/floor";

export default function FloorsPage() {
  const { floors, loading, createFloor, updateFloor, deleteFloor } = useFloors();
  const { buildings } = useBuildings();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Floor | undefined>();
  const [deleteTarget, setDeleteTarget] = useState<Floor | null>(null);

  const buildingName = (id: number) => buildings.find((b) => b.id === id)?.name ?? `#${id}`;

  const filtered = useMemo(() => {
    const q = debouncedSearch.trim().toLowerCase();
    if (!q) return floors;
    return floors.filter(
      (f) => f.floor_name.toLowerCase().includes(q) || buildingName(f.building_id).toLowerCase().includes(q)
    );
  }, [floors, debouncedSearch, buildings]);

  const columns: Column<Floor>[] = [
    {
      key: "floor_name",
      header: "Floor Name",
      accessor: (f) => (
        <Link href={`/floors/${f.id}`} className="font-medium text-primary hover:underline">
          {f.floor_name}
        </Link>
      ),
      sortValue: (f) => f.floor_name.toLowerCase(),
    },
    {
      key: "floor_number",
      header: "Number",
      accessor: (f) => f.floor_number,
      sortValue: (f) => f.floor_number,
    },
    {
      key: "building",
      header: "Building",
      accessor: (f) => (
        <Link href={`/buildings/${f.building_id}`} className="hover:underline">
          {buildingName(f.building_id)}
        </Link>
      ),
      sortValue: (f) => buildingName(f.building_id).toLowerCase(),
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      accessor: (f) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => { setEditing(f); setFormOpen(true); }} aria-label="Edit">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(f)} aria-label="Delete">
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Floors"
        description="Manage floors across all buildings"
        actions={
          <Button onClick={() => { setEditing(undefined); setFormOpen(true); }}>
            <Plus className="h-4 w-4" /> New Floor
          </Button>
        }
      />

      <div className="mb-4 relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search floors…" className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      <Card>
        <DataTable
          columns={columns}
          data={filtered}
          loading={loading}
          rowKey={(f) => f.id}
          emptyTitle="No floors found"
          emptyDescription="Create your first floor to get started."
        />
      </Card>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Edit Floor" : "Create Floor"}</DialogTitle>
          </DialogHeader>
          <FloorForm
            floor={editing}
            buildings={buildings}
            onCancel={() => setFormOpen(false)}
            onSubmit={(values) =>
              editing
                ? updateFloor(editing.id, values)
                : createFloor({
                    floor_name: values.floor_name!,
                    floor_number: values.floor_number!,
                    building_id: values.building_id!,
                  })
            }
          />
        </DialogContent>
      </Dialog>

      <DeleteConfirmDialog
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete floor?"
        description={`This will permanently delete "${deleteTarget?.floor_name}" and all its rooms and structural elements.`}
        onConfirm={() => deleteFloor(deleteTarget!.id)}
      />
    </div>
  );
}
