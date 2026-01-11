import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, Loader2, AlertCircle, RefreshCw } from 'lucide-react';
import { newsAPI } from '../services/api';
import NewsCard from '../components/NewsCard';
import FilterBar from '../components/FilterBar';
import Charts from '../components/Charts';
import { useAuth } from '../App';
import toast from 'react-hot-toast';

const Home = () => {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({});
  const [categories, setCategories] = useState([]);
  const [sources, setSources] = useState([]);
  const [showCharts, setShowCharts] = useState(false);
  
  const [searchParams, setSearchParams] = useSearchParams();
  const { user } = useAuth();

  // Initialize search query from URL params
  useEffect(() => {
    const query = searchParams.get('search');
    if (query) {
      setSearchQuery(query);
    }
  }, [searchParams]);

  // Fetch initial data
  useEffect(() => {
    fetchInitialData();
  }, []);

  // Fetch news when search or filters change
  useEffect(() => {
    if (!loading) {
      fetchNews();
    }
  }, [searchQuery, filters]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchNews(),
        fetchCategories(),
        fetchSources()
      ]);
    } catch (error) {
      console.error('Error fetching initial data:', error);
      setError('Failed to load initial data');
    } finally {
      setLoading(false);
    }
  };

  const fetchNews = async () => {
    try {
      setError(null);
      
      const params = {
        page: 1,
        pageSize: 20,
        ...filters
      };

      let response;
      if (searchQuery.trim()) {
        response = await newsAPI.searchNews(searchQuery.trim(), params);
      } else {
        response = await newsAPI.getNews(params);
      }

      setNews(response.articles || response.data || []);
    } catch (error) {
      console.error('Error fetching news:', error);
      setError('Failed to load news articles');
      setNews([]);
      toast.error('Failed to load news articles');
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await newsAPI.getCategories();
      setCategories(response.categories || response.data || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const fetchSources = async () => {
    try {
      const response = await newsAPI.getSources();
      setSources(response.sources || response.data || []);
    } catch (error) {
      console.error('Error fetching sources:', error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setSearchParams({ search: searchQuery.trim() });
    } else {
      setSearchParams({});
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await fetchNews();
      toast.success('News refreshed successfully');
    } catch (error) {
      toast.error('Failed to refresh news');
    } finally {
      setRefreshing(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchParams({});
  };

  if (loading) {
    return (
      <div className="home-page">
        <div className="loading-container">
          <Loader2 className="loading-spinner" size={32} />
          <p>Loading latest news...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="home-page">
      <div className="home-container">
        {/* Header */}
        <div className="home-header">
          <div className="header-content">
            <h1>Latest News</h1>
            <p>Stay updated with the most recent news articles</p>
          </div>
          
          <div className="header-actions">
            <button
              onClick={handleRefresh}
              className="refresh-btn"
              disabled={refreshing}
            >
              <RefreshCw className={refreshing ? 'spinning' : ''} size={18} />
              {refreshing ? 'Refreshing...' : 'Refresh'}
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <div className="search-section">
          <form onSubmit={handleSearch} className="search-form">
            <div className="search-input-group">
              <Search className="search-icon" size={20} />
              <input
                type="text"
                placeholder="Search news articles..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="search-input"
              />
              {searchQuery && (
                <button
                  type="button"
                  onClick={clearSearch}
                  className="clear-search-btn"
                >
                  ×
                </button>
              )}
            </div>
            <button type="submit" className="search-btn">
              Search
            </button>
          </form>
        </div>

        {/* Filter Bar */}
        <FilterBar
          onFilterChange={handleFilterChange}
          categories={categories}
          sources={sources}
          currentFilters={filters}
        />

        {/* Charts Toggle */}
        {user && (
          <div className="charts-toggle">
            <button
              onClick={() => setShowCharts(!showCharts)}
              className="toggle-charts-btn"
            >
              {showCharts ? 'Hide' : 'Show'} Analytics
            </button>
          </div>
        )}

        {/* Charts Section */}
        {user && showCharts && (
          <div className="charts-section">
            <Charts />
          </div>
        )}

        {/* News Content */}
        <div className="news-content">
          {error ? (
            <div className="error-state">
              <AlertCircle size={48} />
              <h3>Oops! Something went wrong</h3>
              <p>{error}</p>
              <button onClick={fetchNews} className="retry-btn">
                Try Again
              </button>
            </div>
          ) : news.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📰</div>
              <h3>No articles found</h3>
              <p>
                {searchQuery.trim() 
                  ? `No articles found for "${searchQuery}". Try adjusting your search terms.`
                  : 'No articles available at the moment. Please try again later.'
                }
              </p>
              {searchQuery.trim() && (
                <button onClick={clearSearch} className="clear-search-btn">
                  Clear Search
                </button>
              )}
            </div>
          ) : (
            <>
              {/* Results Header */}
              <div className="results-header">
                <h2>
                  {searchQuery.trim() 
                    ? `Search Results for "${searchQuery}"`
                    : 'Latest Articles'
                  }
                </h2>
                <span className="results-count">
                  {news.length} article{news.length !== 1 ? 's' : ''}
                </span>
              </div>

              {/* News Grid */}
              <div className="news-grid">
                {news.map((article, index) => (
                  <NewsCard
                    key={article.id || article.url || index}
                    article={article}
                  />
                ))}
              </div>

              {/* Load More Button */}
              {news.length >= 20 && (
                <div className="load-more-section">
                  <button
                    onClick={() => {
                      // TODO: Implement pagination
                      toast.info('Load more functionality coming soon!');
                    }}
                    className="load-more-btn"
                  >
                    Load More Articles
                  </button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
