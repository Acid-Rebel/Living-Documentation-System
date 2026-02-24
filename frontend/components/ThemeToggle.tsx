"use client";

import { useEffect, useState } from "react";
import { Moon, Sun } from "lucide-react";

const STORAGE_KEY = "lds-theme";

type ThemeMode = "light" | "dark";

export default function ThemeToggle() {
    const [mode, setMode] = useState<ThemeMode>("light");

    useEffect(() => {
        const stored = window.localStorage.getItem(STORAGE_KEY) as ThemeMode | null;
        const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
        const initial = stored ?? (prefersDark ? "dark" : "light");
        setMode(initial);
        document.documentElement.classList.toggle("dark", initial === "dark");
    }, []);

    const toggleMode = () => {
        const next = mode === "dark" ? "light" : "dark";
        setMode(next);
        document.documentElement.classList.toggle("dark", next === "dark");
        window.localStorage.setItem(STORAGE_KEY, next);
    };

    return (
        <button
            onClick={toggleMode}
            className="flex items-center gap-2 rounded-full border border-slate-200/70 dark:border-slate-700 bg-white/70 dark:bg-slate-900/70 px-3 py-1.5 text-xs font-semibold text-slate-600 dark:text-slate-200 shadow-sm transition hover:text-slate-900 dark:hover:text-white"
            aria-label="Toggle theme"
        >
            {mode === "dark" ? <Sun size={14} /> : <Moon size={14} />}
            <span className="mono-caption">{mode === "dark" ? "Light" : "Dark"}</span>
        </button>
    );
}
