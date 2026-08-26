"use client";

import React, { useState, useEffect } from "react";
import { Lab } from "@/types";
import { getLabs, createLab, updateLab, deleteLab } from "@/lib/api";
import { FlaskConical, Plus, Edit2, Trash2, Monitor, Cpu, Wrench, Atom, Sparkles } from "lucide-react";

export function LabManager() {
  const [labs, setLabs] = useState<Lab[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingLab, setEditingLab] = useState<Lab | null>(null);

  // Form State
  const [name, setName] = useState("");
  const [building, setBuilding] = useState("");
  const [capacity, setCapacity] = useState(30);
  const [count, setCount] = useState(1);
  const [labType, setLabType] = useState("COMPUTER");
  const [error, setError] = useState<string | null>(null);

  const loadLabs = async () => {
    setLoading(true);
    try {
      const data = await getLabs();
      setLabs(data);
    } catch (err: any) {
      setError(err.message || "Failed to load labs");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadLabs();
  }, []);

  const openCreateModal = () => {
    setEditingLab(null);
    setName("");
    setBuilding("");
    setCapacity(30);
    setCount(1);
    setLabType("COMPUTER");
    setError(null);
    setIsModalOpen(true);
  };

  const openEditModal = (lab: Lab) => {
    setEditingLab(lab);
    setName(lab.name);
    setBuilding(lab.building || "");
    setCapacity(lab.capacity);
    setCount(lab.count || 1);
    setLabType(lab.lab_type || "COMPUTER");
    setError(null);
    setIsModalOpen(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) {
      setError("Lab name is required");
      return;
    }
    if (capacity <= 0) {
      setError("Workstation capacity must be > 0");
      return;
    }
    if (count <= 0) {
      setError("Lab room count must be >= 1");
      return;
    }

    try {
      if (editingLab) {
        await updateLab(editingLab.id, {
          name,
          building,
          capacity,
          count,
          lab_type: labType,
        });
      } else {
        await createLab({
          institution_id: 1,
          name,
          building,
          capacity,
          count,
          lab_type: labType,
        });
      }
      setIsModalOpen(false);
      loadLabs();
    } catch (err: any) {
      setError(err.message || "Failed to save lab");
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this physical laboratory?")) return;
    try {
      await deleteLab(id);
      loadLabs();
    } catch (err: any) {
      alert(err.message || "Failed to delete lab");
    }
  };

  const getLabIcon = (type: string) => {
    switch (type.toUpperCase()) {
      case "COMPUTER":
        return <Monitor className="w-4 h-4 text-cyan-400" />;
      case "ELECTRONICS":
        return <Cpu className="w-4 h-4 text-purple-400" />;
      case "MECHANICAL":
      case "CIVIL":
        return <Wrench className="w-4 h-4 text-amber-400" />;
      case "PHYSICS":
      case "CHEMISTRY":
        return <Atom className="w-4 h-4 text-emerald-400" />;
      default:
        return <Sparkles className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <FlaskConical className="w-5 h-5 text-emerald-400" /> Physical Laboratories
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Physical hardware resources (e.g. CS Lab 1 with 30 workstations, 2 identical rooms). Decoupled from academic lab subjects.
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-emerald-600/20"
        >
          <Plus className="w-4 h-4" /> Add Physical Lab
        </button>
      </div>

      {/* Grid of Labs */}
      {loading ? (
        <div className="text-center py-12 text-slate-400 text-sm">Loading laboratory resources...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {labs.map((lab) => (
            <div
              key={lab.id}
              className="p-5 rounded-2xl border border-slate-800 bg-slate-900/50 hover:border-slate-700 transition flex flex-col justify-between space-y-4"
            >
              <div className="flex items-start justify-between">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-bold text-white tracking-wide">{lab.name}</h3>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">{lab.building || "Engineering Complex"}</p>
                </div>
                <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-800/80 border border-slate-700/60 text-[11px] font-mono text-emerald-300">
                  {getLabIcon(lab.lab_type)}
                  <span>{lab.lab_type}</span>
                </div>
              </div>

              {/* Lab Stats */}
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800/80 text-xs">
                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50">
                  <div className="text-[10px] text-slate-500 font-medium">Workstations / Lab</div>
                  <div className="font-bold text-emerald-400 text-sm mt-0.5">{lab.capacity} seats</div>
                </div>
                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/50">
                  <div className="text-[10px] text-slate-500 font-medium">Identical Rooms</div>
                  <div className="font-bold text-slate-200 text-sm mt-0.5">{lab.count || 1} room(s)</div>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex items-center justify-end gap-2 pt-2">
                <button
                  onClick={() => openEditModal(lab)}
                  className="p-2 rounded-lg border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition"
                  title="Edit Lab"
                >
                  <Edit2 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => handleDelete(lab.id)}
                  className="p-2 rounded-lg border border-red-900/30 hover:bg-red-500/10 text-red-400 hover:text-red-300 transition"
                  title="Delete Lab"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal Dialog */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-md w-full p-6 shadow-2xl space-y-5 animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <h3 className="text-lg font-bold text-white">
                {editingLab ? "Edit Physical Lab" : "Create Physical Lab"}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-white text-sm">
                ✕
              </button>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-xs">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">
                  Physical Lab Name <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="e.g. Computer Science Lab 1, Electronics Hardware Lab"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                  required
                />
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">Building / Department Block</label>
                <input
                  type="text"
                  value={building}
                  onChange={(e) => setBuilding(e.target.value)}
                  placeholder="e.g. Computing Block, 2nd Floor"
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-semibold mb-1.5">
                    Workstation Capacity <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={capacity}
                    onChange={(e) => setCapacity(parseInt(e.target.value) || 0)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                  <p className="text-[10px] text-slate-500 mt-1">Workstations per room</p>
                </div>

                <div>
                  <label className="block text-slate-300 font-semibold mb-1.5">
                    Identical Rooms Count <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={count}
                    onChange={(e) => setCount(parseInt(e.target.value) || 1)}
                    className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-emerald-500"
                    required
                  />
                  <p className="text-[10px] text-slate-500 mt-1">Parallel room instances</p>
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-semibold mb-1.5">Lab Discipline / Type</label>
                <select
                  value={labType}
                  onChange={(e) => setLabType(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="COMPUTER">Computer Science / IT</option>
                  <option value="ELECTRONICS">Electronics & Communication</option>
                  <option value="MECHANICAL">Mechanical / CAD</option>
                  <option value="CIVIL">Civil Engineering</option>
                  <option value="PHYSICS">Physics Cycle Lab</option>
                  <option value="CHEMISTRY">Chemistry Cycle Lab</option>
                  <option value="INNOVATION">IDEA / Innovation Lab</option>
                </select>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl border border-slate-700 text-slate-300 hover:bg-slate-800 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-lg shadow-emerald-600/20 transition"
                >
                  {editingLab ? "Save Changes" : "Create Lab"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
