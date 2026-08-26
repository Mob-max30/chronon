"use client";

import React from "react";
import {
  X,
  BookOpen,
  User,
  Building2,
  FlaskConical,
  Clock,
  CheckCircle2,
  AlertTriangle,
  Layers,
  ShieldCheck,
  Calendar,
} from "lucide-react";

interface SessionDetailModalProps {
  session: any | null;
  timeSlotLabel?: string;
  dayName?: string;
  onClose: () => void;
}

export function SessionDetailModal({
  session,
  timeSlotLabel,
  dayName,
  onClose,
}: SessionDetailModalProps) {
  if (!session) return null;

  const isLab = session.subject_type === "LAB";
  const isPaired = !!session.paired_slot_group;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-lg w-full overflow-hidden shadow-2xl space-y-0 text-slate-200">
        {/* Header */}
        <div className="p-6 bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border-b border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div
              className={`p-3 rounded-2xl ${
                isLab
                  ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                  : isPaired
                  ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/20"
                  : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
              }`}
            >
              {isLab ? <FlaskConical className="w-6 h-6" /> : <BookOpen className="w-6 h-6" />}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-mono text-sm font-extrabold text-white">{session.subject_code}</span>
                <span
                  className={`text-[10px] font-mono uppercase font-bold px-2 py-0.5 rounded-full border ${
                    isLab
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                      : "bg-blue-500/10 border-blue-500/30 text-blue-400"
                  }`}
                >
                  {isLab ? "Laboratory Practical" : "Theory Lecture"}
                </span>
              </div>
              <h3 className="text-base font-bold text-white mt-0.5 line-clamp-1">{session.subject_name}</h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-5 text-xs">
          {/* Timeline & Schedule Slot */}
          <div className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2 text-slate-300">
              <Calendar className="w-4 h-4 text-blue-400" />
              <span className="font-semibold">{dayName || "Day Schedule"}</span>
            </div>
            <div className="flex items-center gap-2 text-slate-400 font-mono">
              <Clock className="w-4 h-4 text-slate-500" />
              <span>{timeSlotLabel || "Period"}</span>
            </div>
          </div>

          {/* Details Grid */}
          <div className="grid grid-cols-2 gap-3">
            {/* Faculty */}
            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/80 space-y-1.5">
              <div className="text-slate-400 flex items-center gap-1.5 font-medium">
                <User className="w-3.5 h-3.5 text-blue-400" />
                <span>Instructor / Faculty</span>
              </div>
              <div className="text-sm font-bold text-white">{session.faculty_name}</div>
              <div className="text-[10px] text-slate-500 font-mono">ID: #{session.faculty_id}</div>
            </div>

            {/* Room or Lab Location */}
            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/80 space-y-1.5">
              <div className="text-slate-400 flex items-center gap-1.5 font-medium">
                {isLab ? (
                  <FlaskConical className="w-3.5 h-3.5 text-emerald-400" />
                ) : (
                  <Building2 className="w-3.5 h-3.5 text-blue-400" />
                )}
                <span>{isLab ? "Lab Facility" : "Classroom"}</span>
              </div>
              <div className="text-sm font-bold text-white font-mono">
                {session.lab_name || session.room_name || "Assigned Hall"}
              </div>
              <div className="text-[10px] text-slate-500">
                {isLab ? "Hardware Workstations Available" : "Standard Classroom Seating"}
              </div>
            </div>

            {/* Section & Cohort */}
            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/80 space-y-1.5">
              <div className="text-slate-400 flex items-center gap-1.5 font-medium">
                <Layers className="w-3.5 h-3.5 text-purple-400" />
                <span>Cohort & Section</span>
              </div>
              <div className="text-sm font-bold text-white font-mono">
                {session.section_name ? `Section ${session.section_name}` : `Section #${session.section_id}`}
                {session.batch_name && ` (${session.batch_name})`}
              </div>
              {session.cycle_group && (
                <div className="text-[10px] text-indigo-400 font-mono">
                  {session.cycle_group.replace("_CYCLE", " Cycle")}
                </div>
              )}
            </div>

            {/* Invariant & Conflict Verification */}
            <div className="p-4 rounded-2xl bg-slate-950/40 border border-slate-800/80 space-y-1.5">
              <div className="text-slate-400 flex items-center gap-1.5 font-medium">
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                <span>Solver Invariant</span>
              </div>
              {session.has_conflict ? (
                <div className="text-red-400 font-bold flex items-center gap-1">
                  <AlertTriangle className="w-3.5 h-3.5" /> Conflict Detected
                </div>
              ) : (
                <div className="text-emerald-400 font-bold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Zero Clashes Verified
                </div>
              )}
              <div className="text-[10px] text-slate-500">CP-SAT Deterministic Proof</div>
            </div>
          </div>

          {/* Paired-Slot First-Year Explanation (If applicable) */}
          {session.paired_slot_group && (
            <div className="p-3.5 rounded-2xl bg-indigo-950/40 border border-indigo-800/50 text-indigo-300 text-[11px] space-y-1">
              <div className="font-bold flex items-center gap-1.5">
                <span>Joint 1st-Year Paired Group: {session.paired_slot_group}</span>
              </div>
              <p className="text-indigo-400 text-[10px]">
                This session runs synchronously with the corresponding parallel cycle section in an adjacent hall.
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs transition"
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}
