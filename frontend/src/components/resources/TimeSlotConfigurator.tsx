"use client";

import React, { useState, useEffect } from "react";
import { SlotConfig, TimeSlot, SlotBreak } from "@/types";
import { getSlotConfig, saveSlotConfig, generateTimeSlotsAPI } from "@/lib/api";
import { Clock, Calendar, Plus, Trash2, CheckCircle2, RefreshCw, Sun, Coffee, Utensils, BookX } from "lucide-react";

const ALL_DAYS = [
  { id: 0, label: "Mon", full: "Monday" },
  { id: 1, label: "Tue", full: "Tuesday" },
  { id: 2, label: "Wed", full: "Wednesday" },
  { id: 3, label: "Thu", full: "Thursday" },
  { id: 4, label: "Fri", full: "Friday" },
  { id: 5, label: "Sat", full: "Saturday" },
];

export function TimeSlotConfigurator() {
  const [configName, setConfigName] = useState("Standard Working Day");
  const [theoryDuration, setTheoryDuration] = useState(55);
  const [labDuration, setLabDuration] = useState(110);
  const [workingDays, setWorkingDays] = useState<number[]>([0, 1, 2, 3, 4, 5]);
  const [dayStartTime, setDayStartTime] = useState("09:00");
  const [dayEndTime, setDayEndTime] = useState("17:00");
  const [breaks, setBreaks] = useState<SlotBreak[]>([
    { name: "Morning Tea Break", start_time: "11:00", end_time: "11:15", slot_type: "BREAK" },
  ]);
  const [lunchBreak, setLunchBreak] = useState<SlotBreak>({
    name: "Lunch Interval",
    start_time: "13:00",
    end_time: "14:00",
    slot_type: "LUNCH",
  });
  const [nonTeaching, setNonTeaching] = useState<SlotBreak[]>([]);

  const [generatedSlots, setGeneratedSlots] = useState<TimeSlot[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [savedNotice, setSavedNotice] = useState(false);

  const loadConfig = async () => {
    setLoading(true);
    try {
      const cfg = await getSlotConfig();
      setConfigName(cfg.name || "Standard Working Day");
      setTheoryDuration(cfg.theory_duration_minutes || 55);
      setLabDuration(cfg.lab_duration_minutes || 110);
      setWorkingDays(cfg.working_days || [0, 1, 2, 3, 4, 5]);
      setDayStartTime(cfg.day_start_time.substring(0, 5) || "09:00");
      setDayEndTime(cfg.day_end_time.substring(0, 5) || "17:00");
      if (cfg.breaks) setBreaks(cfg.breaks);
      if (cfg.lunch_break) setLunchBreak(cfg.lunch_break);
      if (cfg.non_teaching_periods) setNonTeaching(cfg.non_teaching_periods);
      handleGeneratePreview(cfg);
    } catch (err) {
      console.warn("Failed to load slot config:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  const handleToggleDay = (dayId: number) => {
    if (workingDays.includes(dayId)) {
      if (workingDays.length > 1) {
        setWorkingDays(workingDays.filter((d) => d !== dayId));
      }
    } else {
      setWorkingDays([...workingDays, dayId].sort());
    }
  };

  const handleAddBreak = () => {
    setBreaks([...breaks, { name: "Short Break", start_time: "15:00", end_time: "15:15", slot_type: "BREAK" }]);
  };

  const handleRemoveBreak = (idx: number) => {
    setBreaks(breaks.filter((_, i) => i !== idx));
  };

  const handleAddNonTeaching = () => {
    setNonTeaching([
      ...nonTeaching,
      { name: "Sports / Placement Block", start_time: "16:00", end_time: "17:00", slot_type: "NON_TEACHING" },
    ]);
  };

  const handleRemoveNonTeaching = (idx: number) => {
    setNonTeaching(nonTeaching.filter((_, i) => i !== idx));
  };

  const handleGeneratePreview = async (overrideCfg?: SlotConfig) => {
    const currentConfig: SlotConfig = overrideCfg || {
      institution_id: 1,
      name: configName,
      theory_duration_minutes: theoryDuration,
      lab_duration_minutes: labDuration,
      working_days: workingDays,
      day_start_time: dayStartTime.length === 5 ? `${dayStartTime}:00` : dayStartTime,
      day_end_time: dayEndTime.length === 5 ? `${dayEndTime}:00` : dayEndTime,
      breaks: breaks.map((b) => ({ ...b, start_time: b.start_time.length === 5 ? `${b.start_time}:00` : b.start_time, end_time: b.end_time.length === 5 ? `${b.end_time}:00` : b.end_time })),
      lunch_break: lunchBreak ? { ...lunchBreak, start_time: lunchBreak.start_time.length === 5 ? `${lunchBreak.start_time}:00` : lunchBreak.start_time, end_time: lunchBreak.end_time.length === 5 ? `${lunchBreak.end_time}:00` : lunchBreak.end_time } : null,
      non_teaching_periods: nonTeaching.map((nt) => ({ ...nt, start_time: nt.start_time.length === 5 ? `${nt.start_time}:00` : nt.start_time, end_time: nt.end_time.length === 5 ? `${nt.end_time}:00` : nt.end_time })),
    };

    try {
      const slots = await generateTimeSlotsAPI(currentConfig);
      setGeneratedSlots(slots);
    } catch (err: any) {
      alert(err.message || "Failed to generate time slots preview");
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const currentConfig: SlotConfig = {
        institution_id: 1,
        name: configName,
        theory_duration_minutes: theoryDuration,
        lab_duration_minutes: labDuration,
        working_days: workingDays,
        day_start_time: dayStartTime.length === 5 ? `${dayStartTime}:00` : dayStartTime,
        day_end_time: dayEndTime.length === 5 ? `${dayEndTime}:00` : dayEndTime,
        breaks: breaks.map((b) => ({ ...b, start_time: b.start_time.length === 5 ? `${b.start_time}:00` : b.start_time, end_time: b.end_time.length === 5 ? `${b.end_time}:00` : b.end_time })),
        lunch_break: lunchBreak ? { ...lunchBreak, start_time: lunchBreak.start_time.length === 5 ? `${lunchBreak.start_time}:00` : lunchBreak.start_time, end_time: lunchBreak.end_time.length === 5 ? `${lunchBreak.end_time}:00` : lunchBreak.end_time } : null,
        non_teaching_periods: nonTeaching.map((nt) => ({ ...nt, start_time: nt.start_time.length === 5 ? `${nt.start_time}:00` : nt.start_time, end_time: nt.end_time.length === 5 ? `${nt.end_time}:00` : nt.end_time })),
      };
      await saveSlotConfig(currentConfig);
      setSavedNotice(true);
      setTimeout(() => setSavedNotice(false), 3000);
      handleGeneratePreview(currentConfig);
    } catch (err: any) {
      alert(err.message || "Failed to save slot config");
    } finally {
      setSaving(false);
    }
  };

  // Group generated slots by day
  const slotsByDay: Record<number, TimeSlot[]> = {};
  for (const s of generatedSlots) {
    slotsByDay[s.day_of_week] = slotsByDay[s.day_of_week] || [];
    slotsByDay[s.day_of_week].push(s);
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-slate-900/60 p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Clock className="w-5 h-5 text-amber-400" /> Master Time Slot & Working Schedule Configurator
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Configure customizable daily durations, periods, intervals, breaks, and non-teaching blocks without hardcoding college assumptions.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={() => handleGeneratePreview()}
              className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition"
            >
              <RefreshCw className="w-3.5 h-3.5" /> Preview Schedule
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-5 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-amber-600/20"
            >
              <CheckCircle2 className="w-3.5 h-3.5" /> {saving ? "Saving..." : "Save Master Schedule"}
            </button>
          </div>
        </div>

        {savedNotice && (
          <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Master time slot configuration persisted successfully.
          </div>
        )}

        {/* Configuration Form */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs pt-2">
          {/* Working Days */}
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-amber-400" /> Working Days
            </label>
            <div className="flex flex-wrap gap-1.5 pt-1">
              {ALL_DAYS.map((d) => (
                <button
                  key={d.id}
                  type="button"
                  onClick={() => handleToggleDay(d.id)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-bold transition ${
                    workingDays.includes(d.id)
                      ? "bg-amber-500 text-slate-950 font-bold"
                      : "bg-slate-900 border border-slate-800 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {d.label}
                </button>
              ))}
            </div>
            <p className="text-[10px] text-slate-500">{workingDays.length} working days selected</p>
          </div>

          {/* Theory Duration */}
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold flex items-center gap-1.5">
              <Sun className="w-3.5 h-3.5 text-blue-400" /> Theory Period Duration
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="30"
                max="120"
                value={theoryDuration}
                onChange={(e) => setTheoryDuration(parseInt(e.target.value) || 55)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-bold text-base focus:outline-none focus:border-amber-500"
              />
              <span className="text-slate-400 font-medium">mins</span>
            </div>
            <p className="text-[10px] text-slate-500">e.g. 50, 55, or 60 minutes</p>
          </div>

          {/* Lab Duration */}
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5 text-emerald-400" /> Lab Period Duration
            </label>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min="60"
                max="240"
                value={labDuration}
                onChange={(e) => setLabDuration(parseInt(e.target.value) || 110)}
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-white font-bold text-base focus:outline-none focus:border-amber-500"
              />
              <span className="text-slate-400 font-medium">mins</span>
            </div>
            <p className="text-[10px] text-slate-500">Usually 2x theory duration (110 mins)</p>
          </div>

          {/* Day Hours */}
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-2">
            <label className="block text-slate-300 font-semibold">Daily Academic Hours</label>
            <div className="grid grid-cols-2 gap-2">
              <input
                type="time"
                value={dayStartTime}
                onChange={(e) => setDayStartTime(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-white text-xs"
              />
              <input
                type="time"
                value={dayEndTime}
                onChange={(e) => setDayEndTime(e.target.value)}
                className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-white text-xs"
              />
            </div>
            <p className="text-[10px] text-slate-500">Start and closing bell times</p>
          </div>
        </div>

        {/* Breaks & Lunch Config */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs pt-2">
          {/* Lunch Interval */}
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-slate-300 font-semibold flex items-center gap-1.5">
                <Utensils className="w-3.5 h-3.5 text-amber-400" /> Lunch Interval
              </label>
              <span className="text-[10px] font-mono text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded">LUNCH</span>
            </div>
            <div className="grid grid-cols-3 gap-2">
              <input
                type="text"
                value={lunchBreak.name}
                onChange={(e) => setLunchBreak({ ...lunchBreak, name: e.target.value })}
                placeholder="Label"
                className="bg-slate-900 border border-slate-700 rounded-lg px-2.5 py-1.5 text-white"
              />
              <input
                type="time"
                value={lunchBreak.start_time.substring(0, 5)}
                onChange={(e) => setLunchBreak({ ...lunchBreak, start_time: e.target.value })}
                className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-white text-xs"
              />
              <input
                type="time"
                value={lunchBreak.end_time.substring(0, 5)}
                onChange={(e) => setLunchBreak({ ...lunchBreak, end_time: e.target.value })}
                className="bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-white text-xs"
              />
            </div>
          </div>

          {/* Short Breaks List */}
          <div className="bg-slate-950/70 p-4 rounded-xl border border-slate-800/80 space-y-3">
            <div className="flex items-center justify-between">
              <label className="text-slate-300 font-semibold flex items-center gap-1.5">
                <Coffee className="w-3.5 h-3.5 text-indigo-400" /> Short Tea Breaks
              </label>
              <button
                type="button"
                onClick={handleAddBreak}
                className="text-[11px] text-indigo-400 hover:text-indigo-300 font-semibold flex items-center gap-1"
              >
                <Plus className="w-3 h-3" /> Add Break
              </button>
            </div>

            {breaks.map((b, idx) => (
              <div key={idx} className="grid grid-cols-7 gap-2 items-center">
                <input
                  type="text"
                  value={b.name}
                  onChange={(e) => {
                    const newB = [...breaks];
                    newB[idx].name = e.target.value;
                    setBreaks(newB);
                  }}
                  className="col-span-3 bg-slate-900 border border-slate-700 rounded-lg px-2 py-1 text-white text-xs"
                />
                <input
                  type="time"
                  value={b.start_time.substring(0, 5)}
                  onChange={(e) => {
                    const newB = [...breaks];
                    newB[idx].start_time = e.target.value;
                    setBreaks(newB);
                  }}
                  className="col-span-2 bg-slate-900 border border-slate-700 rounded-lg px-1.5 py-1 text-white text-xs"
                />
                <input
                  type="time"
                  value={b.end_time.substring(0, 5)}
                  onChange={(e) => {
                    const newB = [...breaks];
                    newB[idx].end_time = e.target.value;
                    setBreaks(newB);
                  }}
                  className="col-span-1 bg-slate-900 border border-slate-700 rounded-lg px-1.5 py-1 text-white text-xs"
                />
                <button
                  type="button"
                  onClick={() => handleRemoveBreak(idx)}
                  className="col-span-1 text-slate-500 hover:text-red-400 text-center"
                >
                  <Trash2 className="w-3.5 h-3.5 mx-auto" />
                </button>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Generated Schedule Preview */}
      <div className="bg-slate-900/40 p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Generated Daily Time Slot Matrix ({generatedSlots.length} Total Slots)
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Normalized timeline slots consumed by the OR-Tools CP-SAT scheduler
            </p>
          </div>
        </div>

        {/* First day preview breakdown */}
        {workingDays.length > 0 && (
          <div className="space-y-3">
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-8 gap-3">
              {(slotsByDay[workingDays[0]] || []).map((slot, sIdx) => {
                const isBreak = slot.slot_type === "BREAK" || slot.slot_type === "LUNCH";
                return (
                  <div
                    key={sIdx}
                    className={`p-3.5 rounded-xl border text-xs flex flex-col justify-between space-y-2 ${
                      isBreak
                        ? "bg-slate-950/80 border-slate-800 text-slate-400"
                        : "bg-slate-950 border-blue-900/40 text-white"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-[11px] font-bold text-amber-400">
                        {slot.label || `P${slot.period_index}`}
                      </span>
                      <span
                        className={`text-[9px] font-mono px-1.5 py-0.5 rounded ${
                          isBreak ? "bg-slate-800 text-slate-400" : "bg-blue-500/10 text-blue-300"
                        }`}
                      >
                        {slot.slot_type}
                      </span>
                    </div>

                    <div className="text-[11px] font-mono text-slate-300">
                      {slot.start_time.substring(0, 5)} - {slot.end_time.substring(0, 5)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
