"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, Trash2 } from "lucide-react";

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
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-8 py-5 flex justify-between items-center">
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">
            Projects
          </h1>

          <button
            onClick={() => setShowModal(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl text-sm font-medium shadow-sm transition"
          >
            <Plus size={18} />
            Add Repository
          </button>
        </div>
      </header>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-8 py-10">
        {loading ? (
          <div className="animate-pulse text-slate-400">
            Loading projects...
          </div>
        ) : projects.length === 0 ? (
          <div className="bg-white border border-slate-200 rounded-2xl p-14 text-center shadow-sm">
            <p className="text-lg text-slate-600 mb-2">No projects yet</p>
            <p className="text-sm text-slate-400">
              Add your first repository to generate diagrams
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-7">
            {projects.map((project) => (
              <Link
                key={project.id}
                href={`/projects/${project.id}`}
                className="group"
              >
                <div className="relative bg-white border border-slate-200 rounded-2xl p-6 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all flex flex-col h-full">
                  {/* Delete */}
                  <button
                    onClick={(e) => handleDeleteProject(e, project.id)}
                    className="absolute top-4 right-4 p-2 text-slate-400 hover:text-red-500 rounded-lg"
                  >
                    <Trash2 size={18} />
                  </button>

                  {/* Title */}
                  <h3 className="text-lg font-semibold text-slate-900 mb-2 group-hover:text-blue-600">
                    {project.name}
                  </h3>

                  {/* Repo */}
                  <p className="text-sm text-slate-500 truncate mb-6">
                    {project.repo_url}
                  </p>

                  {/* Status */}
                  <div className="mt-auto pt-4 border-t border-slate-100 text-sm">
                    {project.latest_diagram ? (
                      <span className="text-emerald-600 flex items-center gap-2">
                        ● Commit {project.latest_diagram.commit_hash.slice(0, 7)}
                      </span>
                    ) : (
                      <span className="text-amber-500 flex items-center gap-2">
                        ● No diagrams yet
                      </span>
                    )}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl shadow-xl border border-slate-200 w-full max-w-md p-7">
            <h2 className="text-xl font-semibold mb-6">Add Repository</h2>

            <form onSubmit={handleCreateProject} className="space-y-4">
              <input
                placeholder="Project name"
                className="w-full p-3 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={newProjectName}
                onChange={(e) => setNewProjectName(e.target.value)}
                required
              />

              <input
                placeholder="https://github.com/..."
                className="w-full p-3 bg-slate-50 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                value={newRepoUrl}
                onChange={(e) => setNewRepoUrl(e.target.value)}
                required
              />

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="flex-1 bg-slate-100 rounded-lg py-2 hover:bg-slate-200"
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
