import Head from "next/head";
import Link from "next/link";
import { useState, useEffect } from "react";
import styles from "@/styles/Home.module.css";

interface PageListItem {
  id: number;
  name: string;
  slug: string;
  title: string;
}

export default function CmsIndex() {
  const [pages, setPages] = useState<PageListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPages = async () => {
      try {
        setLoading(true);
        const response = await fetch("http://localhost:8219/api/cms/pages");

        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const result = await response.json();

        if (!result.success) {
          throw new Error(result.error || 'Erreur lors du chargement des pages');
        }

        setPages(result.data || []);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur lors du chargement des pages');
        console.error("Erreur:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPages();
  }, []);

  return (
    <>
      <Head>
        <title>CMS Pages</title>
        <meta name="description" content="Liste des pages CMS" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={styles.page}>
        <main className={styles.main}>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '2rem' }}>
            Pages CMS
          </h1>

          {loading && <p>Chargement des pages...</p>}

          {error && (
            <div style={{ color: "red", padding: "1rem", border: "1px solid red", borderRadius: "4px" }}>
              <strong>Erreur:</strong> {error}
            </div>
          )}

          {!loading && !error && pages.length === 0 && (
            <p>Aucune page trouvée</p>
          )}

          {!loading && !error && pages.length > 0 && (
            <div style={{
              display: 'grid',
              gap: '1rem',
              width: '100%',
              maxWidth: '800px',
              gridTemplateColumns: '1fr'
            }}>
              {pages.map((page) => (
                <Link
                  key={page.id}
                  href={`/cms/${page.slug}`}
                  style={{
                    padding: '1.5rem',
                    border: '1px solid #e0e0e0',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    color: 'inherit',
                    transition: 'all 0.2s',
                    backgroundColor: '#f9f9f9'
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.borderColor = '#667eea';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.borderColor = '#e0e0e0';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.5rem' }}>
                    {page.title}
                  </h2>
                  <p style={{ margin: 0, color: '#666', fontSize: '0.9rem' }}>
                    /{page.slug}
                  </p>
                </Link>
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}
