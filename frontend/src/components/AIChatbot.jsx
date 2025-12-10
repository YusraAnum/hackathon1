import React, { useState, useRef, useEffect } from 'react';
import apiClient from '../services/api_client';
import './AIChatbot.module.css';

const AIChatbot = ({ initialSelectedText = null }) => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [selectedText, setSelectedText] = useState(initialSelectedText);
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages when new messages are added
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Handle text selection from anywhere on the page
  useEffect(() => {
    const handleTextSelection = () => {
      const selectedText = window.getSelection().toString().trim();
      if (selectedText.length > 0) {
        setSelectedText(selectedText);
      }
    };

    document.addEventListener('mouseup', handleTextSelection);
    return () => {
      document.removeEventListener('mouseup', handleTextSelection);
    };
  }, []);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare the context - use selected text if available, otherwise use general context
      const context = selectedText || '';

      // For now, use the non-streaming API; in the future, we could use streaming
      const response = await apiClient.queryAIObject({
        question: inputValue,
        context: context,
        sessionId: sessionId
      });

      // Update session ID if it was returned
      if (response.sessionId && !sessionId) {
        setSessionId(response.sessionId);
      }

      // Add AI response to the chat
      const aiMessage = {
        id: response.id || Date.now(),
        text: response.answer,
        sender: 'ai',
        sources: response.sources,
        confidence: response.confidence,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error querying AI:', error);

      // Add error message to the chat
      const errorMessage = {
        id: Date.now(),
        text: 'Sorry, I encountered an error processing your question. Please try again.',
        sender: 'error',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Streaming version of the submit handler
  const handleSubmitStreaming = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    // Add user message to the chat
    const userMessage = {
      id: Date.now(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Prepare the context - use selected text if available, otherwise use general context
      const context = selectedText || '';

      // Create a temporary AI message for streaming content
      const streamingMessageId = `stream-${Date.now()}`;
      const initialAiMessage = {
        id: streamingMessageId,
        text: '',
        sender: 'ai',
        isStreaming: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, initialAiMessage]);

      // Handle streaming response
      const onMessage = (data) => {
        setMessages(prev => prev.map(msg => {
          if (msg.id === streamingMessageId) {
            return {
              ...msg,
              text: msg.text + (data.answer || ''),
              sources: data.sources || msg.sources,
              confidence: data.confidence || msg.confidence
            };
          }
          return msg;
        }));
      };

      const onError = (error) => {
        console.error('Streaming error:', error);
        setMessages(prev => prev.map(msg => {
          if (msg.id === streamingMessageId) {
            return {
              ...msg,
              text: 'Sorry, I encountered an error processing your question. Please try again.',
              isStreaming: false,
              sender: 'error'
            };
          }
          return msg;
        }));
      };

      // Call the streaming API
      await apiClient.queryAIStream({
        question: inputValue,
        context: context,
        sessionId: sessionId
      }, onMessage, onError);

      // Mark streaming as complete
      setMessages(prev => prev.map(msg => {
        if (msg.id === streamingMessageId) {
          return {
            ...msg,
            isStreaming: false
          };
        }
        return msg;
      }));
    } catch (error) {
      console.error('Error with streaming query:', error);
      // Error handling is done in the onError callback above
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const formatSources = (sources) => {
    if (!sources || sources.length === 0) return null;

    return (
      <div className="ai-sources">
        <strong>Sources:</strong>
        <ul>
          {sources.map((source, index) => (
            <li key={index}>
              <span className="source-title">{source.chapterTitle}</span>
              {source.section && <span className="source-section"> ({source.section})</span>}
              {source.confidence && (
                <span className="source-confidence">
                  (Confidence: {(source.confidence * 100).toFixed(1)}%)
                </span>
              )}
            </li>
          ))}
        </ul>
      </div>
    );
  };

  return (
    <div className="ai-chatbot">
      <div className="chat-header">
        <h3>AI Assistant</h3>
        <p>Ask questions about the textbook content</p>
      </div>

      <div className="chat-messages">
        {messages.length === 0 ? (
          <div className="welcome-message">
            <p>Hello! I'm your AI assistant for the textbook. Ask me any questions about the content, and I'll provide answers based on the textbook material.</p>
            {selectedText && (
              <p className="selected-text-context">
                You've selected: <em>"{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}"</em>
              </p>
            )}
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`message ${message.sender}-message`}
            >
              <div className="message-content">
                <p className={message.isStreaming ? 'streaming-content' : ''}>{message.text}</p>
                {message.sender === 'ai' && !message.isStreaming && message.sources && formatSources(message.sources)}
                {message.sender === 'ai' && !message.isStreaming && message.confidence && (
                  <div className="confidence-score">
                    Confidence: {(message.confidence * 100).toFixed(1)}%
                  </div>
                )}
                {message.sender === 'ai' && message.isStreaming && (
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                )}
              </div>
              <div className="message-timestamp">
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="message ai-message">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmitStreaming}>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the textbook content..."
          disabled={isLoading}
          rows="3"
        />
        <button
          type="submit"
          disabled={!inputValue.trim() || isLoading}
          className="send-button"
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
};

export default AIChatbot;