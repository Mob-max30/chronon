"use client";

import React, { useState, useEffect } from "react";
import { TimetableMatrixResponse } from "@/types";
import { getTimetableMatrix, fetchFaculty, getRooms, getLabs } from "@/lib/api";
import {
  Calendar,
  Filter,
  Download,
  Printer,
  Share2,
  AlertTriangle,
  Users,
  Building2,
  FlaskConical,
  GraduationCap,
  Activity,
  CheckCircle2,
  Clock,
  Sparkles,
} from "lucide-react";

export function TimetableMatrixGrid() {
  const [viewType, setViewType] = useState<string>("SECTION");
  const [selectedSection, setSelectedSection] = useState<string>("3A");
  const [selectedFaculty, setSelectedFaculty] = useState<string>("");
  const [selectedRoom, setSelectedRoom] = useState<string>("");
  const [selectedLab, setSelectedLab] = useState<string>("");
  const [selectedBatch, setSelectedBatch] = useState<string>("");
  const [selectedCycleGroup, setSelectedCycleGroup] = useState<string>("");

  // Live filter catalogues
  const [facultyList, setFacultyList] = useState<any[]>([]);
  const [roomList, setRoomList] = useState<any[]>([]);
  const [labList, setLabList] = useState<any[]>([]);

  const [matrixData, setMatrixData] = useState<TimetableMatrixResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Fetch real filter catalogues on mount
  useEffect(() => {
    const loadFilters = async () => {
      try {
        const [facs, rms, lbs] = await Promise.all([
          fetchFaculty(),
          getRooms(),
          getLabs(),
        ]);
        if (facs && facs.length > 0) setFacultyList(facs);
        if (rms && rms.length > 0) setRoomList(rms);
        if (lbs && lbs.length > 0) setLabList(lbs);
      } catch (err) {
        console.warn("Failed to load filter catalogues:", err);
      }
    };
    loadFilters();
  }, []);

  const fetchMatrix = async () => {
    setLoading(true);
    try {
      const data = await getTimetableMatrix(1, {
        view_type: viewType,
        section_id: selectedSection === "3A" ? 1 : selectedSection === "3B" ? 2 : selectedSection === "1A" ? 10 : selectedSection === "1B" ? 11 : null,
        faculty_id: selectedFaculty ? Number(selectedFaculty) : null,
        room_id: selectedRoom ? Number(selectedRoom) : null,
        lab_id: selectedLab ? Number(selectedLab) : null,
        cycle_group: selectedCycleGroup || null,
      });
      setMatrixData(data);
    } catch (err) {
      console.warn("Failed to load timetable matrix:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMatrix();
  }, [viewType, selectedSection, selectedFaculty, selectedRoom, selectedLab, selectedBatch, selectedCycleGroup]);

  // Calculate real-time utilization stats
  const calculateUtilization = () => {
    if (!matrixData) return { totalSlots: 0, bookedSlots: 0, percentage: 0, freeSlots: 0 };
    let totalSlots = 0;
    let bookedSlots = 0;

    matrixData.rows.forEach((row) => {
      row.cells.forEach((cell) => {
        if (cell.slot_type !== "BREAK" && cell.slot_type !== "LUNCH") {
          totalSlots += 1;
          if (cell.sessions && cell.sessions.length > 0) {
            bookedSlots += 1;
          }
        }
      });
    });

    const percentage = totalSlots > 0 ? Math.round((bookedSlots / totalSlots) * 100) : 0;
    return {
      totalSlots,
      bookedSlots,
      percentage,
      freeSlots: totalSlots - bookedSlots,
    };
  };

  const utilization = calculateUtilization();

  const handlePrint = () => {
    window.print();
  };

  const handleExportCSV = () => {
    window.open(`http://localhost:8000/api/v1/timetables/1/export?export_format=csv&view_type=${viewType}`, "_blank");
  };

  const getActiveFilterLabel = () => {
    if (viewType === "SECTION") return `Section: ${selectedSection}`;
    if (viewType === "FACULTY") {
      const fac = facultyList.find((f) => String(f.id) === selectedFaculty);
      return `Faculty: ${fac ? fac.name : selectedFaculty ? `ID #${selectedFaculty}` : "All Faculty"}`;
    }
    if (viewType === "ROOM") {
      const rm = roomList.find((r) => String(r.id) === selectedRoom);
      return `Room: ${rm ? rm.name : selectedRoom ? `ID #${selectedRoom}` : "All Rooms"}`;
    }
    if (viewType === "LAB") {
      const lb = labList.find((l) => String(l.id) === selectedLab);
      return `Lab: ${lb ? lb.name : selectedLab ? `ID #${selectedLab}` : "All Labs"}`;
    }
    if (viewType === "FIRST_YEAR_CYCLE") {
      return selectedCycleGroup ? `Cohort: ${selectedCycleGroup.replace("_", " ")}` : "Joint 1st-Year Cycle View";
    }
    return "Global Overview";
  };

  return (
    <div className="space-y-6">
      {/* Top Controls Bar (Hidden during Print) */}
      <div className="print:hidden space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 bg-slate-900/60 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <div>
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-400" /> Interactive Timetable Matrix Grid
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Deterministic timetable presentation viewer. Operates strictly on verified, persisted solver snapshots.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleExportCSV}
              className="px-3.5 py-2 rounded-xl border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-2 transition shadow-sm"
            >
              <Download className="w-3.5 h-3.5 text-blue-400" /> Export CSV
            </button>
            <button
              onClick={handlePrint}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold flex items-center gap-2 transition shadow-lg shadow-blue-600/20"
            >
              <Printer className="w-3.5 h-3.5" /> Official Print / PDF Layout
            </button>
          </div>
        </div>

        {/* View Perspective Selector Tabs */}
        <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-950/80 rounded-2xl border border-slate-800/80 text-xs font-semibold">
          <button
            onClick={() => setViewType("SECTION")}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 transition ${
              viewType === "SECTION"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/25"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Users className="w-3.5 h-3.5" /> Section View
          </button>
          <button
            onClick={() => setViewType("FACULTY")}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 transition ${
              viewType === "FACULTY"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/25"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <GraduationCap className="w-3.5 h-3.5" /> Faculty View
          </button>
          <button
            onClick={() => setViewType("ROOM")}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 transition ${
              viewType === "ROOM"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/25"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Building2 className="w-3.5 h-3.5" /> Classroom View
          </button>
          <button
            onClick={() => setViewType("LAB")}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 transition ${
              viewType === "LAB"
                ? "bg-blue-600 text-white shadow-md shadow-blue-600/25"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <FlaskConical className="w-3.5 h-3.5" /> Lab Hardware View
          </button>
          <button
            onClick={() => setViewType("FIRST_YEAR_CYCLE")}
            className={`px-4 py-2 rounded-xl flex items-center gap-2 transition ${
              viewType === "FIRST_YEAR_CYCLE"
                ? "bg-indigo-600 text-white shadow-md shadow-indigo-600/25"
                : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Share2 className="w-3.5 h-3.5" /> 1st-Year Cycle & Paired View
          </button>
        </div>

        {/* Dynamic Filter Controls & Utilization Stat Bar */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          <div className="lg:col-span-8 bg-slate-900/40 p-4 rounded-2xl border border-slate-800 flex flex-wrap items-center gap-4 text-xs">
            <div className="flex items-center gap-1.5 text-slate-400 font-semibold">
              <Filter className="w-3.5 h-3.5 text-blue-400" /> Active Filter:
            </div>

            {viewType === "SECTION" && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Section:</span>
                <select
                  value={selectedSection}
                  onChange={(e) => setSelectedSection(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white font-medium"
                >
                  <option value="3A">CSE - 3rd Sem Section A</option>
                  <option value="3B">CSE - 3rd Sem Section B</option>
                  <option value="1A">CSE - 1st Sem Physics Group (1A)</option>
                  <option value="1B">CSE - 1st Sem Chemistry Group (1B)</option>
                </select>
              </div>
            )}

            {viewType === "FACULTY" && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Faculty:</span>
                <select
                  value={selectedFaculty}
                  onChange={(e) => setSelectedFaculty(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white font-medium"
                >
                  <option value="">-- Select Faculty --</option>
                  {facultyList.length > 0 ? (
                    facultyList.map((f) => (
                      <option key={f.id} value={f.id}>
                        {f.name} ({f.department || "Faculty"})
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="1">Dr. Ramesh K (Data Structures)</option>
                      <option value="2">Prof. Ananya S (Electronics)</option>
                      <option value="3">Dr. Sandeep M (Computer Arch)</option>
                      <option value="4">Dr. Suresh P (Applied Physics)</option>
                      <option value="5">Dr. Geeta V (Applied Chemistry)</option>
                    </>
                  )}
                </select>
              </div>
            )}

            {viewType === "ROOM" && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Classroom:</span>
                <select
                  value={selectedRoom}
                  onChange={(e) => setSelectedRoom(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white font-medium"
                >
                  <option value="">-- Select Classroom --</option>
                  {roomList.length > 0 ? (
                    roomList.map((r) => (
                      <option key={r.id} value={r.id}>
                        {r.name} (Cap: {r.capacity})
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="1">LH-101 (Capacity 60)</option>
                      <option value="2">LH-102 (Capacity 60)</option>
                      <option value="3">LH-201 (Capacity 75)</option>
                    </>
                  )}
                </select>
              </div>
            )}

            {viewType === "LAB" && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Physical Lab:</span>
                <select
                  value={selectedLab}
                  onChange={(e) => setSelectedLab(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white font-medium"
                >
                  <option value="">-- Select Physical Lab --</option>
                  {labList.length > 0 ? (
                    labList.map((l) => (
                      <option key={l.id} value={l.id}>
                        {l.name} ({l.capacity} Workstations)
                      </option>
                    ))
                  ) : (
                    <>
                      <option value="1">Computer Science Lab 1 (30 WS)</option>
                      <option value="2">Electronics Hardware Lab (30 WS)</option>
                      <option value="3">Physics Cycle Lab (30 WS)</option>
                      <option value="4">Chemistry Cycle Lab (30 WS)</option>
                    </>
                  )}
                </select>
              </div>
            )}

            {viewType === "FIRST_YEAR_CYCLE" && (
              <div className="flex items-center gap-2">
                <span className="text-slate-400">Cycle Cohort:</span>
                <select
                  value={selectedCycleGroup}
                  onChange={(e) => setSelectedCycleGroup(e.target.value)}
                  className="bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-white font-medium"
                >
                  <option value="">All Cycle Groups Joint View</option>
                  <option value="PHYSICS_CYCLE">Physics Cycle Cohort</option>
                  <option value="CHEMISTRY_CYCLE">Chemistry Cycle Cohort</option>
                </select>
              </div>
            )}
          </div>

          {/* Utilization Heatmap Card */}
          <div className="lg:col-span-4 bg-slate-900/40 p-4 rounded-2xl border border-slate-800 flex items-center justify-between gap-3 text-xs">
            <div className="space-y-1">
              <div className="text-slate-400 font-medium flex items-center gap-1.5">
                <Activity className="w-3.5 h-3.5 text-emerald-400" />
                <span>Schedule Utilization</span>
              </div>
              <div className="text-sm font-bold text-white">
                {utilization.bookedSlots} / {utilization.totalSlots} Periods{" "}
                <span className="text-xs font-semibold text-emerald-400">({utilization.percentage}%)</span>
              </div>
            </div>

            <div className="text-right">
              <div className="text-[10px] text-slate-400">Free Open Slots</div>
              <div className="text-sm font-bold font-mono text-blue-400">{utilization.freeSlots} Slots</div>
            </div>
          </div>
        </div>
      </div>

      {/* Paired-Slot Visual Feature Cards (When First-Year Cycle view is active) */}
      {viewType === "FIRST_YEAR_CYCLE" && matrixData?.paired_slot_groups && matrixData.paired_slot_groups.length > 0 && (
        <div className="p-5 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-purple-950/30 to-slate-900 border border-indigo-800/50 space-y-3 print:hidden">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-indigo-300 flex items-center gap-2">
              <Share2 className="w-4 h-4 text-indigo-400" /> First-Year Joint Paired-Slot Allocations
            </h3>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300">
              Synced Slot Constraint Active
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {matrixData.paired_slot_groups.map((group, gIdx) => (
              <div key={gIdx} className="p-4 rounded-xl bg-slate-950/80 border border-indigo-900/60 space-y-3">
                <div className="flex items-center justify-between border-b border-slate-800 pb-2">
                  <span className="text-xs font-bold text-white font-mono bg-indigo-500/20 px-2 py-0.5 rounded">
                    Paired Slot Group: {group.paired_slot_group}
                  </span>
                  <span className="text-[11px] text-slate-400">{group.time_slot_label}</span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs">
                  {group.sessions.map((s, sIdx) => (
                    <div
                      key={sIdx}
                      className={`p-3 rounded-lg border flex flex-col justify-between space-y-1.5 ${
                        s.cycle_group === "PHYSICS_CYCLE"
                          ? "bg-purple-950/30 border-purple-800/50"
                          : "bg-emerald-950/30 border-emerald-800/50"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-white font-mono">{s.subject_code}</span>
                        <span className="text-[9px] font-mono uppercase text-slate-300">
                          {s.cycle_group?.replace("_CYCLE", "")}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-300 font-medium truncate">{s.subject_name}</div>
                      <div className="text-[10px] text-slate-400">Faculty: {s.faculty_name}</div>
                      <div className="text-[10px] text-blue-300 font-mono">Room: {s.room_name || s.lab_name}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main 2D Timetable Matrix Table */}
      <div className="bg-slate-900/60 rounded-3xl border border-slate-800 overflow-hidden shadow-2xl print:shadow-none print:border print:border-black print:rounded-none print:bg-white">
        {/* Official Institutional Print Header */}
        <div className="hidden print:block p-6 border-b-2 border-black text-center space-y-1 bg-white text-black">
          <h1 className="text-xl font-extrabold uppercase tracking-wide">
            VTU AUTONOMOUS ENGINEERING COLLEGE
          </h1>
          <h2 className="text-sm font-semibold uppercase text-slate-700">
            DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING
          </h2>
          <div className="text-xs font-bold pt-1 text-slate-900">
            OFFICIAL ACADEMIC TIMETABLE • 2026-2027 (ODD SEMESTER)
          </div>
          <div className="text-xs text-slate-600 flex items-center justify-between pt-2 border-t border-slate-300 mt-2 font-mono">
            <span>{getActiveFilterLabel()}</span>
            <span>Effective Date: 15-Sep-2026</span>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-20 text-slate-400 text-sm">Assembling timetable matrix...</div>
        ) : !matrixData ? (
          <div className="text-center py-20 text-slate-500 text-sm">No timetable data available.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse print:text-black">
              {/* Header Row: Periods */}
              <thead>
                <tr className="bg-slate-950/80 border-b border-slate-800 text-xs print:bg-slate-100 print:border-b-2 print:border-black">
                  <th className="p-4 font-bold text-slate-300 uppercase tracking-wider w-28 border-r border-slate-800 print:text-black print:border-black">
                    Day / Time
                  </th>
                  {matrixData.periods_header.map((p) => {
                    const isBreak = p.slot_type === "BREAK" || p.slot_type === "LUNCH";
                    return (
                      <th
                        key={p.period_index}
                        className={`p-3 font-semibold text-center border-r border-slate-800/80 min-w-[130px] print:border-black ${
                          isBreak ? "bg-slate-950 text-slate-500 text-[10px] print:bg-slate-200 print:text-black" : "text-slate-200 print:text-black"
                        }`}
                      >
                        <div className="font-bold text-slate-100 print:text-black">{p.label}</div>
                        <div className="text-[10px] font-mono text-slate-400 print:text-slate-600 mt-0.5">
                          {p.start_time} - {p.end_time}
                        </div>
                      </th>
                    );
                  })}
                </tr>
              </thead>

              {/* Data Rows: Days */}
              <tbody className="divide-y divide-slate-800/60 text-xs print:divide-black">
                {matrixData.rows.map((row) => (
                  <tr key={row.day_of_week} className="hover:bg-slate-800/20 transition print:hover:bg-transparent">
                    {/* Day Column */}
                    <td className="p-4 font-bold text-white bg-slate-950/40 border-r border-slate-800 align-middle print:bg-slate-50 print:text-black print:border-black">
                      {row.day_name}
                    </td>

                    {/* Periods Cells */}
                    {row.cells.map((cell, cIdx) => {
                      const isBreak = cell.slot_type === "BREAK" || cell.slot_type === "LUNCH";

                      if (isBreak) {
                        return (
                          <td
                            key={cIdx}
                            className="p-3 bg-slate-950/90 text-center border-r border-slate-800/60 align-middle print:bg-slate-200 print:border-black"
                          >
                            <span className="text-[10px] font-mono font-bold tracking-widest text-slate-600 uppercase [writing-mode:vertical-lr] rotate-180 inline-block py-2 print:text-black">
                              {cell.slot_type}
                            </span>
                          </td>
                        );
                      }

                      if (!cell.sessions || cell.sessions.length === 0) {
                        return (
                          <td
                            key={cIdx}
                            className="p-3 border-r border-slate-800/40 text-center text-slate-600 align-middle font-mono text-xs print:border-black print:text-slate-400"
                          >
                            -
                          </td>
                        );
                      }

                      return (
                        <td
                          key={cIdx}
                          className={`p-2.5 border-r border-slate-800/60 align-top print:border-black ${
                            cell.has_conflict ? "bg-red-500/10 border-red-500/30" : ""
                          }`}
                        >
                          <div className="space-y-2">
                            {cell.sessions.map((sess, sIdx) => {
                              const isLab = sess.subject_type === "LAB";
                              const isPaired = !!sess.paired_slot_group;

                              return (
                                <div
                                  key={sIdx}
                                  className={`p-2.5 rounded-xl border flex flex-col justify-between space-y-1.5 transition print:rounded-none print:border-black print:bg-white print:p-2 ${
                                    isLab
                                      ? "bg-emerald-950/40 border-emerald-800/50 hover:border-emerald-700"
                                      : isPaired
                                      ? "bg-indigo-950/40 border-indigo-800/50 hover:border-indigo-700"
                                      : "bg-slate-950/80 border-slate-800 hover:border-slate-700"
                                  }`}
                                >
                                  {/* Subject Code & Batch */}
                                  <div className="flex items-center justify-between gap-1">
                                    <span className="font-bold text-white font-mono text-[11px] print:text-black">
                                      {sess.subject_code}
                                    </span>
                                    {sess.batch_name && (
                                      <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-emerald-500/20 text-emerald-300 print:bg-transparent print:border print:border-black print:text-black">
                                        {sess.batch_name}
                                      </span>
                                    )}
                                    {sess.paired_slot_group && (
                                      <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-indigo-500/20 text-indigo-300 print:bg-transparent print:border print:border-black print:text-black">
                                        {sess.paired_slot_group}
                                      </span>
                                    )}
                                  </div>

                                  {/* Subject Title */}
                                  <div className="text-[10px] text-slate-300 line-clamp-1 font-medium print:text-black">
                                    {sess.subject_name}
                                  </div>

                                  {/* Faculty & Location */}
                                  <div className="pt-1 border-t border-slate-800/80 print:border-black flex items-center justify-between text-[10px] text-slate-400 print:text-black">
                                    <span className="truncate max-w-[80px]">{sess.faculty_name}</span>
                                    <span className="font-mono text-blue-300 font-semibold truncate print:text-black">
                                      {sess.lab_name ? sess.lab_name.split(" ")[0] : sess.room_name}
                                    </span>
                                  </div>

                                  {/* Conflict Badge if applicable */}
                                  {sess.has_conflict && (
                                    <div className="text-[9px] text-red-400 bg-red-500/10 p-1 rounded font-bold flex items-center gap-1 print:border print:border-red-600 print:text-red-700">
                                      <AlertTriangle className="w-3 h-3 text-red-400" /> Clash Detected
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Official Institutional Print Footer (Signatures) */}
        <div className="hidden print:grid grid-cols-4 gap-6 p-8 pt-16 bg-white text-black text-center text-xs font-bold border-t-2 border-black">
          <div className="space-y-8">
            <div className="border-t border-black pt-2">Time Table Coordinator</div>
          </div>
          <div className="space-y-8">
            <div className="border-t border-black pt-2">Head of Department (HOD)</div>
          </div>
          <div className="space-y-8">
            <div className="border-t border-black pt-2">Dean (Academics)</div>
          </div>
          <div className="space-y-8">
            <div className="border-t border-black pt-2">Principal</div>
          </div>
        </div>
      </div>
    </div>
  );
}
