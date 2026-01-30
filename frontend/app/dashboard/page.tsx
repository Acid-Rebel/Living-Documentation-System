"use client";

import { useSearchParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { Suspense } from "react";


function DashboardContent() {
    const searchParams = useSearchParams();
    const imageUrl = searchParams.get("image");

    if (!imageUrl) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px]">
                <p className="text-gray-400">No diagram selected.</p>
                <Link href="/" className="mt-4 text-blue-500 hover:underline">Go back home</Link>
            </div>
        );
    }

    return (
        <div className="w-full max-w-6xl flex flex-col items-center">
            <div className="w-full flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold">Latest Architecture Diagram</h2>
                <Link href="/" className="px-4 py-2 rounded-lg bg-gray-800 text-sm hover:bg-gray-700 transition">
                    Generate Another
                </Link>
            </div>

            <div className="w-full h-auto bg-white rounded-lg p-2 shadow-2xl overflow-hidden border border-gray-700">
                {/* Using standard img tag for simplicity with external/local generic URLs, or Next Image with configuration */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                    src={imageUrl}
                    alt="Architecture Diagram"
                    className="w-full h-auto object-contain"
                />
            </div>

            <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
                <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
                    <h3 className="font-semibold mb-2 text-blue-400">Classes</h3>
                    <p className="text-sm text-gray-400">Visualizes class structure, inheritance, and composition.</p>
                </div>
                <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
                    <h3 className="font-semibold mb-2 text-purple-400">Dependencies</h3>
                    <p className="text-sm text-gray-400">Maps usages and imports between modules.</p>
                </div>
                <div className="p-6 bg-gray-900 rounded-xl border border-gray-800">
                    <h3 className="font-semibold mb-2 text-green-400">Flow</h3>
                    <p className="text-sm text-gray-400">Traces call stacks and data flow through the system.</p>
                </div>
            </div>
        </div>
    );
}

export default function Dashboard() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <DashboardContent />
        </Suspense>
    )
}
