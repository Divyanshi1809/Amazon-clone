import React from 'react';
import { BarChart3, PieChart, TrendingUp } from 'lucide-react';

const Charts = ({ bookmarks = [], newsData = [] }) => {
  // Calculate sentiment distribution
  const sentimentData = bookmarks.reduce((acc, bookmark) => {
    const sentiment = bookmark.sentiment || 'neutral';
    acc[sentiment] = (acc[sentiment] || 0) + 1;
    return acc;
  }, {});

  // Calculate source distribution
  const sourceData = bookmarks.reduce((acc, bookmark) => {
    const source = bookmark.source || 'Unknown';
    acc[source] = (acc[source] || 0) + 1;
    return acc;
  }, {});

  // Calculate monthly bookmark trends
  const monthlyData = bookmarks.reduce((acc, bookmark) => {
    try {
      const month = new Date(bookmark.created_at).toLocaleDateString('en-US', { 
        month: 'short', 
        year: 'numeric' 
      });
      acc[month] = (acc[month] || 0) + 1;
    } catch {
      // Handle invalid dates
    }
    return acc;
  }, {});

  const SentimentChart = () => (
    <div className="chart-container">
      <h3><PieChart size={20} /> Sentiment Distribution</h3>
      <div className="sentiment-chart">
        {Object.entries(sentimentData).map(([sentiment, count]) => {
          const percentage = (count / bookmarks.length) * 100;
          const color = sentiment === 'positive' ? '#10b981' : 
                       sentiment === 'negative' ? '#ef4444' : '#6b7280';
          
          return (
            <div key={sentiment} className="sentiment-item">
              <div 
                className="sentiment-bar"
                style={{ 
                  width: `${percentage}%`,
                  backgroundColor: color 
                }}
              />
              <span className="sentiment-label">
                {sentiment}: {count} ({percentage.toFixed(1)}%)
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );

  const SourceChart = () => (
    <div className="chart-container">
      <h3><BarChart3 size={20} /> Top Sources</h3>
      <div className="source-chart">
        {Object.entries(sourceData)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 5)
          .map(([source, count]) => {
            const maxCount = Math.max(...Object.values(sourceData));
            const percentage = (count / maxCount) * 100;
            
            return (
              <div key={source} className="source-item">
                <span className="source-name">{source}</span>
                <div className="source-bar-container">
                  <div 
                    className="source-bar"
                    style={{ width: `${percentage}%` }}
                  />
                </div>
                <span className="source-count">{count}</span>
              </div>
            );
          })}
      </div>
    </div>
  );

  const TrendChart = () => (
    <div className="chart-container">
      <h3><TrendingUp size={20} /> Bookmark Trends</h3>
      <div className="trend-chart">
        {Object.entries(monthlyData)
          .sort(([a], [b]) => new Date(a) - new Date(b))
          .map(([month, count]) => {
            const maxCount = Math.max(...Object.values(monthlyData));
            const percentage = (count / maxCount) * 100;
            
            return (
              <div key={month} className="trend-item">
                <span className="trend-month">{month}</span>
                <div className="trend-bar-container">
                  <div 
                    className="trend-bar"
                    style={{ height: `${percentage}%` }}
                  />
                </div>
                <span className="trend-count">{count}</span>
              </div>
            );
          })}
      </div>
    </div>
  );

  if (bookmarks.length === 0) {
    return (
      <div className="charts-empty">
        <p>No data available for charts. Start bookmarking articles!</p>
      </div>
    );
  }

  return (
    <div className="charts-container">
      <SentimentChart />
      <SourceChart />
      <TrendChart />
    </div>
  );
};

export default Charts;