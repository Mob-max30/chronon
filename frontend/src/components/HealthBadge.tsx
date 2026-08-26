"use client";

import React, { useEffect, useState } from "react";
import { checkBackendHealth } from "@/lib/api";
import { Activity, CheckCircle2, AlertCircle } from "lucide-react";

export function HealthBadge() {
  const [health, setHealth] = useState<{ status: string; service?: string } | null>(null);

  useEffect(() => {
    checkBackendHealth().then(setHealth);
  }, []);

  const isOk = health?.status === "ok";

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-slate-800 bg-slate-900/90 text-xs">
      <Activity className="w-3.5 h-3.5 text-blue-400 animate-pulse" />
      <span className="text-slate-400">Backend API:</span>
      {health === null ? (
        <span className="text-slate-500">Checking...</span>
      ) : isOk ? (
        <span className="flex items-center gap-1 text-emerald-400 font-medium">
          <CheckCircle2 className="w-3.5 h-3.5" /> Healthy
        </span>
      ) : (
        <span className="flex items-center gap-1 text-amber-400 font-medium">
          <AlertCircle className="w-3.5 h-3.5" /> Ready (Pending Server Start)
        </span>
      )}
    </div>
  );
}
