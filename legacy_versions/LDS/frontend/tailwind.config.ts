import type { Config } from "tailwindcss";

const config: Config = {
    darkMode: "class",
    content: [
        "./app/**/*.{js,ts,jsx,tsx,mdx}",
        "./components/**/*.{js,ts,jsx,tsx,mdx}",
    ],
    theme: {
        extend: {
            fontFamily: {
                display: ["var(--font-display)", "ui-sans-serif", "system-ui"],
                mono: ["var(--font-mono)", "ui-monospace", "SFMono-Regular"],
            },
            backgroundImage: {
                "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
                "gradient-conic":
                    "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
            },
            colors: {
                "brand-dark": "#0f172a",
                "brand-primary": "#3b82f6",
                "brand-accent": "#8b5cf6",
                // Professional Light Theme Colors
                "brand-light-bg": "#f8fafc", // Slate-50
                "brand-light-surface": "#ffffff", // White
                "brand-light-text": "#0f172a", // Slate-900
                "brand-light-muted": "#64748b", // Slate-500
                "brand-light-border": "#e2e8f0", // Slate-200
            },
        },
    },
    plugins: [],
};
export default config;
