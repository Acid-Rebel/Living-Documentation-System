'use client';

import React, { useEffect, useState } from 'react';
import { FaSearch, FaProjectDiagram, FaSpinner, FaCubes, FaArrowRight } from 'react-icons/fa';

interface Symbol {
    name: string;
    type: string;
    complexity: string;
    file_count?: number;
    language?: string;
}

interface Relation {
    source: string;
    target: string;
    type: string;
}

interface SemanticData {
    symbols: Symbol[];
    relations: Relation[];
    primary_language?: string;
    total_code_files?: number;
}

interface SemanticInsightsPanelProps {
    repoInfo: { owner: string; repo: string; type: string };
}

export default function SemanticInsightsPanel({ repoInfo }: SemanticInsightsPanelProps) {
    const [data, setData] = useState<SemanticData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!repoInfo) return;

        const fetchInsights = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/api/lds/semantic-insights?owner=${repoInfo.owner}&repo=${repoInfo.repo}&repo_type=${repoInfo.type}`);
                if (!response.ok) throw new Error('Failed to fetch semantic insights');

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

        fetchInsights();
    }, [repoInfo]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-[var(--muted)]">
                <FaSpinner className="animate-spin text-4xl mb-4 text-[var(--accent-primary)]" />
                <p>Extracting semantic meaning from code patterns...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-500">
                <p>Error loading semantic insights: {error}</p>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="flex flex-col h-full w-full max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-2">
                <FaSearch className="text-2xl text-[var(--accent-primary)]" />
                <h2 className="text-2xl font-bold font-serif">Semantic Insights</h2>
            </div>

            {(data.primary_language || data.total_code_files != null) && (
                <div className="mb-6 text-xs text-[var(--muted)] flex gap-4 flex-wrap">
                    {data.primary_language && <span>Primary language: <strong className="text-[var(--foreground)]">{data.primary_language}</strong></span>}
                    {data.total_code_files != null && <span>{data.total_code_files} source files</span>}
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 h-[calc(100vh-280px)]">
                {/* Symbols list */}
                <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg flex flex-col overflow-hidden">
                    <div className="bg-[var(--background)] p-3 border-b border-[var(--border-color)] font-semibold flex items-center gap-2">
                        <FaCubes className="text-[var(--accent-primary)]" /> Core Entities
                    </div>
                    <div className="p-4 overflow-y-auto flex-1 space-y-3">
                        {data.symbols.map((sym, idx) => (
                            <div key={idx} className="flex justify-between items-center p-3 border border-[var(--border-color)] rounded hover:bg-[var(--accent-primary)]/5 transition-colors">
                                <div>
                                    <div className="font-mono text-sm font-semibold">{sym.name}</div>
                                    {sym.file_count != null && <span className="text-[10px] text-[var(--muted)]">{sym.file_count} files</span>}
                                </div>
                                <div className="flex items-center gap-2 flex-shrink-0">
                                    <span className="text-xs px-2 py-1 bg-[var(--background)] rounded text-[var(--muted)]">{sym.type}</span>
                                    <span className={`text-xs px-2 py-1 rounded capitalize ${sym.complexity === 'high' ? 'bg-red-500/10 text-red-500' :
                                            sym.complexity === 'medium' ? 'bg-yellow-500/10 text-yellow-500' :
                                                'bg-blue-500/10 text-blue-500'
                                        }`}>
                                        {sym.complexity}
                                    </span>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Relations list */}
                <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg flex flex-col overflow-hidden">
                    <div className="bg-[var(--background)] p-3 border-b border-[var(--border-color)] font-semibold flex items-center gap-2">
                        <FaProjectDiagram className="text-[var(--accent-primary)]" /> Entity Relationships
                    </div>
                    <div className="p-4 overflow-y-auto flex-1 space-y-3">
                        {data.relations.map((rel, idx) => (
                            <div key={idx} className="flex items-center p-3 border border-[var(--border-color)] rounded justify-between">
                                <div className="font-mono text-sm flex-1 truncate text-right">{rel.source}</div>
                                <div className="px-4 flex flex-col items-center justify-center flex-shrink-0">
                                    <span className="text-[10px] uppercase text-[var(--muted)] font-bold tracking-wider">{rel.type}</span>
                                    <FaArrowRight className="text-[var(--accent-primary)] my-1" />
                                </div>
                                <div className="font-mono text-sm flex-1 truncate">{rel.target}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
