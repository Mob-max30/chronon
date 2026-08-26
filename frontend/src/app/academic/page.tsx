"use client";

import React, { useState } from "react";
import { NavigationShell } from "@/components/NavigationShell";
import {
  BookOpen,
  Users,
  UploadCloud,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  FileText,
  Plus,
  RefreshCw,
  Search,
  Filter,
  ArrowRight,
  Database,
  Calculator,
} from "lucide-react";

export default function AcademicHubPage() {
  const [activeTab, setActiveTab] = useState<"ingestion" | "branches" | "subjects" | "faculty">("ingestion");

  // Ingestion sample state
  const [uploadStatus, setUploadStatus] = useState<"idle" | "uploading" | "parsed" | "confirmed">("idle");
  const [activeFileName, setActiveFileName] = useState<string>("");

  // Branch & Stream sample state
  const [branches, setBranches] = useState([
    { id: 1, name: "Computer Science & Engineering", code: "CSE", studentCount: 180, stream: "CSE Stream" },
    { id: 2, name: "Information Science & Engineering", code: "ISE", studentCount: 120, stream: "CSE Stream" },
    { id: 3, name: "Artificial Intelligence & Machine Learning", code: "AIML", studentCount: 60, stream: "CSE Stream" },
    { id: 4, name: "Electronics & Communication Engineering", code: "ECE", studentCount: 120, stream: "EEE Stream" },
    { id: 5, name: "Mechanical Engineering", code: "ME", studentCount: 60, stream: "Mechanical Stream" },
    { id: 6, name: "Civil Engineering", code: "CV", studentCount: 60, stream: "Civil Stream" },
  ]);

  // First-year cycle split calculator state
  const [splitMethod, setSplitMethod] = useState<"EVEN" | "MANUAL" | "CAPACITY">("EVEN");
  const [manualPhysics, setManualPhysics] = useState<number>(180);
  const [labCapacity, setLabCapacity] = useState<number>(30);

  const cseTotalStudents = branches
    .filter((b) => b.stream === "CSE Stream")
    .reduce((sum, b) => sum + b.studentCount, 0);

  const calculatedPhysics =
    splitMethod === "EVEN"
      ? Math.ceil(cseTotalStudents / 2)
      : splitMethod === "MANUAL"
      ? manualPhysics
      : Math.round(cseTotalStudents / 2 / labCapacity) * labCapacity;

  const calculatedChemistry = Math.max(0, cseTotalStudents - calculatedPhysics);

  // Subject catalogue sample state
  const [selectedSemester, setSelectedSemester] = useState<number>(1);
  const [subjectFilter, setSubjectFilter] = useState<string>("");

  const sampleSubjects = [
    { id: 1, code: "22MATS11", name: "Mathematics-I for CSE Stream", semester: 1, type: "THEORY", hours: 4, credits: 4, cycle: "COMMON", stream: "CSE" },
    { id: 2, code: "22ENG16", name: "Communicative English", semester: 1, type: "THEORY", hours: 2, credits: 1, cycle: "COMMON", stream: "CSE" },
    { id: 3, code: "22PHYS12", name: "Physics for CSE Stream", semester: 1, type: "THEORY", hours: 4, credits: 4, cycle: "PHYSICS", stream: "CSE" },
    { id: 4, code: "22PHYL16", name: "Physics Laboratory", semester: 1, type: "LAB", hours: 2, credits: 1, cycle: "PHYSICS", stream: "CSE" },
    { id: 5, code: "22CHEM12", name: "Chemistry for CSE Stream", semester: 1, type: "THEORY", hours: 4, credits: 4, cycle: "CHEMISTRY", stream: "CSE" },
    { id: 6, code: "22CHEL16", name: "Chemistry Laboratory", semester: 1, type: "LAB", hours: 2, credits: 1, cycle: "CHEMISTRY", stream: "CSE" },
    { id: 10, code: "21CS31", name: "Transform Calculus & Numerical Techniques", semester: 3, type: "THEORY", hours: 4, credits: 3, cycle: "NONE", stream: "CSE" },
    { id: 11, code: "21CS32", name: "Data Structures and Applications", semester: 3, type: "THEORY", hours: 4, credits: 4, cycle: "NONE", stream: "CSE" },
    { id: 12, code: "21CS33", name: "Analog and Digital Electronics", semester: 3, type: "THEORY", hours: 4, credits: 3, cycle: "NONE", stream: "CSE" },
    { id: 13, code: "21CSL35", name: "Data Structures Laboratory", semester: 3, type: "LAB", hours: 2, credits: 1, cycle: "NONE", stream: "CSE" },
  ];

  // Faculty sample state
  const sampleFaculty = [
    { id: 1, name: "Prof. Rajesh Kumar", code: "FAC101", dept: "Computer Science & Engineering", desig: "Professor & HOD", maxHours: 14, subjects: ["21CS32", "21CSL35"] },
    { id: 2, name: "Dr. Sneha Sharma", code: "FAC102", dept: "Mathematics", desig: "Associate Professor", maxHours: 16, subjects: ["22MATS11", "21CS31"] },
    { id: 3, name: "Prof. Amit Verma", code: "FAC103", dept: "Physics", desig: "Assistant Professor", maxHours: 18, subjects: ["22PHYS12", "22PHYL16"] },
    { id: 4, name: "Dr. Ananya Iyer", code: "FAC104", dept: "Chemistry", desig: "Associate Professor", maxHours: 18, subjects: ["22CHEM12", "22CHEL16"] },
    { id: 5, name: "Prof. Vikram Patil", code: "FAC105", dept: "Computer Science & Engineering", desig: "Assistant Professor", maxHours: 18, subjects: ["21CS34", "21CS33"] },
  ];

  const handleSimulatedUpload = () => {
    setActiveFileName("VTU_CSE_2022_Scheme_Curriculum.pdf");
    setUploadStatus("uploading");
    setTimeout(() => {
      setUploadStatus("parsed");
    }, 1200);
  };

  const handleConfirmIngestion = () => {
    setUploadStatus("confirmed");
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100">
      <NavigationShell />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Ujwal&apos;s Domain
              </span>
              <span className="text-xs text-slate-400 font-mono">Academic Pipeline v1.0</span>
            </div>
            <h1 className="text-3xl font-extrabold tracking-tight text-white">
              Academic Information & Document Ingestion
            </h1>
            <p className="text-sm text-slate-400 mt-1">
              Authoritative management of VTU Schemes, First-Year Streams, Cycle Groups, Subject Catalogue, and Faculty Directory.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <div className="text-xs text-slate-400">Target Scheme</div>
              <div className="text-sm font-semibold text-white">VTU 2022 Scheme (Autonomous)</div>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 border-b border-slate-800/80 pb-3">
          <button
            onClick={() => setActiveTab("ingestion")}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 transition ${
              activeTab === "ingestion"
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25"
                : "bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <UploadCloud className="w-4 h-4" /> VTU Ingestion Studio
          </button>
          <button
            onClick={() => setActiveTab("branches")}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 transition ${
              activeTab === "branches"
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25"
                : "bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <Layers className="w-4 h-4" /> Streams & Cycle Split
          </button>
          <button
            onClick={() => setActiveTab("subjects")}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 transition ${
              activeTab === "subjects"
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25"
                : "bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <BookOpen className="w-4 h-4" /> Curriculum Subjects
          </button>
          <button
            onClick={() => setActiveTab("faculty")}
            className={`px-4 py-2.5 rounded-xl text-sm font-semibold flex items-center gap-2 transition ${
              activeTab === "faculty"
                ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25"
                : "bg-slate-900/60 text-slate-400 hover:text-slate-200 hover:bg-slate-900"
            }`}
          >
            <Users className="w-4 h-4" /> Faculty Directory
          </button>
        </div>

        {/* TAB 1: Ingestion Studio */}
        {activeTab === "ingestion" && (
          <div className="space-y-6">
            {/* Upload Box */}
            <div className="border-2 border-dashed border-slate-800 hover:border-blue-500/60 rounded-3xl bg-slate-900/40 p-8 text-center transition">
              <div className="max-w-md mx-auto space-y-4">
                <div className="w-14 h-14 mx-auto rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
                  <UploadCloud className="w-7 h-7" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Upload VTU Syllabus, Branch Circular, or Staff Roster</h3>
                  <p className="text-xs text-slate-400 mt-1">
                    Supports PDF documents (PyMuPDF), DOCX files (python-docx), and Scanned Image OCR (Tesseract).
                  </p>
                </div>
                <div className="pt-2 flex justify-center gap-3">
                  <button
                    onClick={handleSimulatedUpload}
                    disabled={uploadStatus === "uploading"}
                    className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-blue-800 text-white text-xs font-semibold flex items-center gap-2 shadow-lg shadow-blue-600/20 transition"
                  >
                    {uploadStatus === "uploading" ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" /> Processing OCR / Parser...
                      </>
                    ) : (
                      <>
                        <FileText className="w-4 h-4" /> Stage Sample Syllabus PDF
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Candidate Review Stage */}
            {uploadStatus !== "idle" && (
              <div className="border border-slate-800 rounded-3xl bg-slate-900/60 p-6 space-y-6">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
                      <Sparkles className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-white">Human-in-the-Loop Candidate Review</h3>
                      <p className="text-xs text-slate-400">
                        File: <span className="text-indigo-300 font-mono">{activeFileName}</span> | Category: <span className="text-emerald-400 font-semibold">SYLLABUS (VTU 2022)</span>
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {uploadStatus === "parsed" && (
                      <button
                        onClick={handleConfirmIngestion}
                        className="px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center gap-2 shadow-lg shadow-emerald-600/20 transition"
                      >
                        <CheckCircle2 className="w-4 h-4" /> Confirm & Commit to Database
                      </button>
                    )}
                    {uploadStatus === "confirmed" && (
                      <div className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold">
                        <CheckCircle2 className="w-4 h-4" /> Confirmed & Saved to Database
                      </div>
                    )}
                  </div>
                </div>

                {/* Candidates Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider">
                        <th className="py-3 px-4">Subject Code</th>
                        <th className="py-3 px-4">Course Title</th>
                        <th className="py-3 px-4">Semester</th>
                        <th className="py-3 px-4">Type</th>
                        <th className="py-3 px-4">Cycle Group</th>
                        <th className="py-3 px-4">Confidence</th>
                        <th className="py-3 px-4">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
                      <tr>
                        <td className="py-3 px-4 font-bold text-blue-400">22MATS11</td>
                        <td className="py-3 px-4 font-sans text-slate-200">Mathematics-I for CSE Stream</td>
                        <td className="py-3 px-4">Sem 1</td>
                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">THEORY</span></td>
                        <td className="py-3 px-4"><span className="text-slate-400">Common (NULL)</span></td>
                        <td className="py-3 px-4 text-emerald-400">96%</td>
                        <td className="py-3 px-4 text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Reviewed</td>
                      </tr>
                      <tr>
                        <td className="py-3 px-4 font-bold text-blue-400">22PHYS12</td>
                        <td className="py-3 px-4 font-sans text-slate-200">Physics for CSE Stream</td>
                        <td className="py-3 px-4">Sem 1</td>
                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">THEORY</span></td>
                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">PHYSICS</span></td>
                        <td className="py-3 px-4 text-emerald-400">95%</td>
                        <td className="py-3 px-4 text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Reviewed</td>
                      </tr>
                      <tr>
                        <td className="py-3 px-4 font-bold text-blue-400">22PHYL16</td>
                        <td className="py-3 px-4 font-sans text-slate-200">Physics Laboratory</td>
                        <td className="py-3 px-4">Sem 1</td>
                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">LAB</span></td>
                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">PHYSICS</span></td>
                        <td className="py-3 px-4 text-emerald-400">94%</td>
                        <td className="py-3 px-4 text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Reviewed</td>
                      </tr>
                      <tr>
                        <td className="py-3 px-4 font-bold text-blue-400">22CHEM12</td>
                        <td className="py-3 px-4 font-sans text-slate-200">Chemistry for CSE Stream</td>
                        <td className="py-3 px-4">Sem 1</td>
                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">THEORY</span></td>
                        <td className="py-3 px-4"><span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">CHEMISTRY</span></td>
                        <td className="py-3 px-4 text-emerald-400">95%</td>
                        <td className="py-3 px-4 text-emerald-400 flex items-center gap-1"><CheckCircle2 className="w-3.5 h-3.5" /> Reviewed</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: Streams & Cycle Split */}
        {activeTab === "branches" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Left: Branch Catalogue & Student Counts */}
            <div className="lg:col-span-2 border border-slate-800 rounded-3xl bg-slate-900/60 p-6 space-y-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-base font-bold text-white">Branch Catalogue & Student Intake</h3>
                  <p className="text-xs text-slate-400">Branch identities preserved for academic records and stream rollups.</p>
                </div>
                <div className="text-xs font-mono bg-blue-500/10 text-blue-400 px-3 py-1 rounded-lg border border-blue-500/20">
                  Total Students: {branches.reduce((sum, b) => sum + b.studentCount, 0)}
                </div>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                      <th className="py-3 px-4">Code</th>
                      <th className="py-3 px-4">Branch Name</th>
                      <th className="py-3 px-4">Assigned Stream</th>
                      <th className="py-3 px-4">Intake Students</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {branches.map((b) => (
                      <tr key={b.id}>
                        <td className="py-3 px-4 font-mono font-bold text-blue-400">{b.code}</td>
                        <td className="py-3 px-4 font-medium text-slate-200">{b.name}</td>
                        <td className="py-3 px-4 font-mono text-slate-400">{b.stream}</td>
                        <td className="py-3 px-4 font-mono font-bold text-white">{b.studentCount}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right: First-Year Cycle Split Engine */}
            <div className="border border-slate-800 rounded-3xl bg-slate-900/60 p-6 space-y-6 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Calculator className="w-5 h-5 text-indigo-400" />
                  <h3 className="text-base font-bold text-white">First-Year Cycle Splitter</h3>
                </div>
                <p className="text-xs text-slate-400">
                  First-year timetable construction operates at <span className="text-indigo-300 font-semibold">Stream + Cycle Group</span> granularity.
                </p>

                <div className="p-4 rounded-2xl bg-slate-950 border border-slate-800 space-y-3">
                  <div className="text-xs text-slate-400">Target Stream: <span className="text-white font-bold">CSE Stream</span></div>
                  <div className="text-2xl font-extrabold text-white font-mono">{cseTotalStudents} Students</div>
                  <div className="text-[11px] text-slate-500">(Rollup from CSE 180 + ISE 120 + AIML 60)</div>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-semibold text-slate-300">Split Method</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(["EVEN", "MANUAL", "CAPACITY"] as const).map((m) => (
                      <button
                        key={m}
                        onClick={() => setSplitMethod(m)}
                        className={`py-2 text-xs font-semibold rounded-xl border transition ${
                          splitMethod === m
                            ? "bg-indigo-600 border-indigo-500 text-white"
                            : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        {m}
                      </button>
                    ))}
                  </div>
                </div>

                {splitMethod === "MANUAL" && (
                  <div className="space-y-1">
                    <label className="text-xs text-slate-400">Physics Cohort Intake</label>
                    <input
                      type="number"
                      value={manualPhysics}
                      onChange={(e) => setManualPhysics(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    />
                  </div>
                )}

                {splitMethod === "CAPACITY" && (
                  <div className="space-y-1">
                    <label className="text-xs text-slate-400">Lab Capacity Constraint</label>
                    <input
                      type="number"
                      value={labCapacity}
                      onChange={(e) => setLabCapacity(Number(e.target.value))}
                      className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white"
                    />
                  </div>
                )}

                {/* Result Cohort Badges */}
                <div className="grid grid-cols-2 gap-3 pt-2">
                  <div className="p-3 rounded-xl bg-purple-500/10 border border-purple-500/20 text-center">
                    <div className="text-[11px] font-semibold text-purple-300">Physics Group (P-Cycle)</div>
                    <div className="text-xl font-bold text-purple-400 font-mono mt-1">{calculatedPhysics}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Sem 1: Physics | Sem 2: Chemistry</div>
                  </div>

                  <div className="p-3 rounded-xl bg-cyan-500/10 border border-cyan-500/20 text-center">
                    <div className="text-[11px] font-semibold text-cyan-300">Chemistry Group (C-Cycle)</div>
                    <div className="text-xl font-bold text-cyan-400 font-mono mt-1">{calculatedChemistry}</div>
                    <div className="text-[10px] text-slate-500 mt-0.5">Sem 1: Chemistry | Sem 2: Physics</div>
                  </div>
                </div>
              </div>

              <div className="text-[11px] text-slate-500 border-t border-slate-800 pt-3">
                Paired-slot constraint applies jointly to Physics and Chemistry groups.
              </div>
            </div>
          </div>
        )}

        {/* TAB 3: Subjects */}
        {activeTab === "subjects" && (
          <div className="border border-slate-800 rounded-3xl bg-slate-900/60 p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-white">Curriculum Subject Catalogue</h3>
                <p className="text-xs text-slate-400">Filtered by scheme, semester, theory vs lab classification, and cycle group.</p>
              </div>

              <div className="flex items-center gap-3">
                <div className="flex items-center gap-1 bg-slate-950 border border-slate-800 rounded-xl p-1 text-xs">
                  {[1, 2, 3, 4].map((sem) => (
                    <button
                      key={sem}
                      onClick={() => setSelectedSemester(sem)}
                      className={`px-3 py-1.5 rounded-lg font-semibold transition ${
                        selectedSemester === sem ? "bg-blue-600 text-white" : "text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      Sem {sem}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-semibold uppercase">
                    <th className="py-3 px-4">Subject Code</th>
                    <th className="py-3 px-4">Course Name</th>
                    <th className="py-3 px-4">Type</th>
                    <th className="py-3 px-4">Weekly Hours</th>
                    <th className="py-3 px-4">Credits</th>
                    <th className="py-3 px-4">Cycle Assignment</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 text-slate-300">
                  {sampleSubjects
                    .filter((s) => s.semester === selectedSemester)
                    .map((s) => (
                      <tr key={s.id}>
                        <td className="py-3 px-4 font-mono font-bold text-blue-400">{s.code}</td>
                        <td className="py-3 px-4 font-medium text-slate-200">{s.name}</td>
                        <td className="py-3 px-4">
                          <span
                            className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                              s.type === "LAB" ? "bg-amber-500/10 text-amber-400 border border-amber-500/20" : "bg-blue-500/10 text-blue-400 border border-blue-500/20"
                            }`}
                          >
                            {s.type}
                          </span>
                        </td>
                        <td className="py-3 px-4 font-mono">{s.hours} hrs/wk</td>
                        <td className="py-3 px-4 font-mono">{s.credits} cr</td>
                        <td className="py-3 px-4">
                          {s.cycle === "COMMON" ? (
                            <span className="text-slate-400">Common (Both Cycles)</span>
                          ) : s.cycle === "PHYSICS" ? (
                            <span className="text-purple-400 font-semibold">Physics Cycle</span>
                          ) : s.cycle === "CHEMISTRY" ? (
                            <span className="text-cyan-400 font-semibold">Chemistry Cycle</span>
                          ) : (
                            <span className="text-slate-500">Standard Semester Subject</span>
                          )}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 4: Faculty */}
        {activeTab === "faculty" && (
          <div className="border border-slate-800 rounded-3xl bg-slate-900/60 p-6 space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h3 className="text-base font-bold text-white">Faculty Directory & Subject Assignments</h3>
                <p className="text-xs text-slate-400">Faculty workload capacity and multi-stream subject mapping.</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sampleFaculty.map((f) => (
                <div key={f.id} className="p-5 rounded-2xl border border-slate-800 bg-slate-950 flex flex-col justify-between space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[11px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                        {f.code}
                      </span>
                      <span className="text-[11px] text-slate-400 font-mono">Max {f.maxHours} hrs/wk</span>
                    </div>
                    <h4 className="font-bold text-slate-100">{f.name}</h4>
                    <p className="text-xs text-slate-400 mt-0.5">{f.desig}</p>
                    <p className="text-[11px] text-slate-500 mt-1">{f.dept}</p>
                  </div>

                  <div className="border-t border-slate-800/80 pt-3">
                    <div className="text-[10px] uppercase font-bold text-slate-500 tracking-wider mb-1.5">Assigned Subjects</div>
                    <div className="flex flex-wrap gap-1.5">
                      {f.subjects.map((sub) => (
                        <span key={sub} className="text-[11px] font-mono font-bold px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                          {sub}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
