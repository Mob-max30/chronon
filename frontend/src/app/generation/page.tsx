"use client";

import React, { useState, useEffect, useRef } from "react";
import { NavigationShell } from "@/components/NavigationShell";
import { triggerGenerationRun, getGenerationRunStatus, cancelGenerationRun } from "@/lib/api";
import {
  Cpu,
  Play,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Clock,
  Ban,
  ShieldCheck,
  ArrowRight,
  RefreshCw,
} from "lucide-react";
import Link from "next/link";

type RunStatus = "QUEUED" | "RUNNING" | "SUCCESS" | "FAILED" | "INFEASIBLE" | "TIMEOUT" | "CANCELLED";

export default function GenerationPage() {
  const [timetableId, setTimetableId] = useState(1);
  const [academicYearId, setAcademicYearId] = useState(1);
  const [isJoint, setIsJoint] = useState(false);
  const [maxSolverTime, setMaxSolverTime] = useState(120);
  const [notes, setNotes] = useState("Automated generation run");

  const [activeRunId, setActiveRunId] = useState<number | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null);
  const [statusDetail, setStatusDetail] = useState<any>(null);
  const [isTriggering, setIsTriggering] = useState(false);

  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Polling loop for active run status
  useEffect(() => {
    if (!activeRunId) return;

    const poll = async () => {
      try {
        const res = await getGenerationRunStatus(activeRunId);
        const data = res?.data || res;
        if (data && data.status) {
          setRunStatus(data.status);
          setStatusDetail(data);

          // Stop polling on terminal state
          if (data.is_terminal && pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
        }
      } catch (err) {
        console.error("Polling error:", err);
      }
    };

    // Immediate initial poll
    poll();

    // Setup recurring 1s poll
    pollIntervalRef.current = setInterval(poll, 1000);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
    };
  }, [activeRunId]);

  const handleTrigger = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsTriggering(true);
    setRunStatus("QUEUED");
    setStatusDetail(null);

    try {
      const res = await triggerGenerationRun({
        timetable_id: Number(timetableId),
        academic_year_id: Number(academicYearId),
        semester_ids: isJoint ? [1, 2] : [3],
        is_joint_first_year: isJoint,
        max_solver_time_seconds: Number(maxSolverTime),
        notes: notes,
      });

      const genRun = res?.generation_run || res?.data?.generation_run;
      if (genRun) {
        setActiveRunId(genRun.id);
        setRunStatus(genRun.status);
        setStatusDetail(genRun);
      }
    } catch (err) {
      console.error(err);
      setRunStatus("FAILED");
    } finally {
      setIsTriggering(false);
    }
  };

  const handleCancel = async () => {
    if (!activeRunId) return;
    try {
      const res = await cancelGenerationRun(activeRunId);
      if (res?.data) {
        setRunStatus("CANCELLED");
        setStatusDetail((prev: any) => ({ ...prev, status: "CANCELLED" }));
      }
    } catch (err) {
      console.error(err);
    }
  };

  const isRunning = runStatus === "RUNNING" || runStatus === "QUEUED";

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      <NavigationShell />

      <main className="max-w-6xl w-full mx-auto px-4 py-8 space-y-8">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
            <Cpu className="w-8 h-8 text-blue-500" /> Generation Run Lifecycle
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Application-level orchestrator: Manages state transitions (<code>QUEUED ➔ RUNNING ➔ SUCCESS / FAILED / INFEASIBLE / TIMEOUT / CANCELLED</code>), executes CP-SAT solver, and invokes independent validation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Controls Form */}
          <div className="md:col-span-1 p-6 rounded-2xl border border-slate-800 bg-slate-900/60 space-y-5">
            <h2 className="text-base font-bold text-white">Execution Parameters</h2>
            <form onSubmit={handleTrigger} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Target Timetable ID</label>
                <input
                  type="number"
                  value={timetableId}
                  onChange={(e) => setTimetableId(Number(e.target.value))}
                  disabled={isRunning}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-sm text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Cohort Mode</label>
                <div className="space-y-2 text-xs text-slate-300 pt-1">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="mode"
                      checked={!isJoint}
                      onChange={() => setIsJoint(false)}
                      disabled={isRunning}
                      className="text-blue-600 focus:ring-0"
                    />
                    <span>Single Semester (e.g. Sem 3)</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="mode"
                      checked={isJoint}
                      onChange={() => setIsJoint(true)}
                      disabled={isRunning}
                      className="text-blue-600 focus:ring-0"
                    />
                    <span>1st Year Joint (P & C Cycles)</span>
                  </label>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Max Solver Time (seconds)</label>
                <input
                  type="number"
                  value={maxSolverTime}
                  onChange={(e) => setMaxSolverTime(Number(e.target.value))}
                  disabled={isRunning}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Audit Notes</label>
                <input
                  type="text"
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  disabled={isRunning}
                  className="w-full px-3 py-2 rounded-xl bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
              </div>

              <div className="pt-2 space-y-2">
                <button
                  type="submit"
                  disabled={isRunning || isTriggering}
                  className="w-full py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20 transition disabled:opacity-50"
                >
                  {isTriggering ? (
                    <>
                      <Clock className="w-4 h-4 animate-spin" /> Initializing...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 fill-white" /> Trigger Generation Run
                    </>
                  )}
                </button>

                {isRunning && (
                  <button
                    type="button"
                    onClick={handleCancel}
                    className="w-full py-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 text-xs font-bold flex items-center justify-center gap-2 transition"
                  >
                    <Ban className="w-4 h-4" /> Cancel Active Run
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Live Run Monitor Display */}
          <div className="md:col-span-2 p-6 rounded-2xl border border-slate-800 bg-slate-900/40 flex flex-col justify-between space-y-6">
            <div>
              <div className="flex items-center justify-between border-b border-slate-800 pb-3 mb-4">
                <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                  Generation Run Monitor
                </h3>
                <span className="text-xs text-slate-400 font-mono flex items-center gap-1.5">
                  {runStatus === "QUEUED" && (
                    <span className="px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 border border-blue-500/30">
                      QUEUED
                    </span>
                  )}
                  {runStatus === "RUNNING" && (
                    <span className="px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center gap-1">
                      <RefreshCw className="w-3 h-3 animate-spin" /> RUNNING
                    </span>
                  )}
                  {runStatus === "SUCCESS" && (
                    <span className="px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                      SUCCESS
                    </span>
                  )}
                  {runStatus === "FAILED" && (
                    <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                      FAILED
                    </span>
                  )}
                  {runStatus === "INFEASIBLE" && (
                    <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
                      INFEASIBLE
                    </span>
                  )}
                  {runStatus === "TIMEOUT" && (
                    <span className="px-2 py-0.5 rounded bg-orange-500/20 text-orange-300 border border-orange-500/30">
                      TIMEOUT
                    </span>
                  )}
                  {runStatus === "CANCELLED" && (
                    <span className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                      CANCELLED
                    </span>
                  )}
                  {!runStatus && <span className="text-slate-500">Idle / Ready</span>}
                </span>
              </div>

              {runStatus ? (
                <div className="space-y-4">
                  {/* Status Banner */}
                  <div
                    className={`p-4 rounded-xl border flex items-center gap-3 ${runStatus === "SUCCESS"
                        ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-300"
                        : runStatus === "RUNNING"
                          ? "bg-blue-950/20 border-blue-500/30 text-blue-300"
                          : runStatus === "QUEUED"
                            ? "bg-slate-900 border-slate-700 text-slate-300"
                            : runStatus === "INFEASIBLE"
                              ? "bg-purple-950/20 border-purple-500/30 text-purple-300"
                              : runStatus === "TIMEOUT"
                                ? "bg-orange-950/20 border-orange-500/30 text-orange-300"
                                : runStatus === "CANCELLED"
                                  ? "bg-slate-900/60 border-slate-700 text-slate-400"
                                  : "bg-rose-950/20 border-rose-500/30 text-rose-300"
                      }`}
                  >
                    {runStatus === "SUCCESS" && <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0" />}
                    {runStatus === "RUNNING" && <RefreshCw className="w-6 h-6 text-blue-400 animate-spin shrink-0" />}
                    {runStatus === "QUEUED" && <Clock className="w-6 h-6 text-slate-400 shrink-0" />}
                    {runStatus === "INFEASIBLE" && <AlertTriangle className="w-6 h-6 text-purple-400 shrink-0" />}
                    {runStatus === "TIMEOUT" && <Clock className="w-6 h-6 text-orange-400 shrink-0" />}
                    {runStatus === "CANCELLED" && <Ban className="w-6 h-6 text-slate-400 shrink-0" />}
                    {runStatus === "FAILED" && <XCircle className="w-6 h-6 text-rose-400 shrink-0" />}

                    <div className="flex-1">
                      <div className="text-sm font-bold">
                        {runStatus === "SUCCESS" && "Deterministic CP-SAT Solution Found & Verified!"}
                        {runStatus === "RUNNING" && "CP-SAT Constraint Satisfaction In Progress..."}
                        {runStatus === "QUEUED" && "Generation Request Queued for Execution"}
                        {runStatus === "INFEASIBLE" && "Constraint Set Infeasible (Overconstrained)"}
                        {runStatus === "TIMEOUT" && "Solver Time Limit Exceeded (Timeout)"}
                        {runStatus === "CANCELLED" && "Generation Run Cancelled by User"}
                        {runStatus === "FAILED" && "Generation Failed (Validation or Execution Conflict)"}
                      </div>
                      <p className="text-xs opacity-90 mt-0.5">
                        {statusDetail?.error_message ||
                          (statusDetail?.conflict_summary?.details as string) ||
                          "Orchestration pipeline executing."}
                      </p>
                    </div>
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/80 text-center">
                      <div className="text-xs text-slate-400">Elapsed Time</div>
                      <div className="text-xl font-extrabold text-white mt-1 font-mono">
                        {statusDetail?.elapsed_seconds !== undefined
                          ? `${statusDetail.elapsed_seconds}s`
                          : statusDetail?.solver_time_seconds !== undefined
                            ? `${statusDetail.solver_time_seconds}s`
                            : "0.0s"}
                      </div>
                    </div>
                    <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/80 text-center">
                      <div className="text-xs text-slate-400">Quality Score</div>
                      <div className="text-xl font-extrabold text-blue-400 mt-1">
                        {statusDetail?.quality_score !== null && statusDetail?.quality_score !== undefined
                          ? `${statusDetail.quality_score}%`
                          : "N/A"}
                      </div>
                    </div>
                    <div className="p-3 rounded-xl border border-slate-800 bg-slate-900/80 text-center">
                      <div className="text-xs text-slate-400">Terminal State</div>
                      <div className="text-xl font-extrabold text-emerald-400 mt-1">
                        {statusDetail?.is_terminal ? "YES" : isRunning ? "NO" : "YES"}
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12 text-slate-500 space-y-2">
                  <Cpu className="w-12 h-12 mx-auto text-slate-700" />
                  <p className="text-xs">Click &quot;Trigger Generation Run&quot; to initiate the state machine.</p>
                </div>
              )}
            </div>

            {statusDetail && runStatus === "SUCCESS" && (
              <div className="pt-4 border-t border-slate-800 flex justify-end">
                <Link
                  href="/versions"
                  className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-xs font-semibold text-white flex items-center gap-2 shadow-lg shadow-blue-600/25 transition"
                >
                  Inspect Snapshot Versions & Diffs <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
