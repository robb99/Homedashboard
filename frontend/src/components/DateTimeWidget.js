import React, { useState, useEffect } from 'react';

export function DateTimeWidget() {
  const [dateTime, setDateTime] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setDateTime(new Date());
    }, 60000); // Update every minute

    return () => clearInterval(interval);
  }, []);

  const formatDateTime = (date) => {
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
  };

  return (
    <div className="datetime-widget">
      <span className="datetime-icon">📅</span>
      <span className="datetime-text">{formatDateTime(dateTime)}</span>
    </div>
  );
}
