class ApiClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.defaultHeaders = {
      'Content-Type': 'application/json',
    };
  }

  // Helper method to make API requests
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        ...this.defaultHeaders,
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);

      // Handle different response types
      const contentType = response.headers.get('content-type');
      let data;

      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else {
        data = await response.text();
      }

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Textbook-related methods
  async getChapters(limit = 10, offset = 0) {
    const params = new URLSearchParams({ limit: limit.toString(), offset: offset.toString() });
    return this.request(`/textbook/chapters?${params}`);
  }

  async getChapter(chapterId) {
    return this.request(`/textbook/chapters/${chapterId}`);
  }

  async getChapterToc(chapterId) {
    return this.request(`/textbook/chapters/${chapterId}/toc`);
  }

  // AI-related methods
  async queryAI(question, context = null, sessionId = null, userId = null) {
    // For backward compatibility, accept individual parameters
    const body = {
      question,
      context: context || null,
      sessionId: sessionId || null,
      userId: userId || null,
    };

    return this.request('/ai/query', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Alternative method that accepts an object for easier use in components
  async queryAIObject(requestData) {
    const body = {
      question: requestData.question,
      context: requestData.context || null,
      sessionId: requestData.sessionId || null,
      userId: requestData.userId || null,
    };

    return this.request('/ai/query', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  // Streaming method for real-time responses using fetch and ReadableStream
  queryAIStream(requestData, onMessage, onError) {
    return new Promise((resolve, reject) => {
      const body = {
        question: requestData.question,
        context: requestData.context || null,
        sessionId: requestData.sessionId || null,
        userId: requestData.userId || null,
      };

      const url = `${this.baseURL}/ai/query/stream`;
      const config = {
        method: 'POST',
        headers: {
          ...this.defaultHeaders,
        },
        body: JSON.stringify(body),
      };

      fetch(url, config)
        .then(response => {
          if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
          }

          if (!response.body) {
            throw new Error('ReadableStream not supported in this browser');
          }

          const reader = response.body.getReader();
          const decoder = new TextDecoder();
          let buffer = '';

          const processStream = () => {
            reader.read().then(({ done, value }) => {
              if (done) {
                resolve();
                return;
              }

              buffer += decoder.decode(value, { stream: true });
              const lines = buffer.split('\n');
              buffer = lines.pop(); // Keep last incomplete line in buffer

              for (const line of lines) {
                if (line.startsWith('data: ')) {
                  try {
                    const data = JSON.parse(line.slice(6)); // Remove 'data: ' prefix
                    onMessage(data);
                  } catch (e) {
                    console.error('Error parsing SSE data:', e);
                  }
                }
              }

              processStream(); // Continue reading
            }).catch(error => {
              console.error('Stream reading error:', error);
              if (onError) onError(error);
              reject(error);
            });
          };

          processStream();
        })
        .catch(error => {
          console.error('Streaming request failed:', error);
          if (onError) onError(error);
          reject(error);
        });
    });
  }

  async validateQuestion(question, context) {
    const body = {
      question,
      context,
    };

    return this.request('/ai/validate', {
      method: 'POST',
      body: JSON.stringify(body),
    });
  }

  async getSessionHistory(sessionId) {
    return this.request(`/ai/sessions/${sessionId}`);
  }

  // Health check
  async healthCheck() {
    return this.request('/health');
  }
}

// Create a singleton instance
const apiClient = new ApiClient();
export default apiClient;

// Export the class for potential multiple instances if needed
export { ApiClient };