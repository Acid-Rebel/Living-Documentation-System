'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { FaCodeBranch, FaSpinner, FaPlus, FaCheck, FaTimes, FaEye, FaCheckDouble } from 'react-icons/fa';

interface PRReview {
    reviewer: string;
    status: string;
    comment: string | null;
    created_at: string;
}

interface PullRequest {
    id: string;
    title: string;
    description: string;
    doc_content: string;
    author: string;
    repo_owner: string;
    repo_name: string;
    status: string;
    reviews: PRReview[];
    created_at: string;
    updated_at: string;
    merged_at: string | null;
    merged_by: string | null;
}

interface PullRequestsPanelProps {
    repoInfo: { owner: string; repo: string; type: string };
}

export default function PullRequestsPanel({ repoInfo }: PullRequestsPanelProps) {
    const [prs, setPrs] = useState<PullRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [selectedPR, setSelectedPR] = useState<PullRequest | null>(null);
    const [creating, setCreating] = useState(false);

    // Form state
    const [formTitle, setFormTitle] = useState('');
    const [formDescription, setFormDescription] = useState('');
    const [formContent, setFormContent] = useState('');
    const [formAuthor, setFormAuthor] = useState('user');

    const fetchPRs = useCallback(async () => {
        setLoading(true);
        try {
            const response = await fetch(`/api/lds/pull-requests?repo_owner=${repoInfo.owner}&repo_name=${repoInfo.repo}`);
            if (!response.ok) throw new Error('Failed to fetch pull requests');

            const result = await response.json();
            if (result.status === 'success') {
                setPrs(result.data);
            }
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'An error occurred');
        } finally {
            setLoading(false);
        }
    }, [repoInfo]);

    useEffect(() => {
        if (!repoInfo) return;
        fetchPRs();
    }, [repoInfo, fetchPRs]);

    const handleCreatePR = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreating(true);
        try {
            const response = await fetch('/api/lds/pull-requests', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: formTitle,
                    description: formDescription,
                    doc_content: formContent,
                    author: formAuthor,
                    repo_owner: repoInfo.owner,
                    repo_name: repoInfo.repo,
                }),
            });
            if (!response.ok) throw new Error('Failed to create PR');

            setShowCreateForm(false);
            setFormTitle('');
            setFormDescription('');
            setFormContent('');
            await fetchPRs();
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to create PR');
        } finally {
            setCreating(false);
        }
    };

    const handleMergePR = async (prId: string) => {
        try {
            const response = await fetch(`/api/lds/pull-requests/${prId}/merge`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            });
            if (!response.ok) throw new Error('Failed to merge PR');
            await fetchPRs();
            setSelectedPR(null);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to merge PR');
        }
    };

    const handleClosePR = async (prId: string) => {
        try {
            const response = await fetch(`/api/lds/pull-requests/${prId}/close`, {
                method: 'POST',
            });
            if (!response.ok) throw new Error('Failed to close PR');
            await fetchPRs();
            setSelectedPR(null);
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to close PR');
        }
    };

    const handleApprovePR = async (prId: string) => {
        try {
            const response = await fetch(`/api/lds/pull-requests/${prId}/review`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reviewer: 'user',
                    status: 'APPROVED',
                    comment: 'Approved via UI',
                }),
            });
            if (!response.ok) throw new Error('Failed to approve PR');
            await fetchPRs();
        } catch (err: unknown) {
            setError(err instanceof Error ? err.message : 'Failed to approve');
        }
    };

    const statusBadge = (status: string) => {
        const colors: Record<string, string> = {
            OPEN: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
            APPROVED: 'bg-green-500/10 text-green-500 border-green-500/20',
            MERGED: 'bg-purple-500/10 text-purple-500 border-purple-500/20',
            REJECTED: 'bg-red-500/10 text-red-500 border-red-500/20',
            CLOSED: 'bg-gray-500/10 text-gray-500 border-gray-500/20',
        };
        return colors[status] || colors['OPEN'];
    };

    if (loading && prs.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-[var(--muted)]">
                <FaSpinner className="animate-spin text-4xl mb-4 text-[var(--accent-primary)]" />
                <p>Loading pull requests...</p>
            </div>
        );
    }

    if (error && prs.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-red-500">
                <FaCodeBranch className="text-4xl mb-4" />
                <p>Error: {error}</p>
            </div>
        );
    }

    // Detail view
    if (selectedPR) {
        return (
            <div className="flex flex-col h-full w-full max-w-4xl mx-auto">
                <button
                    onClick={() => setSelectedPR(null)}
                    className="text-sm text-[var(--accent-primary)] hover:underline mb-4 self-start"
                >
                    &larr; Back to list
                </button>

                <div className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-6 shadow-sm mb-4">
                    <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xl font-bold font-serif text-[var(--foreground)]">{selectedPR.title}</h3>
                        <span className={`text-xs px-3 py-1 rounded-full border font-semibold ${statusBadge(selectedPR.status)}`}>
                            {selectedPR.status}
                        </span>
                    </div>
                    <p className="text-sm text-[var(--muted)] mb-2">By {selectedPR.author} &middot; {new Date(selectedPR.created_at).toLocaleString()}</p>
                    <p className="text-sm text-[var(--foreground)] mb-4">{selectedPR.description}</p>

                    {/* Doc Content Preview */}
                    <div className="bg-[var(--background)]/70 border border-[var(--border-color)] rounded-lg p-4 mb-4 max-h-64 overflow-y-auto">
                        <h4 className="text-xs font-semibold text-[var(--muted)] uppercase mb-2">Documentation Content</h4>
                        <pre className="text-xs text-[var(--foreground)] whitespace-pre-wrap font-mono">{selectedPR.doc_content}</pre>
                    </div>

                    {/* Reviews */}
                    {selectedPR.reviews.length > 0 && (
                        <div className="mb-4">
                            <h4 className="text-xs font-semibold text-[var(--muted)] uppercase mb-2">Reviews</h4>
                            <div className="space-y-2">
                                {selectedPR.reviews.map((review, idx) => (
                                    <div key={idx} className="flex items-center gap-2 text-sm">
                                        <span className={`w-2 h-2 rounded-full ${review.status === 'APPROVED' ? 'bg-green-500' : 'bg-red-500'}`} />
                                        <span className="text-[var(--foreground)]">{review.reviewer}</span>
                                        <span className="text-[var(--muted)]">{review.status}</span>
                                        {review.comment && <span className="text-[var(--muted)] italic">&mdash; {review.comment}</span>}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Actions */}
                    {selectedPR.status !== 'MERGED' && selectedPR.status !== 'CLOSED' && (
                        <div className="flex gap-3 pt-3 border-t border-[var(--border-color)]">
                            <button
                                onClick={() => handleApprovePR(selectedPR.id)}
                                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-green-500/10 text-green-600 border border-green-500/20 rounded-lg hover:bg-green-500/20 transition-colors"
                            >
                                <FaCheck /> Approve
                            </button>
                            <button
                                onClick={() => handleMergePR(selectedPR.id)}
                                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-purple-500/10 text-purple-600 border border-purple-500/20 rounded-lg hover:bg-purple-500/20 transition-colors"
                            >
                                <FaCheckDouble /> Merge
                            </button>
                            <button
                                onClick={() => handleClosePR(selectedPR.id)}
                                className="flex items-center gap-1.5 px-4 py-2 text-sm bg-red-500/10 text-red-600 border border-red-500/20 rounded-lg hover:bg-red-500/20 transition-colors"
                            >
                                <FaTimes /> Close
                            </button>
                        </div>
                    )}

                    {selectedPR.merged_at && (
                        <p className="text-xs text-[var(--muted)] mt-3">
                            Merged by {selectedPR.merged_by} on {new Date(selectedPR.merged_at).toLocaleString()}
                        </p>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full w-full max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <FaCodeBranch className="text-2xl text-[var(--accent-primary)]" />
                    <h2 className="text-2xl font-bold font-serif">Documentation PRs</h2>
                </div>
                <button
                    onClick={() => setShowCreateForm(!showCreateForm)}
                    className="flex items-center gap-1.5 px-4 py-2 text-sm btn-japanese rounded-lg"
                >
                    <FaPlus /> New PR
                </button>
            </div>

            <p className="text-sm text-[var(--muted)] mb-6">
                Manage documentation pull requests. Create, review, approve, and merge documentation changes.
            </p>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-500 text-sm p-3 rounded-lg mb-4">
                    {error}
                </div>
            )}

            {/* Create Form */}
            {showCreateForm && (
                <form onSubmit={handleCreatePR} className="bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-5 mb-6 shadow-sm">
                    <h3 className="font-semibold mb-4 text-[var(--foreground)]">Create Documentation PR</h3>
                    <div className="space-y-3">
                        <div>
                            <label className="block text-xs text-[var(--muted)] mb-1">Title</label>
                            <input
                                type="text"
                                required
                                value={formTitle}
                                onChange={(e) => setFormTitle(e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-[var(--border-color)] rounded-lg bg-transparent text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)]"
                                placeholder="Documentation update title..."
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-[var(--muted)] mb-1">Description</label>
                            <textarea
                                required
                                value={formDescription}
                                onChange={(e) => setFormDescription(e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-[var(--border-color)] rounded-lg bg-transparent text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)] min-h-[60px]"
                                placeholder="What changed in the documentation..."
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-[var(--muted)] mb-1">Documentation Content (Markdown)</label>
                            <textarea
                                required
                                value={formContent}
                                onChange={(e) => setFormContent(e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-[var(--border-color)] rounded-lg bg-transparent text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)] min-h-[120px] font-mono"
                                placeholder="# Updated Documentation\n\nYour markdown content here..."
                            />
                        </div>
                        <div>
                            <label className="block text-xs text-[var(--muted)] mb-1">Author</label>
                            <input
                                type="text"
                                value={formAuthor}
                                onChange={(e) => setFormAuthor(e.target.value)}
                                className="w-full px-3 py-2 text-sm border border-[var(--border-color)] rounded-lg bg-transparent text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)]"
                            />
                        </div>
                    </div>
                    <div className="flex gap-3 mt-4">
                        <button
                            type="submit"
                            disabled={creating}
                            className="px-4 py-2 text-sm btn-japanese rounded-lg disabled:opacity-50"
                        >
                            {creating ? 'Creating...' : 'Create PR'}
                        </button>
                        <button
                            type="button"
                            onClick={() => setShowCreateForm(false)}
                            className="px-4 py-2 text-sm border border-[var(--border-color)] rounded-lg text-[var(--muted)] hover:text-[var(--foreground)] transition-colors"
                        >
                            Cancel
                        </button>
                    </div>
                </form>
            )}

            {/* PR List */}
            {prs.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-[var(--muted)]">
                    <FaCodeBranch className="text-4xl mb-3 opacity-40" />
                    <p className="text-sm">No documentation pull requests yet.</p>
                    <p className="text-xs mt-1">Create one to start tracking documentation changes.</p>
                </div>
            ) : (
                <div className="space-y-3 flex-1 overflow-auto">
                    {prs.map((pr) => (
                        <button
                            key={pr.id}
                            onClick={() => setSelectedPR(pr)}
                            className="w-full text-left bg-[var(--card-bg)] border border-[var(--border-color)] rounded-lg p-4 shadow-sm hover:border-[var(--accent-primary)]/40 transition-colors"
                        >
                            <div className="flex items-center justify-between mb-1">
                                <div className="flex items-center gap-2">
                                    <FaCodeBranch className="text-[var(--accent-primary)] text-sm" />
                                    <h4 className="font-semibold text-sm text-[var(--foreground)]">{pr.title}</h4>
                                </div>
                                <span className={`text-xs px-2.5 py-0.5 rounded-full border font-semibold ${statusBadge(pr.status)}`}>
                                    {pr.status}
                                </span>
                            </div>
                            <p className="text-xs text-[var(--muted)] truncate">{pr.description}</p>
                            <div className="flex items-center gap-3 mt-2 text-xs text-[var(--muted)]">
                                <span>by {pr.author}</span>
                                <span>{new Date(pr.created_at).toLocaleDateString()}</span>
                                {pr.reviews.length > 0 && (
                                    <span className="flex items-center gap-1"><FaEye className="text-xs" /> {pr.reviews.length} review(s)</span>
                                )}
                            </div>
                        </button>
                    ))}
                </div>
            )}
        </div>
    );
}
