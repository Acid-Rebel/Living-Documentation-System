"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  Calendar,
  RefreshCw,
  Trash2,
  Download,
  X,
} from "lucide-react";

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
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lightboxImage, setLightboxImage] = useState<DiagramImage | null>(null);

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

  /* ================= HELPERS ================= */

  const groupedImages =
    selectedVersion?.images?.reduce((acc, img) => {
      acc[img.diagram_type] = acc[img.diagram_type] || [];
      acc[img.diagram_type].push(img);
      return acc;
    }, {} as Record<string, DiagramImage[]>) || {};

  /* ================= UI ================= */

  if (loading)
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        Loading...
      </div>
    );

  if (!project) return null;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      {/* ================= HEADER ================= */}
      <header className="sticky top-0 z-30 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 md:px-8 py-4 flex flex-wrap gap-3 justify-between items-center">
          {/* left */}
          <div className="flex items-center gap-3 min-w-0">
            <button
              onClick={() => router.push("/")}
              className="p-2 rounded-lg hover:bg-slate-100"
            >
              <ArrowLeft size={20} />
            </button>

            <div className="truncate">
              <h1 className="font-semibold text-slate-900 truncate">
                {project.name}
              </h1>
              <p className="text-xs text-blue-600 truncate">
                {project.repo_url}
              </p>
            </div>
          </div>

          {/* right */}
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => fetchProject(project.id)}
              className="px-3 md:px-4 py-2 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <RefreshCw size={14} />
              Sync
            </button>

            <button
              onClick={() => router.push("/")}
              className="px-3 md:px-4 py-2 text-sm bg-red-50 text-red-600 border border-red-200 rounded-lg hover:bg-red-100"
            >
              Delete
            </button>
          </div>
        </div>
      </header>

      {/* ================= CONTENT ================= */}
      {/* stack on mobile, row on desktop */}
      <main className="flex-1 max-w-7xl mx-auto w-full flex flex-col lg:flex-row gap-4 md:gap-6 p-4 md:p-8 overflow-hidden">
        {/* ================= SIDEBAR ================= */}
        <aside
          className="
          w-full lg:w-72
          bg-white rounded-xl border border-slate-200 shadow-sm
          max-h-64 lg:max-h-none
          overflow-y-auto
        "
        >
          <div className="p-3 font-semibold text-slate-700 flex items-center gap-2 border-b bg-slate-50">
            <Calendar size={14} />
            History
          </div>

          <div className="p-2 space-y-2">
            {project.diagrams.map((v) => (
              <div
                key={v.id}
                onClick={() => setSelectedVersion(v)}
                className={`p-2 rounded-lg cursor-pointer text-sm
                ${
                  selectedVersion?.id === v.id
                    ? "bg-blue-50 border border-blue-200"
                    : "hover:bg-slate-50"
                }`}
              >
                <p className="font-mono text-xs text-slate-500">
                  {v.commit_hash.slice(0, 7)}
                </p>
                <p className="truncate">{v.commit_message || "No message"}</p>
              </div>
            ))}
          </div>
        </aside>

        {/* ================= GALLERY ================= */}
        <section className="flex-1 overflow-y-auto space-y-8">
          {Object.entries(groupedImages).map(([type, imgs]) => (
            <div key={type}>
              <h3 className="text-base md:text-lg font-semibold mb-4 text-slate-900">
                {type}
              </h3>

              {/* responsive grid */}
              <div
                className="
                grid gap-4 md:gap-6
                grid-cols-1
                sm:grid-cols-2
                lg:grid-cols-3
                xl:grid-cols-4
              "
              >
                {imgs.map((img) => (
                  <div
                    key={img.id}
                    onClick={() => setLightboxImage(img)}
                    className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md hover:-translate-y-1 transition cursor-pointer overflow-hidden"
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
      </main>

      {/* ================= LIGHTBOX ================= */}
      {lightboxImage && (
        <div
          className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4"
          onClick={() => setLightboxImage(null)}
        >
          <div className="relative max-w-full max-h-full">
            <button
              className="absolute top-2 right-2 bg-black/50 text-white p-2 rounded"
              onClick={() => setLightboxImage(null)}
            >
              <X size={18} />
            </button>

            <img
              src={lightboxImage.image_file}
              className="max-w-[95vw] max-h-[85vh] rounded-xl bg-white shadow-xl"
            />
          </div>
        </div>
      )}
    </div>
  );
}
