"use client";

import { use, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Plus, Box } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { EmptyState } from "@/components/tables/empty-state";
import { StructuralElementForm } from "@/components/forms/structural-element-form";
import { useRooms } from "@/hooks/use-rooms";
import { useFloors } from "@/hooks/use-floors";
import { useStructuralElements } from "@/hooks/use-structural-elements";
import { ELEMENT_TYPE_LABELS } from "@/lib/constants";

export default function RoomDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const roomId = Number(id);

  const { rooms, loading: roomsLoading } = useRooms();
  const { floors } = useFloors();
  const { elements, loading: elementsLoading, createElement, refresh } = useStructuralElements(roomId);
  const [formOpen, setFormOpen] = useState(false);

  const room = rooms.find((r) => r.id === roomId);
  const floor = floors.find((f) => f.id === room?.floor_id);

  return (
    <div>
      <Link href="/rooms" className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Back to Rooms
      </Link>

      {roomsLoading ? (
        <Skeleton className="mb-6 h-10 w-64" />
      ) : (
        <PageHeader
          title={room?.room_name ?? "Room"}
          description={floor ? `${floor.floor_name} · ${room?.room_type ?? "No type"}` : undefined}
          actions={
            <Button onClick={() => setFormOpen(true)}>
              <Plus className="h-4 w-4" /> New Element
            </Button>
          }
        />
      )}

      {room && (
        <div className="mb-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
          <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Room Number</p><p className="mt-1 font-medium text-secondary">{room.room_number ?? "—"}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Type</p><p className="mt-1 font-medium text-secondary">{room.room_type ?? "—"}</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Area</p><p className="mt-1 font-medium text-secondary">{room.area ?? "—"} m²</p></CardContent></Card>
          <Card><CardContent className="p-4"><p className="text-xs text-muted-foreground">Occupancy</p><p className="mt-1 font-medium text-secondary">{room.occupancy ?? "—"}</p></CardContent></Card>
        </div>
      )}

      <h2 className="mb-3 text-sm font-semibold text-secondary">Structural Elements</h2>
      {elementsLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
      ) : elements.length === 0 ? (
        <Card><EmptyState title="No structural elements yet" description="Add an element to this room." /></Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {elements.map((el) => (
            <Card key={el.id}>
              <CardContent className="p-5">
                <div className="flex items-start justify-between">
                  <div>
                    <p className="font-medium text-secondary">{el.element_name}</p>
                    <Badge variant="accent" className="mt-2">{ELEMENT_TYPE_LABELS[el.element_type]}</Badge>
                  </div>
                  <Box className="h-5 w-5 text-primary" />
                </div>
                <div className="mt-3 text-xs text-muted-foreground">
                  {el.material && <p>Material: {el.material}</p>}
                  {(el.dim_width || el.dim_height || el.dim_depth) && (
                    <p>Dimensions: {el.dim_width ?? "—"} × {el.dim_height ?? "—"} × {el.dim_depth ?? "—"}</p>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Create Structural Element</DialogTitle></DialogHeader>
          <StructuralElementForm
            floors={floor ? [floor] : []}
            rooms={room ? [room] : []}
            defaultFloorId={room?.floor_id}
            onCancel={() => setFormOpen(false)}
            onSubmit={(values) =>
              createElement({
                element_name: values.element_name!,
                element_type: values.element_type!,
                material: values.material,
                floor_id: room?.floor_id ?? values.floor_id!,
                room_id: roomId,
                dim_width: values.dim_width,
                dim_height: values.dim_height,
                dim_depth: values.dim_depth,
              }).then((r) => { refresh(); return r; })
            }
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
