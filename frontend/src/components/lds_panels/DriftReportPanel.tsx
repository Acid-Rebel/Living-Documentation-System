'use client';

import React, { useEffect, useState } from 'react';
import { FaCodeBranch, FaExclamationTriangle, FaCheckCircle, FaInfoCircle, FaSpinner } from 'react-icons/fa';

interface DriftFinding {
    id: string;
    type: string;
    severity: 'high' | 'medium' | 'low';
    description: string;
    file?: string;
}

interface DriftReportData {
    summary: {
        total_findings: number;
        high_severity: number;
        medium_severity: number;
        low_severity: number;
        files_analyzed?: number;
        code_files?: number;
        doc_files?: number;
    };
    findings: DriftFinding[];
}

interface DriftReportPanelProps {
    repoInfo: { owner: string; repo: string; type: string };
}

export default function DriftReportPanel({ repoInfo }: DriftReportPanelProps) {
    const [data, setData] = useState<DriftReportData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!repoInfo) return;

        const fetchReport = async () => {
            setLoading(true);
            try {
                const response = await fetch(`/api/lds/drift-report?owner=${repoInfo.owner}&repo=${repoInfo.repo}&repo_type=${repoInfo.type}`);
                if (!response.ok) throw new Error('Failed to fetch drift report');

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

        fetchReport();
    }, [repoInfo]);

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-[var(--muted)]">
                <FaSpinner className="animate-spin text-4xl mb-4 text-[var(--accent-primary)]" />
                <p>Analyzing repository for documentation drift...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-500">
                <FaExclamationTriangle className="text-4xl mb-4" />
                <p>Error loading drift report: {error}</p>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="flex flex-col h-full w-full max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-6">
                <FaCodeBranch className="text-2xl text-[var(--accent-primary)]" />
                <h2 className="text-2xl font-bold font-serif">Documentation Drift Report</h2>
            </div>

            {/* Analysis Stats */}
            {(data.summary.files_analyzed != null && data.summary.files_analyzed > 0) && (
                <div className="mb-4 text-xs text-[var(--muted)] flex gap-4 flex-wrap">
                    <span>{data.summary.files_analyzed} files analysed</span>
                    <span>{data.summary.code_files ?? 0} source files</span>
                    <span>{data.summary.doc_files ?? 0} doc files</span>
                </div>
            )}

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
                <div className="bg-[var(--card-bg)] border border-[var(--border-color)] p-4 rounded-lg text-center flex flex-col justify-center">
                    <p className="text-3xl font-bold text-[var(--foreground)]">{data.summary.total_findings}</p>
                    <p className="text-sm text-[var(--muted)] uppercase tracking-wider font-semibold">Total Findings</p>
                </div>
                <div className="bg-red-500/10 border border-red-500/30 p-4 rounded-lg text-center flex flex-col justify-center">
                    <p className="text-3xl font-bold text-red-500">{data.summary.high_severity}</p>
                    <p className="text-sm text-red-500/80 uppercase tracking-wider font-semibold">High Severity</p>
                </div>
                <div className="bg-yellow-500/10 border border-yellow-500/30 p-4 rounded-lg text-center flex flex-col justify-center">
                    <p className="text-3xl font-bold text-yellow-500">{data.summary.medium_severity}</p>
                    <p className="text-sm text-yellow-500/80 uppercase tracking-wider font-semibold">Medium Severity</p>
                </div>
                <div className="bg-blue-500/10 border border-blue-500/30 p-4 rounded-lg text-center flex flex-col justify-center">
                    <p className="text-3xl font-bold text-blue-500">{data.summary.low_severity}</p>
                    <p className="text-sm text-blue-500/80 uppercase tracking-wider font-semibold">Low Severity</p>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto pr-2">
                <h3 className="text-lg font-semibold mb-4 pb-2 border-b border-[var(--border-color)]">Detailed Findings</h3>
                {data.findings.length === 0 ? (
                    <div className="flex items-center gap-2 text-green-500 bg-green-500/10 p-4 rounded-lg border border-green-500/30">
                        <FaCheckCircle />
                        <p>No documentation drift detected! Your documentation is perfectly synchronized with your code.</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {data.findings.map(finding => (
                            <div key={finding.id} className="bg-[var(--card-bg)] border border-[var(--border-color)] p-4 rounded-lg flex items-start gap-4 hover:border-[var(--accent-primary)]/50 transition-colors">
                                <div className="mt-1">
                                    {finding.severity === 'high' && <FaExclamationTriangle className="text-red-500 text-xl" />}
                                    {finding.severity === 'medium' && <FaInfoCircle className="text-yellow-500 text-xl" />}
                                    {finding.severity === 'low' && <FaInfoCircle className="text-blue-500 text-xl" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h4 className="font-semibold text-[var(--foreground)] truncate">{finding.type}</h4>
                                        {finding.file && (
                                            <span className="text-xs bg-[var(--background)] px-2 py-0.5 rounded text-[var(--muted)] border border-[var(--border-color)] font-mono truncate max-w-[50%]">
                                                {finding.file}
                                            </span>
                                        )}
                                    </div>
                                    <p className="text-sm text-[var(--muted)] leading-relaxed break-words">{finding.description}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
