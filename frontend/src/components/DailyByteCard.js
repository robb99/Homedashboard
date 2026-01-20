import React, { useState, useEffect } from 'react';

const CACHE_KEY = 'dailyByteData';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours in ms

const FALLBACK_DATA = {
  quote: { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
  trivia: "The first computer bug was an actual bug—a moth found in a Harvard computer in 1947.",
  joke: { setup: "Why do programmers prefer dark mode?", punchline: "Because light attracts bugs!" }
};

function getCachedData() {
  try {
    const cached = localStorage.getItem(CACHE_KEY);
    if (cached) {
      const { data, timestamp } = JSON.parse(cached);
      if (Date.now() - timestamp < CACHE_DURATION) {
        return data;
      }
    }
  } catch (e) {
    console.error('Error reading cache:', e);
  }
  return null;
}

function setCachedData(data) {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify({
      data,
      timestamp: Date.now()
    }));
  } catch (e) {
    console.error('Error writing cache:', e);
  }
}

async function fetchQuote() {
  try {
    const response = await fetch('https://zenquotes.io/api/today');
    const data = await response.json();
    if (data && data[0]) {
      return { text: data[0].q, author: data[0].a };
    }
  } catch (e) {
    console.error('Error fetching quote:', e);
  }
  return FALLBACK_DATA.quote;
}

async function fetchJoke() {
  try {
    const response = await fetch('https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun?safe-mode');
    const data = await response.json();
    if (data.type === 'twopart') {
      return { setup: data.setup, punchline: data.delivery };
    } else if (data.type === 'single') {
      return { setup: data.joke, punchline: null };
    }
  } catch (e) {
    console.error('Error fetching joke:', e);
  }
  return FALLBACK_DATA.joke;
}

async function fetchTrivia() {
  try {
    const response = await fetch('http://numbersapi.com/random/trivia');
    const text = await response.text();
    if (text) {
      return text;
    }
  } catch (e) {
    console.error('Error fetching trivia:', e);
  }
  return FALLBACK_DATA.trivia;
}

export function DailyByteCard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      // Check cache first
      const cached = getCachedData();
      if (cached) {
        setData(cached);
        setLoading(false);
        return;
      }

      // Fetch fresh data from all APIs in parallel
      const [quote, joke, trivia] = await Promise.all([
        fetchQuote(),
        fetchJoke(),
        fetchTrivia()
      ]);

      const newData = { quote, joke, trivia };
      setCachedData(newData);
      setData(newData);
      setLoading(false);
    }

    loadData();
  }, []);

  return (
    <div className="card daily-byte-card">
      <div className="card-header">
        <h2 className="card-title">
          <span className="card-icon">🧠</span>
          A Daily Byte
        </h2>
      </div>
      <div className="card-body">
        {loading ? (
          <div className="daily-loading">Loading daily content...</div>
        ) : (
          <>
            {/* Quote Section */}
            <div className="daily-section">
              <div className="daily-section-icon">💬</div>
              <div className="daily-section-content">
                <p className="daily-quote-text">"{data?.quote?.text}"</p>
                <span className="daily-quote-author">— {data?.quote?.author}</span>
              </div>
            </div>

            {/* Trivia Section */}
            <div className="daily-section">
              <div className="daily-section-icon">🧠</div>
              <div className="daily-section-content">
                <p className="daily-trivia-text">{data?.trivia}</p>
              </div>
            </div>

            {/* Joke Section */}
            <div className="daily-section">
              <div className="daily-section-icon">😄</div>
              <div className="daily-section-content">
                <p className="daily-joke-text">
                  {data?.joke?.setup}
                  {data?.joke?.punchline && (
                    <span className="daily-joke-punchline"> {data?.joke?.punchline}</span>
                  )}
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
