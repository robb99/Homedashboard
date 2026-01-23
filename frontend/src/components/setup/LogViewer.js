import React, { useEffect, useMemo, useState } from 'react';
import { getLogs, clearLogs, subscribeToLogs, logEvent } from '../../utils/logger';
import '../../styles/setup.css';

function formatTimestamp(ts) {
  try {
    return new Date(ts).toLocaleString();
  } catch (err) {
    return ts;
  }
}

function formatDetails(details) {
  if (details === null || details === undefined) return '';
  if (typeof details === 'string') return details;
  try {
    return JSON.stringify(details, null, 2);
  } catch (err) {
    return String(details);
  }
}

export function LogViewer({ onBack }) {
  const [localLogs, setLocalLogs] = useState(() => getLogs().slice().reverse());
  const [backendLogs, setBackendLogs] = useState([]);
  const [loadingBackend, setLoadingBackend] = useState(false);
  const [filterText, setFilterText] = useState('');
  const [levelFilter, setLevelFilter] = useState('all');

  useEffect(() => {
    const unsubscribe = subscribeToLogs(
      entry => {
        setLocalLogs(prev => [entry, ...prev]);
      },
      () => {
        setLocalLogs([]);
      }
    );
    return unsubscribe;
  }, []);

  const fetchBackendLogs = async () => {
    setLoadingBackend(true);
    try {
      const response = await fetch('/api/logs');
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const result = await response.json();
      const normalized = (result.entries || []).map(entry => ({
        ...entry,
        source: `backend/${entry.logger}`,
      }));
      setBackendLogs(normalized.reverse());
    } catch (err) {
      logEvent({
        level: 'error',
        source: 'LogViewer/backend',
        message: 'Failed to fetch backend logs',
        details: err?.message || err,
      });
    } finally {
      setLoadingBackend(false);
    }
  };

  useEffect(() => {
    fetchBackendLogs();
  }, []);

  const handleClear = async () => {
    clearLogs();
    try {
      await fetch('/api/logs/clear', { method: 'POST' });
      setBackendLogs([]);
    } catch (err) {
      logEvent({
        level: 'error',
        source: 'LogViewer/backend',
        message: 'Failed to clear backend logs',
        details: err?.message || err,
      });
    }
  };

  const logs = useMemo(() => {
    const merged = [...localLogs, ...backendLogs];
    merged.sort((a, b) => {
      const aTime = new Date(a.timestamp).getTime();
      const bTime = new Date(b.timestamp).getTime();
      return bTime - aTime;
    });
    return merged;
  }, [localLogs, backendLogs]);

  const filteredLogs = useMemo(() => {
    const needle = filterText.trim().toLowerCase();
    const levelMatches = level => {
      if (levelFilter === 'all') return true;
      if (levelFilter === 'warn') {
        return level === 'warn' || level === 'warning';
      }
      return level === levelFilter;
    };
    return logs.filter(entry => {
      if (!levelMatches(entry.level)) {
        return false;
      }
      if (!needle) return true;
      const haystack = [
        entry.message,
        entry.source,
        entry.logger,
        typeof entry.details === 'string' ? entry.details : JSON.stringify(entry.details || ''),
      ]
        .filter(Boolean)
        .join(' ')
        .toLowerCase();
      return haystack.includes(needle);
    });
  }, [logs, filterText, levelFilter]);

  return (
    <div className="setup-wizard">
      <div className="setup-container log-viewer">
        <div className="setup-header log-header">
          <h1>Running Error Log</h1>
          <p>Shows client-side and API errors captured by the dashboard.</p>
          <div className="log-actions">
            <button className="skip-btn" onClick={onBack}>
              Back to Settings
            </button>
            <button className="skip-btn" onClick={fetchBackendLogs} disabled={loadingBackend}>
              {loadingBackend ? 'Refreshing...' : 'Refresh Backend Logs'}
            </button>
            <button className="save-btn" onClick={handleClear}>
              Clear Log
            </button>
          </div>
          <div className="log-filters">
            <input
              className="log-filter-input"
              type="text"
              placeholder="Filter by message, source, or details"
              value={filterText}
              onChange={event => setFilterText(event.target.value)}
            />
            <select
              className="log-filter-select"
              value={levelFilter}
              onChange={event => setLevelFilter(event.target.value)}
            >
              <option value="all">All levels</option>
              <option value="error">Error</option>
              <option value="warn">Warn/Warning</option>
              <option value="info">Info</option>
              <option value="debug">Debug</option>
            </select>
          </div>
        </div>

        <div className="log-list">
          {filteredLogs.length === 0 && (
            <div className="log-empty">
              {logs.length === 0 ? 'No errors logged yet.' : 'No logs match your filter.'}
            </div>
          )}
          {filteredLogs.map(entry => (
            <div key={entry.id} className={`log-entry log-${entry.level}`}>
              <div className="log-meta">
                <span className="log-level">{entry.level}</span>
                <span className="log-source">{entry.source || entry.logger || 'app'}</span>
                <span className="log-time">{formatTimestamp(entry.timestamp)}</span>
              </div>
              <div className="log-message">{entry.message}</div>
              {entry.details ? (
                <pre className="log-details">{formatDetails(entry.details)}</pre>
              ) : null}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
