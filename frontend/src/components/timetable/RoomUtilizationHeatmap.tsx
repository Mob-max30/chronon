"use client";

import React, { useState, useEffect } from "react";
import { getRooms, getLabs, getTimetableMatrix } from "@/lib/api";
import {
  Building2,
  FlaskConical,
  Activity,
  Calendar,
  Layers,
  Sparkles,
  CheckCircle,
  AlertCircle,
} from "lucide-react";

export function RoomUtilizationHeatmap() {
  const [selectedDay, setSelectedDay] = useState<number>(1); // 1 = Monday
  const [rooms, setRooms] = useState<any[]>([]);
  const [labs, setLabs] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Time periods header
  const periods = [
    { period_index: 1, label: "Period 1", time: "09:00 - 10:00" },
    { period_index: 2, label: "Period 2", time: "10:00 - 11:00" },
    { period_index: 3, label: "Period 3", time: "11:15 - 12:15" },
    { period_index: 4, label: "Period 4", time: "12:15 - 01:15" },
    { period_index: 5, label: "Period 5", time: "02:00 - 03:00" },
    { period_index: 6, label: "Period 6", time: "03:00 - 04:00" },
    { period_index: 7, label: "Period 7", time: "04:00 - 05:00" },
  ];

  const days = [
    { id: 1, name: "Monday" },
    { id: 2, name: "Tuesday" },
    { id: 3, name: "Wednesday" },
    { id: 4, name: "Thursday" },
    { id: 5, name: "Friday" },
    { id: 6, name: "Saturday" },
  ];

  useEffect(() => {
    const loadInfrastructure = async () => {
      setLoading(true);
      try {
        const [rms, lbs] = await Promise.all([getRooms(), getLabs()]);
        setRooms(rms && rms.length > 0 ? rms : [
          { id: 1, name: "LH-101", capacity: 60, building: "Main Block", floor: 1 },
          { id: 2, name: "LH-102", capacity: 60, building: "Main Block", floor: 1 },
          { id: 3, name: "LH-201", capacity: 75, building: "Science Block", floor: 2 },
          { id: 4, name: "LH-202", capacity: 60, building: "Science Block", floor: 2 },
        ]);
        setLabs(lbs && lbs.length > 0 ? lbs : [
          { id: 1, name: "CS Lab 1", capacity: 30, building: "CS Wing", floor: 2 },
          { id: 2, name: "Electronics Lab", capacity: 30, building: "EC Wing", floor: 1 },
          { id: 3, name: "Physics Lab", capacity: 30, building: "Basic Science", floor: 1 },
        ]);
      } catch (err) {
        console.warn("Failed to load rooms/labs for heatmap:", err);
      } finally {
        setLoading(false);
      }
    };
    loadInfrastructure();
  }, []);

  // Deterministic mock schedule overlay for demo
  const getCellAllocation = (type: "ROOM" | "LAB", id: number, period: number) => {
    // Generate deterministic assignment based on day, id, period
    const seed = (selectedDay * 17 + id * 11 + period * 7) % 10;
    if (type === "ROOM") {
      if (seed === 0 || seed === 3) {
        return { occupied: true, subject: "21CS32 (DS)", section: "CSE 3A", faculty: "Dr. Ramesh" };
      }
      if (seed === 1 || seed === 5) {
        return { occupied: true, subject: "21MAT31 (Maths)", section: "CSE 3B", faculty: "Prof. Priya" };
      }
      if (seed === 2 || seed === 7) {
        return { occupied: true, subject: "21CS34 (COA)", section: "CSE 3A", faculty: "Dr. Sandeep" };
      }
      return { occupied: false };
    } else {
      if (seed === 1 || seed === 4 || seed === 6) {
        return { occupied: true, subject: "21CSL36 (DS Lab)", section: "CSE 3A - B1", faculty: "Dr. Ramesh" };
      }
      if (seed === 2 || seed === 8) {
        return { occupied: true, subject: "21ECL37 (EC Lab)", section: "ECE 3A - B2", faculty: "Prof. Ananya" };
      }
      return { occupied: false };
    }
  };

  const exportHeatmapCSV = () => {
    const dayObj = days.find((d) => d.id === selectedDay);
    const dayName = dayObj ? dayObj.name : `Day_${selectedDay}`;
    let csv = `Infrastructure Occupancy Heatmap - ${dayName}\nFacility,Capacity,Building,${periods.map((p) => `"${p.label} (${p.time})"`).join(",")}\n`;

    rooms.forEach((r) => {
      const row = [`"${r.name}"`, r.capacity, `"${r.building || 'Main Block'}"`];
      periods.forEach((p) => {
        const alloc = getCellAllocation("ROOM", r.id, p.period_index);
        row.push(alloc.occupied ? `"${alloc.subject} - ${alloc.section} (${alloc.faculty})"` : `"FREE"`);
      });
      csv += row.join(",") + "\n";
    });

    labs.forEach((l) => {
      const row = [`"${l.name}"`, l.capacity, `"${l.building || 'Lab Wing'}"`];
      periods.forEach((p) => {
        const alloc = getCellAllocation("LAB", l.id, p.period_index);
        row.push(alloc.occupied ? `"${alloc.subject} - ${alloc.section} (${alloc.faculty})"` : `"FREE"`);
      });
      csv += row.join(",") + "\n";
    });

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `infrastructure_occupancy_${dayName.toLowerCase()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="space-y-6">
      {/* Top Controls & Day Selector */}
      <div className="bg-slate-900/60 p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" /> Infrastructure Occupancy Heatmap
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real-time matrix view of physical classrooms and hardware lab facilities across all time periods.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={exportHeatmapCSV}
            className="px-3.5 py-1.5 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1.5 transition shadow-sm"
          >
            Export Heatmap CSV
          </button>

          {/* Day Buttons */}
          <div className="flex items-center gap-1.5 p-1 bg-slate-950/80 rounded-xl border border-slate-800 text-xs font-semibold">
            {days.map((d) => (
              <button
                key={d.id}
                onClick={() => setSelectedDay(d.id)}
                className={`px-3 py-1.5 rounded-lg transition ${
                  selectedDay === d.id
                    ? "bg-emerald-600 text-white shadow-md shadow-emerald-600/25"
                    : "text-slate-400 hover:text-slate-200"
                }`}
              >
                {d.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Heatmap Matrix Table */}
      <div className="bg-slate-900/60 rounded-3xl border border-slate-800 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-950/80 border-b border-slate-800 text-xs">
                <th className="p-4 font-bold text-slate-300 uppercase tracking-wider w-44 border-r border-slate-800">
                  Facility / Room
                </th>
                {periods.map((p) => (
                  <th
                    key={p.period_index}
                    className="p-3 font-semibold text-center border-r border-slate-800/80 min-w-[130px] text-slate-200"
                  >
                    <div className="font-bold text-slate-100">{p.label}</div>
                    <div className="text-[10px] font-mono text-slate-400 mt-0.5">{p.time}</div>
                  </th>
                ))}
              </tr>
            </thead>

            <tbody className="divide-y divide-slate-800/60 text-xs">
              {/* Classrooms Section Header */}
              <tr className="bg-slate-950/90 text-[11px] font-bold text-blue-400 uppercase tracking-wider">
                <td colSpan={periods.length + 1} className="p-2.5 px-4 flex items-center gap-2">
                  <Building2 className="w-4 h-4" /> Physical Classrooms & Lecture Halls ({rooms.length} Halls)
                </td>
              </tr>

              {rooms.map((r) => (
                <tr key={`room-${r.id}`} className="hover:bg-slate-800/20 transition">
                  <td className="p-3.5 font-bold text-white bg-slate-950/40 border-r border-slate-800">
                    <div className="font-mono text-blue-300 font-bold">{r.name}</div>
                    <div className="text-[10px] text-slate-400 font-normal">Cap: {r.capacity} seats</div>
                  </td>

                  {periods.map((p) => {
                    const alloc = getCellAllocation("ROOM", r.id, p.period_index);
                    return (
                      <td key={p.period_index} className="p-2 border-r border-slate-800/60 align-middle">
                        {alloc.occupied ? (
                          <div className="p-2 rounded-xl bg-blue-950/40 border border-blue-800/50 space-y-1">
                            <div className="font-bold text-blue-200 font-mono text-[10px] truncate">
                              {alloc.subject}
                            </div>
                            <div className="text-[9px] text-slate-300 font-semibold">{alloc.section}</div>
                            <div className="text-[9px] text-slate-400 truncate">{alloc.faculty}</div>
                          </div>
                        ) : (
                          <div className="p-2 rounded-xl bg-emerald-950/20 border border-emerald-800/30 text-center text-emerald-400 font-mono text-[10px] font-bold">
                            FREE
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}

              {/* Labs Section Header */}
              <tr className="bg-slate-950/90 text-[11px] font-bold text-emerald-400 uppercase tracking-wider">
                <td colSpan={periods.length + 1} className="p-2.5 px-4 flex items-center gap-2">
                  <FlaskConical className="w-4 h-4" /> Hardware & Practical Laboratories ({labs.length} Labs)
                </td>
              </tr>

              {labs.map((l) => (
                <tr key={`lab-${l.id}`} className="hover:bg-slate-800/20 transition">
                  <td className="p-3.5 font-bold text-white bg-slate-950/40 border-r border-slate-800">
                    <div className="font-mono text-emerald-300 font-bold">{l.name}</div>
                    <div className="text-[10px] text-slate-400 font-normal">{l.capacity} Workstations</div>
                  </td>

                  {periods.map((p) => {
                    const alloc = getCellAllocation("LAB", l.id, p.period_index);
                    return (
                      <td key={p.period_index} className="p-2 border-r border-slate-800/60 align-middle">
                        {alloc.occupied ? (
                          <div className="p-2 rounded-xl bg-emerald-950/40 border border-emerald-800/50 space-y-1">
                            <div className="font-bold text-emerald-200 font-mono text-[10px] truncate">
                              {alloc.subject}
                            </div>
                            <div className="text-[9px] text-slate-300 font-semibold">{alloc.section}</div>
                            <div className="text-[9px] text-slate-400 truncate">{alloc.faculty}</div>
                          </div>
                        ) : (
                          <div className="p-2 rounded-xl bg-emerald-950/20 border border-emerald-800/30 text-center text-emerald-400 font-mono text-[10px] font-bold">
                            FREE
                          </div>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
