import React from 'react';

export function RefreshIndicator({ loading, lastFetch }) {
  const formatTime = (date) => {
    if (!date) return '';
    return date.toLocaleTimeString();
  };

  return (
    <div className={`refresh-indicator-fixed ${loading ? 'loading' : ''}`}>
      {loading ? '◌ Refreshing...' : `◉ Last refresh: ${formatTime(lastFetch)}`}
    </div>
  );
}
