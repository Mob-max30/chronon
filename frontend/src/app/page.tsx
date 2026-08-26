import Link from "next/link";
import { NavigationShell } from "@/components/NavigationShell";
import { HealthBadge } from "@/components/HealthBadge";
import { WorkflowTimeline } from "@/components/WorkflowTimeline";
import {
  Calendar,
  Sparkles,
  ArrowRight,
  GitBranch,
  Cpu,
  Layers,
  Database,
  Users,
  Grid3X3,
  BookOpen,
  Building2,
  FileText,
} from "lucide-react";

export default function HomePage() {
  return (
    <div className="flex flex-col min-h-screen">
      <NavigationShell />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-10">
        {/* Hero Section */}
        <section className="relative overflow-hidden rounded-3xl border border-slate-800/80 bg-gradient-to-b from-slate-900/90 via-slate-900/40 to-slate-950 p-8 sm:p-12 shadow-2xl">
          <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none" />
          <div className="relative z-10 max-w-3xl space-y-6">
            <div className="flex flex-wrap items-center gap-3">
              <HealthBadge />
              <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full border border-emerald-500/30 bg-emerald-500/10 text-emerald-300 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5 text-emerald-400" /> Milestone 1 Integration Active (dev)
              </div>
            </div>

            <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
              Deterministic Academic Timetable Generation Platform
            </h1>

            <p className="text-base sm:text-lg text-slate-300 leading-relaxed">
              Engineered with <span className="text-blue-400 font-semibold">Google OR-Tools CP-SAT</span> for guaranteed 100% clash-free schedules across classrooms, physical labs, faculty, and first-year cycle cohorts.
            </p>

            <div className="pt-2 flex flex-wrap gap-4">
              <Link
                href="/generation"
                className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm flex items-center gap-2 shadow-lg shadow-blue-600/25 transition"
              >
                <Cpu className="w-4 h-4" /> Start Schedule Generation <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/timetables"
                className="px-6 py-3 rounded-xl border border-slate-700 hover:border-slate-600 bg-slate-800/50 hover:bg-slate-800 text-slate-200 font-medium text-sm transition flex items-center gap-2"
              >
                <Grid3X3 className="w-4 h-4 text-amber-400" /> View Timetable Matrix Grid
              </Link>
            </div>
          </div>
        </section>

        {/* Workflow State Machine */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">Core Generation Workflow</h2>
              <p className="text-xs text-slate-400">Strict deterministic progression state machine</p>
            </div>
          </div>
          <WorkflowTimeline />
        </section>

        {/* 4-Developer Integrated Domain Modules */}
        <section className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight">Integrated Domain Hubs</h2>
              <p className="text-xs text-slate-400">4-Way balanced parallel architecture unified on dev branch</p>
            </div>
            <span className="text-xs text-slate-500 font-mono flex items-center gap-1">
              <GitBranch className="w-3.5 h-3.5 text-emerald-400" /> dev branch integrated
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* Pranav */}
            <Link
              href="/generation"
              className="p-5 rounded-2xl border border-blue-500/30 hover:border-blue-400 bg-slate-900/60 hover:bg-slate-900/90 flex flex-col justify-between space-y-4 transition group shadow-lg hover:shadow-blue-950/30"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-blue-300 bg-blue-500/20 px-2.5 py-1 rounded-md border border-blue-500/30 font-mono">
                    pranav
                  </span>
                  <Layers className="w-4 h-4 text-blue-400 group-hover:scale-110 transition" />
                </div>
                <h3 className="font-bold text-white flex items-center gap-1.5">
                  Pranav (Lead) <ArrowRight className="w-3.5 h-3.5 text-blue-400 opacity-0 group-hover:opacity-100 transition" />
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Academic lifecycle, Generation orchestration (<code className="text-blue-300">GenerationRun</code>), Timetable versioning (<code className="text-blue-300">TimetableVersion</code>), state machine.
                </p>
              </div>
              <div className="text-[11px] text-blue-400 font-semibold flex items-center justify-between">
                <span>Generation & Versioning</span>
                <span className="text-[10px] bg-blue-500/20 px-2 py-0.5 rounded">Integrated</span>
              </div>
            </Link>

            {/* Ujwal */}
            <Link
              href="/academic"
              className="p-5 rounded-2xl border border-emerald-500/30 hover:border-emerald-400 bg-slate-900/60 hover:bg-slate-900/90 flex flex-col justify-between space-y-4 transition group shadow-lg hover:shadow-emerald-950/30"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-emerald-300 bg-emerald-500/20 px-2.5 py-1 rounded-md border border-emerald-500/30 font-mono">
                    ujwal
                  </span>
                  <Database className="w-4 h-4 text-emerald-400 group-hover:scale-110 transition" />
                </div>
                <h3 className="font-bold text-white flex items-center gap-1.5">
                  Ujwal <ArrowRight className="w-3.5 h-3.5 text-emerald-400 opacity-0 group-hover:opacity-100 transition" />
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  VTU Syllabus OCR, Academic Catalog, Branch/Student counts, Physics/Chemistry cycles, Faculty document ingestion.
                </p>
              </div>
              <div className="text-[11px] text-emerald-400 font-semibold flex items-center justify-between">
                <span>Ingestion & Curriculum</span>
                <span className="text-[10px] bg-emerald-500/20 px-2 py-0.5 rounded">Integrated</span>
              </div>
            </Link>

            {/* Pruthvik */}
            <Link
              href="/generation"
              className="p-5 rounded-2xl border border-purple-500/30 hover:border-purple-400 bg-slate-900/60 hover:bg-slate-900/90 flex flex-col justify-between space-y-4 transition group shadow-lg hover:shadow-purple-950/30"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-purple-300 bg-purple-500/20 px-2.5 py-1 rounded-md border border-purple-500/30 font-mono">
                    pruthvik
                  </span>
                  <Cpu className="w-4 h-4 text-purple-400 group-hover:scale-110 transition" />
                </div>
                <h3 className="font-bold text-white flex items-center gap-1.5">
                  Pruthvik <ArrowRight className="w-3.5 h-3.5 text-purple-400 opacity-0 group-hover:opacity-100 transition" />
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Google OR-Tools CP-SAT formulation, hard & soft constraint modeling, independent validator, conflict diagnostics.
                </p>
              </div>
              <div className="text-[11px] text-purple-400 font-semibold flex items-center justify-between">
                <span>CP-SAT Solver & Engine</span>
                <span className="text-[10px] bg-purple-500/20 px-2 py-0.5 rounded">Integrated</span>
              </div>
            </Link>

            {/* Nivish */}
            <Link
              href="/resources"
              className="p-5 rounded-2xl border border-amber-500/30 hover:border-amber-400 bg-slate-900/60 hover:bg-slate-900/90 flex flex-col justify-between space-y-4 transition group shadow-lg hover:shadow-amber-950/30"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-bold text-amber-300 bg-amber-500/20 px-2.5 py-1 rounded-md border border-amber-500/30 font-mono">
                    nivish
                  </span>
                  <Users className="w-4 h-4 text-amber-400 group-hover:scale-110 transition" />
                </div>
                <h3 className="font-bold text-white flex items-center gap-1.5">
                  Nivish <ArrowRight className="w-3.5 h-3.5 text-amber-400 opacity-0 group-hover:opacity-100 transition" />
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  Classrooms, physical lab mappings, section partitioning, batching, time slots, timetable matrix grid UI.
                </p>
              </div>
              <div className="text-[11px] text-amber-400 font-semibold flex items-center justify-between">
                <span>Resources & Matrix UI</span>
                <span className="text-[10px] bg-amber-500/20 px-2 py-0.5 rounded">Integrated</span>
              </div>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>© 2026 Chronon Project. Built for VTU & Autonomous Academic Scheduling.</p>
          <div className="flex items-center space-x-4">
            <span>Authoritative Spec: <code className="text-slate-400">CHRONON_FINAL_README.txt</code></span>
          </div>
        </div>
      </footer>
    </div>
  );
}
