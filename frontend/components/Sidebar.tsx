"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  FileText,
  Briefcase,
  GitBranch,
  Layers,
  Sparkles,
  Settings,
  ShieldCheck,
  Cpu,
  Compass,
  Shield,
} from "lucide-react";

const navigationItems = [
  { name: "Dashboard", href: "/", icon: LayoutDashboard },
  { name: "Get Started", href: "/get-started", icon: Compass, tag: "Agent" },
  { name: "Resume", href: "/resume", icon: FileText, tag: "Phase 2" },
  { name: "Job Descriptions", href: "/job-descriptions", icon: Briefcase, tag: "Phase 2" },
  { name: "Projects", href: "/projects", icon: GitBranch, tag: "Phase 3" },
  { name: "Applications", href: "/applications", icon: Layers, tag: "Phase 2" },
  { name: "Analysis", href: "/analysis", icon: Sparkles, tag: "Phase 5" },
  { name: "Privacy Center", href: "/privacy", icon: Shield, tag: "Local" },
  { name: "Settings", href: "/settings", icon: Settings },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-64 border-r border-surface-border bg-surface flex flex-col shrink-0 h-screen sticky top-0 select-none">
      {/* Brand Header */}
      <div className="p-6 border-b border-surface-border flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center text-indigo-400">
          <Cpu className="w-5 h-5" />
        </div>
        <div>
          <h1 className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
            CAREERCREW
          </h1>
          <p className="text-[11px] text-slate-400 font-medium">Local AI Intelligence</p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className="px-3 py-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500">
          Platform
        </div>
        {navigationItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;

          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center justify-between px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-indigo-600/15 text-indigo-300 border border-indigo-500/30"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/40"
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? "text-indigo-400" : "text-slate-400"}`} />
                <span>{item.name}</span>
              </div>
              {item.tag && (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700/50">
                  {item.tag}
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Privacy Guarantee Footer */}
      <div className="p-4 m-3 rounded-lg bg-slate-900/60 border border-slate-800 text-xs">
        <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-1">
          <ShieldCheck className="w-4 h-4" />
          <span>Privacy Guaranteed</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Zero Cloud APIs. Resumes & code evidence never leave your local machine.
        </p>
      </div>
    </aside>
  );
}
