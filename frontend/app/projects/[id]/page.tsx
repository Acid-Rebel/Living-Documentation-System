"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, GitCommit, Calendar, Copy, Check, Trash2, RefreshCw, X, Maximize2 } from "lucide-react";

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
    author: string;
    image_file: string; // Keep as fallback main
    created_at: string;
    images?: DiagramImage[];
}

interface Project {
    id: string;
    name: string;
    repo_url: string;
    diagrams: DiagramVersion[];
}

export default function ProjectDetail() {
    const params = useParams();
    const router = useRouter();
    const [project, setProject] = useState<Project | null>(null);
    const [selectedVersion, setSelectedVersion] = useState<DiagramVersion | null>(null);
    const [loading, setLoading] = useState(true);
    const [copied, setCopied] = useState(false);
    const [refreshing, setRefreshing] = useState(false);
    const [lightboxImage, setLightboxImage] = useState<DiagramImage | null>(null);

    useEffect(() => {
        if (params.id) {
            fetchProject(params.id as string);
            const interval = setInterval(() => {
                fetchProject(params.id as string, true);
            }, 5000);
            return () => clearInterval(interval);
        }
    }, [params.id]);

    const fetchProject = async (id: string, isSilent = false) => {
        try {
            const res = await fetch(`http://localhost:8000/api/projects/${id}/`);
            if (res.ok) {
                const data = await res.json();
                setProject(data);

                // If it's the first load, set selection
                if (!isSilent && !selectedVersion && data.diagrams && data.diagrams.length > 0) {
                    setSelectedVersion(data.diagrams[0]);
                }
                // If silent and a new version has arrived (list length changed)
                // and we were looking at the 'old' latest, switch to 'new' latest
                else if (isSilent && data.diagrams && data.diagrams.length > (project?.diagrams.length || 0)) {
                    // Check if we were looking at the old top one
                    const wasLookingAtLatest = selectedVersion?.id === project?.diagrams[0]?.id;
                    if (wasLookingAtLatest || !selectedVersion) {
                        setSelectedVersion(data.diagrams[0]);
                    }
                }
                else if (isSilent && !selectedVersion && data.diagrams && data.diagrams.length > 0) {
                    setSelectedVersion(data.diagrams[0]);
                }
            } else if (!isSilent) {
                router.push("/");
            }
        } catch (error) {
            if (!isSilent) console.error("Failed to fetch project", error);
        } finally {
            if (!isSilent) setLoading(false);
        }
    };

    const handleRefresh = async () => {
        if (!project) return;
        setRefreshing(true);
        try {
            const res = await fetch(`http://localhost:8000/api/projects/${project.id}/refresh/`, {
                method: "POST"
            });
            if (res.ok) {
                const resP = await fetch(`http://localhost:8000/api/projects/${project.id}/`);
                if (resP.ok) {
                    const data = await resP.json();
                    setProject(data);
                    if (data.diagrams.length > 0) {
                        setSelectedVersion(data.diagrams[0]);
                    }
                }
            } else {
                alert("Refresh failed.");
            }
        } catch (error) {
            alert("Error refreshing project.");
        } finally {
            setRefreshing(false);
        }
    };

    const handleDelete = async () => {
        if (!project || !confirm("Delete this project?")) return;
        try {
            const res = await fetch(`http://localhost:8000/api/projects/${project.id}/`, {
                method: "DELETE"
            });
            if (res.ok) router.push("/");
        } catch (e) { alert("Delete failed"); }
    };

    const [showWebhookModal, setShowWebhookModal] = useState(false);
    const [webhookTab, setWebhookTab] = useState<'github' | 'hook'>('github');

    const getGithubConfig = () => `
# In your GitHub Action:
- name: Trigger Diagram Update
  run: |
    curl -X POST http://YOUR_BACKEND_IP:8000/api/webhook/commit/ \\
    -H "Content-Type: application/json" \\
    -d '{
      "project_id": "${project?.id}",
      "branch": "main",
      "commit_sha": "\${{ github.sha }}",
      "message": "\${{ github.event.head_commit.message }}",
      "author": "\${{ github.event.head_commit.author.name }}"
    }'`.trim();

    const getHookConfig = () => `
#!/bin/bash
# .git/hooks/post-commit

export PROJECT_ID="${project?.id}"
export BACKEND_URL="http://localhost:8000"
export COMMIT_SHA=$(git rev-parse HEAD)
export MESSAGE=$(git log -1 --pretty=%B)
export AUTHOR=$(git log -1 --pretty=%an)

# Use Python for robust JSON encoding and sending
python3 -c "
import json, urllib.request, os

data = {
    'project_id': os.environ.get('PROJECT_ID'),
    'commit_sha': os.environ.get('COMMIT_SHA'),
    'message': os.environ.get('MESSAGE'),
    'author': os.environ.get('AUTHOR')
}

req = urllib.request.Request(
    f\"{os.environ.get('BACKEND_URL')}/api/webhook/commit/\",
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        pass
except Exception as e:
    print(f'Failed to trigger diagram update: {e}')
" &
`.trim();

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    // Group images by type
    const groupedImages = selectedVersion?.images?.reduce((acc, img) => {
        acc[img.diagram_type] = acc[img.diagram_type] || [];
        acc[img.diagram_type].push(img);
        return acc;
    }, {} as Record<string, DiagramImage[]>) || {};

    // Helper to get friendly title
    const getTypeTitle = (type: string) => {
        switch (type) {
            case 'class_global': return 'Architecture Overview';
            case 'class_module': return 'Class Structure';
            case 'dependency': return 'Dependencies';
            case 'call': return 'Call Graphs';
            case 'api': return 'API Endpoints';
            default: return 'Other Diagrams';
        }
    }

    // Order of types
    const typeOrder = ['class_global', 'dependency', 'api', 'class_module', 'call', 'other'];

    if (loading) return <div className="p-10 text-center animate-pulse">Loading project details...</div>;
    if (!project) return <div className="p-10 text-center">Project not found</div>;

    return (
        <div className="h-screen flex flex-col pt-20 pb-4 px-6 max-w-[1920px] mx-auto w-full gap-6">
            <div className="flex justify-between items-center shrink-0">
                <div className="flex items-center gap-4">
                    <button
                        onClick={() => router.push("/")}
                        className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
                    >
                        <ArrowLeft size={24} />
                    </button>
                    <div>
                        <h1 className="text-2xl font-bold">{project.name}</h1>
                        <a href={project.repo_url} target="_blank" className="text-sm text-blue-400 hover:underline">
                            {project.repo_url}
                        </a>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    <button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-white transition-colors disabled:opacity-50"
                    >
                        {refreshing ? (
                            <RefreshCw size={16} className="animate-spin" />
                        ) : (
                            <RefreshCw size={16} />
                        )}
                        {refreshing ? "Syncing..." : "Sync Latest"}
                    </button>

                    <button
                        onClick={() => setShowWebhookModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-700 transition-colors text-sm"
                    >
                        <Copy size={16} />
                        Webhook Setup
                    </button>

                    <button
                        onClick={handleDelete}
                        className="flex items-center gap-2 px-4 py-2 bg-red-600/10 hover:bg-red-600/20 text-red-400 hover:text-red-300 rounded-lg border border-red-500/20 transition-colors"
                        title="Delete Project"
                    >
                        <Trash2 size={16} />
                        Delete
                    </button>
                </div>
            </div>

            <div className="flex-1 flex gap-6 min-h-0">
                {/* Sidebar: History */}
                <div className="w-80 flex flex-col bg-gray-900 border border-gray-800 rounded-xl overflow-hidden shrink-0">
                    <div className="p-4 border-b border-gray-800 bg-gray-800/50">
                        <h2 className="font-semibold flex items-center gap-2">
                            <Calendar size={18} />
                            Version History
                        </h2>
                    </div>
                    <div className="flex-1 overflow-y-auto p-2 space-y-2">
                        {project.diagrams.map((version) => (
                            <div
                                key={version.id}
                                onClick={() => setSelectedVersion(version)}
                                className={`p-3 rounded-lg cursor-pointer transition-all border ${selectedVersion?.id === version.id
                                    ? "bg-blue-600/10 border-blue-500/50"
                                    : "bg-transparent border-transparent hover:bg-gray-800"
                                    }`}
                            >
                                <div className="flex items-center gap-2 mb-1">
                                    <GitCommit size={16} className={selectedVersion?.id === version.id ? "text-blue-400" : "text-gray-500"} />
                                    <span className={`font-mono text-sm ${selectedVersion?.id === version.id ? "text-blue-200" : "text-gray-400"}`}>
                                        {version.commit_hash.substring(0, 7)}
                                    </span>
                                </div>
                                <p className="text-sm font-medium line-clamp-1 mb-1">{version.commit_message || "No message"}</p>
                                <div className="text-xs text-gray-500 flex justify-between">
                                    <span>{version.author}</span>
                                    <span>{new Date(version.created_at).toLocaleDateString()}</span>
                                </div>
                            </div>
                        ))}
                        {project.diagrams.length === 0 && (
                            <div className="p-4 text-center text-sm text-gray-500">
                                No versions yet.
                            </div>
                        )}
                    </div>
                </div>

                {/* Main View: Gallery */}
                <div className="flex-1 bg-gray-900 border border-gray-800 rounded-xl overflow-hidden flex flex-col relative">
                    {selectedVersion ? (
                        <div className="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
                            {!selectedVersion.images || selectedVersion.images.length === 0 ? (
                                // Fallback to legacy single image if no images array
                                <div className="flex flex-col items-center">
                                    <h3 className="text-xl font-bold mb-4">Main Diagram</h3>
                                    <div
                                        onClick={() => setLightboxImage({ id: 0, image_file: selectedVersion.image_file, diagram_type: 'main', description: 'Main Diagram' })}
                                        className="cursor-pointer border border-gray-700 rounded-lg overflow-hidden hover:border-blue-500 transition-all max-w-full"
                                    >
                                        <img src={selectedVersion.image_file} className="max-w-md w-full h-auto object-contain bg-gray-800" />
                                    </div>
                                </div>
                            ) : (
                                typeOrder.map(type => {
                                    const images = groupedImages[type];
                                    if (!images || images.length === 0) return null;

                                    return (
                                        <div key={type}>
                                            <h3 className="text-lg font-bold text-gray-300 mb-4 border-b border-gray-800 pb-2">
                                                {getTypeTitle(type)}
                                            </h3>
                                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                                                {images.map(img => (
                                                    <div
                                                        key={img.id}
                                                        onClick={() => setLightboxImage(img)}
                                                        className="group cursor-pointer bg-gray-800 border border-gray-700 rounded-lg overflow-hidden hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/10 transition-all"
                                                    >
                                                        <div className="aspect-video w-full bg-gray-950 flex items-center justify-center relative overflow-hidden">
                                                            <img src={img.image_file} alt={img.description} className="max-w-full max-h-full object-contain p-2" />
                                                            <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                                                <Maximize2 className="text-white" />
                                                            </div>
                                                        </div>
                                                        <div className="p-3">
                                                            <p className="text-sm font-medium text-gray-300 truncate" title={img.description}>
                                                                {img.description}
                                                            </p>
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    )
                                })
                            )}
                        </div>
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-gray-500">
                            Select a version to view diagrams
                        </div>
                    )}

                    {/* Webhook Modal */}
                    {showWebhookModal && (
                        <div className="absolute inset-0 z-50 bg-black/95 backdrop-blur-md flex flex-col animate-in fade-in duration-200 items-center justify-center p-4">
                            <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 max-w-2xl w-full shadow-2xl">
                                <div className="flex justify-between items-center mb-6">
                                    <h3 className="text-xl font-bold">Automation Setup</h3>
                                    <button onClick={() => setShowWebhookModal(false)} className="p-1 hover:bg-gray-800 rounded"><X size={20} /></button>
                                </div>

                                <div className="flex gap-4 border-b border-gray-800 mb-4">
                                    <button
                                        onClick={() => setWebhookTab('github')}
                                        className={`pb-2 px-1 text-sm font-medium transition-colors ${webhookTab === 'github' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
                                    >
                                        GitHub Action
                                    </button>
                                    <button
                                        onClick={() => setWebhookTab('hook')}
                                        className={`pb-2 px-1 text-sm font-medium transition-colors ${webhookTab === 'hook' ? 'text-blue-400 border-b-2 border-blue-400' : 'text-gray-400 hover:text-white'}`}
                                    >
                                        Local Git Hook
                                    </button>
                                </div>

                                <div className="bg-gray-950 rounded-lg p-4 border border-gray-800 font-mono text-xs overflow-x-auto relative group">
                                    <button
                                        onClick={() => copyToClipboard(webhookTab === 'github' ? getGithubConfig() : getHookConfig())}
                                        className="absolute top-2 right-2 p-2 bg-gray-800 hover:bg-gray-700 rounded text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity"
                                    >
                                        {copied ? <Check size={14} className="text-green-400" /> : <Copy size={14} />}
                                    </button>
                                    <pre className="text-gray-300">
                                        {webhookTab === 'github' ? getGithubConfig() : getHookConfig()}
                                    </pre>
                                </div>
                                <p className="mt-4 text-sm text-gray-500">
                                    {webhookTab === 'github'
                                        ? "Add this to your .github/workflows/doc-update.yml file."
                                        : "Save this as .git/hooks/post-commit and run `chmod +x .git/hooks/post-commit`."}
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Lightbox Modal */}
                    {lightboxImage && (
                        <div className="absolute inset-0 z-50 bg-black/95 backdrop-blur-md flex flex-col animate-in fade-in duration-200">
                            <div className="flex justify-between items-center p-4 border-b border-white/10 shrink-0">
                                <div>
                                    <h3 className="text-lg font-bold text-white">{lightboxImage.description}</h3>
                                    <span className="text-sm text-gray-400 capitalize">{getTypeTitle(lightboxImage.diagram_type).replace('Diagram', '')}</span>
                                </div>
                                <div className="flex items-center gap-4">
                                    <a
                                        href={lightboxImage.image_file}
                                        download
                                        className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium transition-colors"
                                    >
                                        Download
                                    </a>
                                    <button
                                        onClick={() => setLightboxImage(null)}
                                        className="p-2 hover:bg-white/10 rounded-full transition-colors"
                                    >
                                        <X size={24} />
                                    </button>
                                </div>
                            </div>
                            <div className="flex-1 overflow-auto flex items-center justify-center p-4 bg-[url('/grid.svg')] bg-repeat">
                                <img
                                    src={lightboxImage.image_file}
                                    alt={lightboxImage.description}
                                    className="max-w-none shadow-2xl rounded border border-white/10"
                                />
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

