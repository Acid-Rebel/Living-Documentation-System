"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import ThemeToggle from "./ThemeToggle";

export default function Navbar() {
  const pathname = usePathname();

  // Helper to determine styles based on active route
  const getLinkStyles = (path: string) => {
    const baseStyles = "px-3 py-2 rounded-md text-sm transition-colors duration-200";
    const activeStyles = "text-blue-600 dark:text-sky-300 font-semibold bg-blue-50/70 dark:bg-slate-900/60";
    const inactiveStyles = "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100/70 dark:hover:bg-slate-900/80";

    return `${baseStyles} ${pathname === path ? activeStyles : inactiveStyles}`;
  };

  return (
    <nav className="sticky top-0 z-50 w-full bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200/80 dark:border-slate-800 shadow-sm">
      <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Link href="/" className="flex-shrink-0 flex items-center gap-3 hover:opacity-90 transition-opacity">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 via-sky-400 to-cyan-300 flex items-center justify-center shadow-lg">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <div className="leading-tight">
              <span className="text-lg font-semibold tracking-tight">LivingDocs</span>
              <span className="block mono-caption text-slate-400">Architecture Intelligence</span>
            </div>
          </Link>

          <div className="hidden md:flex items-center gap-6">
            <Link href="/" className={getLinkStyles("/")}>Projects</Link>
            <Link href="/setup" className={getLinkStyles("/setup")}>CI Setup</Link>
          </div>

          <ThemeToggle />
        </div>
      </div>
    </nav>
  );
}