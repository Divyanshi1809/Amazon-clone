import React, { useState, useEffect } from 'react';
import { BarChart3, Clock, MousePointerClick, TrendingUp, BookOpen, AlertTriangle } from 'lucide-react';
import { analyticsAPI } from '../services/api';
import { useAuth } from '../App';
import toast from 'react-hot-toast';

const AnalyticsDashboard = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [days, setDays] = useState(30);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      fetchAnalytics();
    }
  }, [user, days]);

  const fetchAnalytics = async () => {
    if (!user) return;

    setLoading(true);
    try {
      const data = await analyticsAPI.getDashboard(days);
      setAnalytics(data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
      toast.error('Failed to load analytics');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className="analytics-dashboard">
        <p>Please login to view analytics</p>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="analytics-dashboard loading">
        <p>Loading analytics...</p>
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="analytics-dashboard">
        <p>No analytics data available</p>
      </div>
    );
  }

  const readingStats = analytics.user_reading_stats || {};
  const interactionStats = analytics.user_interaction_stats || {};
  const ctr = analytics.click_through_rate || {};
  const sentiment = analytics.sentiment_analysis || {};
  const trending = analytics.trending_topics || [];
  const fakeNewsStats = analytics.fake_news_stats || {};

  return (
    <div className="analytics-dashboard">
      <div className="dashboard-header">
        <h2><BarChart3 size={24} /> Analytics Dashboard</h2>
        <select value={days} onChange={(e) => setDays(Number(e.target.value))} className="days-selector">
          <option value={7}>Last 7 days</option>
          <option value={30}>Last 30 days</option>
          <option value={90}>Last 90 days</option>
        </select>
      </div>

      <div className="analytics-grid">
        {/* Reading Statistics */}
        <div className="analytics-card">
          <div className="card-header">
            <Clock size={20} />
            <h3>Reading Statistics</h3>
          </div>
          <div className="card-content">
            <div className="stat-item">
              <span className="stat-label">Total Reading Time</span>
              <span className="stat-value">
                {readingStats.total_reading_time_minutes || 0} min
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Articles Read</span>
              <span className="stat-value">{readingStats.total_articles_read || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Reading Time</span>
              <span className="stat-value">
                {Math.round(readingStats.average_reading_time_seconds || 0)}s
              </span>
            </div>
          </div>
        </div>

        {/* Top Categories */}
        <div className="analytics-card">
          <div className="card-header">
            <BookOpen size={20} />
            <h3>Top Categories</h3>
          </div>
          <div className="card-content">
            {readingStats.top_categories?.length > 0 ? (
              readingStats.top_categories.map((cat, idx) => (
                <div key={idx} className="category-item">
                  <span>{cat.category}</span>
                  <span className="category-count">{cat.count} articles</span>
                </div>
              ))
            ) : (
              <p>No category data yet</p>
            )}
          </div>
        </div>

        {/* Click-Through Rate */}
        <div className="analytics-card">
          <div className="card-header">
            <MousePointerClick size={20} />
            <h3>Engagement</h3>
          </div>
          <div className="card-content">
            <div className="stat-item">
              <span className="stat-label">Click-Through Rate</span>
              <span className="stat-value">{ctr.click_through_rate || 0}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Clicks</span>
              <span className="stat-value">{ctr.total_clicks || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total Views</span>
              <span className="stat-value">{ctr.total_views || 0}</span>
            </div>
          </div>
        </div>

        {/* Sentiment Analysis */}
        <div className="analytics-card">
          <div className="card-header">
            <TrendingUp size={20} />
            <h3>Sentiment Distribution</h3>
          </div>
          <div className="card-content">
            {sentiment.sentiment_counts ? (
              Object.entries(sentiment.sentiment_counts).map(([sent, count]) => {
                const percentage = sentiment.sentiment_percentages?.[sent] || 0;
                const color = sent === 'Positive' ? '#10b981' : 
                             sent === 'Negative' ? '#ef4444' : '#6b7280';
                return (
                  <div key={sent} className="sentiment-stat">
                    <div className="sentiment-label-bar">
                      <span>{sent}</span>
                      <span>{count} ({percentage}%)</span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ width: `${percentage}%`, backgroundColor: color }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p>No sentiment data</p>
            )}
          </div>
        </div>

        {/* Trending Topics */}
        <div className="analytics-card">
          <div className="card-header">
            <TrendingUp size={20} />
            <h3>Trending Topics</h3>
          </div>
          <div className="card-content">
            {trending.length > 0 ? (
              trending.map((topic, idx) => (
                <div key={idx} className="trending-item">
                  <span className="trending-rank">#{idx + 1}</span>
                  <span className="trending-category">{topic.category}</span>
                  <span className="trending-count">{topic.interaction_count} interactions</span>
                </div>
              ))
            ) : (
              <p>No trending data</p>
            )}
          </div>
        </div>

        {/* Fake News Stats */}
        <div className="analytics-card">
          <div className="card-header">
            <AlertTriangle size={20} />
            <h3>Content Reliability</h3>
          </div>
          <div className="card-content">
            <div className="stat-item">
              <span className="stat-label">Articles Analyzed</span>
              <span className="stat-value">{fakeNewsStats.total_analyzed || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Fake News Detected</span>
              <span className="stat-value fake">{fakeNewsStats.fake_count || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Verified Real</span>
              <span className="stat-value real">{fakeNewsStats.real_count || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;

