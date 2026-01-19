import React from 'react';
import { getStatusClass, formatRelativeTime } from '../hooks/useDashboard';

export function StatusCard({ title, icon, status, lastUpdated, error, children }) {
  const statusClass = getStatusClass(status);
  const statusLabel = status ? status.charAt(0).toUpperCase() + status.slice(1) : 'Unknown';

  return (
    <div className="card">
      <div className="card-header">
        <h2 className="card-title">
          <span className="card-icon">{icon}</span>
          {title}
        </h2>
        <div className={`card-status ${statusClass}`}>
          <span className="status-dot"></span>
          {statusLabel}
        </div>
      </div>
      <div className="card-body">
        {error ? (
          <div className="error-message">{error}</div>
        ) : (
          children
        )}
      </div>
      {lastUpdated && (
        <div className="card-footer">
          Updated {formatRelativeTime(lastUpdated)}
        </div>
      )}
    </div>
  );
}
