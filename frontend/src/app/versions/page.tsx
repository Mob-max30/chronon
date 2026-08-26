"use client";

import React, { useState, useEffect, useCallback } from "react";
import { NavigationShell } from "@/components/NavigationShell";
import { getTimetableVersions, setActiveVersion, compareVersions } from "@/lib/api";
import { Layers, GitCommit, CheckCircle2, ArrowRightLeft, Clock, History } from "lucide-react";

export default function VersionsPage() {
  const [timetableId, setTimetableId] = useState(1);
  const [versions, setVersions] = useState<any[]>([]);
  const [fromVer, setFromVer] = useState<number | null>(null);
  const [toVer, setToVer] = useState<number | null>(null);
  const [diffResult, setDiffResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadVersions = useCallback(async () => {
    try {
      const res = await getTimetableVersions(timetableId);
      const data = Array.isArray(res) ? res : res?.data || [];
      if (Array.isArray(data)) {
        setVersions(data);
        if (data.length >= 2) {
          setFromVer(data[1].id);
          setToVer(data[0].id);
        } else if (data.length === 1) {
          setToVer(data[0].id);
        }
      }
    } catch (e) {
      console.error("Failed to load versions:", e);
    }
  }, [timetableId]);

  useEffect(() => {
    loadVersions();
  }, [loadVersions]);

  const handlePromote = async (versionId: number) => {
    await setActiveVersion(timetableId, versionId);
    await loadVersions();
  };

  const handleCompare = async () => {
    if (!fromVer || !toVer) return;
    setLoading(true);
    try {
      const res = await compareVersions(timetableId, fromVer, toVer);
      const data = res?.differences ? res : (res?.data || res);
      if (data) {
        setDiffResult(data);
      }
    } catch (e) {
      console.error("Failed to compare versions:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      <NavigationShell />

      <main className="max-w-6xl w-full mx-auto px-4 py-8 space-y-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Layers className="w-8 h-8 text-blue-500" /> Timetable Versioning & Audit Diffs
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Audit historical timetable snapshots, promote or rollback active schedules, and inspect granular session diffs.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Version Snapshot History Timeline */}
          <div className="md:col-span-1 p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <History className="w-4 h-4 text-blue-400" /> Snapshot History
              </h2>
              <span className="text-xs font-mono text-slate-500">{versions.length} versions</span>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto pr-1">
              {versions.length > 0 ? (
                versions.map((ver) => (
                  <div
                    key={ver.id}
                    className={`p-3.5 rounded-xl border transition ${
                      ver.is_active
                        ? "bg-blue-950/30 border-blue-500/40"
                        : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-white flex items-center gap-1.5">
                        <GitCommit className="w-4 h-4 text-blue-400" /> v{ver.version_number}
                      </span>
                      {ver.is_active ? (
                        <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center gap-1">
                          <CheckCircle2 className="w-3 h-3" /> Active
                        </span>
                      ) : (
                        <button
                          onClick={() => handlePromote(ver.id)}
                          className="text-xs text-blue-400 hover:underline font-medium"
                        >
                          Promote Active
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-slate-400 mt-2 line-clamp-1">{ver.notes || "No audit notes"}</p>
                    <div className="text-[10px] text-slate-500 mt-1 flex items-center gap-1">
                      <Clock className="w-3 h-3" /> {new Date(ver.created_at).toLocaleDateString()}
                    </div>
                  </div>
                ))
              ) : (
                <p className="text-xs text-slate-500 italic py-4">No version snapshots created yet.</p>
              )}
            </div>
          </div>

          {/* Version Diff Engine Comparison Panel */}
          <div className="md:col-span-2 p-6 rounded-2xl border border-slate-800 bg-slate-900/40 space-y-6">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
                <ArrowRightLeft className="w-4 h-4 text-blue-400" /> Granular Version Diff
              </h2>
            </div>

            {/* Compare Controls */}
            <div className="flex flex-wrap items-center gap-4 bg-slate-900/90 p-4 rounded-xl border border-slate-800">
              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400 font-medium">Base:</span>
                <select
                  value={fromVer || ""}
                  onChange={(e) => setFromVer(Number(e.target.value))}
                  className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none"
                >
                  {versions.map((v) => (
                    <option key={v.id} value={v.id}>
                      v{v.version_number}
                    </option>
                  ))}
                </select>
              </div>

              <span className="text-slate-600">➔</span>

              <div className="flex items-center gap-2 text-xs">
                <span className="text-slate-400 font-medium">Compare with:</span>
                <select
                  value={toVer || ""}
                  onChange={(e) => setToVer(Number(e.target.value))}
                  className="bg-slate-800 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-white focus:outline-none"
                >
                  {versions.map((v) => (
                    <option key={v.id} value={v.id}>
                      v{v.version_number}
                    </option>
                  ))}
                </select>
              </div>

              <button
                onClick={handleCompare}
                disabled={loading || !fromVer || !toVer}
                className="ml-auto px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition disabled:opacity-50"
              >
                {loading ? "Diffing..." : "Compare Snapshots"}
              </button>
            </div>

            {/* Diff Results Grid */}
            {diffResult ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>
                    Total Differences Detected:{" "}
                    <strong className="text-white">{diffResult.total_differences}</strong>
                  </span>
                  <span>
                    Comparing v{diffResult.from_version_number} vs v{diffResult.to_version_number}
                  </span>
                </div>

                <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
                  {diffResult.differences.map((d: any, idx: number) => (
                    <div
                      key={idx}
                      className="p-3 rounded-xl border border-slate-800 bg-slate-900/80 flex items-center justify-between text-xs font-mono"
                    >
                      <div className="space-x-2">
                        <span className="text-slate-300">Subject #{d.subject_id}</span>
                        <span className="text-slate-500">(Section #{d.section_id})</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                            d.diff_type === "MODIFIED"
                              ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                              : d.diff_type === "ADDED"
                              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                              : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                          }`}
                        >
                          {d.diff_type}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-10 text-slate-500 text-xs">
                Select two version snapshots above and click &quot;Compare Snapshots&quot; to audit changes.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
