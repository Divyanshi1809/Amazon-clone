import React, { useState } from 'react';
import { Filter, X, Search } from 'lucide-react';

const FilterBar = ({ 
  onFilterChange, 
  categories = [], 
  sources = [],
  currentFilters = {} 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [localFilters, setLocalFilters] = useState(currentFilters);

  const handleFilterChange = (key, value) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleClearFilters = () => {
    const clearedFilters = {};
    setLocalFilters(clearedFilters);
    onFilterChange(clearedFilters);
  };

  const hasActiveFilters = Object.values(localFilters).some(value => 
    value && value !== '' && value !== 'all'
  );

  return (
    <div className="filter-bar">
      <div className="filter-header">
        <button
          className={`filter-toggle ${isOpen ? 'active' : ''}`}
          onClick={() => setIsOpen(!isOpen)}
        >
          <Filter size={18} />
          Filters
          {hasActiveFilters && <span className="filter-indicator"></span>}
        </button>

        {hasActiveFilters && (
          <button
            className="clear-filters-btn"
            onClick={handleClearFilters}
          >
            <X size={16} />
            Clear All
          </button>
        )}
      </div>

      {isOpen && (
        <div className="filter-content">
          <div className="filter-group">
            <label htmlFor="category-filter">Category</label>
            <select
              id="category-filter"
              value={localFilters.category || 'all'}
              onChange={(e) => handleFilterChange('category', e.target.value)}
              className="filter-select"
            >
              <option value="all">All Categories</option>
              {categories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="source-filter">Source</label>
            <select
              id="source-filter"
              value={localFilters.source || 'all'}
              onChange={(e) => handleFilterChange('source', e.target.value)}
              className="filter-select"
            >
              <option value="all">All Sources</option>
              {sources.map((source) => (
                <option key={source.id} value={source.id}>
                  {source.name}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sort-filter">Sort By</label>
            <select
              id="sort-filter"
              value={localFilters.sortBy || 'publishedAt'}
              onChange={(e) => handleFilterChange('sortBy', e.target.value)}
              className="filter-select"
            >
              <option value="publishedAt">Date Published</option>
              <option value="relevancy">Relevancy</option>
              <option value="popularity">Popularity</option>
              <option value="title">Title</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="sentiment-filter">Sentiment</label>
            <select
              id="sentiment-filter"
              value={localFilters.sentiment || 'all'}
              onChange={(e) => handleFilterChange('sentiment', e.target.value)}
              className="filter-select"
            >
              <option value="all">All Sentiments</option>
              <option value="positive">Positive</option>
              <option value="negative">Negative</option>
              <option value="neutral">Neutral</option>
            </select>
          </div>

          <div className="filter-group">
            <label htmlFor="date-filter">Date Range</label>
            <select
              id="date-filter"
              value={localFilters.dateRange || 'all'}
              onChange={(e) => handleFilterChange('dateRange', e.target.value)}
              className="filter-select"
            >
              <option value="all">All Time</option>
              <option value="today">Today</option>
              <option value="week">Past Week</option>
              <option value="month">Past Month</option>
            </select>
          </div>
        </div>
      )}
    </div>
  );
};

export default FilterBar;