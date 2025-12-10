import React from 'react';
import AIChatbot from '../components/AIChatbot';
import Navigation from '../components/Navigation';
import './ChatPage.module.css';

const ChatPage = () => {
  return (
    <div className="chat-page">
      <header className="chat-header">
        <h1>AI Chat Assistant</h1>
        <p>Ask questions about the textbook content and get answers based on the material</p>
      </header>

      <main className="chat-main">
        <div className="chat-container">
          <AIChatbot />
        </div>

        <aside className="chat-sidebar">
          <Navigation />
        </aside>
      </main>

      <footer className="chat-footer">
        <p>Powered by AI - Answers are based solely on textbook content</p>
      </footer>
    </div>
  );
};

export default ChatPage;