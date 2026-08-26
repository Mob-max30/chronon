"use client";

import React from "react";
import { Check, Calendar, School, Users2, Layers, Cpu, ShieldCheck, Grid } from "lucide-react";

const steps = [
  { id: 1, name: "Academic Year", desc: "Select Current vs Historical", icon: Calendar },
  { id: 2, name: "Scheme & Semesters", desc: "VTU / Autonomous & P/C Cycle", icon: School },
  { id: 3, name: "Courses & Intake", desc: "Student Counts & Sections", icon: Users2 },
  { id: 4, name: "Curriculum & Faculty", desc: "Theory/Labs & Staff mappings", icon: Layers },
  { id: 5, name: "Physical Resources", desc: "Rooms, Labs, Batches & Slots", icon: Grid },
  { id: 6, name: "CP-SAT Engine", desc: "100% Deterministic Solve", icon: Cpu },
  { id: 7, name: "Independent Validation", desc: "Zero-solver Bias Verification", icon: ShieldCheck },
];

export function WorkflowTimeline() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-7 gap-3 py-4">
      {steps.map((step, idx) => {
        const Icon = step.icon;
        return (
          <div
            key={step.id}
            className="p-3 rounded-xl border border-slate-800/80 bg-slate-900/50 flex flex-col justify-between hover:border-slate-700 transition"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="w-6 h-6 rounded-full bg-blue-500/10 text-blue-400 font-mono text-xs flex items-center justify-center font-bold">
                0{step.id}
              </span>
              <Icon className="w-4 h-4 text-slate-400" />
            </div>
            <div>
              <h4 className="text-xs font-semibold text-slate-200">{step.name}</h4>
              <p className="text-[11px] text-slate-400 mt-0.5">{step.desc}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
