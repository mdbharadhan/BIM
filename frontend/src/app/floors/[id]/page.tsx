"use client";

import { use, useMemo, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Plus, DoorOpen, Box } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { EmptyState } from "@/components/tables/empty-state";
import { RoomForm } from "@/components/forms/room-form";
import { useFloors } from "@/hooks/use-floors";
import { useRooms } from "@/hooks/use-rooms";
import { useStructuralElements } from "@/hooks/use-structural-elements";
import { ELEMENT_TYPE_LABELS } from "@/lib/constants";

export default function FloorDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const floorId = Number(id);

  const { floors, loading: floorsLoading } = useFloors();
  const { rooms, loading: roomsLoading, createRoom, refresh } = useRooms(floorId);
  const { elements, loading: elementsLoading } = useStructuralElements();
  const [formOpen, setFormOpen] = useState(false);

  const floor = floors.find((f) => f.id === floorId);

  // No /floors/{id}/elements endpoint exists on the backend — derive the
  // floor's unassigned (room_id = null) elements client-side from the full list.
  const unassignedElements = useMemo(
    () => elements.filter((e) => e.floor_id === floorId && e.room_id === null),
    [elements, floorId]
  );

  return (
    <div>
      <Link href="/floors" className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Back to Floors
      </Link>

      {floorsLoading ? (
        <Skeleton className="mb-6 h-10 w-64" />
      ) : (
        <PageHeader
          title={floor?.floor_name ?? "Floor"}
          description={floor ? `Floor #${floor.floor_number}` : undefined}
          actions={
            <Button onClick={() => setFormOpen(true)}>
              <Plus className="h-4 w-4" /> New Room
            </Button>
          }
        />
      )}

      <h2 className="mb-3 text-sm font-semibold text-secondary">Rooms</h2>
      {roomsLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
      ) : rooms.length === 0 ? (
        <Card><EmptyState title="No rooms yet" description="Add a room to this floor." /></Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {rooms.map((room) => (
            <Link key={room.id} href={`/rooms/${room.id}`}>
              <Card className="transition-shadow hover:shadow-md">
                <CardContent className="flex items-center justify-between p-5">
                  <div>
                    <p className="font-medium text-secondary">{room.room_name}</p>
                    <p className="mt-1 text-xs text-muted-foreground">{room.room_type ?? "—"}</p>
                  </div>
                  <DoorOpen className="h-5 w-5 text-primary" />
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}

      <h2 className="mb-3 mt-8 text-sm font-semibold text-secondary">Unassigned Structural Elements</h2>
      <p className="mb-3 -mt-2 text-xs text-muted-foreground">
        Elements on this floor with no specific room (e.g. exterior walls, roof slabs).
      </p>
      {elementsLoading ? (
        <Skeleton className="h-20 w-full" />
      ) : unassignedElements.length === 0 ? (
        <Card><EmptyState title="No unassigned elements" /></Card>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {unassignedElements.map((el) => (
            <Card key={el.id}>
              <CardContent className="flex items-center justify-between p-4">
                <div>
                  <p className="text-sm font-medium text-secondary">{el.element_name}</p>
                  <Badge variant="accent" className="mt-1">{ELEMENT_TYPE_LABELS[el.element_type]}</Badge>
                </div>
                <Box className="h-4 w-4 text-muted-foreground" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create Room</DialogTitle></DialogHeader>
          <RoomForm
            floors={floor ? [floor] : []}
            defaultFloorId={floorId}
            onCancel={() => setFormOpen(false)}
            onSubmit={(values) =>
              createRoom({
                room_name: values.room_name!,
                room_number: values.room_number,
                room_type: values.room_type,
                floor_id: values.floor_id ?? floorId,
                area: values.area,
                occupancy: values.occupancy,
              }).then((r) => { refresh(); return r; })
            }
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
