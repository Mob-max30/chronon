"use client";

import React, { useState, useEffect } from "react";
import { NavigationShell } from "@/components/NavigationShell";
import { getAcademicYears, createAcademicYear, setCurrentAcademicYear } from "@/lib/api";
import { Calendar, CheckCircle2, History, Plus, ArrowRight, Sparkles } from "lucide-react";
import Link from "next/link";

export default function AcademicYearPage() {
  const [years, setYears] = useState<any[]>([]);
  const [newYearName, setNewYearName] = useState("");
  const [isCurrent, setIsCurrent] = useState(true);
  const [loading, setLoading] = useState(false);

  const loadYears = async () => {
    try {
      const res = await getAcademicYears();
      if (res?.data) setYears(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    loadYears();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newYearName) return;
    setLoading(true);
    try {
      await createAcademicYear(newYearName, isCurrent);
      setNewYearName("");
      await loadYears();
    } finally {
      setLoading(false);
    }
  };

  const currentYear = years.find((y) => y.is_current);
  const oldYears = years.filter((y) => !y.is_current);

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      <NavigationShell />

      <main className="max-w-6xl w-full mx-auto px-4 py-8 space-y-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Calendar className="w-8 h-8 text-blue-500" /> Choose Academic Year
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Chronon Step 1: Select between generating a timetable for the <strong>Current Year</strong> session or viewing <strong>Old Year</strong> historical versions.
          </p>
        </div>

        {/* Workflow Choice Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Current Year Choice */}
          <div className="p-8 rounded-3xl border border-blue-500/50 bg-gradient-to-b from-blue-950/40 to-slate-900/60 flex flex-col justify-between space-y-6 shadow-xl shadow-blue-950/20">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider font-extrabold text-blue-300 bg-blue-500/20 px-3 py-1 rounded-md border border-blue-500/30">
                  Current Session
                </span>
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              </div>
              <h2 className="text-2xl font-bold text-white">
                {currentYear ? currentYear.name : "2026-2027 (Active Session)"}
              </h2>
              <p className="text-sm text-slate-300 leading-relaxed">
                Start the complete deterministic timetable generation pipeline: select institution type, engineering year (1st–4th), and applicable Odd/Even semester.
              </p>
            </div>

            <Link
              href="/academic-year/current"
              className="w-full py-3.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-blue-600/30 transition"
            >
              <Sparkles className="w-4 h-4" /> Create New Timetable <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {/* Old Year Choice */}
          <div className="p-8 rounded-3xl border border-slate-800 bg-slate-900/50 flex flex-col justify-between space-y-6">
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs uppercase tracking-wider font-bold text-slate-400 bg-slate-800 px-3 py-1 rounded-md border border-slate-700">
                  Historical Archive
                </span>
                <History className="w-6 h-6 text-slate-400" />
              </div>
              <h2 className="text-2xl font-bold text-slate-200">
                Old Academic Years
              </h2>
              <p className="text-sm text-slate-400 leading-relaxed">
                Inspect previous academic sessions, view published timetable version snapshots, examine session schedules, and audit historical configuration parameters.
              </p>
            </div>

            <Link
              href="/academic-year/historical"
              className="w-full py-3.5 rounded-xl border border-slate-700 hover:border-slate-600 bg-slate-800/80 hover:bg-slate-800 text-slate-200 font-bold text-sm flex items-center justify-center gap-2 transition"
            >
              <History className="w-4 h-4" /> View / Edit Previous Versions <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>

        {/* Add New Session Form */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/40 max-w-xl space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
            <Plus className="w-4 h-4 text-blue-400" /> Register New Academic Session
          </h3>
          <form onSubmit={handleCreate} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Session Name</label>
              <input
                type="text"
                placeholder="e.g. 2027-2028"
                value={newYearName}
                onChange={(e) => setNewYearName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800/80 border border-slate-700 text-sm text-white focus:outline-none focus:border-blue-500"
              />
            </div>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="isCurrent"
                checked={isCurrent}
                onChange={(e) => setIsCurrent(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800 text-blue-600 focus:ring-0"
              />
              <label htmlFor="isCurrent" className="text-xs text-slate-300 cursor-pointer">
                Set as active current session (atomically unsets previous active year)
              </label>
            </div>
            <button
              type="submit"
              disabled={loading || !newYearName}
              className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition disabled:opacity-50"
            >
              {loading ? "Registering..." : "Save Academic Year"}
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}
