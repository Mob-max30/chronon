"use client";

import React, { useState } from "react";
import { NavigationShell } from "@/components/NavigationShell";
import { School, Layers, CheckCircle2, ArrowRight, ArrowLeft, Info } from "lucide-react";
import Link from "next/link";

export default function CurrentYearSetupPage() {
  const [institutionType, setInstitutionType] = useState<"VTU_AFFILIATED" | "AUTONOMOUS_UNIVERSITY">("VTU_AFFILIATED");
  const [yearLevel, setYearLevel] = useState<number>(2); // 1, 2, 3, 4
  const [termType, setTermType] = useState<"ODD" | "EVEN">("ODD");
  const [firstYearCycle, setFirstYearCycle] = useState<"PHYSICS" | "CHEMISTRY" | "JOINT">("JOINT");

  // Determine applicable semesters based on chosen year level and term type
  const getSemesterNumber = () => {
    if (yearLevel === 1) {
      return termType === "ODD" ? 1 : 2;
    } else if (yearLevel === 2) {
      return termType === "ODD" ? 3 : 4;
    } else if (yearLevel === 3) {
      return termType === "ODD" ? 5 : 6;
    } else {
      return termType === "ODD" ? 7 : 8;
    }
  };

  const selectedSem = getSemesterNumber();

  const romanSemesters: Record<number, string> = {
    1: "I Sem",
    2: "II Sem",
    3: "III Sem",
    4: "IV Sem",
    5: "V Sem",
    6: "VI Sem",
    7: "VII Sem",
    8: "VIII Sem",
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      <NavigationShell />

      <main className="max-w-4xl w-full mx-auto px-4 py-8 space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <Link
              href="/academic-year"
              className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 mb-2 transition"
            >
              <ArrowLeft className="w-3.5 h-3.5" /> Back to Academic Year Choice
            </Link>
            <h1 className="text-3xl font-extrabold text-white tracking-tight flex items-center gap-3">
              <School className="w-8 h-8 text-blue-500" /> Create New Timetable
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Step 1: Select institution affiliation scheme, engineering academic year, and applicable semester.
            </p>
          </div>
          <span className="text-xs font-mono px-3 py-1.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20 font-bold">
            Workflow: Step 01 / 07
          </span>
        </div>

        <div className="space-y-6">
          {/* 1. Institution Type Selection */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              1. Institution / Affiliation Type
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-1">
              <div
                onClick={() => setInstitutionType("VTU_AFFILIATED")}
                className={`p-4 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                  institutionType === "VTU_AFFILIATED"
                    ? "bg-blue-950/30 border-blue-500/60 shadow-lg shadow-blue-950/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div>
                  <h4 className="text-sm font-bold text-white">VTU-Affiliated College</h4>
                  <p className="text-xs text-slate-400 mt-0.5">Pre-populated VTU curriculum scheme & subjects</p>
                </div>
                {institutionType === "VTU_AFFILIATED" && <CheckCircle2 className="w-5 h-5 text-blue-400" />}
              </div>

              <div
                onClick={() => setInstitutionType("AUTONOMOUS_UNIVERSITY")}
                className={`p-4 rounded-xl border cursor-pointer transition flex items-center justify-between ${
                  institutionType === "AUTONOMOUS_UNIVERSITY"
                    ? "bg-blue-950/30 border-blue-500/60 shadow-lg shadow-blue-950/20"
                    : "bg-slate-900/80 border-slate-800 hover:border-slate-700"
                }`}
              >
                <div>
                  <h4 className="text-sm font-bold text-white">Autonomous University</h4>
                  <p className="text-xs text-slate-400 mt-0.5">Custom autonomous syllabus & course structures</p>
                </div>
                {institutionType === "AUTONOMOUS_UNIVERSITY" && <CheckCircle2 className="w-5 h-5 text-blue-400" />}
              </div>
            </div>
          </div>

          {/* 2. Choose Year Level */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-3">
            <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
              2. Choose Engineering Year
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
              {[
                { level: 1, label: "1st Year", note: "I & II Sem (P&C Cycle)" },
                { level: 2, label: "2nd Year", note: "III & IV Sem" },
                { level: 3, label: "3rd Year", note: "V & VI Sem" },
                { level: 4, label: "4th Year", note: "VII & VIII Sem" },
              ].map((yr) => (
                <div
                  key={yr.level}
                  onClick={() => setYearLevel(yr.level)}
                  className={`p-4 rounded-xl border cursor-pointer text-center transition ${
                    yearLevel === yr.level
                      ? "bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-600/30"
                      : "bg-slate-900/80 border-slate-800 text-slate-300 hover:border-slate-700"
                  }`}
                >
                  <div className="text-base font-extrabold">{yr.label}</div>
                  <div className="text-[11px] opacity-80 mt-0.5">{yr.note}</div>
                </div>
              ))}
            </div>
          </div>

          {/* 3. Applicable Semester Selection */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/50 space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300">
                3. Applicable Semester Target
              </h3>
              <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-md border border-emerald-500/20">
                Auto-Prompt: {romanSemesters[selectedSem]} Selected
              </span>
            </div>

            {/* Odd / Even Toggle */}
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setTermType("ODD")}
                className={`py-3 px-4 rounded-xl border text-xs font-bold transition flex items-center justify-center gap-2 ${
                  termType === "ODD"
                    ? "bg-blue-950/40 border-blue-500/60 text-blue-300 shadow-md"
                    : "bg-slate-900/80 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                Odd Semester (e.g. {yearLevel === 1 ? "I Sem" : yearLevel === 2 ? "III Sem" : yearLevel === 3 ? "V Sem" : "VII Sem"})
              </button>

              <button
                type="button"
                onClick={() => setTermType("EVEN")}
                className={`py-3 px-4 rounded-xl border text-xs font-bold transition flex items-center justify-center gap-2 ${
                  termType === "EVEN"
                    ? "bg-blue-950/40 border-blue-500/60 text-blue-300 shadow-md"
                    : "bg-slate-900/80 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                Even Semester (e.g. {yearLevel === 1 ? "II Sem" : yearLevel === 2 ? "IV Sem" : yearLevel === 3 ? "VI Sem" : "VIII Sem"})
              </button>
            </div>

            {/* First Year Special Handling Note */}
            {yearLevel === 1 && (
              <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs flex items-start gap-2.5">
                <Info className="w-4 h-4 shrink-0 mt-0.5 text-amber-400" />
                <div>
                  <strong>First Year Stream Cycle Exception:</strong> First year engineering cohorts alternate between <strong>Physics Cycle</strong> and <strong>Chemistry Cycle</strong>. The joint dual-stream scheduler is supported for cross-stream resource optimization.
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Action Button */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <Link
            href="/academic-year"
            className="px-5 py-2.5 rounded-xl border border-slate-700 text-slate-300 text-xs font-semibold hover:bg-slate-800 transition"
          >
            Cancel
          </Link>
          <Link
            href="/generation"
            className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/30 transition"
          >
            Continue to Academic Curriculum & Course Setup <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </main>
    </div>
  );
}
