'use client';

import React, { useEffect, useState } from 'react';
import { FaProjectDiagram, FaSpinner, FaSitemap, FaStream, FaCubes } from 'react-icons/fa';
import Mermaid from '@/components/Mermaid';

interface DiagramsData {
    class_diagram: string;
    dependency_diagram: string;
    call_diagram: string;
    diagram_types: string[];
}

interface DiagramsPanelProps {
    repoInfo: { owner: string; repo: string; type: string };
}

type DiagramTab = 'class' | 'dependency' | 'call';

export default function DiagramsPanel({ repoInfo }: DiagramsPanelProps) {
    const [data, setData] = useState<DiagramsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [activeTab, setActiveTab] = useState<DiagramTab>('dependency');

    useEffect(() => {
        if (!repoInfo) return;

        const fetchDiagrams = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/api/lds/diagrams?owner=${repoInfo.owner}&repo=${repoInfo.repo}&repo_type=${repoInfo.type}`);
                if (!response.ok) throw new Error('Failed to fetch diagrams');

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

        fetchDiagrams();
    }, [repoInfo]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-[var(--muted)]">
                <FaSpinner className="animate-spin text-4xl mb-4 text-[var(--accent-primary)]" />
                <p>Generating AI-enhanced diagrams...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-500">
                <FaProjectDiagram className="text-4xl mb-4" />
                <p>Error loading diagrams: {error}</p>
            </div>
        );
    }

    if (!data) return null;

    const tabs: { id: DiagramTab; label: string; icon: React.ElementType; diagram: string }[] = [
        { id: 'dependency', label: 'Architecture', icon: FaSitemap, diagram: data.dependency_diagram },
        { id: 'class', label: 'Module Structure', icon: FaCubes, diagram: data.class_diagram },
        { id: 'call', label: 'Request Flow', icon: FaStream, diagram: data.call_diagram },
    ];

    const currentDiagram = tabs.find(t => t.id === activeTab)?.diagram || '';

    return (
        <div className="flex flex-col h-full w-full max-w-5xl mx-auto">
            <div className="flex items-center gap-3 mb-4">
                <FaProjectDiagram className="text-2xl text-[var(--accent-primary)]" />
                <h2 className="text-2xl font-bold font-serif">AI-Enhanced Diagrams</h2>
            </div>

            <p className="text-sm text-[var(--muted)] mb-6">
                Auto-generated diagrams showing the repository&apos;s architecture, module structure, and request flow.
            </p>

            {/* Diagram Type Tabs */}
            <div className="flex border-b border-[var(--border-color)] mb-6 overflow-x-auto">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 text-sm font-medium whitespace-nowrap border-b-2 transition-colors ${
                            activeTab === tab.id
                                ? 'border-[var(--accent-primary)] text-[var(--accent-primary)] bg-[var(--accent-primary)]/5'
                                : 'border-transparent text-[var(--muted)] hover:text-[var(--foreground)] hover:bg-[var(--background)]/50'
                        }`}
                    >
                        <tab.icon /> {tab.label}
                    </button>
                ))}
            </div>

            {/* Diagram Content */}
            <div className="flex-1 overflow-auto">
                {currentDiagram ? (
                    <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-6 shadow-sm">
                        <Mermaid chart={currentDiagram} />
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-64 text-[var(--muted)]">
                        <FaProjectDiagram className="text-3xl mb-3 opacity-40" />
                        <p className="text-sm">No diagram data available for this repository.</p>
                        <p className="text-xs mt-1">The repository may be private or the API rate limit was reached.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
