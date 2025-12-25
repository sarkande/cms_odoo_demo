import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface Language {
  code: string;
  name: string;
  iso_code: string;
}

interface TranslationContextType {
  t: (key: string) => string;
  currentLang: string;
  setLanguage: (lang: string) => void;
  availableLanguages: Language[];
  loading: boolean;
}

const TranslationContext = createContext<TranslationContextType | undefined>(undefined);

interface TranslationProviderProps {
  children: ReactNode;
}

export function TranslationProvider({ children }: TranslationProviderProps) {
  const [currentLang, setCurrentLang] = useState<string>('en_US');
  const [translations, setTranslations] = useState<Record<string, string>>({});
  const [availableLanguages, setAvailableLanguages] = useState<Language[]>([]);
  const [loading, setLoading] = useState(true);

  // Charger les langues disponibles
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await fetch('http://localhost:8219/api/languages');
        const result = await response.json();
        if (result.success) {
          setAvailableLanguages(result.data || []);
        }
      } catch (error) {
        console.error('Error fetching languages:', error);
      }
    };

    fetchLanguages();
  }, []);

  // Charger les traductions pour la langue courante
  useEffect(() => {
    const fetchTranslations = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8219/api/translations/${currentLang}`);
        const result = await response.json();
        if (result.success) {
          setTranslations(result.data || {});
        }
      } catch (error) {
        console.error('Error fetching translations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTranslations();
  }, [currentLang]);

  // Fonction de traduction
  const t = (key: string): string => {
    return translations[key] || key;
  };

  // Changer de langue
  const setLanguage = (lang: string) => {
    setCurrentLang(lang);
    // Sauvegarder dans localStorage
    if (typeof window !== 'undefined') {
      localStorage.setItem('preferred_language', lang);
    }
  };

  // Charger la langue préférée au démarrage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedLang = localStorage.getItem('preferred_language');
      if (savedLang) {
        setCurrentLang(savedLang);
      }
    }
  }, []);

  return (
    <TranslationContext.Provider value={{ t, currentLang, setLanguage, availableLanguages, loading }}>
      {children}
    </TranslationContext.Provider>
  );
}

export function useTranslation() {
  const context = useContext(TranslationContext);
  if (context === undefined) {
    throw new Error('useTranslation must be used within a TranslationProvider');
  }
  return context;
}
