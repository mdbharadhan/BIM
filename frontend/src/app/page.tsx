"use client";

import Link from "next/link";
import { Building2, Layers, DoorOpen, Box } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useBuildings } from "@/hooks/use-buildings";
import { useFloors } from "@/hooks/use-floors";
import { useRooms } from "@/hooks/use-rooms";
import { useStructuralElements } from "@/hooks/use-structural-elements";

const STAT_CARDS = [
  { key: "buildings", label: "Buildings", href: "/buildings", icon: Building2 },
  { key: "floors", label: "Floors", href: "/floors", icon: Layers },
  { key: "rooms", label: "Rooms", href: "/rooms", icon: DoorOpen },
  { key: "elements", label: "Structural Elements", href: "/structural-elements", icon: Box },
] as const;

export default function DashboardPage() {
  const { buildings, loading: bLoading } = useBuildings();
  const { floors, loading: fLoading } = useFloors();
  const { rooms, loading: rLoading } = useRooms();
  const { elements, loading: eLoading } = useStructuralElements();

  const counts: Record<string, number> = {
    buildings: buildings.length,
    floors: floors.length,
    rooms: rooms.length,
    elements: elements.length,
  };
  const loadingMap: Record<string, boolean> = {
    buildings: bLoading,
    floors: fLoading,
    rooms: rLoading,
    elements: eLoading,
  };

  return (
    <div>
      <PageHeader title="Dashboard" description="Overview of your building information model" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {STAT_CARDS.map(({ key, label, href, icon: Icon }) => (
          <Link key={key} href={href}>
            <Card className="transition-shadow hover:shadow-md">
              <CardContent className="flex items-center justify-between p-5">
                <div>
                  <p className="text-sm text-muted-foreground">{label}</p>
                  {loadingMap[key] ? (
                    <Skeleton className="mt-2 h-8 w-12" />
                  ) : (
                    <p className="mt-1 text-3xl font-semibold text-secondary">{counts[key]}</p>
                  )}
                </div>
                <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary/10">
                  <Icon className="h-5 w-5 text-primary" />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardContent className="p-5">
            <h3 className="mb-3 text-sm font-semibold text-secondary">Recent Buildings</h3>
            {bLoading ? (
              <Skeleton className="h-24 w-full" />
            ) : buildings.length === 0 ? (
              <p className="text-sm text-muted-foreground">No buildings yet.</p>
            ) : (
              <ul className="space-y-2">
                {buildings.slice(0, 5).map((b) => (
                  <li key={b.id} className="flex items-center justify-between text-sm">
                    <span className="font-medium text-secondary">{b.name}</span>
                    <span className="text-muted-foreground">{b.address ?? "—"}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-5">
            <h3 className="mb-3 text-sm font-semibold text-secondary">Element Types</h3>
            {eLoading ? (
              <Skeleton className="h-24 w-full" />
            ) : elements.length === 0 ? (
              <p className="text-sm text-muted-foreground">No structural elements yet.</p>
            ) : (
              <ul className="space-y-2">
                {Object.entries(
                  elements.reduce<Record<string, number>>((acc, e) => {
                    acc[e.element_type] = (acc[e.element_type] ?? 0) + 1;
                    return acc;
                  }, {})
                ).map(([type, count]) => (
                  <li key={type} className="flex items-center justify-between text-sm">
                    <span className="capitalize text-secondary">{type}</span>
                    <span className="text-muted-foreground">{count}</span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
