"use client";

import React, { useState, useEffect } from "react";
import { NavigationShell } from "@/components/NavigationShell";
import { getHistoricalAcademicYears, getTimetableVersions, getVersionDetail } from "@/lib/api";
import { History, Calendar, Layers, FileText, ArrowLeft, Clock, CheckCircle2, Eye } from "lucide-react";
import Link from "next/link";

export default function HistoricalYearPage() {
  const [historicalYears, setHistoricalYears] = useState<any[]>([]);
  const [selectedYearId, setSelectedYearId] = useState<number | null>(null);
  const [versions, setVersions] = useState<any[]>([]);
  const [selectedVersion, setSelectedVersion] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getHistoricalAcademicYears().then((res: any) => {
      const data = Array.isArray(res) ? res : res?.data;
      if (data) {
        setHistoricalYears(data);
        if (data.length > 0) {
          setSelectedYearId(data[0].id);
        }
      }
    });
  }, []);

  useEffect(() => {
    if (selectedYearId) {
      setLoading(true);
      getTimetableVersions(1) // Default timetable container ID
        .then((res: any) => {
          const data = Array.isArray(res) ? res : res?.data;
          if (data) setVersions(data);
        })
        .finally(() => setLoading(false));
    }
  }, [selectedYearId]);

  const handleOpenVersion = async (versionId: number) => {
    setLoading(true);
    try {
      const res = await getVersionDetail(1, versionId);
      if (res?.data) {
        setSelectedVersion(res.data);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      <NavigationShell />

      <main className="max-w-6xl w-full mx-auto px-4 py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <Link
              href="/academic-year"
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 mb-2 transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Academic Year Choice
            </Link>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              <History className="w-8 h-8 text-blue-500" /> Historical Timetable Archives
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Select an old academic session to inspect published version snapshots and historical session schedules.
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 border border-slate-700 font-bold">
            Historical Audit Mode
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Year & Version Selector */}
          <div className="md:col-span-1 p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-5">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                1. Select Academic Year
              </label>
              <select
                value={selectedYearId || ""}
                onChange={(e) => setSelectedYearId(Number(e.target.value))}
                className="w-full px-3.5 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-sm text-white focus:outline-none focus:border-blue-500"
              >
                {historicalYears.length > 0 ? (
                  historicalYears.map((y) => (
                    <option key={y.id} value={y.id}>
                      {y.name} (Past Session)
                    </option>
                  ))
                ) : (
                  <option value="">No historical years found</option>
                )}
              </select>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <label className="text-xs font-bold uppercase tracking-wider text-slate-400">
                  2. Timetable Versions
                </label>
                <span className="text-[11px] text-slate-500 font-mono">{versions.length} available</span>
              </div>

              <div className="space-y-2 max-h-64 overflow-y-auto">
                {versions.length > 0 ? (
                  versions.map((v) => (
                    <div
                      key={v.id}
                      onClick={() => handleOpenVersion(v.id)}
                      className={`p-3 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                        selectedVersion?.id === v.id
                          ? "bg-blue-950/40 border-blue-500/60"
                          : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div>
                        <div className="text-xs font-bold text-white flex items-center gap-1.5">
                          <FileText className="w-3.5 h-3.5 text-blue-400" /> Version #{v.version_number}
                        </div>
                        <div className="text-[11px] text-slate-400 mt-0.5">{v.notes || "Snapshot"}</div>
                      </div>
                      <Eye className="w-4 h-4 text-slate-400" />
                    </div>
                  ))
                ) : (
                  <p className="text-xs text-slate-500 italic py-2">No versions recorded for this session.</p>
                )}
              </div>
            </div>
          </div>

          {/* Version Snapshot Detail View */}
          <div className="md:col-span-2 p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <Layers className="w-4 h-4 text-blue-400" /> Version Configuration & Session Audit
              </h2>
              {selectedVersion && (
                <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                  Version #{selectedVersion.version_number} Loaded
                </span>
              )}
            </div>

            {selectedVersion ? (
              <div className="space-y-5">
                <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex items-center justify-between">
                  <div>
                    <h3 className="text-sm font-bold text-white">Version #{selectedVersion.version_number} Snapshot</h3>
                    <p className="text-xs text-slate-400 mt-0.5">{selectedVersion.notes}</p>
                  </div>
                  <div className="text-right text-xs text-slate-400">
                    <div>Total Sessions: <strong className="text-white">{selectedVersion.sessions?.length || 0}</strong></div>
                    <div className="text-[10px] text-slate-500 mt-0.5">{new Date(selectedVersion.created_at).toLocaleString()}</div>
                  </div>
                </div>

                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Recorded Timetable Sessions
                  </h4>
                  <div className="space-y-1.5 max-h-72 overflow-y-auto pr-1">
                    {(selectedVersion.sessions || []).map((s: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-3 rounded-lg border border-slate-800 bg-slate-900/60 flex items-center justify-between text-xs font-mono"
                      >
                        <div>
                          <span className="text-blue-300 font-bold">Subject #{s.subject_id}</span>
                          <span className="text-slate-500 ml-2">Section #{s.section_id}</span>
                        </div>
                        <div className="text-slate-400">
                          Faculty #{s.faculty_id} • Room #{s.room_id || "Lab"} • Slot #{s.time_slot_id}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-500 space-y-2">
                <FileText className="w-12 h-12 mx-auto text-slate-700" />
                <p className="text-xs">Select a version from the left panel to inspect its configuration and session schedules.</p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
