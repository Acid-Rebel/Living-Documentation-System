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
                <Link href="/" className="text-blue-500 hover:text-blue-400">← Back to Home</Link>
            </div>

            <h1 className="text-3xl font-bold mb-6">Continuous Integration Setup</h1>

            <p className="mb-6 text-gray-300">
                To automatically generate and update diagrams on every push, add this GitHub Action to your repository.
            </p>

            <div className="space-y-6">
                <div className="step">
                    <h3 className="text-xl font-semibold mb-2">1. Create the Workflow File</h3>
                    <p className="text-gray-400 mb-2">Create a new file in your repository at:</p>
                    <code className="bg-gray-800 px-3 py-1 rounded text-sm text-yellow-500">.github/workflows/doc-update.yml</code>
                </div>

                <div className="step">
                    <h3 className="text-xl font-semibold mb-2">2. Paste the Configuration</h3>
                    <div className="relative">
                        <pre className="p-6 rounded-xl bg-gray-900 border border-gray-700 overflow-x-auto text-sm">
                            <code className="text-gray-300">{templateContent}</code>
                        </pre>
                    </div>
                </div>

                <div className="step">
                    <h3 className="text-xl font-semibold mb-2">3. Configure Secrets (Optional)</h3>
                    <p className="text-gray-400">
                        If your backend is protected, you may need to add authentication headers in the `curl` command using GitHub Secrets.
                    </p>
                </div>
            </div>
        </div>
    );
}
