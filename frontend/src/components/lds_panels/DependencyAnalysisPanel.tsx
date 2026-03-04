'use client';

import React, { useEffect, useState } from 'react';
import { FaNetworkWired, FaSpinner, FaBox, FaLink } from 'react-icons/fa';

interface ModuleDep {
    name: string;
    dependencies: string[];
}

interface DependencyData {
    modules: ModuleDep[];
    external_packages: string[];
    total_files?: number;
    primary_language?: string;
}

interface DependencyAnalysisPanelProps {
    repoInfo: { owner: string; repo: string; type: string };
}

export default function DependencyAnalysisPanel({ repoInfo }: DependencyAnalysisPanelProps) {
    const [data, setData] = useState<DependencyData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!repoInfo) return;

        const fetchAnalysis = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/api/lds/dependency-analysis?owner=${repoInfo.owner}&repo=${repoInfo.repo}&repo_type=${repoInfo.type}`);
                if (!response.ok) throw new Error('Failed to fetch dependency analysis');

                const result = await response.json();
                if (result.status === 'success') {
                    setData(result.data);
                } else {
                    throw new Error('Invalid response format');
                }
            } catch (err: unknown) {
                setError(err instanceof Error ? err.message : 'An error occurred');
            } finally {
                setLoading(false);
            }
        };

        fetchAnalysis();
    }, [repoInfo]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-[var(--muted)]">
                <FaSpinner className="animate-spin text-4xl mb-4 text-[var(--accent-primary)]" />
                <p>Analyzing cross-module dependencies...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-500">
                <p>Error loading dependency analysis: {error}</p>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="flex flex-col h-full w-full max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-2">
                <FaNetworkWired className="text-2xl text-[var(--accent-primary)]" />
                <h2 className="text-2xl font-bold font-serif">Dependency Intelligence</h2>
            </div>

            {(data.primary_language || data.total_files != null) && (
                <div className="mb-6 text-xs text-[var(--muted)] flex gap-4 flex-wrap">
                    {data.primary_language && <span>Primary language: <strong className="text-[var(--foreground)]">{data.primary_language}</strong></span>}
                    {data.total_files != null && <span>{data.total_files} files in repository</span>}
                    <span>{data.modules.length} modules detected</span>
                </div>
            )}

            <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg shadow-sm mb-6 p-5">
                <h3 className="font-semibold mb-3 flex items-center gap-2 border-b border-[var(--border-color)] pb-2 text-[var(--foreground)]">
                    <FaBox className="text-[var(--accent-primary)]" /> External Packages
                </h3>
                <div className="flex flex-wrap gap-2">
                    {data.external_packages.map((pkg, idx) => (
                        <span key={idx} className="bg-[var(--background)] border border-[var(--border-color)] text-[var(--muted)] text-sm px-3 py-1.5 rounded-full font-mono">
                            {pkg}
                        </span>
                    ))}
                    {data.external_packages.length === 0 && (
                        <span className="text-[var(--muted)] text-sm italic">No external packages detected.</span>
                    )}
                </div>
            </div>

            <div className="flex-1 bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg shadow-sm p-5 overflow-y-auto">
                <h3 className="font-semibold mb-4 flex items-center gap-2 border-b border-[var(--border-color)] pb-2 text-[var(--foreground)]">
                    <FaLink className="text-[var(--accent-primary)]" /> Internal Module Dependencies
                </h3>

                <div className="space-y-4">
                    {data.modules.map((mod, idx) => (
                        <div key={idx} className="border border-[var(--border-color)] rounded p-4 hover:border-[var(--accent-primary)]/40 transition-colors">
                            <h4 className="font-bold text-lg mb-2 font-mono text-[var(--foreground)]">{mod.name}</h4>
                            <div className="flex flex-wrap items-center gap-2">
                                <span className="text-xs text-[var(--muted)] uppercase font-semibold">Depends on:</span>
                                {mod.dependencies.length > 0 ? (
                                    mod.dependencies.map((dep, dIdx) => (
                                        <span key={dIdx} className="bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20 text-xs px-2 py-1 rounded font-mono">
                                            {dep}
                                        </span>
                                    ))
                                ) : (
                                    <span className="text-sm italic text-[var(--muted)]">None</span>
                                )}
                            </div>
                        </div>
                    ))}
                    {data.modules.length === 0 && (
                        <div className="text-center p-8 text-[var(--muted)] border border-dashed border-[var(--border-color)] rounded-lg">
                            No internal module dependencies detected.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
