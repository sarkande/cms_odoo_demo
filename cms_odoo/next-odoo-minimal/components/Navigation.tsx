import Link from 'next/link';
import { useState, useEffect } from 'react';
import { useTranslation } from '@/contexts/TranslationContext';
import LanguageSelector from './LanguageSelector';
import styles from './Navigation.module.scss';

interface Page {
  id: number;
  name: string;
  slug: string;
  title: string;
}

export default function Navigation() {
  const [pages, setPages] = useState<Page[]>([]);
  const { t } = useTranslation();

  useEffect(() => {
    const fetchPages = async () => {
      try {
        const response = await fetch('http://localhost:8219/api/cms/pages');
        const result = await response.json();
        if (result.success) {
          setPages(result.data || []);
        }
      } catch (err) {
        console.error('Error fetching pages:', err);
      }
    };

    fetchPages();
  }, []);

  return (
    <nav className={styles.nav}>
      <div className={styles.container}>
        <div className={styles.links}>
          {pages.map((page) => (
            <Link key={page.id} href={`/${page.slug}`} className={styles.link}>
              {t(`nav.${page.slug}`)}
            </Link>
          ))}
        </div>
        <LanguageSelector />
      </div>
    </nav>
  );
}
