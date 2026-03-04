"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  Plus,
  Trash2,
  Sparkles,
  Radar,
  Activity,
  ShieldAlert,
  Network,
} from "lucide-react";

interface Project {
  id: string;
  name: string;
  repo_url: string;
  created_at: string;
  latest_diagram?: {
    image_file: string;
    created_at: string;
    commit_hash: string;
  };
}

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const [newRepoUrl, setNewRepoUrl] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const healthScore = 86;

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/projects/");
      if (res.ok) setProjects(await res.json());
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteProject = async (e: React.MouseEvent, id: string) => {
    e.preventDefault();
    if (!confirm("Delete this project?")) return;

    await fetch(`http://localhost:8000/api/projects/${id}/`, {
      method: "DELETE",
    });

    setProjects((prev) => prev.filter((p) => p.id !== id));
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);

    await fetch("http://localhost:8000/api/projects/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: newProjectName,
        repo_url: newRepoUrl,
      }),
    });

    setSubmitting(false);
    setShowModal(false);
    setNewProjectName("");
    setNewRepoUrl("");
    fetchProjects();
  };

  return (
    <div className="min-h-screen">
      <section className="relative overflow-hidden rounded-[32px] border border-slate-200/70 dark:border-slate-800 glass-panel bg-grid">
        <div className="relative px-6 py-10 md:px-10 lg:px-12">
          <div className="flex flex-col lg:flex-row gap-10">
            <div className="flex-1 space-y-6">
              <div className="inline-flex items-center gap-2 rounded-full border border-blue-200/70 dark:border-sky-900/70 bg-blue-50/70 dark:bg-slate-900/70 px-4 py-2 text-xs font-semibold text-blue-700 dark:text-sky-300">
                <Sparkles size={14} />
                Live architecture intelligence
              </div>
              <h1 className="text-3xl md:text-4xl font-semibold text-slate-900 dark:text-white leading-tight">
                Living Documentation System
              </h1>
              <p className="text-base md:text-lg text-slate-600 dark:text-slate-300 max-w-2xl">
                Track structural drift, visualize dependencies, and keep your architecture aligned with your intended design.
              </p>
              <div className="flex flex-wrap items-center gap-4">
                <button
                  onClick={() => setShowModal(true)}
                  className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-3 rounded-2xl text-sm font-semibold shadow-sm transition"
                >
                  <Plus size={18} />
                  Add Repository
                </button>
                <div className="flex items-center gap-3 text-sm text-slate-500 dark:text-slate-400">
                  <Radar size={16} />
                  Drift engine ready to run
                </div>
              </div>
            </div>

            <div className="w-full lg:w-[360px] space-y-4">
              <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-5">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="mono-caption text-slate-400">Architecture Health</p>
                    <p className="text-2xl font-semibold text-slate-900 dark:text-white">{healthScore}%</p>
                  </div>
                  <div
                    className="h-16 w-16 rounded-full"
                    style={{
                      background: `conic-gradient(#38bdf8 ${healthScore * 3.6}deg, rgba(148, 163, 184, 0.2) 0deg)`,
                    }}
                  >
                    <div className="h-16 w-16 rounded-full flex items-center justify-center bg-white dark:bg-slate-950 scale-75">
                      <Activity size={18} className="text-sky-500" />
                    </div>
                  </div>
                </div>
                <p className="text-sm text-slate-500 dark:text-slate-400 mt-4">
                  Weighted drift score trending down 4% over the last 7 days.
                </p>
              </div>
              <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-5">
                <p className="mono-caption text-slate-400">Live Modules</p>
                <div className="mt-4 space-y-3 text-sm text-slate-600 dark:text-slate-300">
                  <div className="flex items-center gap-3">
                    <ShieldAlert size={16} className="text-amber-500" />
                    Rule-based drift detection
                  </div>
                  <div className="flex items-center gap-3">
                    <Network size={16} className="text-emerald-500" />
                    Knowledge graph + ontology
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="mt-10 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {[
          {
            title: "Architecture View",
            desc: "Inspect diagrams, call flows, and dependency layers in one panel.",
            icon: <Radar size={18} className="text-sky-500" />,
          },
          {
            title: "Drift Analysis",
            desc: "Trace violations, explore root causes, and generate fixes.",
            icon: <ShieldAlert size={18} className="text-amber-500" />,
          },
          {
            title: "Validation Reports",
            desc: "Export markdown and HTML reports with action-ready findings.",
            icon: <Activity size={18} className="text-emerald-500" />,
          },
        ].map((item) => (
          <div
            key={item.title}
            className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6 transition hover:-translate-y-1 hover:shadow-lg"
          >
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-2xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center">
                {item.icon}
              </div>
              <h3 className="text-lg font-semibold text-slate-900 dark:text-white">
                {item.title}
              </h3>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400 mt-3">
              {item.desc}
            </p>
          </div>
        ))}
      </section>

      <section className="mt-12">
        <div className="flex items-center justify-between mb-6">
          <div>
            <p className="mono-caption text-slate-400">Workspace</p>
            <h2 className="text-2xl font-semibold text-slate-900 dark:text-white">Projects</h2>
          </div>
        </div>

        {loading ? (
          <div className="animate-pulse text-slate-400">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-14 text-center shadow-sm">
            <p className="text-lg text-slate-600 dark:text-slate-300 mb-2">No projects yet</p>
            <p className="text-sm text-slate-400">Add your first repository to generate diagrams</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-7">
            {projects.map((project) => (
              <Link key={project.id} href={`/projects/${project.id}`} className="group">
                <div className="relative rounded-3xl border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-6 shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all flex flex-col h-full">
                  <button
                    onClick={(e) => handleDeleteProject(e, project.id)}
                    className="absolute top-4 right-4 p-2 text-slate-400 hover:text-red-500 rounded-lg"
                  >
                    <Trash2 size={18} />
                  </button>

                  <p className="mono-caption text-slate-400">Repository</p>
                  <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-2 group-hover:text-blue-600">
                    {project.name}
                  </h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 truncate mb-6">
                    {project.repo_url}
                  </p>

                  <div className="mt-auto pt-4 border-t border-slate-100 dark:border-slate-800 text-sm">
                    {project.latest_diagram ? (
                      <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-2">
                        ● Commit {project.latest_diagram.commit_hash.slice(0, 7)}
                      </span>
                    ) : (
                      <span className="text-amber-500 flex items-center gap-2">● No diagrams yet</span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white dark:bg-slate-950 rounded-2xl shadow-xl border border-slate-200/70 dark:border-slate-800 w-full max-w-md p-7">
            <h2 className="text-xl font-semibold mb-6 text-slate-900 dark:text-white">Add Repository</h2>

            <form onSubmit={handleCreateProject} className="space-y-4">
              <input
                placeholder="Project name"
                className="w-full p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                required
              />

              <input
                placeholder="https://github.com/..."
                className="w-full p-3 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={newRepoUrl}
                onChange={(e) => setNewRepoUrl(e.target.value)}
                required
              />

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-slate-100 dark:bg-slate-900 rounded-lg py-2 hover:bg-slate-200 dark:hover:bg-slate-800"
                >
                  Cancel
                </button>

                <button
                  disabled={submitting}
                  className="flex-1 bg-blue-600 text-white rounded-lg py-2 hover:bg-blue-700 disabled:opacity-50"
                >
                  {submitting ? "Adding..." : "Add"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
