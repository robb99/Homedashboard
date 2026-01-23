const LOG_STORAGE_KEY = 'homedashboard.logs';
const MAX_LOGS = 200;

function safeReadLogs() {
  try {
    const raw = localStorage.getItem(LOG_STORAGE_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (err) {
    return [];
  }
}

function safeWriteLogs(logs) {
  try {
    localStorage.setItem(LOG_STORAGE_KEY, JSON.stringify(logs));
  } catch (err) {
    // Ignore storage errors
  }
}

export function getLogs() {
  return safeReadLogs();
}

export function clearLogs() {
  try {
    localStorage.removeItem(LOG_STORAGE_KEY);
  } catch (err) {
    // Ignore storage errors
  }
  window.dispatchEvent(new CustomEvent('homedashboard-log-cleared'));
}

export function logEvent({
  level = 'error',
  source = 'app',
  message = 'Unknown error',
  details = null,
} = {}) {
  const entry = {
    id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    timestamp: new Date().toISOString(),
    level,
    source,
    message,
    details,
  };

  const logs = safeReadLogs();
  logs.push(entry);
  if (logs.length > MAX_LOGS) {
    logs.splice(0, logs.length - MAX_LOGS);
  }
  safeWriteLogs(logs);

  window.dispatchEvent(new CustomEvent('homedashboard-log-added', { detail: entry }));
  return entry;
}

export function subscribeToLogs(onAdd, onClear) {
  const handleAdd = event => {
    if (onAdd) onAdd(event.detail);
  };
  const handleClear = () => {
    if (onClear) onClear();
  };

  window.addEventListener('homedashboard-log-added', handleAdd);
  window.addEventListener('homedashboard-log-cleared', handleClear);

  return () => {
    window.removeEventListener('homedashboard-log-added', handleAdd);
    window.removeEventListener('homedashboard-log-cleared', handleClear);
  };
}
