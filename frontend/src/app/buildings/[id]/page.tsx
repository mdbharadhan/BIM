"use client";

import { use, useState } from "react";
import Link from "next/link";
import { ArrowLeft, Plus, Layers } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { EmptyState } from "@/components/tables/empty-state";
import { FloorForm } from "@/components/forms/floor-form";
import { useBuildings } from "@/hooks/use-buildings";
import { useFloors } from "@/hooks/use-floors";

export default function BuildingDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const buildingId = Number(id);

  const { buildings, loading: buildingsLoading } = useBuildings();
  const { floors, loading: floorsLoading, createFloor, refresh } = useFloors(buildingId);
  const [formOpen, setFormOpen] = useState(false);

  const building = buildings.find((b) => b.id === buildingId);

  return (
    <div>
      <Link href="/buildings" className="mb-4 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
        <ArrowLeft className="h-4 w-4" /> Back to Buildings
      </Link>

      {buildingsLoading ? (
        <Skeleton className="mb-6 h-10 w-64" />
      ) : (
        <PageHeader
          title={building?.name ?? "Building"}
          description={building?.address ?? undefined}
          actions={
            <Button onClick={() => setFormOpen(true)}>
              <Plus className="h-4 w-4" /> New Floor
            </Button>
          }
        />
      )}

      {floorsLoading ? (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <Skeleton key={i} className="h-28 w-full" />
          ))}
        </div>
      ) : floors.length === 0 ? (
        <Card>
          <EmptyState title="No floors yet" description="Add a floor to this building to get started." />
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {floors
            .slice()
            .sort((a, b) => a.floor_number - b.floor_number)
            .map((floor) => (
              <Link key={floor.id} href={`/floors/${floor.id}`}>
                <Card className="transition-shadow hover:shadow-md">
                  <CardContent className="flex items-center justify-between p-5">
                    <div>
                      <p className="font-medium text-secondary">{floor.floor_name}</p>
                      <Badge variant="outline" className="mt-2">
                        Floor #{floor.floor_number}
                      </Badge>
                    </div>
                    <Layers className="h-5 w-5 text-primary" />
                  </CardContent>
                </Card>
              </Link>
            ))}
        </div>
      )}

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Create Floor</DialogTitle>
          </DialogHeader>
          <FloorForm
            buildings={building ? [building] : []}
            defaultBuildingId={buildingId}
            onCancel={() => setFormOpen(false)}
            onSubmit={(values) =>
              createFloor({
                floor_name: values.floor_name!,
                floor_number: values.floor_number!,
                building_id: values.building_id ?? buildingId,
              }).then((r) => {
                refresh();
                return r;
              })
            }
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}
