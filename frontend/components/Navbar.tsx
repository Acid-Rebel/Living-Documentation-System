"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Navbar() {
  const pathname = usePathname();

  // Helper to determine styles based on active route
  const getLinkStyles = (path: string) => {
    const baseStyles = "px-3 py-2 rounded-md text-sm transition-colors duration-200";
    const activeStyles = "text-brand-primary font-medium bg-brand-light-bg";
    const inactiveStyles = "text-brand-light-muted hover:text-brand-light-text hover:bg-brand-light-surface";
    
    return `${baseStyles} ${pathname === path ? activeStyles : inactiveStyles}`;
  };

  return (
    <nav className="sticky top-0 z-50 w-full bg-brand-light-surface/80 backdrop-blur-md border-b border-brand-light-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          
          {/* Branding - Link added so clicking logo takes you home */}
          <Link href="/" className="flex-shrink-0 flex items-center gap-2 hover:opacity-90 transition-opacity">
            <div className="w-8 h-8 rounded-lg bg-brand-primary flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
            </div>
            <span className="text-xl font-bold ">
              LivingDocs
            </span>
          </Link>

          {/* Navigation */}
          <div className="hidden md:flex space-x-8">
            <Link
              href="/"
              className={getLinkStyles("/")}
            >
              Projects
            </Link>
          </div>
          
        </div>
      </div>
    </nav>
  );
}