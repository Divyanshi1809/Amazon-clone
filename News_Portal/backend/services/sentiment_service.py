from textblob import TextBlob
from typing import Dict, Any, List

# Initialize VADER analyzer (more accurate for social media/news)
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    vader_analyzer = SentimentIntensityAnalyzer()
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False
    vader_analyzer = None


def analyze_sentiment(text: str, method: str = "vader") -> str:
    """
    Perform sentiment analysis on text.
    Returns sentiment as Positive, Negative, or Neutral.
    
    Args:
        text: Input text to analyze
        method: "vader" (default, better for news) or "textblob"
    """
    if not text or not text.strip():
        return "Neutral"
    
    if method == "vader" and VADER_AVAILABLE and vader_analyzer:
        # VADER is better for news/social media content
        scores = vader_analyzer.polarity_scores(text)
        compound = scores['compound']
        
        if compound >= 0.05:
            return "Positive"
        elif compound <= -0.05:
            return "Negative"
        else:
            return "Neutral"
    else:
        # TextBlob fallback
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
        
        if polarity > 0.1:
            return "Positive"
        elif polarity < -0.1:
            return "Negative"
        else:
            return "Neutral"


def analyze_sentiment_detailed(text: str) -> Dict[str, Any]:
    """
    Perform detailed sentiment analysis returning scores and label.
    """
    if not text or not text.strip():
        return {
            "sentiment": "Neutral",
            "polarity": 0.0,
            "subjectivity": 0.0,
            "scores": {"positive": 0.0, "neutral": 1.0, "negative": 0.0}
        }
    
    # VADER scores (if available)
    if VADER_AVAILABLE and vader_analyzer:
        vader_scores = vader_analyzer.polarity_scores(text)
    else:
        # Fallback to TextBlob scores
        blob = TextBlob(text)
        vader_scores = {
            'pos': max(0, blob.sentiment.polarity) if blob.sentiment.polarity > 0 else 0,
            'neg': max(0, -blob.sentiment.polarity) if blob.sentiment.polarity < 0 else 0,
            'neu': 1 - abs(blob.sentiment.polarity),
            'compound': blob.sentiment.polarity
        }
    
    # TextBlob for subjectivity
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    sentiment = analyze_sentiment(text, method="vader")
    
    return {
        "sentiment": sentiment,
        "polarity": float(polarity),
        "subjectivity": float(subjectivity),
        "scores": {
            "positive": float(vader_scores['pos']),
            "neutral": float(vader_scores['neu']),
            "negative": float(vader_scores['neg']),
            "compound": float(vader_scores['compound'])
        }
    }


def analyze_articles_sentiment(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Adds sentiment field to each article in the list.
    """
    enriched = []
    for article in articles:
        text = article.get("description") or article.get("title") or ""
        article_copy = dict(article)
        article_copy["sentiment"] = analyze_sentiment(text)
        enriched.append(article_copy)
    return enriched
