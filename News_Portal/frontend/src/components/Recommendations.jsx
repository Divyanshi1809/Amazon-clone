import React, { useState, useEffect } from 'react';
import { Sparkles, Loader2, AlertCircle } from 'lucide-react';
import { newsAPI } from '../services/api';
import { useAuth } from '../App';
import NewsCard from './NewsCard';
import toast from 'react-hot-toast';

const Recommendations = ({ category = null }) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchRecommendations();
    }
  }, [user, category]);

  const fetchRecommendations = async () => {
    if (!user) return;

    setLoading(true);
    setError(null);
    try {
      const params = { limit: 10 };
      if (category) {
        params.category = category;
      }
      const data = await newsAPI.getRecommendations(params);
      setRecommendations(data.recommendations || []);
    } catch (err) {
      console.error('Error fetching recommendations:', err);
      setError('Failed to load recommendations');
      toast.error('Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="recommendations-container">
        <div className="recommendations-header">
          <Sparkles size={24} />
          <h2>Personalized Recommendations</h2>
        </div>
        <div className="recommendations-empty">
          <p>Please login to get personalized news recommendations based on your reading history.</p>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="recommendations-container">
        <div className="recommendations-header">
          <Sparkles size={24} />
          <h2>Personalized Recommendations</h2>
        </div>
        <div className="loading-container">
          <Loader2 className="loading-spinner" size={32} />
          <p>Finding articles you'll love...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="recommendations-container">
        <div className="recommendations-header">
          <Sparkles size={24} />
          <h2>Personalized Recommendations</h2>
        </div>
        <div className="error-state">
          <AlertCircle size={48} />
          <p>{error}</p>
          <button onClick={fetchRecommendations} className="retry-btn">
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (recommendations.length === 0) {
    return (
      <div className="recommendations-container">
        <div className="recommendations-header">
          <Sparkles size={24} />
          <h2>Personalized Recommendations</h2>
        </div>
        <div className="recommendations-empty">
          <p>No recommendations available yet. Start reading articles to get personalized suggestions!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <Sparkles size={24} />
        <h2>Recommended for You</h2>
        <button onClick={fetchRecommendations} className="refresh-btn-small">
          Refresh
        </button>
      </div>
      <div className="news-grid">
        {recommendations.map((article, index) => (
          <NewsCard key={article.id || article.url || index} article={article} />
        ))}
      </div>
    </div>
  );
};

export default Recommendations;

