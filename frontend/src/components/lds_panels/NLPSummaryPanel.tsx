'use client';

import React, { useEffect, useState } from 'react';
import { FaFileAlt, FaSpinner, FaLightbulb, FaCubes, FaChartBar } from 'react-icons/fa';

interface ModuleSummary {
    name: string;
    file_count: number;
    extensions: string;
    complexity: string;
    description: string;
}

interface NLPSummaryData {
    overview: string;
    primary_language: string;
    total_files: number;
    code_files: number;
    doc_files: number;
    config_files: number;
    frontend_files: number;
    module_count: number;
    module_summaries: ModuleSummary[];
    key_findings: string[];
}

interface NLPSummaryPanelProps {
    repoInfo: { owner: string; repo: string; type: string };
}

export default function NLPSummaryPanel({ repoInfo }: NLPSummaryPanelProps) {
    const [data, setData] = useState<NLPSummaryData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!repoInfo) return;

        const fetchSummary = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/api/lds/nlp-summary?owner=${repoInfo.owner}&repo=${repoInfo.repo}&repo_type=${repoInfo.type}`);
                if (!response.ok) throw new Error('Failed to fetch NLP summary');

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

        fetchSummary();
    }, [repoInfo]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-[var(--muted)]">
                <FaSpinner className="animate-spin text-4xl mb-4 text-[var(--accent-primary)]" />
                <p>Generating NLP summary of repository...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-500">
                <FaFileAlt className="text-4xl mb-4" />
                <p>Error loading NLP summary: {error}</p>
            </div>
        );
    }

    if (!data) return null;

    const complexityColor = (c: string) => {
        switch (c) {
            case 'high': return 'text-red-500 bg-red-500/10 border-red-500/20';
            case 'medium': return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
            default: return 'text-green-500 bg-green-500/10 border-green-500/20';
        }
    };

    return (
        <div className="w-full max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-4">
                <FaFileAlt className="text-2xl text-[var(--accent-primary)]" />
                <h2 className="text-2xl font-bold font-serif">NLP Code Summary</h2>
            </div>

            {/* Overview */}
            <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-5 mb-6 shadow-sm">
                <p className="text-[var(--foreground)] leading-relaxed">{data.overview}</p>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
                {[
                    { label: 'Total Files', value: data.total_files, icon: FaChartBar },
                    { label: 'Source Code', value: data.code_files, icon: FaCubes },
                    { label: 'Documentation', value: data.doc_files, icon: FaFileAlt },
                    { label: 'Modules', value: data.module_count, icon: FaCubes },
                ].map((stat, idx) => (
                    <div key={idx} className="bg-[var(--card-bg)] border border-[var(--border-color)] p-4 rounded-lg text-center">
                        <stat.icon className="text-[var(--accent-primary)] text-lg mx-auto mb-1" />
                        <p className="text-2xl font-bold text-[var(--foreground)]">{stat.value}</p>
                        <p className="text-xs text-[var(--muted)] uppercase tracking-wider">{stat.label}</p>
                    </div>
                ))}
            </div>

            {/* Key Findings */}
            {data.key_findings.length > 0 && (
                <div className="bg-[var(--accent-primary)]/5 border border-[var(--accent-primary)]/20 rounded-lg p-5 mb-6">
                    <h3 className="font-semibold mb-3 flex items-center gap-2 text-[var(--accent-primary)]">
                        <FaLightbulb /> Key Findings
                    </h3>
                    <ul className="space-y-2">
                        {data.key_findings.map((finding, idx) => (
                            <li key={idx} className="flex items-start gap-2 text-sm text-[var(--foreground)]">
                                <span className="text-[var(--accent-primary)] mt-1">•</span>
                                {finding}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Module Summaries */}
            <div>
                <h3 className="font-semibold mb-3 flex items-center gap-2 text-[var(--foreground)]">
                    <FaCubes className="text-[var(--accent-primary)]" /> Module Breakdown
                </h3>
                <div className="space-y-3">
                    {data.module_summaries.map((mod, idx) => (
                        <div key={idx} className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-4 shadow-sm">
                            <div className="flex items-center justify-between mb-2">
                                <h4 className="font-semibold text-[var(--foreground)] font-mono text-sm">{mod.name}/</h4>
                                <div className="flex items-center gap-2">
                                    <span className="text-xs text-[var(--muted)]">{mod.file_count} files</span>
                                    <span className={`text-xs px-2 py-0.5 rounded-full border ${complexityColor(mod.complexity)}`}>
                                        {mod.complexity}
                                    </span>
                                </div>
                            </div>
                            <p className="text-sm text-[var(--muted)]">{mod.description}</p>
                            <p className="text-xs text-[var(--muted)] mt-1 font-mono">Extensions: {mod.extensions}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
