"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Plus, Pencil, Trash2, Search } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { DataTable, type Column } from "@/components/tables/data-table";
import { DeleteConfirmDialog } from "@/components/tables/delete-confirm-dialog";
import { RoomForm } from "@/components/forms/room-form";
import { useRooms } from "@/hooks/use-rooms";
import { useFloors } from "@/hooks/use-floors";
import { useDebounce } from "@/hooks/use-debounce";
import type { Room } from "@/types/room";

export default function RoomsPage() {
  const { rooms, loading, createRoom, updateRoom, deleteRoom } = useRooms();
  const { floors } = useFloors();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search);
  const [formOpen, setFormOpen] = useState(false);
  const [editing, setEditing] = useState<Room | undefined>();
  const [deleteTarget, setDeleteTarget] = useState<Room | null>(null);

  const floorName = (id: number) => floors.find((f) => f.id === id)?.floor_name ?? `#${id}`;

  const filtered = useMemo(() => {
    const q = debouncedSearch.trim().toLowerCase();
    if (!q) return rooms;
    return rooms.filter(
      (r) =>
        r.room_name.toLowerCase().includes(q) ||
        (r.room_number ?? "").toLowerCase().includes(q) ||
        (r.room_type ?? "").toLowerCase().includes(q)
    );
  }, [rooms, debouncedSearch]);

  const columns: Column<Room>[] = [
    {
      key: "room_name",
      header: "Room Name",
      accessor: (r) => (
        <Link href={`/rooms/${r.id}`} className="font-medium text-primary hover:underline">
          {r.room_name}
        </Link>
      ),
      sortValue: (r) => r.room_name.toLowerCase(),
    },
    { key: "room_number", header: "Number", accessor: (r) => r.room_number ?? "—", sortValue: (r) => r.room_number ?? "" },
    {
      key: "room_type",
      header: "Type",
      accessor: (r) => (r.room_type ? <Badge variant="outline">{r.room_type}</Badge> : "—"),
      sortValue: (r) => r.room_type ?? "",
    },
    {
      key: "floor",
      header: "Floor",
      accessor: (r) => <Link href={`/floors/${r.floor_id}`} className="hover:underline">{floorName(r.floor_id)}</Link>,
      sortValue: (r) => floorName(r.floor_id).toLowerCase(),
    },
    { key: "area", header: "Area (m²)", accessor: (r) => r.area ?? "—", sortValue: (r) => r.area ?? 0 },
    { key: "occupancy", header: "Occupancy", accessor: (r) => r.occupancy ?? "—", sortValue: (r) => r.occupancy ?? 0 },
    {
      key: "actions",
      header: "",
      className: "text-right",
      accessor: (r) => (
        <div className="flex justify-end gap-1">
          <Button variant="ghost" size="icon" onClick={() => { setEditing(r); setFormOpen(true); }} aria-label="Edit">
            <Pencil className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={() => setDeleteTarget(r)} aria-label="Delete">
            <Trash2 className="h-4 w-4 text-destructive" />
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div>
      <PageHeader
        title="Rooms"
        description="Manage rooms across all floors"
        actions={
          <Button onClick={() => { setEditing(undefined); setFormOpen(true); }}>
            <Plus className="h-4 w-4" /> New Room
          </Button>
        }
      />

      <div className="mb-4 relative max-w-sm">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search rooms…" className="pl-9" value={search} onChange={(e) => setSearch(e.target.value)} />
      </div>

      <Card>
        <DataTable
          columns={columns}
          data={filtered}
          loading={loading}
          rowKey={(r) => r.id}
          emptyTitle="No rooms found"
          emptyDescription="Create your first room to get started."
        />
      </Card>

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>{editing ? "Edit Room" : "Create Room"}</DialogTitle></DialogHeader>
          <RoomForm
            room={editing}
            floors={floors}
            onCancel={() => setFormOpen(false)}
            onSubmit={(values) =>
              editing
                ? updateRoom(editing.id, values)
                : createRoom({
                    room_name: values.room_name!,
                    room_number: values.room_number,
                    room_type: values.room_type,
                    floor_id: values.floor_id!,
                    area: values.area,
                    occupancy: values.occupancy,
                  })
            }
          />
        </DialogContent>
      </Dialog>

      <DeleteConfirmDialog
        open={Boolean(deleteTarget)}
        onOpenChange={(open) => !open && setDeleteTarget(null)}
        title="Delete room?"
        description={`This will permanently delete "${deleteTarget?.room_name}". Structural elements referencing it will have their room unset, not be deleted.`}
        onConfirm={() => deleteRoom(deleteTarget!.id)}
      />
    </div>
  );
}
