import React, { useState, useEffect } from 'react';
import { logEvent } from '../utils/logger';

const CACHE_KEY = 'dailyByteData';
const CACHE_DURATION = 6 * 60 * 60 * 1000; // 6 hours in ms
const ROTATION_INTERVAL = 60000; // 60 seconds
const ITEMS_PER_TYPE = 5;

const FALLBACK_DATA = {
  quotes: [
    { text: "The only way to do great work is to love what you do.", author: "Steve Jobs" },
    { text: "In the middle of difficulty lies opportunity.", author: "Albert Einstein" },
    { text: "The best way to predict the future is to create it.", author: "Peter Drucker" },
    { text: "Be the change that you want to see in the world.", author: "Mahatma Gandhi" },
    { text: "Through discipline comes freedom.", author: "Aristotle" }
  ],
  trivia: [
    "The first computer bug was an actual moth found in a Harvard computer in 1947.",
    "The QWERTY keyboard was designed to slow typists down to prevent jamming.",
    "The first computer programmer was Ada Lovelace in the 1840s.",
    "Email is older than the World Wide Web.",
    "The first 1GB hard drive weighed 550 pounds and cost $40,000."
  ],
  jokes: [
    { setup: "Why do programmers prefer dark mode?", punchline: "Because light attracts bugs!" },
    { setup: "Why do Java developers wear glasses?", punchline: "Because they can't C#!" },
    { setup: "A SQL query walks into a bar, walks up to two tables and asks...", punchline: "Can I join you?" },
    { setup: "Why did the developer go broke?", punchline: "Because he used up all his cache!" },
    { setup: "What's a programmer's favorite hangout place?", punchline: "Foo Bar!" }
  ],
  history: [
    { year: 1969, text: "Apollo 11 astronauts Neil Armstrong and Buzz Aldrin landed on the Moon." },
    { year: 1776, text: "The United States Declaration of Independence was adopted." },
    { year: 1989, text: "Tim Berners-Lee proposed the World Wide Web." },
    { year: 1903, text: "The Wright Brothers made the first powered airplane flight." },
    { year: 1962, text: "John Glenn became the first American to orbit the Earth." }
  ],
  words: [
    { word: "serendipity", partOfSpeech: "noun", definition: "The occurrence of events by chance in a happy way." },
    { word: "ephemeral", partOfSpeech: "adjective", definition: "Lasting for a very short time." },
    { word: "ubiquitous", partOfSpeech: "adjective", definition: "Present, appearing, or found everywhere." },
    { word: "paradigm", partOfSpeech: "noun", definition: "A typical example or pattern of something." },
    { word: "eloquent", partOfSpeech: "adjective", definition: "Fluent or persuasive in speaking or writing." }
  ]
};

function logFallback(section, reason, details = null) {
  logEvent({
    level: 'warn',
    source: `DailyByte/${section}`,
    message: 'Using fallback data',
    details: {
      reason,
      ...(details ? { details } : {}),
    },
  });
}

function buildErrorDetails(error, extra = {}) {
  return {
    error: error?.message || error,
    ...getNetworkContext(),
    ...extra,
  };
}

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
    logEvent({
      level: 'warn',
      source: 'DailyByte/cache',
      message: 'Failed to read local cache',
      details: buildErrorDetails(e),
    });
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
    logEvent({
      level: 'warn',
      source: 'DailyByte/cache',
      message: 'Failed to write local cache',
      details: buildErrorDetails(e),
    });
  }
}

function getNetworkContext() {
  return {
    online: typeof navigator !== 'undefined' ? navigator.onLine : null,
    userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : null,
  };
}

// Quotes fetched via backend to avoid CORS issues and centralize logging
async function fetchQuotes() {
  try {
    const response = await fetch('/api/quotes');
    if (!response.ok) {
      const reason = `Backend returned HTTP ${response.status}`;
      logEvent({
        level: 'error',
        source: 'DailyByte/quotes',
        message: 'Failed to fetch quotes from backend',
        details: {
          status: response.status,
          statusText: response.statusText,
          url: response.url,
          ...getNetworkContext(),
        },
      });
      logFallback('quotes', reason, {
        url: response.url,
        ...getNetworkContext(),
      });
      return FALLBACK_DATA.quotes;
    }

    const payload = await response.json();
    if (payload?.fallback) {
      logFallback('quotes', payload.reason || 'Backend reported fallback', {
        source: payload.source,
        ...getNetworkContext(),
      });
    }

    if (Array.isArray(payload?.quotes) && payload.quotes.length > 0) {
      return payload.quotes;
    }

    logFallback('quotes', 'Backend returned empty or invalid quotes payload', {
      payload,
      ...getNetworkContext(),
    });
    return FALLBACK_DATA.quotes;
  } catch (e) {
    console.error('Error fetching quotes from backend:', e);
    logEvent({
      level: 'error',
      source: 'DailyByte/quotes',
      message: 'Failed to fetch quotes from backend',
      details: buildErrorDetails(e),
    });
    logFallback('quotes', 'Backend request failed', buildErrorDetails(e));
  }

  return FALLBACK_DATA.quotes;
}

