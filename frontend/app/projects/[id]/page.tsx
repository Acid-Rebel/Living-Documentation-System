"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Calendar,
  RefreshCw,
  Download,
  X,
  FileText,
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

  const [activeTab, setActiveTab] = useState<'diagrams' | 'readme' | 'summary'>('diagrams');
  const [loading, setLoading] = useState(true);
  const [isSyncing, setIsSyncing] = useState(false);
  const [lightboxImage, setLightboxImage] =
    useState<DiagramImage | null>(null);

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

  /* ================= LOADING ================= */

  if (loading)
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        Loading...
      </div>
    );

  if (!project) return null;

  /* ================= UI ================= */

  return (
    <div className="h-screen bg-slate-50 flex flex-col overflow-hidden">
      {/* ================= HEADER ================= */}
      <header className="flex-none bg-white border-b border-slate-200 z-50">
        <div className="max-w-[1600px] mx-auto px-4 md:px-6 py-3 flex justify-between items-center">
          <div className="flex items-center gap-3 min-w-0">
            <button onClick={() => router.push("/")} className="p-2 rounded-lg hover:bg-slate-100">
              <ArrowLeft size={20} />
            </button>
            <div className="truncate">
              <h1 className="font-semibold text-slate-800 truncate">{project.name}</h1>
              <p className="text-xs text-blue-600 truncate">{project.repo_url}</p>
            </div>
          </div>
          <button
            onClick={handleSync}
            disabled={isSyncing}
            className={`px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2 shadow-sm transition-all active:scale-95 ${isSyncing ? 'opacity-70 cursor-not-allowed' : ''}`}
          >
            <RefreshCw size={14} className={isSyncing ? "animate-spin" : ""} />
            <span className="hidden sm:inline">{isSyncing ? "Syncing..." : "Sync"}</span>
          </button>
        </div>
      </header>

      {/* ================= MAIN LAYOUT ================= */}
      <main className="flex-1 flex overflow-hidden max-w-[1600px] mx-auto w-full p-4 md:p-6 gap-6">

        {/* ================= SIDEBAR (History) ================= */}
        <aside className="hidden lg:flex flex-col w-72 flex-none bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b bg-slate-50/50 flex items-center justify-between">
            <div className="flex items-center gap-2 font-semibold text-slate-700">
              <Calendar size={16} className="text-slate-400" />
              History
            </div>
          </div>

          <div className="p-3 border-b">
            <button
              onClick={downloadApiSummary}
              className="w-full py-2.5 text-xs font-bold flex items-center justify-center gap-2 border border-blue-200 bg-blue-50 text-blue-700 rounded-xl hover:bg-blue-100 transition-colors"
            >
              <FileDown size={14} />
              Download API Doc
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin scrollbar-thumb-slate-200">
            {project.diagrams.map((v) => (
              <button
                key={v.id}
                onClick={() => setSelectedVersion(v)}
                className={`w-full text-left p-3 rounded-xl transition-all border
                  ${selectedVersion?.id === v.id
                    ? "bg-blue-50 border-blue-200 shadow-sm"
                    : "hover:bg-slate-50 border-transparent"}`}
              >
                <p className="font-mono text-[10px] text-blue-500 font-bold uppercase mb-1">
                  {v.commit_hash.slice(0, 7)}
                </p>
                <p className="text-sm font-medium text-slate-700 line-clamp-2 leading-snug">
                  {v.commit_message || "Automatic Web Update"}
                </p>
              </button>
            ))}
          </div>
        </aside>

        {/* ================= CONTENT AREA ================= */}
        <div className="flex-1 flex flex-col min-w-0 relative">

          {/* STICKY NAVIGATION PILL */}
          <div className="absolute top-4 left-0 right-0 z-30 flex justify-center pointer-events-none">
            <nav className="pointer-events-auto bg-white/80 backdrop-blur-md border border-slate-200 shadow-xl rounded-full p-1.5 flex items-center gap-1">
              {['diagrams', 'readme', 'summary'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab as any)}
                  className={`px-6 sm:px-10 py-2 text-sm font-bold rounded-full transition-all capitalize
                    ${activeTab === tab
                      ? "bg-blue-600 text-white shadow-lg shadow-blue-200"
                      : "text-slate-500 hover:bg-slate-100 hover:text-slate-800"}`}
                >
                  {tab}
                </button>
              ))}
            </nav>
          </div>

          {/* ===== SCROLLABLE CONTENT BODY ===== */}
          <div className="flex-1 overflow-y-auto pt-20 pb-10 px-1 scrollbar-hide">

            {activeTab === 'readme' && (
              <div className="bg-[#0d1117] p-6 md:p-10 rounded-3xl border border-slate-200 shadow-sm animate-in fade-in zoom-in-95 duration-300">
                <div className="markdown-body !max-w-none">
                  <ReactMarkdown>{selectedVersion?.readme_content || ""}</ReactMarkdown>
                </div>
              </div>
            )}

            {activeTab === 'summary' && (
              <div className="bg-[#0d1117] p-6 md:p-10 rounded-3xl border border-slate-800 shadow-2xl animate-in fade-in zoom-in-95 duration-300">
                <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-3">
                  <span className="w-2 h-8 bg-blue-500 rounded-full"></span>
                  Summary
                </h2>
                <div className="markdown-body !max-w-none prose-invert">
                  <ReactMarkdown>{selectedVersion?.summary_content || ""}</ReactMarkdown>
                </div>
              </div>
            )}

            {activeTab === 'diagrams' && (
              <div className="space-y-10 animate-in fade-in duration-300">
                {Object.entries(groupedImages).map(([type, imgs]) => (
                  <div key={type} className="space-y-4">
                    <h3 className="text-xl font-bold text-slate-800 px-2 flex items-center gap-2 capitalize">
                      {type}
                      <span className="text-xs font-normal text-slate-400 bg-slate-100 px-2 py-0.5 rounded-full">
                        {imgs.length}
                      </span>
                    </h3>
                    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
                      {imgs.map((img) => (
                        <div
                          key={img.id}
                          onClick={() => setLightboxImage(img)}
                          className="bg-white rounded-2xl border border-slate-200 shadow-sm hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-pointer overflow-hidden group"
                        >
                          <div className="aspect-video bg-slate-50 flex items-center justify-center p-6">
                            <img
                              src={img.image_file}
                              className="object-contain max-h-full drop-shadow-md group-hover:scale-110 transition-transform duration-500"
                            />
                          </div>
                          <div className="p-4 border-t bg-white flex justify-between items-center">
                            <span className="text-sm font-bold text-slate-600 truncate">{img.description}</span>
                            <div className="p-2 bg-slate-50 rounded-lg group-hover:bg-blue-50 group-hover:text-blue-600 transition-colors">
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
        </div>
      </main>

      {/* ================= LIGHTBOX ================= */}
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
