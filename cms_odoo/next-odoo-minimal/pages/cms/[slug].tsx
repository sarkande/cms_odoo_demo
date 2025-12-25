import Head from "next/head";
import { useRouter } from "next/router";
import { useState, useEffect } from "react";
import BlockRenderer from "@/components/blocks/BlockRenderer";
import styles from "@/styles/Home.module.css";

interface BlockData {
  id: number;
  name: string;
  type: string;
  sequence: number;
  [key: string]: any;
}

interface PageData {
  id: number;
  name: string;
  slug: string;
  title: string;
  meta_description: string;
  blocks: BlockData[];
}

export default function CmsPage() {
  const router = useRouter();
  const { slug } = router.query;

  const [pageData, setPageData] = useState<PageData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!slug) return;

    const fetchPage = async () => {
      try {
        setLoading(true);
        const response = await fetch(`http://localhost:8219/api/cms/page/${slug}`);

        if (!response.ok) {
          throw new Error(`Erreur HTTP: ${response.status}`);
        }

        const result = await response.json();

        if (!result.success) {
          throw new Error(result.error || 'Erreur lors du chargement de la page');
        }

        setPageData(result.data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erreur lors du chargement de la page');
        console.error("Erreur:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchPage();
  }, [slug]);

  if (loading) {
    return (
      <div className={styles.page}>
        <main className={styles.main}>
          <p>Chargement de la page...</p>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.page}>
        <main className={styles.main}>
          <div style={{ color: "red", padding: "1rem", border: "1px solid red", borderRadius: "4px" }}>
            <strong>Erreur:</strong> {error}
          </div>
        </main>
      </div>
    );
  }

  if (!pageData) {
    return (
      <div className={styles.page}>
        <main className={styles.main}>
          <p>Page non trouvée</p>
        </main>
      </div>
    );
  }

  return (
    <>
      <Head>
        <title>{pageData.title}</title>
        <meta name="description" content={pageData.meta_description} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className={styles.page}>
        <main className={styles.main}>
          <div style={{ width: '100%', maxWidth: '1200px', padding: '0 1rem' }}>
            {pageData.blocks.map((block) => (
              <BlockRenderer key={block.id} block={block} />
            ))}
          </div>
        </main>
      </div>
    </>
  );
}
