"use client";

import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";

function DashboardContent() {
  const searchParams = useSearchParams();
  const imageUrl = searchParams.get("image");

  if (!imageUrl) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50">
        <p className="text-slate-500 text-lg">No diagram selected</p>
        <Link
          href="/"
          className="mt-6 px-5 py-2 rounded-lg bg-blue-600 text-white shadow hover:bg-blue-700 transition"
        >
          Go back home
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Header */}
      <header className="w-full bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold text-slate-900 tracking-tight">
            Architecture Dashboard
          </h1>

          <Link
            href="/"
            className="px-4 py-2 rounded-lg text-blue-600 bg-blue-50 hover:bg-blue-100 text-sm font-medium transition"
          >
            Generate Another
          </Link>
          <a
            href={imageUrl}
            download="diagram.png"
            className="ml-3 px-4 py-2 rounded-lg bg-blue-600 text-white text-sm font-medium shadow hover:bg-blue-700 transition flex items-center gap-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="7 10 12 15 17 10" /><line x1="12" x2="12" y1="15" y2="3" /></svg>
            Download PNG
          </a>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-10 flex flex-col gap-10">
        {/* Diagram Section */}
        <section className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-lg font-semibold text-slate-800 mb-5">
            Latest Diagram
          </h2>

          <div className="rounded-xl border border-slate-200 bg-slate-100 p-4 flex items-center justify-center">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={imageUrl}
              alt="Architecture Diagram"
              className="max-h-[650px] w-auto object-contain rounded-lg"
            />
          </div>
        </section>

        {/* Info Cards */}
        <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: "Classes",
              desc: "Visualizes class structure, inheritance and relationships.",
            },
            {
              title: "Dependencies",
              desc: "Tracks imports and module coupling across the system.",
            },
            {
              title: "Flow",
              desc: "Shows call stacks and runtime data flow paths.",
            },
          ].map((item) => (
            <div
              key={item.title}
              className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm hover:shadow-md transition"
            >
              <h3 className="font-semibold text-slate-900 mb-2">
                {item.title}
              </h3>
              <p className="text-sm text-slate-600 leading-relaxed">
                {item.desc}
              </p>
            </div>
          ))}
        </section>
      </main>
    </div>
  );
}

export default function Dashboard() {
  return (
    <Suspense fallback={<div className="p-6">Loading...</div>}>
      <DashboardContent />
    </Suspense>
  );
}
