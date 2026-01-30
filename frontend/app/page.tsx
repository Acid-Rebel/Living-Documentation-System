"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { Plus, Trash2, RefreshCw } from "lucide-react";

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
            if (res.ok) {
                const data = await res.json();
                setProjects(data);
            }
        } catch (error) {
            console.error("Failed to fetch projects", error);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteProject = async (e: React.MouseEvent, id: string) => {
        e.preventDefault(); // Prevent navigation
        if (!confirm("Are you sure you want to delete this project?")) return;

        try {
            const res = await fetch(`http://localhost:8000/api/projects/${id}/`, {
                method: "DELETE",
            });
            if (res.ok) {
                setProjects(projects.filter(p => p.id !== id));
            } else {
                alert("Failed to delete project");
            }
        } catch (error) {
            alert("Error deleting project");
        }
    };

    const handleCreateProject = async (e: React.FormEvent) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            const res = await fetch("http://localhost:8000/api/projects/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: newProjectName,
                    repo_url: newRepoUrl
                })
            });
            if (res.ok) {
                setShowModal(false);
                setNewProjectName("");
                setNewRepoUrl("");
                fetchProjects();
            } else {
                alert("Failed to create project");
            }
        } catch (error) {
            alert("Error creating project");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <main className="w-full max-w-6xl flex flex-col items-center">
            <div className="w-full flex justify-between items-center mb-10">
                <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-600">
                    Dashboard
                </h1>
                <button
                    onClick={() => setShowModal(true)}
                    className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg text-white font-medium transition-all"
                >
                    <Plus size={20} />
                    Add Repository
                </button>
            </div>

            {loading ? (
                <div className="text-gray-400 animate-pulse">Loading projects...</div>
            ) : projects.length === 0 ? (
                <div className="text-center py-20 text-gray-500">
                    <p className="text-xl mb-4">No projects yet.</p>
                    <p>Add a repository to get started.</p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 w-full">
                    {projects.map((project) => (
                        <Link key={project.id} href={`/projects/${project.id}`} className="group relative">
                            <div className="bg-gray-900 border border-gray-800 rounded-xl p-6 hover:border-blue-500/50 hover:shadow-lg hover:shadow-blue-500/10 transition-all h-full flex flex-col">
                                <button
                                    onClick={(e) => handleDeleteProject(e, project.id)}
                                    className="absolute top-4 right-4 p-2 text-gray-500 hover:text-red-500 hover:bg-gray-800 rounded-lg transition-colors z-10"
                                    title="Delete Project"
                                >
                                    <Trash2 size={18} />
                                </button>
                                <div className="flex justify-between items-start mb-4 pr-10">
                                    <h3 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">
                                        {project.name}
                                    </h3>
                                </div>

                                <p className="text-sm text-gray-400 mb-6 truncate">
                                    {project.repo_url}
                                </p>

                                <div className="mt-auto pt-4 border-t border-gray-800">
                                    {project.latest_diagram ? (
                                        <div className="flex items-center gap-2 text-sm text-green-400">
                                            <div className="w-2 h-2 rounded-full bg-green-400"></div>
                                            <span>Latest: {project.latest_diagram.commit_hash.substring(0, 7)}</span>
                                        </div>
                                    ) : (
                                        <div className="flex items-center gap-2 text-sm text-yellow-500">
                                            <div className="w-2 h-2 rounded-full bg-yellow-500"></div>
                                            <span>No diagrams yet</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>
            )}

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-gray-900 p-8 rounded-2xl w-full max-w-md border border-gray-800 shadow-2xl">
                        <h2 className="text-2xl font-bold mb-6">Add New Repository</h2>
                        <form onSubmit={handleCreateProject} className="flex flex-col gap-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Project Name</label>
                                <input
                                    type="text"
                                    className="w-full bg-gray-800 border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    placeholder="e.g. My Backend API"
                                    value={newProjectName}
                                    onChange={(e) => setNewProjectName(e.target.value)}
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Repository URL</label>
                                <input
                                    type="url"
                                    className="w-full bg-gray-800 border-gray-700 rounded-lg p-3 text-white focus:ring-2 focus:ring-blue-500 outline-none"
                                    placeholder="https://github.com/..."
                                    value={newRepoUrl}
                                    onChange={(e) => setNewRepoUrl(e.target.value)}
                                    required
                                />
                            </div>
                            <div className="flex gap-3 mt-4">
                                <button
                                    type="button"
                                    onClick={() => setShowModal(false)}
                                    className="flex-1 p-3 rounded-lg bg-gray-800 hover:bg-gray-700 font-medium transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    type="submit"
                                    disabled={submitting}
                                    className="flex-1 p-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors disabled:opacity-50"
                                >
                                    {submitting ? "Adding..." : "Add Project"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </main>
    );
}
