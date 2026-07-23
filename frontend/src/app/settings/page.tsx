"use client";

import { useState } from "react";
import { toast } from "sonner";
import { CheckCircle2, XCircle, Loader2 } from "lucide-react";
import { PageHeader } from "@/components/layout/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { api } from "@/services/api";

export default function SettingsPage() {
  const [status, setStatus] = useState<"idle" | "checking" | "ok" | "error">("idle");

  const checkConnection = async () => {
    setStatus("checking");
    try {
      await api.get("/health");
      setStatus("ok");
      toast.success("Backend is reachable");
    } catch {
      setStatus("error");
      toast.error("Could not reach the backend");
    }
  };

  return (
    <div>
      <PageHeader title="Settings" description="Backend connection and environment info" />

      <Card>
        <CardHeader>
          <CardTitle>API Connection</CardTitle>
          <CardDescription>The base URL used by every request in this app.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="rounded-lg bg-muted px-4 py-3 font-mono text-sm">
            {process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"}
          </div>
          <p className="text-xs text-muted-foreground">
            Set via <code>NEXT_PUBLIC_API_URL</code> in <code>.env.local</code>. Restart the dev server after changing it.
          </p>
          <div className="flex items-center gap-3">
            <Button onClick={checkConnection} disabled={status === "checking"} variant="outline">
              {status === "checking" ? <Loader2 className="h-4 w-4 animate-spin" /> : null}
              Test Connection
            </Button>
            {status === "ok" && (
              <span className="flex items-center gap-1 text-sm text-accent">
                <CheckCircle2 className="h-4 w-4" /> Connected
              </span>
            )}
            {status === "error" && (
              <span className="flex items-center gap-1 text-sm text-destructive">
                <XCircle className="h-4 w-4" /> Unreachable
              </span>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
