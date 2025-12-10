import React, { useState, useEffect } from 'react';
import { useLocation, useHistory } from '@docusaurus/router';
import apiClient from '../services/api_client';
import styles from './Navigation.module.css';

const Navigation = ({ currentChapterId }) => {
  const [chapters, setChapters] = useState([]);
  const [chapterTocs, setChapterTocs] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedChapters, setExpandedChapters] = useState({});
  const [searchQuery, setSearchQuery] = useState('');
  const [activeSection, setActiveSection] = useState(null);
  const location = useLocation();

  useEffect(() => {
    loadChapters();
  }, []);

  // Update active section when location hash changes
  useEffect(() => {
    if (location.hash) {
      const sectionId = location.hash.replace('#', '');
      if (sectionId) {
        setActiveSection(sectionId);
      }
    }
  }, [location.hash]);

  // Load TOC for a specific chapter
  const loadChapterToc = async (chapterId) => {
    try {
      const toc = await apiClient.getChapterToc(chapterId);
      setChapterTocs(prev => ({
        ...prev,
        [chapterId]: toc
      }));
    } catch (err) {
      console.error(`Error loading TOC for chapter ${chapterId}:`, err);
      // Set an empty TOC so we don't try to reload on every render
      setChapterTocs(prev => ({
        ...prev,
        [chapterId]: { chapterId, title: '', sections: [] }
      }));
    }
  };

  const loadChapters = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getChapters(100, 0); // Get all chapters
      setChapters(response.chapters || []);

      // Preload TOCs for all chapters
      for (const chapter of response.chapters || []) {
        await loadChapterToc(chapter.id);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleChapter = (chapterId) => {
    const isCurrentlyExpanded = expandedChapters[chapterId];

    setExpandedChapters(prev => ({
      ...prev,
      [chapterId]: !isCurrentlyExpanded
    }));

    // Load TOC if not already loaded and expanding
    if (!isCurrentlyExpanded && !chapterTocs[chapterId]) {
      loadChapterToc(chapterId);
    }
  };

  if (loading) {
    return (
      <div className={styles.navigation}>
        <div className={styles.loading}>Loading navigation...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.navigation}>
        <div className={styles.error}>Error loading navigation: {error}</div>
      </div>
    );
  }

  // Filter chapters and sections based on search query
  const filteredResults = searchQuery
    ? chapters.map(chapter => {
        const toc = chapterTocs[chapter.id];
        const matchingSections = toc?.sections?.filter(section =>
          section.title.toLowerCase().includes(searchQuery.toLowerCase())
        ) || [];

        return {
          ...chapter,
          matchingSections
        };
      }).filter(item =>
        item.matchingSections.length > 0 ||
        item.title.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : chapters;

  return (
    <div className={styles.navigation}>
      <h3 className={styles.title}>Textbook Contents</h3>

      <div className={styles.searchContainer}>
        <input
          type="text"
          placeholder="Search sections..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className={styles.searchInput}
        />
      </div>

      <nav className={styles.navList}>
        {filteredResults.map((chapter) => {
          const isExpanded = expandedChapters[chapter.id] || searchQuery !== '';
          const toc = chapterTocs[chapter.id];
          const hasSections = toc && toc.sections && toc.sections.length > 0;
          const matchingSections = searchQuery ? chapter.matchingSections : toc?.sections || [];

          return (
            <div key={chapter.id} className={styles.chapterItem}>
              <div className={styles.chapterHeader}>
                {hasSections && !searchQuery && (
                  <button
                    className={styles.expandButton}
                    onClick={() => toggleChapter(chapter.id)}
                    aria-label={isExpanded ? "Collapse" : "Expand"}
                  >
                    {isExpanded ? '▼' : '►'}
                  </button>
                )}
                <a
                  href={`/chapter/${chapter.id}`}
                  className={`${styles.chapterLink} ${currentChapterId === chapter.id ? styles.active : ''}`}
                >
                  {chapter.order}. {chapter.title}
                </a>
              </div>

              {((hasSections && isExpanded && !searchQuery) || (searchQuery && matchingSections.length > 0)) && (
                <div className={styles.sectionsList}>
                  {matchingSections.map((section, index) => (
                    <div key={section.id || `section-${index}`} className={styles.sectionItem}>
                      <a
                        href={`/chapter/${chapter.id}#${section.id || ''}`}
                        className={`${styles.sectionLink} ${
                          activeSection === section.id ? styles.active : ''
                        }`}
                        onClick={() => {
                          setActiveSection(section.id);
                          setSearchQuery(''); // Clear search after clicking
                        }}
                      >
                        {section.title}
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}

        {searchQuery && filteredResults.length === 0 && (
          <div className={styles.noResults}>
            No sections found matching "{searchQuery}"
          </div>
        )}
      </nav>
    </div>
  );
};

export default Navigation;