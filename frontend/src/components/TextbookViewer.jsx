import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useHistory } from '@docusaurus/router';
import apiClient from '../services/api_client';
import styles from './TextbookViewer.module.css';

const TextbookViewer = ({ chapterId, title, content }) => {
  const [currentChapter, setCurrentChapter] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const history = useHistory();

  // If chapterId is provided, load that chapter; otherwise use props
  useEffect(() => {
    if (chapterId) {
      loadChapter(chapterId);
    } else if (content) {
      setCurrentChapter({ id: 'temp', title, content });
    }
  }, [chapterId, title, content]);

  // Load all chapters to enable navigation
  const [chapters, setChapters] = useState([]);
  useEffect(() => {
    const loadAllChapters = async () => {
      try {
        const response = await apiClient.getChapters(100, 0);
        setChapters(response.chapters || []);
      } catch (err) {
        console.error('Error loading chapters for navigation:', err);
      }
    };
    loadAllChapters();
  }, []);

  const loadChapter = async (id) => {
    setLoading(true);
    setError(null);

    try {
      const chapterData = await apiClient.getChapter(id);
      setCurrentChapter(chapterData);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Keyboard navigation
  const navigateToChapter = useCallback((direction) => {
    if (!currentChapter || chapters.length === 0) return;

    const currentIndex = chapters.findIndex(ch => ch.id === currentChapter.id);
    if (currentIndex === -1) return;

    let nextIndex;
    if (direction === 'next' && currentIndex < chapters.length - 1) {
      nextIndex = currentIndex + 1;
    } else if (direction === 'prev' && currentIndex > 0) {
      nextIndex = currentIndex - 1;
    } else {
      return; // No navigation possible
    }

    const nextChapterId = chapters[nextIndex].id;
    history.push(`/chapter/${nextChapterId}`);
    window.location.reload(); // Force reload to update content
  }, [currentChapter, chapters, history]);

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (event) => {
      // Left arrow key for previous chapter
      if (event.key === 'ArrowLeft') {
        navigateToChapter('prev');
      }
      // Right arrow key for next chapter
      else if (event.key === 'ArrowRight') {
        navigateToChapter('next');
      }
      // Ctrl/Cmd + F for search (if we had search functionality)
      else if ((event.ctrlKey || event.metaKey) && event.key === 'f') {
        event.preventDefault();
        // Would open search functionality if implemented
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [navigateToChapter]);

  if (loading) {
    return (
      <div className={styles.textbookViewer}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading chapter...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.textbookViewer}>
        <div className={styles.error}>
          <h2>Error loading chapter</h2>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  if (!currentChapter) {
    return (
      <div className={styles.textbookViewer}>
        <div className={styles.empty}>
          <p>No chapter selected or available.</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.textbookViewer} tabIndex={0} aria-label="Textbook content">
      <header className={styles.chapterHeader}>
        <h1>{currentChapter.title || title}</h1>
        <div className={styles.navigationControls}>
          <button
            onClick={() => navigateToChapter('prev')}
            disabled={chapters.length > 0 && chapters.findIndex(ch => ch.id === currentChapter.id) === 0}
            className={styles.navButton}
            aria-label="Previous chapter"
          >
            ← Previous
          </button>
          <button
            onClick={() => navigateToChapter('next')}
            disabled={chapters.length > 0 && chapters.findIndex(ch => ch.id === currentChapter.id) === chapters.length - 1}
            className={styles.navButton}
            aria-label="Next chapter"
          >
            Next →
          </button>
        </div>
      </header>

      <main className={styles.chapterContent}>
        {currentChapter.content ? (
          <div
            className={styles.contentBody}
            dangerouslySetInnerHTML={{ __html: currentChapter.content }}
          />
        ) : (
          <div className={styles.contentPlaceholder}>
            <p>Chapter content will be displayed here.</p>
          </div>
        )}
      </main>
    </div>
  );
};

export default TextbookViewer;