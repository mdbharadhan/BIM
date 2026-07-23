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
import { BuildingForm } from "@/components/forms/building-form";
import { useBuildings } from "@/hooks/use-buildings";
import { useDebounce } from "@/hooks/use-debounce";
import type { Building } from "@/types/building";

export default function BuildingsPage() {
  const { buildings, loading, createBuilding, updateBuilding, deleteBuilding } = useBuildings();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Building | undefined>();
  const [deleteTarget, setDeleteTarget] = useState<Building | null>(null);

  const filtered = useMemo(() => {
    const q = debouncedSearch.trim().toLowerCase();
    if (!q) return buildings;
    return buildings.filter(
      (b) => b.name.toLowerCase().includes(q) || (b.address ?? "").toLowerCase().includes(q)
    );
  }, [buildings, debouncedSearch]);

  const columns: Column<Building>[] = [
    {
      key: "name",
      header: "Name",
      accessor: (b) => (
        <Link href={`/buildings/${b.id}`} className="font-medium text-primary hover:underline">
          {b.name}
        </Link>
      ),
      sortValue: (b) => b.name.toLowerCase(),
    },
    {
      key: "address",
      header: "Address",
      accessor: (b) => b.address ?? <span className="text-muted-foreground">—</span>,
      sortValue: (b) => (b.address ?? "").toLowerCase(),
    },
    {
      key: "actions",
      header: "",
      className: "text-right",
      accessor: (b) => (
        <div className="flex justify-end gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => {
              setEditing(b);
              setFormOpen(true);
            }}
            aria-label="Edit"
          >
            <Pencil className="h-4 w-4" />
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setDeleteTarget(b)}
            aria-label="Delete"
          >
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Buildings"
        description="Manage buildings in your portfolio"
        actions={
          <Button
            onClick={() => {
              setEditing(undefined);
              setFormOpen(true);
            }}
          >
            <Plus className="h-4 w-4" /> New Building
          </Button>
        }
      />

      <div className="mb-4 relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search buildings…"
          className="pl-9"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <Card>
        <DataTable
          columns={columns}
          data={filtered}
          loading={loading}
          rowKey={(b) => b.id}
          emptyTitle="No buildings found"
          emptyDescription="Create your first building to get started."
        />
      </Card>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editing ? "Edit Building" : "Create Building"}</DialogTitle>
          </DialogHeader>
          <BuildingForm
            building={editing}
            onCancel={() => setFormOpen(false)}
            onSubmit={(values) =>
              editing ? updateBuilding(editing.id, values) : createBuilding({ name: values.name!, address: values.address })
            }
          />
        </DialogContent>
      </Dialog>

      <DeleteConfirmDialog
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete building?"
        description={`This will permanently delete "${deleteTarget?.name}" and all its floors, rooms, and structural elements.`}
        onConfirm={() => deleteBuilding(deleteTarget!.id)}
      />
    </div>
  );
}
