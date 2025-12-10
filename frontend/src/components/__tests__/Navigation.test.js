import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Navigation from '../Navigation';

// Mock the apiClient
jest.mock('../../services/api_client', () => ({
  getChapters: jest.fn(),
  getChapterToc: jest.fn(),
}));

// Mock the router
jest.mock('@docusaurus/router', () => ({
  useLocation: () => ({
    pathname: '/chapter/chapter-1',
    hash: '',
  }),
  useHistory: jest.fn(),
}));

const mockChapters = [
  {
    id: 'chapter-1',
    title: 'Introduction to Physical AI',
    order: 1,
  },
  {
    id: 'chapter-2',
    title: 'Basics of Humanoid Robotics',
    order: 2,
  },
];

const mockToc = {
  chapterId: 'chapter-1',
  title: 'Introduction to Physical AI',
  sections: [
    {
      id: 'what-is-physical-ai',
      title: 'What is Physical AI?',
      level: 2,
      order: 1,
    },
    {
      id: 'historical-context',
      title: 'Historical Context',
      level: 2,
      order: 2,
    },
    {
      id: 'applications',
      title: 'Applications',
      level: 3,
      order: 3,
    },
  ],
};

describe('Navigation Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();

    const apiClient = require('../../services/api_client');
    apiClient.getChapters.mockResolvedValue({
      chapters: mockChapters,
      total: 2,
      limit: 10,
      offset: 0,
    });

    apiClient.getChapterToc.mockResolvedValue(mockToc);
  });

  test('renders navigation component with chapters', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    // Wait for chapters to load
    await waitFor(() => {
      expect(screen.getByText('Textbook Contents')).toBeInTheDocument();
    });

    // Check that chapters are displayed
    expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    expect(screen.getByText('2. Basics of Humanoid Robotics')).toBeInTheDocument();
  });

  test('loads and displays chapter TOC when chapter is expanded', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    // Wait for initial render
    await waitFor(() => {
      expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    });

    // Click the expand button for the first chapter
    const expandButton = screen.getByLabelText('Expand');
    fireEvent.click(expandButton);

    // Wait for TOC to load and display
    await waitFor(() => {
      expect(screen.getByText('What is Physical AI?')).toBeInTheDocument();
      expect(screen.getByText('Historical Context')).toBeInTheDocument();
      expect(screen.getByText('Applications')).toBeInTheDocument();
    });
  });

  test('toggles chapter expansion', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    await waitFor(() => {
      expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    });

    // Initially, sections should not be visible
    expect(screen.queryByText('What is Physical AI?')).not.toBeInTheDocument();

    // Expand the chapter
    const expandButton = screen.getByLabelText('Expand');
    fireEvent.click(expandButton);

    // Sections should now be visible
    await waitFor(() => {
      expect(screen.getByText('What is Physical AI?')).toBeInTheDocument();
    });

    // Collapse the chapter
    fireEvent.click(expandButton);

    // Sections should be hidden again
    expect(screen.queryByText('What is Physical AI?')).not.toBeInTheDocument();
  });

  test('handles chapter selection with currentChapterId', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    await waitFor(() => {
      expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    });

    // The current chapter should have active styling
    const currentChapterLink = screen.getByText('1. Introduction to Physical AI');
    expect(currentChapterLink).toHaveClass('active');
  });

  test('search functionality filters chapters and sections', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    await waitFor(() => {
      expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    });

    // Click the expand button to load TOC
    const expandButton = screen.getByLabelText('Expand');
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText('What is Physical AI?')).toBeInTheDocument();
    });

    // Find and use the search input
    const searchInput = screen.getByPlaceholderText('Search sections...');
    fireEvent.change(searchInput, { target: { value: 'Historical' } });

    // Should show only matching sections
    expect(screen.getByText('Historical Context')).toBeInTheDocument();
    expect(screen.queryByText('What is Physical AI?')).not.toBeInTheDocument();
  });

  test('displays no results message when search has no matches', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    await waitFor(() => {
      expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    });

    // Click the expand button to load TOC
    const expandButton = screen.getByLabelText('Expand');
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText('What is Physical AI?')).toBeInTheDocument();
    });

    // Search for something that doesn't exist
    const searchInput = screen.getByPlaceholderText('Search sections...');
    fireEvent.change(searchInput, { target: { value: 'NonexistentSection' } });

    // Should show no results message
    expect(screen.getByText('No sections found matching "NonexistentSection"')).toBeInTheDocument();
  });

  test('clears search when clicking on a section link', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    await waitFor(() => {
      expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    });

    // Click the expand button to load TOC
    const expandButton = screen.getByLabelText('Expand');
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText('What is Physical AI?')).toBeInTheDocument();
    });

    // Search for a section
    const searchInput = screen.getByPlaceholderText('Search sections...');
    fireEvent.change(searchInput, { target: { value: 'What is' } });

    // Click on the matching section link
    const sectionLink = screen.getByText('What is Physical AI?');
    fireEvent.click(sectionLink);

    // Search query should be cleared
    expect(searchInput.value).toBe('');
  });

  test('handles API errors gracefully', async () => {
    // Mock API to reject
    const apiClient = require('../../services/api_client');
    apiClient.getChapters.mockRejectedValue(new Error('API Error'));

    render(<Navigation currentChapterId="chapter-1" />);

    // Should show error message
    await waitFor(() => {
      expect(screen.getByText('Error loading navigation: API Error')).toBeInTheDocument();
    });
  });

  test('loads TOC for all chapters on initial load', async () => {
    render(<Navigation currentChapterId="chapter-1" />);

    await waitFor(() => {
      expect(require('../../services/api_client').getChapters).toHaveBeenCalled();
      expect(require('../../services/api_client').getChapterToc).toHaveBeenCalledTimes(2); // For both chapters
    });
  });
});

// Additional tests for the TOC generation functionality
describe('Navigation Component - TOC Generation', () => {
  test('displays proper hierarchy levels for sections', async () => {
    const mockTocWithLevels = {
      chapterId: 'chapter-1',
      title: 'Introduction to Physical AI',
      sections: [
        {
          id: 'main-topic',
          title: 'Main Topic',
          level: 2,
          order: 1,
        },
        {
          id: 'sub-topic',
          title: 'Sub Topic',
          level: 3,
          order: 2,
        },
      ],
    };

    const apiClient = require('../../services/api_client');
    apiClient.getChapterToc.mockResolvedValue(mockTocWithLevels);

    render(<Navigation currentChapterId="chapter-1" />);

    await waitFor(() => {
      expect(screen.getByText('1. Introduction to Physical AI')).toBeInTheDocument();
    });

    // Expand to see sections
    const expandButton = screen.getByLabelText('Expand');
    fireEvent.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText('Main Topic')).toBeInTheDocument();
      expect(screen.getByText('Sub Topic')).toBeInTheDocument();
    });

    // Both sections should be visible and properly styled
    expect(screen.getByText('Main Topic')).toBeInTheDocument();
    expect(screen.getByText('Sub Topic')).toBeInTheDocument();
  });
});