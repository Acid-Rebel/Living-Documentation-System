import Link from "next/link";
import fs from "fs";
import path from "path";

export default async function Setup() {
    // Read the template file from the server
    let templateContent = "";
    try {
        // Trying to read from where we saved it in the root
        // In Next.js server component, we can read files.
        // But we need to know the path relative to the process.cwd()
        // The app is running in /root/Living-Documentation-System/frontend usually during dev
        // So the file is ../doc-update.yml.template
        const templatePath = path.join(process.cwd(), "..", "doc-update.yml.template");
        templateContent = fs.readFileSync(templatePath, "utf-8");
    } catch (e) {
        templateContent = "# Error reading template file. Please verify backend setup.";
    }

    return (
        <div className="w-full max-w-4xl">
            <div className="mb-6">
                <Link href="/" className="text-blue-600 hover:text-blue-700 font-medium">← Back to Home</Link>
            </div>

            <div className="rounded-[28px] border border-slate-200/70 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 p-8">
                <p className="mono-caption text-slate-400">Automation</p>
                <h1 className="text-3xl font-semibold mb-4 text-slate-900 dark:text-white">Continuous Integration Setup</h1>

                <p className="mb-8 text-slate-600 dark:text-slate-300">
                    To automatically generate and update diagrams on every push, add this GitHub Action to your repository.
                </p>

                <div className="space-y-6">
                    <div className="step">
                        <h3 className="text-lg font-semibold mb-2 text-slate-800 dark:text-slate-100">1. Create the Workflow File</h3>
                        <p className="text-slate-600 dark:text-slate-400 mb-2">Create a new file in your repository at:</p>
                        <code className="bg-slate-100 dark:bg-slate-950 px-3 py-1 rounded text-sm text-amber-600 border border-amber-200/70 dark:border-amber-900/50">.github/workflows/doc-update.yml</code>
                    </div>

                    <div className="step">
                        <h3 className="text-lg font-semibold mb-2 text-slate-800 dark:text-slate-100">2. Paste the Configuration</h3>
                        <div className="relative">
                            <pre className="p-6 rounded-2xl bg-slate-950 text-slate-50 border border-slate-800 overflow-x-auto text-sm shadow-md">
                                <code>{templateContent}</code>
                            </pre>
                        </div>
                    </div>

                    <div className="step">
                        <h3 className="text-lg font-semibold mb-2 text-slate-800 dark:text-slate-100">3. Configure Secrets (Optional)</h3>
                        <p className="text-slate-600 dark:text-slate-400">
                            If your backend is protected, you may need to add authentication headers in the `curl` command using GitHub Secrets.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
