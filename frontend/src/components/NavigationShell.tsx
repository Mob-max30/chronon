"use client";

import React from "react";
import Link from "next/link";
<<<<<<< HEAD
import { Clock, Calendar, BookOpen, Users, Cpu, FileText, Grid } from "lucide-react";
=======
import { usePathname } from "next/navigation";
import { Clock, Calendar, Building2, Grid3X3, Layers } from "lucide-react";
>>>>>>> origin/nivish

export function NavigationShell() {
  const pathname = usePathname();

  return (
    <header className="border-b border-slate-800 bg-slate-900/70 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition">
            <Clock className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight text-white">CHRONON</span>
            <span className="ml-2 text-xs uppercase tracking-wider font-semibold px-2 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
              Deterministic
            </span>
          </div>
        </Link>

<<<<<<< HEAD
        <nav className="hidden md:flex items-center space-x-5 text-sm font-medium text-slate-400">
          <Link href="/academic-year" className="hover:text-slate-100 transition flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-blue-400" /> Academic Years
          </Link>
          <Link href="/academic" className="hover:text-slate-100 transition flex items-center gap-1.5">
            <BookOpen className="w-4 h-4 text-emerald-400" /> Curriculum & Ingestion
          </Link>
          <Link href="/resources" className="hover:text-slate-100 transition flex items-center gap-1.5">
            <Users className="w-4 h-4 text-amber-400" /> Resources
          </Link>
          <Link href="/generation" className="hover:text-slate-100 transition flex items-center gap-1.5">
            <Cpu className="w-4 h-4 text-purple-400" /> Orchestration
          </Link>
          <Link href="/versions" className="hover:text-slate-100 transition flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-cyan-400" /> Versions
          </Link>
          <Link href="/timetables" className="hover:text-slate-100 transition flex items-center gap-1.5">
            <Grid className="w-4 h-4 text-rose-400" /> Timetables
          </Link>
        </nav>

        <div className="flex items-center space-x-3">
          <div className="text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            Branch: <span className="font-mono text-emerald-400 font-bold">dev (integrated)</span>
=======
        <nav className="flex items-center space-x-2 sm:space-x-4 text-xs font-semibold">
          <Link
            href="/"
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
              pathname === "/" ? "bg-slate-800 text-white" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Calendar className="w-3.5 h-3.5 text-blue-400" />
            <span>Dashboard</span>
          </Link>

          <Link
            href="/resources"
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
              pathname === "/resources" ? "bg-blue-600 text-white shadow-md shadow-blue-600/20" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Building2 className="w-3.5 h-3.5" />
            <span>Physical Resources & Math</span>
          </Link>

          <Link
            href="/timetables"
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
              pathname === "/timetables" ? "bg-blue-600 text-white shadow-md shadow-blue-600/20" : "text-slate-400 hover:text-slate-200"
            }`}
          >
            <Grid3X3 className="w-3.5 h-3.5" />
            <span>Timetable Matrix Grid</span>
          </Link>
        </nav>

        <div className="hidden sm:flex items-center space-x-3">
          <div className="text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700 font-mono">
            Owner: <span className="text-amber-400 font-bold">nivish</span>
>>>>>>> origin/nivish
          </div>
        </div>
      </div>
    </header>
  );
}
