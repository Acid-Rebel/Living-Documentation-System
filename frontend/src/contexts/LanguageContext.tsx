/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { locales } from '@/i18n';

type Messages = Record<string, any>;
type LanguageContextType = {
  language: string;
  setLanguage: (lang: string) => void;
  messages: Messages;
  supportedLanguages: Record<string, string>;
};

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [language, setLanguageState] = useState<string>('en');
  const [messages, setMessages] = useState<Messages>({});
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [supportedLanguages, setSupportedLanguages] = useState({});
  const [defaultLanguage, setDefaultLanguage] = useState('en');

  const detectBrowserLanguage = (): string => {
    try {
      if (typeof window === 'undefined' || typeof navigator === 'undefined') {
        return 'en';
      }

      const browserLang = navigator.language || (navigator as any).userLanguage || '';
      if (!browserLang) {
        return 'en';
      }

      const langCode = browserLang.split('-')[0].toLowerCase();
      if (locales.includes(langCode as any)) {
        return langCode;
      }

      if (langCode === 'zh') {
        if (browserLang.includes('TW') || browserLang.includes('HK')) {
          return 'zh';
        }
        return 'zh';
      }

      return 'en';
    } catch (error) {
      console.error('Error detecting browser language:', error);
      return 'en';
    }
  };

  useEffect(() => {
    const getSupportedLanguages = async () => {
      try {
        const response = await fetch('/api/lang/config');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setSupportedLanguages(data.supported_languages);
        setDefaultLanguage(data.default);
      } catch (err) {
        console.error('Failed to fetch language config:', err);
        const defaultSupportedLanguages = {
          en: 'English',
          ja: 'Japanese (\u65e5\u672c\u8a9e)',
          zh: 'Mandarin Chinese (\u4e2d\u6587)',
          'zh-tw': 'Traditional Chinese (\u7e41\u9ad4\u4e2d\u6587)',
          es: 'Spanish (Espa\u00f1ol)',
          kr: 'Korean (\ud55c\uad6d\uc5b4)',
          vi: 'Vietnamese (Ti\u1ebfng Vi\u1ec7t)',
          'pt-br': 'Brazilian Portuguese (Portugu\u00eas Brasileiro)',
          fr: 'Fran\u00e7ais (French)',
          ru: '\u0420\u0443\u0441\u0441\u043a\u0438\u0439 (Russian)',
        };
        setSupportedLanguages(defaultSupportedLanguages);
        setDefaultLanguage('en');
      }
    };

    getSupportedLanguages();
  }, []);

  useEffect(() => {
    if (Object.keys(supportedLanguages).length > 0) {
      const loadLanguage = async () => {
        try {
          let storedLanguage;
          if (typeof window !== 'undefined') {
            storedLanguage = localStorage.getItem('language');

            if (!storedLanguage) {
              storedLanguage = detectBrowserLanguage();
              localStorage.setItem('language', storedLanguage);
            }
          } else {
            storedLanguage = 'en';
          }

          const validLanguage = Object.keys(supportedLanguages).includes(storedLanguage as any)
            ? storedLanguage
            : defaultLanguage;

          const langMessages = (await import(`../messages/${validLanguage}.json`)).default;

          setLanguageState(validLanguage);
          setMessages(langMessages);

          if (typeof document !== 'undefined') {
            document.documentElement.lang = validLanguage;
          }
        } catch (error) {
          console.error('Failed to load language:', error);
          const enMessages = (await import('../messages/en.json')).default;
          setMessages(enMessages);
        } finally {
          setIsLoading(false);
        }
      };

      loadLanguage();
    }
  }, [supportedLanguages, defaultLanguage]);

  const setLanguage = async (lang: string) => {
    try {
      const validLanguage = Object.keys(supportedLanguages).includes(lang as any) ? lang : defaultLanguage;
      const langMessages = (await import(`../messages/${validLanguage}.json`)).default;

      setLanguageState(validLanguage);
      setMessages(langMessages);

      if (typeof window !== 'undefined') {
        localStorage.setItem('language', validLanguage);
      }

      if (typeof document !== 'undefined') {
        document.documentElement.lang = validLanguage;
      }
    } catch (error) {
      console.error('Failed to set language:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-100 dark:bg-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, messages, supportedLanguages }}>
      {children}
    </LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (context === undefined) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
}