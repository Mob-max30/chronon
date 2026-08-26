import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Chronon | Deterministic Timetable Generation System",
  description: "High-performance academic scheduling platform for VTU and autonomous engineering colleges using Google OR-Tools CP-SAT.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col selection:bg-blue-500/30 selection:text-blue-200">
        {children}
      </body>
    </html>
  );
}
