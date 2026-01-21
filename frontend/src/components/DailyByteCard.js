import React, { useState, useEffect } from 'react';

const CACHE_KEY = 'dailyByteData';
const CACHE_DURATION = 24 * 60 * 60 * 1000; // 24 hours in ms
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

// ZenQuotes API - returns array of 50 quotes, we pick 5 random ones
async function fetchQuotes() {
  try {
    const response = await fetch('https://zenquotes.io/api/quotes');
    const data = await response.json();
    if (Array.isArray(data) && data.length > 0) {
      // Shuffle and pick 5 random quotes
      const shuffled = data.sort(() => 0.5 - Math.random());
      return shuffled.slice(0, ITEMS_PER_TYPE).map(q => ({ text: q.q, author: q.a }));
    }
  } catch (e) {
    console.error('Error fetching quotes:', e);
  }
  return FALLBACK_DATA.quotes;
}

// JokeAPI - fetch multiple jokes
async function fetchJokes() {
  try {
    const response = await fetch('https://v2.jokeapi.dev/joke/Programming,Miscellaneous,Pun?safe-mode&amount=5');
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
  } catch (e) {
    console.error('Error fetching jokes:', e);
  }
  return FALLBACK_DATA.jokes;
}

// Numbers API (HTTPS) - fetch multiple trivia facts
async function fetchTrivia() {
  try {
    const promises = [];
    for (let i = 0; i < ITEMS_PER_TYPE; i++) {
      promises.push(
        fetch('https://numbersapi.com/random/trivia')
          .then(res => res.text())
          .catch(() => null)
      );
    }
    const results = await Promise.all(promises);
    const validResults = results.filter(r => r && r.length > 0);
    if (validResults.length >= 3) {
      // Pad with fallbacks if needed
      while (validResults.length < ITEMS_PER_TYPE) {
        validResults.push(FALLBACK_DATA.trivia[validResults.length]);
      }
      return validResults;
    }
  } catch (e) {
    console.error('Error fetching trivia:', e);
  }
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
    const data = await response.json();
    if (data.events && Array.isArray(data.events) && data.events.length > 0) {
      // Get 5 random events from the list
      const shuffled = data.events.sort(() => 0.5 - Math.random());
      return shuffled.slice(0, ITEMS_PER_TYPE).map(e => ({
        year: e.year,
        text: e.text
      }));
    }
  } catch (e) {
    console.error('Error fetching history:', e);
  }
  return FALLBACK_DATA.history;
}

// Random Word + Dictionary API
async function fetchWords() {
  try {
    const words = [];
    for (let i = 0; i < ITEMS_PER_TYPE; i++) {
      try {
        const wordRes = await fetch('https://random-word-api.herokuapp.com/word');
        const wordData = await wordRes.json();
        const word = wordData[0];

        const defRes = await fetch(`https://api.dictionaryapi.dev/api/v2/entries/en/${word}`);
        const defData = await defRes.json();

        if (Array.isArray(defData) && defData[0]?.meanings?.[0]) {
          words.push({
            word,
            partOfSpeech: defData[0].meanings[0].partOfSpeech || 'word',
            definition: defData[0].meanings[0].definitions[0]?.definition || 'No definition available'
          });
        } else {
          // If no definition found, try another word
          words.push(FALLBACK_DATA.words[i]);
        }
      } catch (e) {
        // If individual word fails, use fallback
        words.push(FALLBACK_DATA.words[i]);
      }
    }
    return words.length > 0 ? words : FALLBACK_DATA.words;
  } catch (e) {
    console.error('Error fetching words:', e);
  }
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
