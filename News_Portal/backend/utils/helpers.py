import hashlib
import json
import re
from datetime import datetime,timezone
from typing import Any,Dict,List,Optional,Tuple

import requests

def fetch_json(
    url:str,
    headers:Optional[Dict[str,str]]=None,
    params:Optional[Dict[str,str]]=None,
    timeout:int=12,
)->Tuple[Optional[Dict[str,Any]],Optional[str]]:
    """
     Fetch JSON from a URL with basic error handling.
    Returns  (data,error) . Exactly one of the two will be non-None.
    """
    try:
        response=requests.get(url,headers=headers,params=params,timeout=timeout)
        response.raise_for_status()
        return response.json(),None
    except requests.exceptions.RequestException as e:
        return None, f"Network error: {str(e)}"
    except ValueError:
        return None,"Invalid JSON format"

def to_iso8601(dt: datetime) -> str:
    """
    Convert a datetime to ISO8601 (UTC, Z suffix).
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt.isoformat().replace("+00:00", "Z")


def parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Try to parse common timestamp formats from news APIs.
    Returns a timezone-aware UTC datetime, or None if parsing fails.
    """
    if not date_str:
        return None

    candidates: List[str] = [
        "%Y-%m-%dT%H:%M:%S.%fZ",  # 2024-01-01T12:34:56.123Z
        "%Y-%m-%dT%H:%M:%SZ",     # 2024-01-01T12:34:56Z
        "%Y-%m-%d %H:%M:%S",      # 2024-01-01 12:34:56
        "%Y-%m-%d",               # 2024-01-01
    ]

    for fmt in candidates:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None
   
_slug_invalid_chars = re.compile(r"[^a-z0-9]+")
_multi_dash = re.compile(r"-{2,}")


def slugify(text: str, max_length: int = 80) -> str:
    """
    Create a URL-safe slug from arbitrary text.
    """
    if not text:
        return "item"
    text = text.lower()
    text = _slug_invalid_chars.sub("-", text)
    text = _multi_dash.sub("-", text).strip("-")
    if not text:
        text = "item"
    return text[:max_length]


def sanitize_text(text: Optional[str]) -> str:
    """
    Trim and collapse whitespace; return empty string for None.
    """
    if not text:
        return ""
    return " ".join(text.split())


def stable_id_from_url(url: Optional[str]) -> str:
    """
    Generate a stable id for an article using its URL (or content fallback).
    """
    key = (url or "").strip()
    if not key:
        key = f"no-url-{datetime.now(timezone.utc).timestamp()}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def normalize_article(article: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map a NewsAPI-style article dict to a consistent schema used by the app.
    Fields:
      - id, title, description, url, imageUrl, publishedAt, source, author, category
    """
    title = sanitize_text(article.get("title"))
    description = sanitize_text(article.get("description"))
    url = (article.get("url") or "").strip()
    image_url = (article.get("urlToImage") or "").strip()

    # Source can be dict or string depending on provider
    raw_source = article.get("source")
    if isinstance(raw_source, dict):
        source = raw_source.get("name") or raw_source.get("id") or ""
    else:
        source = sanitize_text(str(raw_source or ""))

    author = sanitize_text(article.get("author"))
    published_raw = article.get("publishedAt") or article.get("published_at")
    published_dt = parse_datetime(published_raw)
    published_at = to_iso8601(published_dt) if published_dt else None

    return {
        "id": stable_id_from_url(url),
        "title": title,
        "description": description,
        "url": url,
        "imageUrl": image_url,
        "publishedAt": published_at,
        "source": source,
        "author": author,
        "category": article.get("category"),  # optional, may be None
    }


def add_sentiment_to_articles(
    articles: List[Dict[str, Any]],
    analyze_func,
) -> List[Dict[str, Any]]:
    """
    Apply sentiment to each article using the provided analyze_func(text) -> str.
    Mutates a copy of each article and returns a new list.
    """
    enriched: List[Dict[str, Any]] = []
    for a in articles:
        text = (a.get("description") or a.get("title") or "") or ""
        item = dict(a)
        item["sentiment"] = analyze_func(text)
        enriched.append(item)
    return enriched


def pick(d: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """
    Return a new dict with only the provided keys if present.
    """
    return {k: d[k] for k in keys if k in d}


def coalesce(*values: Any, default: Any = None) -> Any:
    """
    Return the first value that is not None and not empty (for str).
    """
    for v in values:
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        return v
    return default
    