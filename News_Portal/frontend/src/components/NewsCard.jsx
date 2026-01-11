import React, { useState, useEffect } from 'react';
import { Bookmark, ExternalLink, Calendar, User } from 'lucide-react';
import { format } from 'date-fns';
import { bookmarksAPI, interactionAPI } from '../services/api';
import { useAuth } from '../App';
import FakeNewsIndicator from './FakeNewsIndicator';
import toast from 'react-hot-toast';

const NewsCard = ({ article }) => {
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user && article.id) {
      checkBookmarkStatus();
    }
  }, [user, article.id]);

  const checkBookmarkStatus = async () => {
    try {
      const newsId = article.id || article.news_id || article.url;
      const response = await bookmarksAPI.isBookmarked(newsId);
      setIsBookmarked(response.is_bookmarked || false);
    } catch (error) {
      console.error('Error checking bookmark status:', error);
    }
  };

  const handleBookmark = async () => {
    if (!user) {
      toast.error('Please login to bookmark articles');
      return;
    }

    setIsLoading(true);
    try {
      if (isBookmarked) {
        const newsId = article.id || article.news_id || article.url;
        await bookmarksAPI.removeBookmark(newsId);
        setIsBookmarked(false);
        toast.success('Removed from bookmarks');
      } else {
        await bookmarksAPI.addBookmark({
          news_id: article.id || article.news_id || article.url,
          title: article.title,
          url: article.url,
          image_url: article.urlToImage || article.image_url || article.imageUrl,
          source: article.source?.name || article.source || 'Unknown',
          sentiment: article.sentiment || 'neutral',
          category: article.category,
        });
        setIsBookmarked(true);
        toast.success('Added to bookmarks');
      }
    } catch (error) {
      toast.error('Failed to update bookmark');
      console.error('Bookmark error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReadMore = () => {
    if (article.url) {
      // Track click interaction
      if (user) {
        const category = article.category || article.source?.category;
        interactionAPI.trackInteraction(
          article.id || article.news_id || article.url,
          'click',
          category
        ).catch(err => console.error('Error tracking interaction:', err));
      }
      window.open(article.url, '_blank', 'noopener,noreferrer');
    }
  };

  useEffect(() => {
    // Track view when card is rendered
    if (user && article.id) {
      const category = article.category || article.source?.category;
      interactionAPI.trackInteraction(
        article.id || article.news_id || article.url,
        'view',
        category
      ).catch(err => console.error('Error tracking view:', err));
    }
  }, [user, article.id]);

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

  return (
    <article className="news-card">
      {/* Image */}
      {(article.urlToImage || article.image_url || article.imageUrl) && (
        <div className="news-card-image">
          <img 
            src={article.urlToImage || article.image_url || article.imageUrl} 
            alt={article.title}
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        </div>
      )}

      {/* Content */}
      <div className="news-card-content">
        {/* Header */}
        <div className="news-card-header">
          <div className="news-source">
            <User size={14} />
            <span>{article.source?.name || article.source || 'Unknown Source'}</span>
          </div>
          
          <div className="news-meta">
            <div className="news-date">
              <Calendar size={14} />
              <span>{formatDate(article.publishedAt)}</span>
            </div>
            
            {article.sentiment && (
              <div 
                className="sentiment-badge"
                style={{ backgroundColor: getSentimentColor(article.sentiment) }}
              >
                {article.sentiment}
              </div>
            )}
          </div>
        </div>

        {/* Title */}
        <h3 className="news-card-title">
          {article.title}
        </h3>

        {/* Description */}
        {article.description && (
          <p className="news-card-description">
            {article.description}
          </p>
        )}

        {/* Fake News Indicator */}
        <FakeNewsIndicator article={article} />

        {/* Footer */}
        <div className="news-card-footer">
          <button
            onClick={handleReadMore}
            className="read-more-btn"
            disabled={!article.url}
          >
            <ExternalLink size={16} />
            Read More
          </button>

          {user && (
            <button
              onClick={handleBookmark}
              className={`bookmark-btn ${isBookmarked ? 'bookmarked' : ''}`}
              disabled={isLoading}
            >
              <Bookmark size={16} />
              {isLoading ? '...' : (isBookmarked ? 'Bookmarked' : 'Bookmark')}
            </button>
          )}
        </div>
      </div>
    </article>
  );
};

export default NewsCard;