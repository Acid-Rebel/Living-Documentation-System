"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  RefreshCw,
  Download,
  Calendar,
  ShieldAlert,
  Network,
  Layers,
  SlidersHorizontal,
  Activity,
  GitBranch,
  BookOpen,
  GitCommit,
  FileDown,
} from "lucide-react";
import ReactMarkdown from 'react-markdown';
import 'github-markdown-css/github-markdown.css';

/* ================= TYPES ================= */

interface DiagramImage {
  id: number;
  image_file: string;
  diagram_type: string;
  description: string;
}

interface DiagramVersion {
  id: number;
  commit_hash: string;
  commit_message: string;
  image_file: string;
  readme_content?: string;
  summary_content?: string;
  created_at: string;
  images?: DiagramImage[];
}

interface Project {
  id: string;
  name: string;
  repo_url: string;
  diagrams: DiagramVersion[];
}

/* ================= COMPONENT ================= */

export default function ProjectDetail() {
  const params = useParams();
  const router = useRouter();

  const [project, setProject] = useState<Project | null>(null);
  const [selectedVersion, setSelectedVersion] =
    useState<DiagramVersion | null>(null);

  const [activeView, setActiveView] = useState<"code" | "graph" | "report">("graph");
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lightboxImage, setLightboxImage] =
    useState<DiagramImage | null>(null);
  const [openViolationId, setOpenViolationId] = useState<string | null>(null);
  const [compareIndex, setCompareIndex] = useState(0);

  /* ================= FETCH ================= */

  useEffect(() => {
    if (!params.id) return;
    fetchProject(params.id as string);
  }, [params.id]);

  const fetchProject = async (id: string) => {
    const res = await fetch(`http://localhost:8000/api/projects/${id}/`);
    const data = await res.json();

    setProject(data);

    if (!selectedVersion && data.diagrams.length > 0) {
      setSelectedVersion(data.diagrams[0]);
    }

    if (data.diagrams.length > 0) {
      setCompareIndex(0);
    }

    setLoading(false);
  };

  const handleSync = async () => {
    if (!project || isSyncing) return;
    setIsSyncing(true);
    try {
      const res = await fetch(`http://localhost:8000/api/projects/${project.id}/refresh/`, {
        method: 'POST',
      });
      if (res.ok) {
        // Re-fetch project to get new data
        await fetchProject(project.id);
      } else {
        const err = await res.json();
        alert(`Sync failed: ${err.error || 'Unknown error'}`);
      }
    } catch (e) {
      console.error("Sync error:", e);
      alert("Sync failed. See console.");
    } finally {
      setIsSyncing(false);
    }
  };

  const downloadApiSummary = async () => {
    if (!project) return;
    try {
      // Show some loading indicator if needed (using global loading or toast)
      // For now we just await.
      const res = await fetch(`http://localhost:8000/api/projects/${project.id}/api_summary/`);
      if (res.ok) {
        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${project.name}_api_summary.pdf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
      } else {
        console.error("Failed to download PDF");
        alert("Failed to generate PDF. Check backend logs.");
      }
    } catch (e) {
      console.error(e);
      alert("Error downloading PDF");
    }
  };

  /* ================= GROUP IMAGES ================= */

  const groupedImages =
    selectedVersion?.images?.reduce((acc, img) => {
      acc[img.diagram_type] = acc[img.diagram_type] || [];
      acc[img.diagram_type].push(img);
      return acc;
    }, {} as Record<string, DiagramImage[]>) || {};

  const healthScore = 82;

  const violations = [
    {
      id: "SR-102",
      severity: "HIGH",
      component: "api_gateway",
      expected: "No direct dependency on firmware adapters",
      actual: "Imports firmware_adapter",
      explanation: "Gateway now couples to a firmware adapter, bypassing the integration boundary.",
      suggestedFix: "Route through integration-service and move adapter usage to the edge layer.",
    },
    {
      id: "DR-207",
      severity: "MEDIUM",
      component: "graph_builder",
      expected: "No cycles in analyzer pipeline",
      actual: "Cycle detected between analyzer_manager and parser_manager",
      explanation: "Analyzer depends on parser output while parser imports analyzer utils.",
      suggestedFix: "Extract shared helpers into a neutral core module.",
    },
    {
      id: "SR-311",
      severity: "LOW",
      component: "diagram_renderer",
      expected: "SVG export only",
      actual: "PNG export introduced",
      explanation: "PNG output not registered in ontology metadata.",
      suggestedFix: "Update ontology registry or revert PNG output.",
    },
  ];

  const severityStyles: Record<string, { badge: string; dot: string }> = {
    CRITICAL: { badge: "bg-red-600 text-white", dot: "bg-red-500" },
    HIGH: { badge: "bg-amber-500 text-white", dot: "bg-amber-400" },
    MEDIUM: { badge: "bg-sky-500 text-white", dot: "bg-sky-400" },
    LOW: { badge: "bg-emerald-500 text-white", dot: "bg-emerald-400" },
  };

  const heatmap = [
    "bg-emerald-400",
    "bg-sky-400",
    "bg-amber-400",
    "bg-emerald-400",
    "bg-slate-200",
    "bg-sky-400",
    "bg-amber-400",
    "bg-red-500",
    "bg-slate-200",
    "bg-emerald-400",
    "bg-amber-400",
    "bg-sky-400",
  ];

  const latestVersion = project?.diagrams?.[0];
  const compareVersion = project?.diagrams?.[compareIndex];

  /* ================= LOADING ================= */

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-500 dark:text-slate-400">
        Loading...
      </div>
    );

  if (!project) return null;

  /* ================= UI ================= */

  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex-none bg-white/80 dark:bg-slate-950/80 border-b border-slate-200/70 dark:border-slate-800 z-40">
        <div className="max-w-[1600px] mx-auto px-4 md:px-6 py-3 flex flex-wrap gap-3 justify-between items-center">
          <div className="flex items-center gap-3 min-w-0">
            <button onClick={() => router.push("/")} className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-900">
              <ArrowLeft size={20} />
            </button>
            <div className="truncate">
              <p className="mono-caption text-slate-400">Project</p>
              <h1 className="font-semibold text-slate-800 dark:text-white truncate">{project.name}</h1>
              <p className="text-xs text-blue-600 truncate">{project.repo_url}</p>
            </div>
          </div>
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className={`px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 shadow-sm transition-all active:scale-95 ${isSyncing ? "opacity-70 cursor-not-allowed" : ""}`}
          >
            <RefreshCw size={14} className={isSyncing ? "animate-spin" : ""} />
            <span className="hidden sm:inline">{isSyncing ? "Syncing..." : "Sync"}</span>
          </button>
        </div>
      </header>

      <main className="flex-1 grid grid-cols-1 xl:grid-cols-[260px_minmax(0,1fr)_320px] gap-6 max-w-[1600px] mx-auto w-full px-4 md:px-6 py-6">
        <aside className="hidden xl:flex flex-col gap-4">
          <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 overflow-hidden">
            <div className="p-4 border-b border-slate-200/70 dark:border-slate-800">
              <p className="mono-caption text-slate-400">Navigation</p>
              <div className="mt-3 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                {[
                  { label: "Project Overview", icon: BookOpen },
                  { label: "Architecture View", icon: Layers },
                  { label: "Drift Analysis", icon: ShieldAlert },
                  { label: "Validation Reports", icon: Activity },
                  { label: "Knowledge Graph Explorer", icon: Network },
                  { label: "Settings", icon: SlidersHorizontal },
                ].map((item) => (
                  <div key={item.label} className="flex items-center gap-2 rounded-xl px-3 py-2 hover:bg-slate-100 dark:hover:bg-slate-800">
                    <item.icon size={14} className="text-slate-400" />
                    {item.label}
                  </div>
                ))}
              </div>
            </div>
            <div className="p-4 border-b border-slate-200/70 dark:border-slate-800">
              <button
                onClick={downloadApiSummary}
                className="w-full py-2.5 text-xs font-bold flex items-center justify-center gap-2 border border-blue-200/70 dark:border-sky-900 bg-blue-50/70 dark:bg-slate-900 text-blue-700 dark:text-sky-300 rounded-xl hover:bg-blue-100 dark:hover:bg-slate-800 transition-colors"
              >
                <FileDown size={14} />
                Download API Doc
              </button>
            </div>
            <div className="p-4">
              <div className="flex items-center gap-2 font-semibold text-slate-700 dark:text-slate-200">
                <Calendar size={16} className="text-slate-400" />
                History
              </div>
              <div className="mt-3 space-y-2 max-h-[360px] overflow-y-auto pr-1">
                {project.diagrams.map((v) => (
                  <button
                    key={v.id}
                    onClick={() => setSelectedVersion(v)}
                    className={`w-full text-left p-3 rounded-xl transition-all border
                      ${selectedVersion?.id === v.id
                        ? "bg-blue-50 dark:bg-slate-800 border-blue-200 dark:border-slate-700 shadow-sm"
                        : "hover:bg-slate-50 dark:hover:bg-slate-800 border-transparent"}`}
                  >
                    <p className="font-mono text-[10px] text-blue-500 font-bold uppercase mb-1">
                      {v.commit_hash.slice(0, 7)}
                    </p>
                    <p className="text-sm font-medium text-slate-700 dark:text-slate-200 line-clamp-2 leading-snug">
                      {v.commit_message || "Automatic Web Update"}
                    </p>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </aside>

        <section className="flex flex-col min-w-0">
          <div className="sticky top-4 z-20 flex justify-center">
            <nav className="bg-white/80 dark:bg-slate-900/80 backdrop-blur-md border border-slate-200/70 dark:border-slate-800 shadow-xl rounded-full p-1.5 flex items-center gap-1">
              {[
                { id: "code", label: "Code" },
                { id: "graph", label: "Graph" },
                { id: "report", label: "Report" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveView(tab.id as "code" | "graph" | "report")}
                  className={`px-6 sm:px-10 py-2 text-sm font-bold rounded-full transition-all capitalize
                    ${activeView === tab.id
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-200"
                      : "text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-white"}`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="flex-1 overflow-y-auto pt-16 pb-10 px-1">
            {activeView === "code" && (
              <div className="grid gap-6 lg:grid-cols-[2fr_1fr] animate-in fade-in duration-300">
                <div className="bg-slate-950 p-6 md:p-10 rounded-3xl border border-slate-800 shadow-2xl">
                  <div className="markdown-body !max-w-none prose-invert">
                    <ReactMarkdown>{selectedVersion?.readme_content || ""}</ReactMarkdown>
                  </div>
                </div>
                <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6 space-y-4">
                  <div className="flex items-center gap-2 text-slate-700 dark:text-slate-200">
                    <BookOpen size={16} />
                    <span className="font-semibold">Quick Summary</span>
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400 space-y-3">
                    <p>Latest commit: <span className="font-semibold text-slate-900 dark:text-white">{selectedVersion?.commit_hash?.slice(0, 7)}</span></p>
                    <p>Artifacts: {selectedVersion?.images?.length || 0} diagrams</p>
                    <p>Documentation coverage estimated at 78%.</p>
                  </div>
                  <div className="border-t border-slate-200/70 dark:border-slate-800 pt-4">
                    <p className="mono-caption text-slate-400">Extracted Highlights</p>
                    <div className="mt-3 text-xs text-slate-500 dark:text-slate-400 space-y-2">
                      <div className="flex items-center gap-2">
                        <GitBranch size={12} />
                        Service boundaries aligned across 4 core modules.
                      </div>
                      <div className="flex items-center gap-2">
                        <Activity size={12} />
                        Analyzer throughput stable at 12k LOC/min.
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeView === "report" && (
              <div className="space-y-6 animate-in fade-in duration-300">
                <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="mono-caption text-slate-400">Executive Summary</p>
                      <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Architecture Impact</h2>
                    </div>
                    <span className="text-xs text-slate-500 dark:text-slate-400">Risk rating: Medium</span>
                  </div>
                  <div className="mt-4 text-sm text-slate-600 dark:text-slate-300">
                    <ReactMarkdown>{selectedVersion?.summary_content || "No summary available."}</ReactMarkdown>
                  </div>
                </div>
                <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="mono-caption text-slate-400">Validation Report</p>
                      <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Drift Overview</h2>
                    </div>
                    <div className="text-xs text-slate-500 dark:text-slate-400">Last sync: {selectedVersion?.created_at?.slice(0, 10)}</div>
                  </div>
                  <div className="mt-4 overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead className="text-slate-500 dark:text-slate-400">
                        <tr>
                          <th className="py-2">Rule</th>
                          <th className="py-2">Severity</th>
                          <th className="py-2">Component</th>
                          <th className="py-2">Expected</th>
                          <th className="py-2">Actual</th>
                        </tr>
                      </thead>
                      <tbody className="text-slate-700 dark:text-slate-200">
                        {violations.map((v) => (
                          <tr key={v.id} className="border-t border-slate-200/70 dark:border-slate-800">
                            <td className="py-3 font-mono text-xs text-slate-500">{v.id}</td>
                            <td className="py-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-semibold ${severityStyles[v.severity].badge}`}>
                                {v.severity}
                              </span>
                            </td>
                            <td className="py-3 font-semibold">{v.component}</td>
                            <td className="py-3 text-slate-500 dark:text-slate-400">{v.expected}</td>
                            <td className="py-3 text-slate-500 dark:text-slate-400">{v.actual}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6">
                  <div className="flex items-center gap-2 text-slate-800 dark:text-white">
                    <ShieldAlert size={16} />
                    <h3 className="text-lg font-semibold">Explain This Drift</h3>
                  </div>
                  <p className="text-sm text-slate-500 dark:text-slate-400 mt-2">
                    Click a violation to see contextual explanations, affected ontology nodes, and suggested fixes.
                  </p>
                  <div className="mt-4 space-y-3">
                    {violations.map((v) => (
                      <div key={v.id} className="rounded-2xl border border-slate-200/70 dark:border-slate-800 p-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                          <div className="flex items-center gap-2">
                            <span className={`h-2.5 w-2.5 rounded-full ${severityStyles[v.severity].dot}`} />
                            <span className="text-sm font-semibold text-slate-800 dark:text-white">{v.component}</span>
                            <span className="font-mono text-xs text-slate-500">{v.id}</span>
                          </div>
                          <button
                            onClick={() => setOpenViolationId(openViolationId === v.id ? null : v.id)}
                            className="text-xs font-semibold text-blue-600 hover:text-blue-700"
                          >
                            {openViolationId === v.id ? "Hide explanation" : "Explain this drift"}
                          </button>
                        </div>
                        {openViolationId === v.id && (
                          <div className="mt-3 grid gap-3 text-sm text-slate-600 dark:text-slate-400">
                            <div><span className="font-semibold text-slate-800 dark:text-white">Context:</span> {v.explanation}</div>
                            <div><span className="font-semibold text-slate-800 dark:text-white">Ontology nodes:</span> boundary.integration, adapter.firmware, service.gateway</div>
                            <div><span className="font-semibold text-slate-800 dark:text-white">Before/After:</span> integration_service -> adapter (before) vs gateway -> adapter (after)</div>
                            <div><span className="font-semibold text-slate-800 dark:text-white">Suggested fix:</span> {v.suggestedFix}</div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeView === "graph" && (
              <div className="space-y-10 animate-in fade-in duration-300">
                {Object.entries(groupedImages).map(([type, imgs]) => (
                  <div key={type} className="space-y-4">
                    <h3 className="text-xl font-bold text-slate-800 dark:text-white px-2 flex items-center gap-2 capitalize">
                      {type}
                      <span className="text-xs font-normal text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-0.5 rounded-full">
                        {imgs.length}
                      </span>
                    </h3>
                    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                      {imgs.map((img) => (
                        <div
                          key={img.id}
                          onClick={() => setLightboxImage(img)}
                          className="bg-white/80 dark:bg-slate-900/80 rounded-2xl border border-slate-200/70 dark:border-slate-800 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer overflow-hidden group"
                        >
                          <div className="aspect-video bg-slate-50 dark:bg-slate-950 flex items-center justify-center p-6">
                            <img
                              src={img.image_file}
                              className="object-contain max-h-full drop-shadow-md group-hover:scale-110 transition-transform duration-500"
                            />
                          </div>
                          <div className="p-4 border-t border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 flex justify-between items-center">
                            <span className="text-sm font-bold text-slate-600 dark:text-slate-300 truncate">{img.description}</span>
                            <div className="p-2 bg-slate-50 dark:bg-slate-800 rounded-lg group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
                              <Download size={14} />
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </section>

        <aside className="hidden lg:flex flex-col gap-4">
          <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-5">
            <p className="mono-caption text-slate-400">Architecture Health</p>
            <div className="mt-3 flex items-center justify-between">
              <div>
                <p className="text-2xl font-semibold text-slate-900 dark:text-white">{healthScore}%</p>
                <p className="text-sm text-slate-500 dark:text-slate-400">Weighted drift score</p>
              </div>
              <div
                className="h-16 w-16 rounded-full"
                style={{
                  background: `conic-gradient(#38bdf8 ${healthScore * 3.6}deg, rgba(148, 163, 184, 0.25) 0deg)`,
                }}
              />
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-5">
            <p className="mono-caption text-slate-400">Drift Severity Heatmap</p>
            <div className="mt-4 grid grid-cols-6 gap-2">
              {heatmap.map((tone, index) => (
                <div key={`${tone}-${index}`} className={`h-6 rounded-lg ${tone} opacity-90`} />
              ))}
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-5">
            <p className="mono-caption text-slate-400">Knowledge Graph Preview</p>
            <div className="mt-4 h-28 rounded-2xl bg-slate-50 dark:bg-slate-950 border border-slate-200/70 dark:border-slate-800 flex items-center justify-center">
              <svg width="160" height="80" viewBox="0 0 160 80" fill="none">
                <circle cx="25" cy="40" r="8" fill="#38bdf8" />
                <circle cx="80" cy="20" r="6" fill="#a78bfa" />
                <circle cx="80" cy="60" r="6" fill="#fb7185" />
                <circle cx="135" cy="40" r="8" fill="#34d399" />
                <path d="M33 40L72 22M33 40L72 58M88 20L128 38M88 60L128 42" stroke="#94a3b8" strokeWidth="1.2" />
              </svg>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-5">
            <p className="mono-caption text-slate-400">Version Comparison</p>
            <div className="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2"><GitCommit size={14} />Baseline</span>
                <span className="font-mono text-xs text-slate-500">{latestVersion?.commit_hash?.slice(0, 7)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2"><GitBranch size={14} />Compare</span>
                <span className="font-mono text-xs text-slate-500">{compareVersion?.commit_hash?.slice(0, 7)}</span>
              </div>
              <input
                type="range"
                min={0}
                max={Math.max(project.diagrams.length - 1, 0)}
                value={compareIndex}
                onChange={(e) => setCompareIndex(Number(e.target.value))}
                className="w-full accent-sky-400"
              />
              <p className="text-xs text-slate-500">Slide to compare architecture drift over time.</p>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-5">
            <p className="mono-caption text-slate-400">Context Panel</p>
            <div className="mt-3 space-y-3 text-sm text-slate-600 dark:text-slate-300">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2"><BookOpen size={14} />Docs</span>
                <span>{selectedVersion?.readme_content ? "Ready" : "Missing"}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2"><Activity size={14} />Drift Status</span>
                <span className="text-amber-500">3 active</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-2"><Network size={14} />Ontology</span>
                <span className="text-emerald-500">Aligned</span>
              </div>
            </div>
          </div>
        </aside>
      </main>

      {lightboxImage && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setLightboxImage(null)}
        >
          <img
            src={lightboxImage.image_file}
            className="max-w-[95vw] max-h-[85vh] rounded-xl bg-white shadow-xl"
          />
        </div>
      )}
    </div>
  );
}
