"use client";

import React, { useState, useEffect } from "react";
import { SectionCalculationResult } from "@/types";
import { calculateSectionsAPI } from "@/lib/api";
import { Calculator, Users, AlertCircle, CheckCircle, RefreshCw, SlidersHorizontal, Edit3 } from "lucide-react";

export function SectionCalculator() {
  const [studentCount, setStudentCount] = useState<number>(180);
  const [roomCapacity, setRoomCapacity] = useState<number>(60);
  const [namingPattern, setNamingPattern] = useState<string>("ALPHABETIC");
  const [balanceDistribution, setBalanceDistribution] = useState<boolean>(false);
  const [manualCount, setManualCount] = useState<number | null>(null);
  const [streamId, setStreamId] = useState<number | null>(null);
  const [cycleGroup, setCycleGroup] = useState<string>("");
  const [isOverrideMode, setIsOverrideMode] = useState<boolean>(false);

  const [result, setResult] = useState<SectionCalculationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const runCalculation = async () => {
    setLoading(true);
    try {
      const res = await calculateSectionsAPI({
        student_count: Math.max(0, studentCount),
        room_capacity: Math.max(1, roomCapacity),
        naming_pattern: namingPattern,
        manual_count: isOverrideMode ? manualCount : null,
        stream_id: streamId,
        cycle_group: cycleGroup || null,
        balance_distribution: balanceDistribution,
      });
      setResult(res);
    } catch (err) {
      console.error("Section calculation error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runCalculation();
  }, [studentCount, roomCapacity, namingPattern, balanceDistribution, isOverrideMode, manualCount, streamId, cycleGroup]);

  return (
    <div className="space-y-6">
      {/* Formula & Explainer Card */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Calculator className="w-5 h-5 text-blue-400" /> Deterministic Section Calculation
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Calculates academic classroom sections strictly from admitted student counts and classroom capacity.
            </p>
          </div>
          <div className="px-3.5 py-1.5 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-300 font-mono text-xs">
            Formula: <b>ceil(students / room_capacity)</b>
          </div>
        </div>

        {/* Input Parameters Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs pt-2">
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-blue-400" /> Admitted Student Count
            </label>
            <input
              type="number"
              min="0"
              value={studentCount}
              onChange={(e) => setStudentCount(parseInt(e.target.value) || 0)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-bold text-base focus:outline-none focus:border-blue-500"
            />
            <p className="text-[10px] text-slate-500">e.g. 180, 181, 60, 240</p>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold flex items-center gap-1.5">
              <SlidersHorizontal className="w-3.5 h-3.5 text-indigo-400" /> Classroom Capacity
            </label>
            <input
              type="number"
              min="1"
              value={roomCapacity}
              onChange={(e) => setRoomCapacity(parseInt(e.target.value) || 1)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-bold text-base focus:outline-none focus:border-blue-500"
            />
            <p className="text-[10px] text-slate-500">From verified Room entity</p>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold">Naming Pattern</label>
            <select
              value={namingPattern}
              onChange={(e) => setNamingPattern(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="ALPHABETIC">Alphabetic (A, B, C...)</option>
              <option value="Section {index}">Prefix (Section 1, Section 2...)</option>
              <option value="SEC-{index}">Code (SEC-1, SEC-2...)</option>
            </select>
            <div className="flex items-center gap-2 pt-1">
              <input
                type="checkbox"
                id="balancedSplit"
                checked={balanceDistribution}
                onChange={(e) => setBalanceDistribution(e.target.checked)}
                className="rounded border-slate-800 bg-slate-900 text-blue-600 focus:ring-0"
              />
              <label htmlFor="balancedSplit" className="text-[10px] text-slate-400">
                Balance students evenly
              </label>
            </div>
          </div>

          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold">First-Year Cycle Cohort</label>
            <select
              value={cycleGroup}
              onChange={(e) => setCycleGroup(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white text-xs focus:outline-none focus:border-blue-500"
            >
              <option value="">None (Higher Semester 3-8)</option>
              <option value="PHYSICS_CYCLE">Physics Cycle Cohort</option>
              <option value="CHEMISTRY_CYCLE">Chemistry Cycle Cohort</option>
            </select>
            <p className="text-[10px] text-slate-500">Mirrored joint 1st-year cycle</p>
          </div>
        </div>

        {/* Manual Override Controls */}
        <div className="pt-3 border-t border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={() => {
                setIsOverrideMode(!isOverrideMode);
                if (!isOverrideMode && result) setManualCount(result.calculated_section_count);
              }}
              className={`px-3 py-1.5 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition ${
                isOverrideMode
                  ? "bg-amber-500/10 border-amber-500/30 text-amber-300"
                  : "bg-slate-800 border-slate-700 text-slate-300 hover:text-white"
              }`}
            >
              <Edit3 className="w-3.5 h-3.5" />
              {isOverrideMode ? "Override Active" : "Enable Manual Section Override"}
            </button>

            {isOverrideMode && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Manual Section Count:</span>
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
            className="text-xs text-blue-400 hover:text-blue-300 flex items-center gap-1 font-medium"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin" : ""}`} /> Recalculate
          </button>
        </div>
      </div>

      {/* Result Display */}
      {result && (
        <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Calculation Output
                {result.is_override ? (
                  <span className="text-[10px] text-amber-400 bg-amber-500/10 px-2.5 py-0.5 rounded-full border border-amber-500/20 font-mono font-semibold">
                    MANUAL OVERRIDE APPLIED
                  </span>
                ) : (
                  <span className="text-[10px] text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20 font-mono font-semibold">
                    DETERMINISTIC STRICT MATCH
                  </span>
                )}
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Calculated {result.calculated_section_count} section(s) • Actual configured: {result.actual_section_count} section(s)
              </p>
            </div>

            <div className="flex items-center gap-2 text-xs font-mono">
              <span className="text-slate-400">Total Enrolled:</span>
              <span className="text-white font-bold">{result.student_count}</span>
            </div>
          </div>

          {/* Section Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {result.sections.map((sec, idx) => (
              <div
                key={idx}
                className="p-4 rounded-xl border border-slate-800 bg-slate-950/60 flex flex-col justify-between space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-base font-bold text-white font-mono bg-blue-500/10 px-2.5 py-1 rounded-lg border border-blue-500/20">
                    Section {sec.name}
                  </span>
                  {sec.cycle_group && (
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-300">
                      {sec.cycle_group.replace("_CYCLE", "")}
                    </span>
                  )}
                </div>

                <div className="text-xs space-y-1">
                  <div className="flex items-center justify-between text-slate-400">
                    <span>Student Count:</span>
                    <span className="font-bold text-white text-sm">{sec.student_count} students</span>
                  </div>
                  <div className="flex items-center justify-between text-slate-500 text-[10px]">
                    <span>Room Capacity:</span>
                    <span>{result.room_capacity} seats</span>
                  </div>
                </div>

                {sec.student_count > result.room_capacity ? (
                  <div className="text-[10px] text-amber-400 bg-amber-500/10 p-1.5 rounded flex items-center gap-1 font-medium">
                    <AlertCircle className="w-3 h-3" /> Exceeds room capacity
                  </div>
                ) : (
                  <div className="text-[10px] text-emerald-400 bg-emerald-500/10 p-1.5 rounded flex items-center gap-1 font-medium">
                    <CheckCircle className="w-3 h-3" /> Within room capacity
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
