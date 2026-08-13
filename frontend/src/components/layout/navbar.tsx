"use client";

import { Menu } from "lucide-react";
import { Breadcrumbs } from "@/components/layout/breadcrumbs";

interface NavbarProps {
  onOpenMobile: () => void;
}

export function Navbar({ onOpenMobile }: NavbarProps) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border bg-card/80 px-4 backdrop-blur sm:px-6">
      <button
        onClick={onOpenMobile}
        className="rounded-md p-2 text-muted-foreground hover:bg-muted lg:hidden"
        aria-label="Open menu"
      >
        <Menu className="h-5 w-5" />
      </button>
      <Breadcrumbs />
      <div className="ml-auto flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-primary/10 text-xs font-semibold text-primary">
          AD
        </div>
      </div>
    </header>
  );
}
