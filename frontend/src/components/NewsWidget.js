import React, { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function NewsWidget() {
  const [news, setNews] = useState(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const response = await fetch(`${API_URL}/news`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'healthy' && data.headlines?.length > 0) {
            setNews(data);
          }
        }
      } catch (err) {
        console.error('Failed to fetch news:', err);
      }
    };

    fetchNews();
    const fetchInterval = setInterval(fetchNews, 300000); // Refresh every 5 minutes

    return () => clearInterval(fetchInterval);
  }, []);

  // Rotate through headlines every 10 seconds
  useEffect(() => {
    if (!news || !news.headlines?.length) return;

    const rotateInterval = setInterval(() => {
      setCurrentIndex((prev) => (prev + 1) % news.headlines.length);
    }, 10000);

    return () => clearInterval(rotateInterval);
  }, [news]);

  if (!news || !news.headlines?.length) {
    return null;
  }

  const headline = news.headlines[currentIndex];

  return (
    <div className="news-widget">
      <span className="news-icon">📰</span>
      <span className="news-headline" title={headline.title}>
        {headline.title}
      </span>
    </div>
  );
}
