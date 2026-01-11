import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';
import { newsAPI } from '../services/api';
import toast from 'react-hot-toast';

const FakeNewsIndicator = ({ article }) => {
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    if (article && article.fake_news_prediction) {
      // If prediction already exists in article
      setPrediction({
        prediction: article.fake_news_prediction,
        confidence: article.fake_news_score || 0.5,
        fake_news_score: article.fake_news_score || 0.5
      });
    } else if (article && article.title) {
      // Predict on component mount
      predictFakeNews();
    }
  }, [article]);

  const predictFakeNews = async () => {
    if (!article) return;

    setLoading(true);
    try {
      const result = await newsAPI.predictFakeNews(article);
      setPrediction(result);
    } catch (error) {
      console.error('Error predicting fake news:', error);
      toast.error('Failed to analyze article');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="fake-news-indicator loading">
        <Loader2 size={16} className="spinning" />
        <span>Analyzing...</span>
      </div>
    );
  }

  if (!prediction) {
    return null;
  }

  const isFake = prediction.prediction === 'fake';
  const confidence = prediction.confidence || prediction.fake_news_score || 0.5;
  const confidencePercent = Math.round(confidence * 100);

  const getIndicatorStyle = () => {
    if (isFake) {
      return {
        backgroundColor: '#fef2f2',
        borderColor: '#ef4444',
        color: '#dc2626'
      };
    } else {
      return {
        backgroundColor: '#f0fdf4',
        borderColor: '#10b981',
        color: '#059669'
      };
    }
  };

  return (
    <div 
      className="fake-news-indicator"
      style={getIndicatorStyle()}
      onClick={() => setShowDetails(!showDetails)}
    >
      <div className="fake-news-header">
        {isFake ? (
          <>
            <AlertTriangle size={16} />
            <span>Potential Fake News ({confidencePercent}% confidence)</span>
          </>
        ) : (
          <>
            <CheckCircle size={16} />
            <span>Verified Content ({confidencePercent}% confidence)</span>
          </>
        )}
      </div>

      {showDetails && (
        <div className="fake-news-details">
          <div className="fake-news-score">
            <span>Reliability Score:</span>
            <div className="score-bar">
              <div 
                className="score-fill"
                style={{ 
                  width: `${(1 - confidence) * 100}%`,
                  backgroundColor: isFake ? '#ef4444' : '#10b981'
                }}
              />
            </div>
            <span>{Math.round((1 - confidence) * 100)}%</span>
          </div>
          <p className="fake-news-note">
            {isFake 
              ? "This article may contain misinformation. Please verify facts from reliable sources."
              : "This article appears to be from a reliable source."}
          </p>
        </div>
      )}
    </div>
  );
};

export default FakeNewsIndicator;

