import { useTranslation } from '@/contexts/TranslationContext';
import styles from './LanguageSelector.module.scss';

export default function LanguageSelector() {
  const { currentLang, setLanguage, availableLanguages } = useTranslation();

  if (availableLanguages.length === 0) {
    return null;
  }

  return (
    <div className={styles.languageSelector}>
      <select
        value={currentLang}
        onChange={(e) => setLanguage(e.target.value)}
        className={styles.select}
      >
        {availableLanguages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
}