// JokeAPI - fetch multiple jokes
async function fetchJokes() {
  try {
    const response = await fetch('https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun?safe-mode&amount=5');
    if (!response.ok) {
      logFallback('jokes', `JokeAPI returned HTTP ${response.status}`);
    } else {
      const data = await response.json();
      if (data.jokes && Array.isArray(data.jokes)) {
        return data.jokes.map(joke => {
          if (joke.type === 'twopart') {
            return { setup: joke.setup, punchline: joke.delivery };
          } else {
            return { setup: joke.joke, punchline: null };
          }
        });
      }
      logFallback('jokes', 'JokeAPI returned an empty or invalid payload');
    }
  } catch (e) {
    console.error('Error fetching jokes:', e);
    logEvent({
      level: 'error',
      source: 'DailyByte/jokes',
      message: 'Failed to fetch jokes',
      details: buildErrorDetails(e),
    });
  }
  logFallback('jokes', 'Using built-in fallback jokes due to fetch failure');
  return FALLBACK_DATA.jokes;
}

function decodeTriviaValue(value) {
  if (typeof value !== 'string') {
    return value;
  }
  try {
    return decodeURIComponent(value);
  } catch (e) {
    return value;
  }
}

// Useless Facts API - fetch multiple trivia facts
async function fetchTrivia() {
  try {
    const promises = [];
    for (let i = 0; i < ITEMS_PER_TYPE; i++) {
      promises.push(
        fetch('https://uselessfacts.jsph.pl/api/v2/facts/random')
          .then(res => res.json())
          .then(data => decodeTriviaValue(data.text))
          .catch(() => null)
      );
    }
    const results = await Promise.all(promises);
    const validResults = results.filter(r => r && r.length > 0);
    if (validResults.length >= 3) {
      while (validResults.length < ITEMS_PER_TYPE) {
        validResults.push(FALLBACK_DATA.trivia[validResults.length]);
      }
      return validResults;
    }
    logFallback('trivia', `Only ${validResults.length} trivia facts fetched successfully`);
  } catch (e) {
    console.error('Error fetching trivia:', e);
    logEvent({
      level: 'error',
      source: 'DailyByte/trivia',
      message: 'Failed to fetch trivia',
      details: buildErrorDetails(e),
    });
  }
  logFallback('trivia', 'Using built-in fallback trivia due to fetch failure');
  return FALLBACK_DATA.trivia;
}

// Wikimedia API - This Day in History
async function fetchHistory() {
  try {
    const now = new Date();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const response = await fetch(
      `https://api.wikimedia.org/feed/v1/wikipedia/en/onthisday/all/${month}/${day}`
    );
    if (!response.ok) {
      logFallback('history', `Wikimedia returned HTTP ${response.status}`);
    } else {
      const data = await response.json();
      if (data.events && Array.isArray(data.events) && data.events.length > 0) {
        // Get 5 random events from the list
        const shuffled = data.events.sort(() => 0.5 - Math.random());
        return shuffled.slice(0, ITEMS_PER_TYPE).map(e => ({
          year: e.year,
          text: e.text
        }));
      }
      logFallback('history', 'Wikimedia returned an empty or invalid payload');
    }
  } catch (e) {
    console.error('Error fetching history:', e);
    logEvent({
      level: 'error',
      source: 'DailyByte/history',
      message: 'Failed to fetch history',
      details: buildErrorDetails(e),
    });
  }
  logFallback('history', 'Using built-in fallback history due to fetch failure');
  return FALLBACK_DATA.history;
}

