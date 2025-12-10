import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AIChatbot from '../AIChatbot';

// Mock the apiClient
jest.mock('../../services/api_client', () => ({
  queryAIObject: jest.fn(),
  queryAIStream: jest.fn(),
}));

const mockQuestions = [
  "What is Physical AI?",
  "Explain humanoid robotics basics",
  "What are ROS2 fundamentals?",
  "How does digital twin simulation work?",
  "What is vision-language-action system?",
  "Describe the capstone project"
];

describe('AIChatbot Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders AI chatbot component with initial state', () => {
    render(<AIChatbot />);

    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    expect(screen.getByText('Ask questions about the textbook content')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ask a question about the textbook content...')).toBeInTheDocument();
    expect(screen.getByText('Send')).toBeInTheDocument();
  });

  test('allows user to type and submit a question', async () => {
    const { container } = render(<AIChatbot />);

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(textarea, { target: { value: 'What is Physical AI?' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(textarea.value).toBe('');
    });
  });

  test('shows loading state when submitting question', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.queryAIObject.mockResolvedValue({
      answer: 'Physical AI is the intersection of artificial intelligence and physical systems...',
      sources: [],
      confidence: 0.89,
      timestamp: new Date().toISOString()
    });

    render(<AIChatbot />);

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(textarea, { target: { value: 'What is Physical AI?' } });
    fireEvent.click(sendButton);

    // Check that the send button shows "Sending..." while loading
    expect(sendButton).toHaveTextContent('Sending...');
  });

  test('displays AI response after successful query', async () => {
    const mockResponse = {
      answer: 'Physical AI is the intersection of artificial intelligence and physical systems...',
      sources: [
        {
          chapterId: 'chapter-1',
          chapterTitle: 'Introduction to Physical AI',
          section: 'Core Principles',
          confidence: 0.95
        }
      ],
      confidence: 0.89,
      timestamp: new Date().toISOString()
    };

    const apiClient = require('../../services/api_client');
    apiClient.queryAIObject.mockResolvedValue(mockResponse);

    render(<AIChatbot />);

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(textarea, { target: { value: 'What is Physical AI?' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText(mockResponse.answer)).toBeInTheDocument();
    });

    expect(screen.getByText('Sources:')).toBeInTheDocument();
    expect(screen.getByText('Introduction to Physical AI')).toBeInTheDocument();
  });

  test('handles error when AI query fails', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.queryAIObject.mockRejectedValue(new Error('API Error'));

    render(<AIChatbot />);

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(textarea, { target: { value: 'What is Physical AI?' } });
    fireEvent.click(sendButton);

    await waitFor(() => {
      expect(screen.getByText('Sorry, I encountered an error processing your question. Please try again.')).toBeInTheDocument();
    });
  });

  test('displays selected text context when provided', () => {
    render(<AIChatbot initialSelectedText="Selected text from the textbook" />);

    expect(screen.getByText('You\'ve selected:')).toBeInTheDocument();
    expect(screen.getByText('"Selected text from the textbook"')).toBeInTheDocument();
  });

  test('validates that questions are not empty before submission', async () => {
    render(<AIChatbot />);

    const sendButton = screen.getByText('Send');

    // Initially, button should be disabled since input is empty
    expect(sendButton).toBeDisabled();

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');
    fireEvent.change(textarea, { target: { value: ' ' } }); // Only whitespace

    // Button should still be disabled with only whitespace
    expect(sendButton).toBeDisabled();

    fireEvent.change(textarea, { target: { value: 'What is Physical AI?' } });

    // Button should now be enabled
    expect(sendButton).not.toBeDisabled();
  });

  test('handles Enter key submission', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.queryAIObject.mockResolvedValue({
      answer: 'Test response',
      sources: [],
      confidence: 0.8,
      timestamp: new Date().toISOString()
    });

    render(<AIChatbot />);

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');

    fireEvent.change(textarea, { target: { value: 'Test question' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: false });

    await waitFor(() => {
      expect(textarea.value).toBe('');
    });
  });

  test('does not submit on Shift+Enter', () => {
    render(<AIChatbot />);

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(textarea, { target: { value: 'Test question' } });
    fireEvent.keyDown(textarea, { key: 'Enter', shiftKey: true });

    // Button should still be disabled if input was empty before
    // If input has content, button should be enabled but not clicked
    expect(textarea.value).toBe('Test question');
  });
});

// Additional tests for streaming functionality
describe('AIChatbot Streaming Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('handles streaming responses correctly', async () => {
    const mockOnMessage = jest.fn();
    const mockOnError = jest.fn();

    // Mock the streaming function to simulate streaming behavior
    const apiClient = require('../../services/api_client');
    apiClient.queryAIStream.mockImplementation((requestData, onMessage, onError) => {
      // Simulate receiving multiple chunks
      setTimeout(() => {
        onMessage({ answer: 'Part 1 of response ', sources: [], confidence: 0.8 });
      }, 10);
      setTimeout(() => {
        onMessage({ answer: 'Part 2 of response ', sources: [], confidence: 0.85 });
      }, 20);
      setTimeout(() => {
        onMessage({ answer: 'Part 3 of response', sources: [], confidence: 0.9, done: true });
      }, 30);

      return Promise.resolve();
    });

    render(<AIChatbot />);

    const textarea = screen.getByPlaceholderText('Ask a question about the textbook content...');
    const sendButton = screen.getByText('Send');

    fireEvent.change(textarea, { target: { value: 'Stream test question' } });
    fireEvent.click(sendButton);

    // Wait for all streaming parts to be processed
    await new Promise(resolve => setTimeout(resolve, 50));

    // Verify that the full message is displayed
    await waitFor(() => {
      expect(screen.getByText(/Part 1 of response Part 2 of response Part 3 of response/)).toBeInTheDocument();
    });
  });
});