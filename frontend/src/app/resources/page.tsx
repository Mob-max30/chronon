"use client";

import React, { useState } from "react";
import { NavigationShell } from "@/components/NavigationShell";
import { RoomManager } from "@/components/resources/RoomManager";
import { LabManager } from "@/components/resources/LabManager";
import { LabSubjectMappingCard } from "@/components/resources/LabSubjectMappingCard";
import { SectionCalculator } from "@/components/resources/SectionCalculator";
import { BatchCalculator } from "@/components/resources/BatchCalculator";
import { TimeSlotConfigurator } from "@/components/resources/TimeSlotConfigurator";
import { Building2, FlaskConical, Share2, Calculator, Divide, Clock } from "lucide-react";

export default function ResourcesPage() {
  const [activeTab, setActiveTab] = useState<string>("rooms");

  const tabs = [
    { id: "rooms", label: "Classrooms & Capacities", icon: Building2 },
    { id: "labs", label: "Physical Laboratories", icon: FlaskConical },
    { id: "mappings", label: "Academic Lab ⟷ Hardware Mappings", icon: Share2 },
    { id: "sections", label: "Section Calculator", icon: Calculator },
    { id: "batches", label: "Batch Partitioning ($C$)", icon: Divide },
    { id: "slots", label: "Master Time Slots & Intervals", icon: Clock },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      <NavigationShell />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Page Title */}
        <div className="space-y-1">
          <h1 className="text-3xl font-extrabold tracking-tight text-white">
            Physical Resources, Batching & Time Configuration
          </h1>
          <p className="text-sm text-slate-400 max-w-3xl">
            Domain ownership for classrooms, physical hardware spaces, deterministic section and batch calculations, and configurable time slot schedules.
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap items-center gap-2 p-1.5 bg-slate-950/80 rounded-2xl border border-slate-800/80 text-xs font-semibold">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2.5 rounded-xl flex items-center gap-2 transition ${
                  isActive
                    ? "bg-blue-600 text-white shadow-lg shadow-blue-600/25"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Active Tab Panel */}
        <div className="animate-in fade-in duration-200">
          {activeTab === "rooms" && <RoomManager />}
          {activeTab === "labs" && <LabManager />}
          {activeTab === "mappings" && <LabSubjectMappingCard />}
          {activeTab === "sections" && <SectionCalculator />}
          {activeTab === "batches" && <BatchCalculator />}
          {activeTab === "slots" && <TimeSlotConfigurator />}
        </div>
      </main>

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4">
          <p>© 2026 Chronon Project • Physical Resources & Deterministic Utilities Domain</p>
        </div>
      </footer>
    </div>
  );
}