// Random Word + Dictionary API
async function fetchWords() {
  try {
    const words = [];
    let fallbackCount = 0;
    for (let i = 0; i < ITEMS_PER_TYPE; i++) {
      try {
        const wordRes = await fetch('https://random-word-api.herokuapp.com/word');
        if (!wordRes.ok) {
          fallbackCount += 1;
          words.push(FALLBACK_DATA.words[i]);
          continue;
        }
        const wordData = await wordRes.json();
        const word = wordData[0];

        const defRes = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${word}`);
        if (!defRes.ok) {
          fallbackCount += 1;
          words.push(FALLBACK_DATA.words[i]);
          continue;
        }
        const defData = await defRes.json();

        if (Array.isArray(defData) && defData[0]?.meanings?.[0]) {
          words.push({
            word,
            partOfSpeech: defData[0].meanings[0].partOfSpeech || 'word',
            definition: defData[0].meanings[0].definitions[0]?.definition || 'No definition available'
          });
        } else {
          fallbackCount += 1;
          words.push(FALLBACK_DATA.words[i]);
        }
      } catch (e) {
        // If individual word fails, use fallback
        fallbackCount += 1;
        words.push(FALLBACK_DATA.words[i]);
      }
    }
    if (fallbackCount > 0) {
      logFallback(
        'words',
        `Used fallback definitions for ${fallbackCount} of ${ITEMS_PER_TYPE} words`,
        'Random word or dictionary lookup failed or returned no definitions'
      );
    }
    return words.length > 0 ? words : FALLBACK_DATA.words;
  } catch (e) {
    console.error('Error fetching words:', e);
    logEvent({
      level: 'error',
      source: 'DailyByte/words',
      message: 'Failed to fetch words',
      details: buildErrorDetails(e),
    });
  }
  logFallback('words', 'Using built-in fallback words due to fetch failure');
  return FALLBACK_DATA.words;
}

export function DailyByteCard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [indices, setIndices] = useState({ quote: 0, trivia: 0, joke: 0, history: 0, word: 0 });

  // Rotation effect - every 60 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      setIndices(prev => ({
        quote: (prev.quote + 1) % ITEMS_PER_TYPE,
        trivia: (prev.trivia + 1) % ITEMS_PER_TYPE,
        joke: (prev.joke + 1) % ITEMS_PER_TYPE,
        history: (prev.history + 1) % ITEMS_PER_TYPE,
        word: (prev.word + 1) % ITEMS_PER_TYPE
      }));
    }, ROTATION_INTERVAL);
    return () => clearInterval(interval);
  }, []);

  // Data fetching effect
  useEffect(() => {
    async function loadData() {
      // Check cache first
      const cached = getCachedData();
      if (cached && cached.quotes && cached.history && cached.words) {
        setData(cached);
        setLoading(false);
        return;
      }

      // Fetch fresh data from all APIs in parallel
      const [quotes, jokes, trivia, history, words] = await Promise.all([
        fetchQuotes(),
        fetchJokes(),
        fetchTrivia(),
        fetchHistory(),
        fetchWords()
      ]);

      const newData = { quotes, jokes, trivia, history, words };
      setCachedData(newData);
      setData(newData);
      setLoading(false);
    }

    loadData();
  }, []);

  const currentQuote = data?.quotes?.[indices.quote] || FALLBACK_DATA.quotes[0];
  const currentTrivia = data?.trivia?.[indices.trivia] || FALLBACK_DATA.trivia[0];
  const currentJoke = data?.jokes?.[indices.joke] || FALLBACK_DATA.jokes[0];
  const currentHistory = data?.history?.[indices.history] || FALLBACK_DATA.history[0];
  const currentWord = data?.words?.[indices.word] || FALLBACK_DATA.words[0];

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
                <p className="daily-quote-text">"{currentQuote.text}"</p>
                <span className="daily-quote-author">— {currentQuote.author}</span>
              </div>
            </div>

            {/* Trivia Section */}
            <div className="daily-section">
              <div className="daily-section-icon">🧠</div>
              <div className="daily-section-content">
                <p className="daily-trivia-text">{currentTrivia}</p>
              </div>
            </div>

            {/* Joke Section */}
            <div className="daily-section">
              <div className="daily-section-icon">😄</div>
              <div className="daily-section-content">
                <p className="daily-joke-text">
                  {currentJoke.setup}
                  {currentJoke.punchline && (
                    <span className="daily-joke-punchline"> {currentJoke.punchline}</span>
                  )}
                </p>
              </div>
            </div>

            {/* History Section */}
            <div className="daily-section">
              <div className="daily-section-icon">📅</div>
              <div className="daily-section-content">
                <p className="daily-history-text">
                  On this day in <span className="daily-history-year">{currentHistory.year}</span>, {currentHistory.text.charAt(0).toLowerCase() + currentHistory.text.slice(1)}
                </p>
              </div>
            </div>

            {/* Word of the Day Section */}
            <div className="daily-section">
              <div className="daily-section-icon">📖</div>
              <div className="daily-section-content">
                <p className="daily-word-text">
                  <span className="daily-word-term">{currentWord.word}</span>
                  <span className="daily-word-pos"> ({currentWord.partOfSpeech})</span>
                  <span className="daily-word-def">: {currentWord.definition}</span>
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
