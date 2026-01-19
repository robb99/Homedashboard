import React, { useState, useEffect } from 'react';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export function WeatherWidget() {
  const [weather, setWeather] = useState(null);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch(`${API_URL}/weather`);
        if (response.ok) {
          const data = await response.json();
          if (data.status === 'healthy') {
            setWeather(data);
          }
        }
      } catch (err) {
        console.error('Failed to fetch weather:', err);
      }
    };

    fetchWeather();
    const interval = setInterval(fetchWeather, 300000); // Refresh every 5 minutes

    return () => clearInterval(interval);
  }, []);

  if (!weather || !weather.today) {
    return null;
  }

  return (
    <div className="weather-widget">
      <span className="weather-icon">{weather.today.icon}</span>
      <span className="weather-temp">{weather.today.temperature}°F Today</span>
      {weather.tomorrow && (
        <>
          <span className="weather-label">|</span>
          <span className="weather-temp">{weather.tomorrow.temperature}°F Tomorrow</span>
        </>
      )}
    </div>
  );
}
