"use client";

import React from "react";
import Link from "next/link";
import { Clock, Calendar, BookOpen, Users, Cpu, FileText } from "lucide-react";

export function NavigationShell() {
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
              Deterministic Scheduler
            </span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center space-x-6 text-sm font-medium text-slate-400">
          <Link href="/" className="hover:text-slate-200 transition flex items-center gap-1.5">
            <Calendar className="w-4 h-4 text-blue-400" /> Dashboard
          </Link>
          <Link href="/academic" className="text-emerald-400 hover:text-emerald-300 transition flex items-center gap-1.5">
            <BookOpen className="w-4 h-4" /> Academic & Ingestion Hub
          </Link>
          <span className="hover:text-slate-200 transition flex items-center gap-1.5 cursor-pointer">
            <Users className="w-4 h-4" /> Resources
          </span>
          <span className="hover:text-slate-200 transition flex items-center gap-1.5 cursor-pointer">
            <Cpu className="w-4 h-4" /> CP-SAT Solver
          </span>
          <span className="hover:text-slate-200 transition flex items-center gap-1.5 cursor-pointer">
            <FileText className="w-4 h-4" /> Versions
          </span>
        </nav>

        <div className="flex items-center space-x-3">
          <div className="text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            Branch: <span className="font-mono text-emerald-400">ujwal</span>
          </div>
        </div>
      </div>
    </header>
  );
}

