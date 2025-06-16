import React, { useEffect, useState } from 'react';
import styles from './KnowledgeBasePage.module.css';

interface Article {
  agent: string;
  agent_name: string;
  category: string;
  title: string;
  content: string;
  keywords: string[];
  type: string;
}

export const KnowledgeBasePage: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchArticles = async (q = '') => {
    setLoading(true);
    setError(null);
    try {
      const url = q ? `/api/v1/knowledge?q=${encodeURIComponent(q)}` : '/api/v1/knowledge';
      const res = await fetch(url);
      if (!res.ok) throw new Error('Failed to fetch articles');
      const data = await res.json();
      setArticles(data.articles || []);
    } catch (err: any) {
      setError(err.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchArticles(search);
  };

  return (
    <div className={styles.knowledgeBasePage}>
      <header className={styles.header}>
        <h1>Knowledge Base</h1>
        <form onSubmit={handleSearch}>
          <input
            className={styles.searchInput}
            type="text"
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search knowledge articles..."
          />
        </form>
      </header>
      <section className={styles.articlesSection}>
        {loading && <div className={styles.placeholder}>Loading...</div>}
        {error && <div className={styles.placeholder} style={{color: 'red'}}>{error}</div>}
        {!loading && !error && articles.length === 0 && (
          <div className={styles.placeholder}>No articles found.</div>
        )}
        {!loading && !error && articles.length > 0 && (
          <ul className={styles.articleList}>
            {articles.map((a, i) => (
              <li key={i} className={styles.articleItem}>
                <h3>{a.title}</h3>
                <div className={styles.meta}>
                  <span>Agent: {a.agent_name}</span>
                  <span>Category: {a.category}</span>
                </div>
                <p>{a.content}</p>
                {a.keywords.length > 0 && (
                  <div className={styles.keywords}>
                    <strong>Keywords:</strong> {a.keywords.join(', ')}
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}; 