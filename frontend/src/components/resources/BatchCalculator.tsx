"use client";

import React, { useState, useEffect } from "react";
import { BatchCalculationResult } from "@/types";
import { calculateBatchesAPI } from "@/lib/api";
import { Divide, Users, CheckCircle2, AlertTriangle, RefreshCw, Edit3 } from "lucide-react";

export function BatchCalculator() {
  const [sectionStudents, setSectionStudents] = useState<number>(65);
  const [labCapacity, setLabCapacity] = useState<number>(30);
  const [namingPattern, setNamingPattern] = useState<string>("B{index}");
  const [manualCount, setManualCount] = useState<number | null>(null);
  const [isOverrideMode, setIsOverrideMode] = useState<boolean>(false);

  const [result, setResult] = useState<BatchCalculationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const runCalculation = async () => {
    setLoading(true);
    try {
      const res = await calculateBatchesAPI({
        section_students: Math.max(0, sectionStudents),
        lab_capacity: Math.max(1, labCapacity),
        naming_pattern: namingPattern,
        manual_count: isOverrideMode ? manualCount : null,
      });
      setResult(res);
    } catch (err) {
      console.error("Batch calculation error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCalculation();
  }, [sectionStudents, labCapacity, namingPattern, isOverrideMode, manualCount]);

  const totalAssigned = result?.batches.reduce((sum, b) => sum + b.student_count, 0) || 0;
  const isInvariantSatisfied = totalAssigned === sectionStudents;

  return (
    <div className="space-y-6">
      {/* Header & Formula */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Divide className="w-5 h-5 text-emerald-400" /> Deterministic Lab Batch Partitioning
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Partitions section students into lab batches based strictly on physical lab workstation capacity ($C$).
            </p>
          </div>
          <div className="px-3.5 py-1.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 font-mono text-xs">
            Formula: <b>ceil(section_students / lab_capacity)</b>
          </div>
        </div>

        {/* Inputs */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs pt-2">
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-emerald-400" /> Section Student Count
            </label>
            <input
              type="number"
              min="0"
              value={sectionStudents}
              onChange={(e) => setSectionStudents(parseInt(e.target.value) || 0)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-bold text-base focus:outline-none focus:border-emerald-500"
            />
            <p className="text-[10px] text-slate-500">e.g. 60, 65, 75</p>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-cyan-400" /> Lab Workstation Capacity
            </label>
            <input
              type="number"
              min="1"
              value={labCapacity}
              onChange={(e) => setLabCapacity(parseInt(e.target.value) || 1)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-bold text-base focus:outline-none focus:border-emerald-500"
            />
            <p className="text-[10px] text-slate-500">Workstations available in target physical lab</p>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold">Batch Naming Format</label>
            <select
              value={namingPattern}
              onChange={(e) => setNamingPattern(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs focus:outline-none focus:border-emerald-500"
            >
              <option value="B{index}">B1, B2, B3...</option>
              <option value="Batch {index}">Batch 1, Batch 2...</option>
              <option value="Group {index}">Group 1, Group 2...</option>
            </select>
            <p className="text-[10px] text-slate-500">Configurable naming pattern</p>
          </div>
        </div>

        {/* Override Bar */}
        <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => {
                setIsOverrideMode(!isOverrideMode);
                if (!isOverrideMode && result) setManualCount(result.calculated_batch_count);
              }}
              className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition ${
                isOverrideMode
                  ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
                  : "bg-slate-800 border-slate-700 text-slate-300 hover:text-white"
              }`}
            >
              <Edit3 className="w-3.5 h-3.5" />
              {isOverrideMode ? "Override Active" : "Manual Batch Count Override"}
            </button>

            {isOverrideMode && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Manual Batch Count:</span>
                <input
                  type="number"
                  min="0"
                  value={manualCount ?? ""}
                  onChange={(e) => setManualCount(parseInt(e.target.value) || 0)}
                  className="w-20 bg-slate-950 border border-amber-500/40 rounded-lg px-2.5 py-1 text-white font-bold"
                />
              </div>
            )}
          </div>

          <button
            onClick={runCalculation}
            className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Recalculate
          </button>
        </div>
      </div>

      {/* Output Results */}
      {result && (
        <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Partitioned Lab Batches ({result.actual_batch_count} Batches)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Section Size: {result.section_students} • Lab Workstation Capacity: {result.lab_capacity}
              </p>
            </div>

            {/* Invariant Badge */}
            {isInvariantSatisfied ? (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-mono font-bold">
                <CheckCircle2 className="w-3.5 h-3.5" /> Invariant: Σ Batch Students = {totalAssigned}
              </div>
            ) : (
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 border border-red-500/20 text-red-400 text-xs font-mono font-bold">
                <AlertTriangle className="w-3.5 h-3.5" /> Invariant Mismatch: Σ = {totalAssigned} != {sectionStudents}
              </div>
            )}
          </div>

          {/* Batches Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {result.batches.map((batch, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 flex flex-col justify-between space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-base font-bold text-emerald-300 font-mono bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20">
                    {batch.name}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">
                    Batch {idx + 1} of {result.actual_batch_count}
                  </span>
                </div>

                <div className="text-xs space-y-1">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Workstations Used:</span>
                    <span className="font-bold text-white text-sm">{batch.student_count} students</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-500 text-[10px]">
                    <span>Capacity Headroom:</span>
                    <span>{result.lab_capacity - batch.student_count} free seats</span>
                  </div>
                </div>

                {/* Progress bar of capacity fill */}
                <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                  <div
                    className="bg-emerald-500 h-1.5 rounded-full transition-all"
                    style={{ width: `${Math.min(100, (batch.student_count / result.lab_capacity) * 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
