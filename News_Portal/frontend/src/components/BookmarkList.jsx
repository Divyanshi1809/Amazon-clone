import React from 'react';
import { Trash2, ExternalLink, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import { bookmarksAPI } from '../services/api';
import toast from 'react-hot-toast';

const BookmarkList = ({ bookmarks, onBookmarkRemoved }) => {
  const handleRemoveBookmark = async (newsId) => {
    try {
      await bookmarksAPI.removeBookmark(newsId);
      toast.success('Bookmark removed');
      onBookmarkRemoved(newsId);
    } catch (error) {
      toast.error('Failed to remove bookmark');
      console.error('Remove bookmark error:', error);
    }
  };

  const handleReadMore = (url) => {
    if (url) {
      window.open(url, '_blank', 'noopener,noreferrer');
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM dd, yyyy');
    } catch {
      return 'Unknown date';
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment?.toLowerCase()) {
      case 'positive': return '#10b981';
      case 'negative': return '#ef4444';
      case 'neutral': return '#6b7280';
      default: return '#6b7280';
    }
  };

  if (bookmarks.length === 0) {
    return (
      <div className="empty-bookmarks">
        <div className="empty-icon">📚</div>
        <h3>No bookmarks yet</h3>
        <p>Start bookmarking articles to see them here!</p>
      </div>
    );
  }

  return (
    <div className="bookmark-list">
      {bookmarks.map((bookmark) => (
        <div key={bookmark.id} className="bookmark-item">
          {/* Image */}
          {bookmark.image_url && (
            <div className="bookmark-image">
              <img 
                src={bookmark.image_url} 
                alt={bookmark.title}
                onError={(e) => {
                  e.target.style.display = 'none';
                }}
              />
            </div>
          )}

          {/* Content */}
          <div className="bookmark-content">
            <div className="bookmark-header">
              <div className="bookmark-meta">
                <span className="bookmark-source">{bookmark.source}</span>
                <div className="bookmark-date">
                  <Calendar size={14} />
                  <span>{formatDate(bookmark.created_at)}</span>
                </div>
              </div>
              
              {bookmark.sentiment && (
                <div 
                  className="sentiment-badge"
                  style={{ backgroundColor: getSentimentColor(bookmark.sentiment) }}
                >
                  {bookmark.sentiment}
                </div>
              )}
            </div>

            <h3 className="bookmark-title">{bookmark.title}</h3>

            <div className="bookmark-actions">
              <button
                onClick={() => handleReadMore(bookmark.url)}
                className="read-more-btn"
                disabled={!bookmark.url}
              >
                <ExternalLink size={16} />
                Read More
              </button>

              <button
                onClick={() => handleRemoveBookmark(bookmark.news_id)}
                className="remove-bookmark-btn"
              >
                <Trash2 size={16} />
                Remove
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default BookmarkList;