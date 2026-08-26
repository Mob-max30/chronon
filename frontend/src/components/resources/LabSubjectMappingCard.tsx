"use client";

import React, { useState, useEffect } from "react";
import { Lab, LabSubjectMapping } from "@/types";
import { getLabs, getLabMappings, createLabMapping, deleteLabMapping } from "@/lib/api";
import { Share2, Plus, Trash2, ArrowRight, ShieldAlert, Monitor, BookOpen } from "lucide-react";

export function LabSubjectMappingCard() {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [mappings, setMappings] = useState<LabSubjectMapping[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSubjectCode, setSelectedSubjectCode] = useState("21CSL38");
  const [selectedSubjectName, setSelectedSubjectName] = useState("Data Structures Lab");
  const [selectedLabId, setSelectedLabId] = useState<number>(1);
  const [isAdding, setIsAdding] = useState(false);

  // Available academic lab catalog fixtures
  const availableAcademicSubjects = [
    { id: 101, code: "21CSL38", name: "Data Structures Laboratory" },
    { id: 102, code: "21CSL46", name: "Operating Systems Laboratory" },
    { id: 103, code: "21IDL48", name: "IDEA / Innovation Design Lab" },
    { id: 104, code: "21CSL57", name: "Database Applications Lab" },
    { id: 201, code: "22PHYL16", name: "Applied Physics Laboratory (Physics Cycle)" },
    { id: 202, code: "22CHEL16", name: "Applied Chemistry Laboratory (Chemistry Cycle)" },
  ];

  const loadData = async () => {
    setLoading(true);
    try {
      const [lData, mData] = await Promise.all([getLabs(), getLabMappings()]);
      setLabs(lData);
      setMappings(mData);
      if (lData.length > 0) setSelectedLabId(lData[0].id);
    } catch (err) {
      console.warn("Failed to load mappings data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleAddMapping = async (e: React.FormEvent) => {
    e.preventDefault();
    const matchedSubject = availableAcademicSubjects.find((s) => s.code === selectedSubjectCode);
    if (!matchedSubject) return;

    try {
      await createLabMapping({
        subject_id: matchedSubject.id,
        lab_id: Number(selectedLabId),
      });
      setIsAdding(false);
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to create lab mapping");
    }
  };

  const handleDeleteMapping = async (id: number) => {
    try {
      await deleteLabMapping(id);
      loadData();
    } catch (err: any) {
      alert(err.message || "Failed to remove mapping");
    }
  };

  // Group mappings by physical lab
  const mappingsByLab: Record<number, LabSubjectMapping[]> = {};
  for (const m of mappings) {
    mappingsByLab[m.lab_id] = mappingsByLab[m.lab_id] || [];
    mappingsByLab[m.lab_id].push(m);
  }

  return (
    <div className="space-y-6">
      {/* Informative Header */}
      <div className="bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-6 rounded-2xl border border-indigo-900/50 shadow-xl space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-start gap-3">
            <div className="p-2.5 rounded-xl bg-indigo-500/10 border border-indigo-500/30 text-indigo-400">
              <Share2 className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">
                Academic Lab Subject ⟷ Physical Hardware Mapping
              </h2>
              <p className="text-xs text-slate-300 mt-1 max-w-2xl leading-relaxed">
                Decouples curricular lab subjects from physical spaces. Multiple academic subjects (e.g. <span className="text-indigo-300 font-mono">DSA Lab</span>, <span className="text-indigo-300 font-mono">OS Lab</span>, <span className="text-indigo-300 font-mono">IDEA Lab</span>) can map to one shared physical lab (e.g. <span className="text-emerald-300 font-mono">CS-LAB-01</span>).
              </p>
            </div>
          </div>
          <button
            onClick={() => setIsAdding(!isAdding)}
            className="px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-indigo-600/20"
          >
            <Plus className="w-4 h-4" /> Link Lab Subject
          </button>
        </div>

        {/* Conflict Warning Callout */}
        <div className="flex items-center gap-2.5 p-3 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-300 text-xs">
          <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
          <span>
            <b>Shared Hardware Constraint</b>: The solver guarantees that subjects sharing the same physical lab resource will never be booked in overlapping time slots across all sections, batches, and streams.
          </span>
        </div>
      </div>

      {/* Add Mapping Form Dropdown */}
      {isAdding && (
        <form
          onSubmit={handleAddMapping}
          className="bg-slate-900/80 border border-slate-800 p-5 rounded-2xl space-y-4 animate-in fade-in zoom-in-95 duration-200"
        >
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Plus className="w-4 h-4 text-indigo-400" /> Create Physical Lab Subject Binding
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1.5">Academic Lab Subject</label>
              <select
                value={selectedSubjectCode}
                onChange={(e) => {
                  setSelectedSubjectCode(e.target.value);
                  const matched = availableAcademicSubjects.find((s) => s.code === e.target.value);
                  if (matched) setSelectedSubjectName(matched.name);
                }}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-500"
              >
                {availableAcademicSubjects.map((s) => (
                  <option key={s.id} value={s.code}>
                    {s.code} — {s.name}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1.5">Physical Lab Target</label>
              <select
                value={selectedLabId}
                onChange={(e) => setSelectedLabId(Number(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-indigo-500"
              >
                {labs.map((l) => (
                  <option key={l.id} value={l.id}>
                    {l.name} ({l.capacity} workstations, {l.count || 1} room)
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => setIsAdding(false)}
              className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 transition text-xs"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs shadow-lg shadow-indigo-600/20 transition"
            >
              Bind to Physical Lab
            </button>
          </div>
        </form>
      )}

      {/* Visual Relationship Diagram Cards */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading lab mappings...</div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {labs.map((lab) => {
            const mappedList = mappingsByLab[lab.id] || [];
            return (
              <div
                key={lab.id}
                className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 hover:border-slate-700 transition space-y-4"
              >
                {/* Physical Lab Header */}
                <div className="flex items-start justify-between pb-3 border-b border-slate-800/80">
                  <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                      <Monitor className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white">{lab.name}</h3>
                      <div className="flex items-center gap-2 mt-0.5 text-xs text-slate-400">
                        <span>{lab.capacity} workstations</span>
                        <span>•</span>
                        <span className="text-emerald-400 font-medium">{lab.count || 1} room instance(s)</span>
                      </div>
                    </div>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-1 rounded bg-slate-800 text-slate-300">
                    {mappedList.length} Subject(s) Bound
                  </span>
                </div>

                {/* Mapped Subjects Flow */}
                <div className="space-y-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Academic Subjects Using This Hardware Space:
                  </div>

                  {mappedList.length === 0 ? (
                    <div className="p-4 rounded-xl border border-dashed border-slate-800 text-center text-xs text-slate-500">
                      No academic lab subjects mapped to this physical resource yet.
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {mappedList.map((m) => (
                        <div
                          key={m.id}
                          className="flex items-center justify-between p-3 rounded-xl bg-slate-950/70 border border-slate-800/80 text-xs"
                        >
                          <div className="flex items-center gap-3">
                            <BookOpen className="w-4 h-4 text-indigo-400 shrink-0" />
                            <div>
                              <div className="font-bold text-slate-200">
                                {m.subject_code} <span className="font-normal text-slate-400">— {m.subject_name}</span>
                              </div>
                            </div>
                          </div>

                          <div className="flex items-center gap-2">
                            <ArrowRight className="w-3.5 h-3.5 text-slate-600" />
                            <button
                              onClick={() => handleDeleteMapping(m.id)}
                              className="p-1.5 rounded-lg text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition"
                              title="Unlink Mapping"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
