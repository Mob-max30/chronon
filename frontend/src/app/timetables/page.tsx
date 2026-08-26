"use client";

import React from "react";
import { NavigationShell } from "@/components/NavigationShell";
import { TimetableMatrixGrid } from "@/components/timetable/TimetableMatrixGrid";

export default function TimetablesPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <NavigationShell />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <TimetableMatrixGrid />
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500 print:hidden">
        <div className="max-w-7xl mx-auto px-4">
          <p>© 2026 Chronon Project • Timetable Presentation & Matrix Grid Viewer</p>
        </div>
      </footer>
    </div>
  );
}
