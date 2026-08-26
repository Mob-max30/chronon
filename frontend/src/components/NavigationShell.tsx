"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Clock, Calendar, BookOpen, Building2, Cpu, FileText, Grid3X3 } from "lucide-react";

export function NavigationShell() {
  const pathname = usePathname();

  const navItems = [
    { href: "/academic-year", label: "Academic Years", icon: Calendar, color: "text-blue-400" },
    { href: "/academic", label: "Curriculum & OCR", icon: BookOpen, color: "text-emerald-400" },
    { href: "/resources", label: "Resources", icon: Building2, color: "text-amber-400" },
    { href: "/generation", label: "Orchestration", icon: Cpu, color: "text-purple-400" },
    { href: "/versions", label: "Versions", icon: FileText, color: "text-cyan-400" },
    { href: "/timetables", label: "Matrix Grid", icon: Grid3X3, color: "text-rose-400" },
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-50">
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

        <nav className="hidden lg:flex items-center space-x-2 text-xs font-semibold">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname.startsWith(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition ${
                  isActive
                    ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${item.color}`} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="flex items-center space-x-3">
          <div className="text-xs text-slate-400 bg-slate-800/80 px-3 py-1.5 rounded-lg border border-slate-700">
            Branch: <span className="font-mono text-emerald-400 font-bold">dev (integrated)</span>
          </div>
        </div>
      </div>
    </header>
  );
}
