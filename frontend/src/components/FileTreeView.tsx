'use client';

import React, { useState, useMemo } from 'react';
import { FaChevronRight, FaChevronDown, FaFolder, FaFolderOpen, FaFile } from 'react-icons/fa';

interface TreeNode {
  name: string;
  path: string;
  isDir: boolean;
  children: TreeNode[];
}

interface FileTreeViewProps {
  /** Newline-delimited file paths (relative to repo root) */
  filePaths: string;
  /** Optional callback when a file is clicked */
  onFileClick?: (path: string) => void;
}

function buildTree(paths: string[]): TreeNode[] {
  const root: TreeNode[] = [];
  const map = new Map<string, TreeNode>();

  for (const p of paths) {
    const parts = p.split('/');
    let current = root;
    let accumulated = '';

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      accumulated = accumulated ? `${accumulated}/${part}` : part;
      const isDir = i < parts.length - 1;

      let node = map.get(accumulated);
      if (!node) {
        node = { name: part, path: accumulated, isDir, children: [] };
        map.set(accumulated, node);
        current.push(node);
      }
      // Promote to dir if we later see children beneath it
      if (isDir && !node.isDir) {
        node.isDir = true;
      }
      current = node.children;
    }
  }

  // Sort: dirs first, then alphabetically
  const sortNodes = (nodes: TreeNode[]) => {
    nodes.sort((a, b) => {
      if (a.isDir !== b.isDir) return a.isDir ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
    for (const n of nodes) sortNodes(n.children);
  };
  sortNodes(root);
  return root;
}

const FileTreeNode: React.FC<{
  node: TreeNode;
  depth: number;
  expanded: Set<string>;
  toggle: (path: string) => void;
  onFileClick?: (path: string) => void;
}> = ({ node, depth, expanded, toggle, onFileClick }) => {
  const isOpen = expanded.has(node.path);
  const indent = depth * 14;

  if (node.isDir) {
    return (
      <>
        <button
          className="flex items-center w-full text-left py-1 px-1 rounded hover:bg-[var(--background)]/70 text-sm transition-colors group"
          style={{ paddingLeft: `${indent + 4}px` }}
          onClick={() => toggle(node.path)}
        >
          <span className="mr-1.5 text-[10px] text-[var(--muted)] flex-shrink-0">
            {isOpen ? <FaChevronDown /> : <FaChevronRight />}
          </span>
          <span className="mr-1.5 text-[var(--accent-primary)] opacity-70 flex-shrink-0">
            {isOpen ? <FaFolderOpen className="text-xs" /> : <FaFolder className="text-xs" />}
          </span>
          <span className="truncate text-[var(--foreground)]">{node.name}</span>
          <span className="ml-auto text-[10px] text-[var(--muted)] opacity-0 group-hover:opacity-100 pl-2 flex-shrink-0">
            {node.children.length}
          </span>
        </button>
        {isOpen &&
          node.children.map((child) => (
            <FileTreeNode
              key={child.path}
              node={child}
              depth={depth + 1}
              expanded={expanded}
              toggle={toggle}
              onFileClick={onFileClick}
            />
          ))}
      </>
    );
  }

  // file icon colour by extension
  const ext = node.name.split('.').pop()?.toLowerCase() ?? '';
  const extColors: Record<string, string> = {
    ts: '#3178c6', tsx: '#3178c6', js: '#f0db4f', jsx: '#f0db4f',
    py: '#3776ab', java: '#b07219', go: '#00add8', rs: '#dea584',
    md: '#083fa1', json: '#292929', yaml: '#cb171e', yml: '#cb171e',
    html: '#e34c26', css: '#563d7c', scss: '#c6538c',
  };
  const fileColor = extColors[ext] || 'var(--muted)';

  return (
    <button
      className="flex items-center w-full text-left py-1 px-1 rounded hover:bg-[var(--background)]/70 text-sm transition-colors"
      style={{ paddingLeft: `${indent + 4}px` }}
      onClick={() => onFileClick?.(node.path)}
    >
      <span className="mr-1.5 flex-shrink-0" style={{ color: fileColor }}>
        <FaFile className="text-[10px]" />
      </span>
      <span className="truncate text-[var(--foreground)]">{node.name}</span>
    </button>
  );
};

const FileTreeView: React.FC<FileTreeViewProps> = ({ filePaths, onFileClick }) => {
  const tree = useMemo(() => {
    const paths = filePaths
      .split('\n')
      .map((p) => p.trim())
      .filter(Boolean);
    return buildTree(paths);
  }, [filePaths]);

  // Auto-expand top-level directories
  const [expanded, setExpanded] = useState<Set<string>>(() => {
    const initial = new Set<string>();
    for (const node of tree) {
      if (node.isDir) initial.add(node.path);
    }
    return initial;
  });

  const toggle = (path: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  if (tree.length === 0) {
    return (
      <div className="text-sm text-[var(--muted)] p-4 text-center">
        No files found.
      </div>
    );
  }

  return (
    <div className="space-y-0.5 text-sm">
      {tree.map((node) => (
        <FileTreeNode
          key={node.path}
          node={node}
          depth={0}
          expanded={expanded}
          toggle={toggle}
          onFileClick={onFileClick}
        />
      ))}
    </div>
  );
};

export default FileTreeView;
