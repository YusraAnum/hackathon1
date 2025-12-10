import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import TextbookViewer from '../TextbookViewer';

// Mock the apiClient
jest.mock('../../services/api_client', () => ({
  getChapter: jest.fn(),
  getChapters: jest.fn(),
}));

const mockChapter = {
  id: 'introduction-to-physical-ai',
  title: 'Introduction to Physical AI',
  content: '<h1>Introduction to Physical AI</h1><p>This is the content for the introduction chapter.</p>',
  order: 1,
  wordCount: 1200,
  readingTime: '6 min',
};

const mockChapters = [
  {
    id: 'introduction-to-physical-ai',
    title: 'Introduction to Physical AI',
    order: 1,
  },
  {
    id: 'basics-humanoid-robotics',
    title: 'Basics of Humanoid Robotics',
    order: 2,
  },
  {
    id: 'ros2-fundamentals',
    title: 'ROS2 Fundamentals',
    order: 3,
  },
];

describe('TextbookViewer Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders loading state initially', () => {
    const { getByText } = render(<TextbookViewer chapterId="test-chapter" />);
    expect(getByText('Loading chapter...')).toBeInTheDocument();
  });

  test('renders chapter content when loaded', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.getChapter.mockResolvedValue(mockChapter);
    apiClient.getChapters.mockResolvedValue({ chapters: mockChapters, total: 3, limit: 10, offset: 0 });

    render(<TextbookViewer chapterId="introduction-to-physical-ai" />);

    await waitFor(() => {
      expect(screen.getByText('Introduction to Physical AI')).toBeInTheDocument();
    });

    expect(screen.getByText('This is the content for the introduction chapter.')).toBeInTheDocument();
  });

  test('displays error when chapter fails to load', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.getChapter.mockRejectedValue(new Error('Failed to load chapter'));
    apiClient.getChapters.mockResolvedValue({ chapters: mockChapters, total: 3, limit: 10, offset: 0 });

    render(<TextbookViewer chapterId="non-existent-chapter" />);

    await waitFor(() => {
      expect(screen.getByText('Error loading chapter')).toBeInTheDocument();
    });
  });

  test('renders navigation controls when chapters are available', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.getChapter.mockResolvedValue(mockChapter);
    apiClient.getChapters.mockResolvedValue({ chapters: mockChapters, total: 3, limit: 10, offset: 0 });

    render(<TextbookViewer chapterId="basics-humanoid-robotics" />);

    await waitFor(() => {
      expect(screen.getByText('← Previous')).toBeInTheDocument();
      expect(screen.getByText('Next →')).toBeInTheDocument();
    });
  });

  test('disables previous button on first chapter', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.getChapter.mockResolvedValue(mockChapters[0]); // First chapter
    apiClient.getChapters.mockResolvedValue({ chapters: mockChapters, total: 3, limit: 10, offset: 0 });

    render(<TextbookViewer chapterId="introduction-to-physical-ai" />);

    await waitFor(() => {
      const prevButton = screen.getByText('← Previous');
      expect(prevButton).toBeDisabled();
    });
  });

  test('disables next button on last chapter', async () => {
    const apiClient = require('../../services/api_client');
    apiClient.getChapter.mockResolvedValue(mockChapters[2]); // Last chapter
    apiClient.getChapters.mockResolvedValue({ chapters: mockChapters, total: 3, limit: 10, offset: 0 });

    render(<TextbookViewer chapterId="ros2-fundamentals" />);

    await waitFor(() => {
      const nextButton = screen.getByText('Next →');
      expect(nextButton).toBeDisabled();
    });
  });
});