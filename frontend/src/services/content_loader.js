import apiClient from './api_client';

class ContentLoader {
  constructor() {
    this.cache = new Map();
    this.loadingPromises = new Map();
  }

  /**
   * Load all textbook chapters with pagination
   */
  async loadAllChapters(limit = 100, offset = 0) {
    const cacheKey = `chapters_${limit}_${offset}`;

    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Check if already loading
    if (this.loadingPromises.has(cacheKey)) {
      return this.loadingPromises.get(cacheKey);
    }

    const loadingPromise = apiClient.getChapters(limit, offset)
      .then(data => {
        this.cache.set(cacheKey, data);
        this.loadingPromises.delete(cacheKey);
        return data;
      })
      .catch(error => {
        this.loadingPromises.delete(cacheKey);
        throw error;
      });

    this.loadingPromises.set(cacheKey, loadingPromise);
    return loadingPromise;
  }

  /**
   * Load a specific chapter by ID
   */
  async loadChapter(chapterId) {
    const cacheKey = `chapter_${chapterId}`;

    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Check if already loading
    if (this.loadingPromises.has(cacheKey)) {
      return this.loadingPromises.get(cacheKey);
    }

    const loadingPromise = apiClient.getChapter(chapterId)
      .then(data => {
        this.cache.set(cacheKey, data);
        this.loadingPromises.delete(cacheKey);
        return data;
      })
      .catch(error => {
        this.loadingPromises.delete(cacheKey);
        throw error;
      });

    this.loadingPromises.set(cacheKey, loadingPromise);
    return loadingPromise;
  }

  /**
   * Load table of contents for a chapter
   */
  async loadChapterToc(chapterId) {
    const cacheKey = `toc_${chapterId}`;

    // Check cache first
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    // Check if already loading
    if (this.loadingPromises.has(cacheKey)) {
      return this.loadingPromises.get(cacheKey);
    }

    const loadingPromise = apiClient.getChapterToc(chapterId)
      .then(data => {
        this.cache.set(cacheKey, data);
        this.loadingPromises.delete(cacheKey);
        return data;
      })
      .catch(error => {
        this.loadingPromises.delete(cacheKey);
        throw error;
      });

    this.loadingPromises.set(cacheKey, loadingPromise);
    return loadingPromise;
  }

  /**
   * Load all chapters and their TOCs in parallel
   */
  async loadTextbookStructure() {
    try {
      const chaptersData = await this.loadAllChapters();
      const chapters = chaptersData.chapters;

      // Load TOCs for all chapters in parallel
      const tocPromises = chapters.map(chapter =>
        this.loadChapterToc(chapter.id).catch(() => ({
          chapterId: chapter.id,
          title: chapter.title,
          sections: []
        }))
      );

      const tocs = await Promise.all(tocPromises);

      return {
        chapters,
        tocs: tocs.reduce((acc, toc) => {
          acc[toc.chapterId] = toc;
          return acc;
        }, {}),
        total: chaptersData.total
      };
    } catch (error) {
      console.error('Error loading textbook structure:', error);
      throw error;
    }
  }

  /**
   * Clear cache for specific content
   */
  clearCache(key) {
    if (key) {
      this.cache.delete(key);
    } else {
      this.cache.clear();
    }
  }

  /**
   * Preload content for better performance
   */
  async preloadContent(chapterIds) {
    const promises = chapterIds.map(id => this.loadChapter(id));
    return Promise.allSettled(promises);
  }
}

// Create a singleton instance
const contentLoader = new ContentLoader();
export default contentLoader;

// Export the class for potential multiple instances if needed
export { ContentLoader };