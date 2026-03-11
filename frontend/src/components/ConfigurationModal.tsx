'use client';

import React, { useState } from 'react';
import { useLanguage } from '@/contexts/LanguageContext';
import TokenInput from '@/components/TokenInput';

interface ConfigurationModalProps {
  isOpen: boolean;
  onClose: () => void;

  // Repository input
  repositoryInput: string;

  // Language selection
  selectedLanguage: string;
  setSelectedLanguage: (value: string) => void;
  supportedLanguages: Record<string, string>;

  // Wiki type options
  isComprehensiveView: boolean;
  setIsComprehensiveView: (value: boolean) => void;

  // Model selection
  provider: string;
  setProvider: (value: string) => void;
  model: string;
  setModel: (value: string) => void;
  isCustomModel: boolean;
  setIsCustomModel: (value: boolean) => void;
  customModel: string;
  setCustomModel: (value: string) => void;

  // Platform selection
  selectedPlatform: 'github' | 'gitlab' | 'bitbucket';
  setSelectedPlatform: (value: 'github' | 'gitlab' | 'bitbucket') => void;

  // Access token
  accessToken: string;
  setAccessToken: (value: string) => void;

  // File filter options
  excludedDirs: string;
  setExcludedDirs: (value: string) => void;
  excludedFiles: string;
  setExcludedFiles: (value: string) => void;
  includedDirs: string;
  setIncludedDirs: (value: string) => void;
  includedFiles: string;
  setIncludedFiles: (value: string) => void;

  // Form submission
  onSubmit: () => void;
  isSubmitting: boolean;

  // Authentication
  authRequired?: boolean;
  authCode?: string;
  setAuthCode?: (code: string) => void;
  isAuthLoading?: boolean;
}

export default function ConfigurationModal(props: ConfigurationModalProps) {
  const { messages: t } = useLanguage();
  const [showTokenSection, setShowTokenSection] = useState(false);

  if (!props.isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex min-h-screen items-center justify-center p-4 text-center bg-black/50">
        <div className="relative transform overflow-hidden rounded-lg bg-[var(--card-bg)] text-left shadow-xl transition-all sm:my-8 sm:max-w-2xl sm:w-full">
          <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-color)]">
            <h3 className="text-lg font-medium text-[var(--accent-primary)]">
              <span className="text-[var(--accent-primary)]">{t.form?.configureWiki || 'Configure Docs'}</span>
            </h3>
            <button
              type="button"
              onClick={props.onClose}
              className="text-[var(--muted)] hover:text-[var(--foreground)] focus:outline-none transition-colors"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <div className="p-6 max-h-[70vh] overflow-y-auto">
            <div className="mb-4">
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                {t.form?.repository || 'Repository'}
              </label>
              <div className="bg-[var(--background)]/70 p-3 rounded-md border border-[var(--border-color)] text-sm text-[var(--foreground)]">
                {props.repositoryInput}
              </div>
            </div>

            <div className="mb-4">
              <label htmlFor="language-select" className="block text-sm font-medium text-[var(--foreground)] mb-2">
                {t.form?.wikiLanguage || 'Docs Language'}
              </label>
              <select
                id="language-select"
                value={props.selectedLanguage}
                onChange={(e) => props.setSelectedLanguage(e.target.value)}
                className="input-japanese block w-full px-3 py-2 text-sm rounded-md bg-transparent text-[var(--foreground)] focus:outline-none focus:border-[var(--accent-primary)]"
              >
                {Object.entries(props.supportedLanguages).map(([key, value]) => (
                  <option key={key} value={key}>{value}</option>
                ))}
              </select>
            </div>

            <div className="mb-4">
              <label className="block text-sm font-medium text-[var(--foreground)] mb-2">
                {t.form?.wikiType || 'Docs Type'}
              </label>
              <div className="flex gap-3">
                <button
                  type="button"
                  onClick={() => props.setIsComprehensiveView(true)}
                  className={`flex-1 flex items-center justify-between p-2 rounded-md border transition-colors ${
                    props.isComprehensiveView
                      ? 'bg-[var(--accent-primary)]/10 border-[var(--accent-primary)]/30 text-[var(--accent-primary)]'
                      : 'bg-[var(--background)]/50 border-[var(--border-color)] text-[var(--foreground)] hover:bg-[var(--background)]'
                  }`}
                >
                  <div className="text-left">
                    <div className="font-medium text-sm">{t.form?.comprehensive || 'Comprehensive'}</div>
                    <div className="text-xs opacity-80">
                      {t.form?.comprehensiveDescription || 'Detailed docs with structured sections and more pages'}
                    </div>
                  </div>
                  {props.isComprehensiveView && (
                    <div className="ml-2 h-4 w-4 rounded-full bg-[var(--accent-primary)]/20 flex items-center justify-center">
                      <div className="h-2 w-2 rounded-full bg-[var(--accent-primary)]"></div>
                    </div>
                  )}
                </button>

                <button
                  type="button"
                  onClick={() => props.setIsComprehensiveView(false)}
                  className={`flex-1 flex items-center justify-between p-2 rounded-md border transition-colors ${
                    !props.isComprehensiveView
                      ? 'bg-[var(--accent-primary)]/10 border-[var(--accent-primary)]/30 text-[var(--accent-primary)]'
                      : 'bg-[var(--background)]/50 border-[var(--border-color)] text-[var(--foreground)] hover:bg-[var(--background)]'
                  }`}
                >
                  <div className="text-left">
                    <div className="font-medium text-sm">{t.form?.concise || 'Concise'}</div>
                    <div className="text-xs opacity-80">
                      {t.form?.conciseDescription || 'Simplified docs with fewer pages and essential information'}
                    </div>
                  </div>
                  {!props.isComprehensiveView && (
                    <div className="ml-2 h-4 w-4 rounded-full bg-[var(--accent-primary)]/20 flex items-center justify-center">
                      <div className="h-2 w-2 rounded-full bg-[var(--accent-primary)]"></div>
                    </div>
                  )}
                </button>
              </div>
            </div>

            {/* Access Token for Private Repositories */}
            <TokenInput
              selectedPlatform={props.selectedPlatform}
              setSelectedPlatform={props.setSelectedPlatform}
              accessToken={props.accessToken}
              setAccessToken={props.setAccessToken}
              showTokenSection={showTokenSection}
              onToggleTokenSection={() => setShowTokenSection(!showTokenSection)}
            />
          </div>

          <div className="flex items-center justify-end gap-2 px-6 py-4 border-t border-[var(--border-color)]">
            <button
              type="button"
              onClick={props.onClose}
              className="px-4 py-2 text-sm font-medium rounded-md border border-[var(--border-color)]/50 text-[var(--muted)] bg-transparent hover:bg-[var(--background)] hover:text-[var(--foreground)] transition-colors"
            >
              {t.common?.cancel || 'Cancel'}
            </button>
            <button
              type="button"
              onClick={props.onSubmit}
              disabled={props.isSubmitting}
              className="px-4 py-2 text-sm font-medium rounded-md border border-transparent bg-[var(--accent-primary)]/90 text-white hover:bg-[var(--accent-primary)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {props.isSubmitting ? (t.common?.processing || 'Processing...') : (t.common?.generateWiki || 'Generate Docs')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
