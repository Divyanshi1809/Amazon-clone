import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bookmark, Search, Filter, Loader2 } from 'lucide-react';
import { useAuth } from '../App';
import { bookmarksAPI } from '../services/api';
import BookmarkList from '../components/BookmarkList';
import toast from 'react-hot-toast';

const Bookmarks = () => {
  const [bookmarks, setBookmarks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSource, setFilterSource] = useState('');
  const [filterSentiment, setFilterSentiment] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [filteredBookmarks, setFilteredBookmarks] = useState([]);
  
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  // Redirect if not authenticated
  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/login');
    }
  }, [user, authLoading, navigate]);

  // Fetch bookmarks on component mount
  useEffect(() => {
    if (user) {
      fetchBookmarks();
    }
  }, [user]);

  // Filter and sort bookmarks when dependencies change
  useEffect(() => {
    filterAndSortBookmarks();
  }, [bookmarks, searchQuery, filterSource, filterSentiment, sortBy]);

  const fetchBookmarks = async () => {
    try {
      setLoading(true);
      const response = await bookmarksAPI.getBookmarks();
      setBookmarks(response.data || response);
    } catch (error) {
      console.error('Error fetching bookmarks:', error);
      toast.error('Failed to load bookmarks');
      setBookmarks([]);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortBookmarks = () => {
    let filtered = [...bookmarks];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(bookmark =>
        bookmark.title?.toLowerCase().includes(query) ||
        bookmark.source?.toLowerCase().includes(query)
      );
    }

    // Apply source filter
    if (filterSource) {
      filtered = filtered.filter(bookmark =>
        bookmark.source?.toLowerCase() === filterSource.toLowerCase()
      );
    }

    // Apply sentiment filter
    if (filterSentiment) {
      filtered = filtered.filter(bookmark =>
        bookmark.sentiment?.toLowerCase() === filterSentiment.toLowerCase()
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'newest':
          return new Date(b.created_at) - new Date(a.created_at);
        case 'oldest':
          return new Date(a.created_at) - new Date(b.created_at);
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'source':
          return (a.source || '').localeCompare(b.source || '');
        default:
          return 0;
      }
    });

    setFilteredBookmarks(filtered);
  };

  const handleBookmarkRemoved = (newsId) => {
    setBookmarks(prevBookmarks => 
      prevBookmarks.filter(bookmark => bookmark.news_id !== newsId)
    );
  };

  const clearFilters = () => {
    setSearchQuery('');
    setFilterSource('');
    setFilterSentiment('');
    setSortBy('newest');
  };

  const getUniqueSources = () => {
    const sources = [...new Set(bookmarks.map(bookmark => bookmark.source).filter(Boolean))];
    return sources.sort();
  };

  const getUniqueSentiments = () => {
    const sentiments = [...new Set(bookmarks.map(bookmark => bookmark.sentiment).filter(Boolean))];
    return sentiments.sort();
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (searchQuery.trim()) count++;
    if (filterSource) count++;
    if (filterSentiment) count++;
    if (sortBy !== 'newest') count++;
    return count;
  };

  if (authLoading || loading) {
    return (
      <div className="bookmarks-page">
        <div className="loading-container">
          <Loader2 className="loading-spinner" size={32} />
          <p>Loading your bookmarks...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null; // Will redirect to login
  }

  return (
    <div className="bookmarks-page">
      <div className="bookmarks-container">
        {/* Header */}
        <div className="bookmarks-header">
          <div className="header-content">
            <div className="header-title">
              <Bookmark className="header-icon" size={28} />
              <h1>My Bookmarks</h1>
            </div>
            <div className="bookmarks-count">
              {filteredBookmarks.length} of {bookmarks.length} bookmarks
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="bookmarks-filters">
          <div className="filters-row">
            {/* Search */}
            <div className="filter-group">
              <Search className="filter-icon" size={18} />
              <input
                type="text"
                placeholder="Search bookmarks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="filter-input"
              />
            </div>

            {/* Source Filter */}
            <div className="filter-group">
              <Filter className="filter-icon" size={18} />
              <select
                value={filterSource}
                onChange={(e) => setFilterSource(e.target.value)}
                className="filter-select"
              >
                <option value="">All Sources</option>
                {getUniqueSources().map(source => (
                  <option key={source} value={source}>
                    {source}
                  </option>
                ))}
              </select>
            </div>

            {/* Sentiment Filter */}
            <div className="filter-group">
              <select
                value={filterSentiment}
                onChange={(e) => setFilterSentiment(e.target.value)}
                className="filter-select"
              >
                <option value="">All Sentiments</option>
                {getUniqueSentiments().map(sentiment => (
                  <option key={sentiment} value={sentiment}>
                    {sentiment.charAt(0).toUpperCase() + sentiment.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            {/* Sort */}
            <div className="filter-group">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="filter-select"
              >
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
                <option value="title">Title A-Z</option>
                <option value="source">Source A-Z</option>
              </select>
            </div>

            {/* Clear Filters */}
            {getActiveFiltersCount() > 0 && (
              <button
                onClick={clearFilters}
                className="clear-filters-btn"
              >
                Clear Filters ({getActiveFiltersCount()})
              </button>
            )}
          </div>
        </div>

        {/* Bookmarks List */}
        <div className="bookmarks-content">
          {filteredBookmarks.length === 0 ? (
            <div className="empty-state">
              {bookmarks.length === 0 ? (
                <>
                  <div className="empty-icon">📚</div>
                  <h3>No bookmarks yet</h3>
                  <p>Start bookmarking articles from the home page to see them here!</p>
                  <button
                    onClick={() => navigate('/')}
                    className="browse-news-btn"
                  >
                    Browse News
                  </button>
                </>
              ) : (
                <>
                  <div className="empty-icon">🔍</div>
                  <h3>No bookmarks found</h3>
                  <p>Try adjusting your search or filter criteria.</p>
                  <button
                    onClick={clearFilters}
                    className="clear-filters-btn"
                  >
                    Clear Filters
                  </button>
                </>
              )}
            </div>
          ) : (
            <BookmarkList
              bookmarks={filteredBookmarks}
              onBookmarkRemoved={handleBookmarkRemoved}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Bookmarks;
