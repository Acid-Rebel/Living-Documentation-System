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

  const [showReadme, setShowReadme] = useState(false);
  const [loading, setLoading] = useState(true);
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
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* ================= HEADER ================= */}
      <header className="sticky top-0 z-30 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => router.push("/")}
              className="p-2 rounded-lg hover:bg-slate-100"
            >
              <ArrowLeft size={20} />
            </button>

            <div className="truncate">
              <h1 className="font-semibold truncate">{project.name}</h1>
              <p className="text-xs text-blue-600 truncate">
                {project.repo_url}
              </p>
            </div>
          </div>

          <button
            onClick={() => fetchProject(project.id)}
            className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
          >
            <RefreshCw size={14} />
            Sync
          </button>
        </div>
      </header>

      {/* ================= CONTENT ================= */}
      <main className="flex-1 max-w-7xl mx-auto w-full flex flex-col lg:flex-row gap-6 p-4 md:p-8 overflow-hidden">
        {/* ================= SIDEBAR ================= */}
        <aside className="w-full lg:w-72 bg-white rounded-xl border shadow-sm overflow-y-auto">
          {/* ===== Sidebar Header ===== */}
          <div className="p-3 border-b bg-slate-50 flex items-center justify-between">
            <div className="flex items-center gap-2 font-semibold text-slate-700">
              <Calendar size={14} />
              History
            </div>

            {/* 🔥 SWITCH TOGGLE */}
            <div className="flex items-center gap-2 select-none">
              <span
                className={`text-xs font-medium transition-colors ${!showReadme ? "text-indigo-600" : "text-slate-400"
                  }`}
              >
                Diagrams
              </span>

              <button
                onClick={() => setShowReadme(!showReadme)}
                className={`relative w-11 h-6 rounded-full transition-all duration-300
                  ${showReadme ? "bg-indigo-600" : "bg-slate-300"}`}
              >
                <span
                  className={`absolute top-0.5 left-0.5 h-5 w-5 bg-white rounded-full shadow-md
                    transition-transform duration-300
                    ${showReadme ? "translate-x-5" : ""}`}
                />
              </button>

              <span
                className={`text-xs font-medium transition-colors ${showReadme ? "text-indigo-600" : "text-slate-400"
                  }`}
              >
                Readme
              </span>
            </div>
          </div>

          {/* ===== Actions ===== */}
          <div className="p-3 border-b bg-slate-50">
            <button
              onClick={downloadApiSummary}
              className="w-full py-2 text-xs font-medium flex items-center justify-center gap-2 border border-blue-200 bg-blue-50 text-blue-700 rounded hover:bg-blue-100 transition-colors"
              title="Generate and Download API Documentation PDF"
            >
              <FileDown size={14} />
              Download API Summary
            </button>
          </div>

          {/* ===== Versions List ===== */}
          <div className="p-2 space-y-2">
            {project.diagrams.map((v) => (
              <div
                key={v.id}
                onClick={() => setSelectedVersion(v)}
                className={`p-2 rounded-lg cursor-pointer text-sm
                  ${selectedVersion?.id === v.id
                    ? "bg-blue-50 border border-blue-200"
                    : "hover:bg-slate-50"
                  }`}
              >
                <p className="font-mono text-xs text-slate-500">
                  {v.commit_hash.slice(0, 7)}
                </p>
                <p className="truncate">
                  {v.commit_message || "No message"}
                </p>
              </div>
            ))}
          </div>
        </aside>

        {/* ================= MAIN VIEW ================= */}
        {showReadme ? (
          /* ===== README VIEW ===== */
          <section className="flex-1 overflow-y-auto bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            {selectedVersion?.readme_content ? (
              <div className="markdown-body">
                <ReactMarkdown>{selectedVersion.readme_content}</ReactMarkdown>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full text-slate-500 min-h-[300px]">
                <FileText size={48} className="mb-4 opacity-20" />
                <p className="font-semibold text-lg text-slate-700">No Documentation Available</p>
                <p className="text-sm max-w-md text-center mt-2">
                  A README has not been generated for this version yet.
                  Trigger a new sync to generate one.
                </p>
              </div>
            )}
          </section>
        ) : (
          /* ===== DIAGRAM VIEW ===== */
          <section className="flex-1 overflow-y-auto space-y-8">
            {Object.entries(groupedImages).map(([type, imgs]) => (
              <div key={type}>
                <h3 className="font-semibold text-lg mb-4">{type}</h3>

                <div className="grid gap-5 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
                  {imgs.map((img) => (
                    <div
                      key={img.id}
                      onClick={() => setLightboxImage(img)}
                      className="bg-white rounded-xl border shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer overflow-hidden"
                    >
                      <div className="aspect-video bg-slate-50 flex items-center justify-center">
                        <img
                          src={img.image_file}
                          className="object-contain p-3 max-h-full"
                        />
                      </div>

                      <div className="p-2 flex justify-between items-center border-t text-sm">
                        <span className="truncate">{img.description}</span>

                        <a
                          href={img.image_file}
                          download
                          onClick={(e) => e.stopPropagation()}
                          className="p-1.5 hover:bg-slate-100 rounded"
                        >
                          <Download size={14} />
                        </a>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </section>
        )}
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
