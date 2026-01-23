import React, { useState, useEffect } from 'react';
import { Dashboard } from './components/Dashboard';
import { SetupWizard } from './components/setup/SetupWizard';
import { LogViewer } from './components/setup/LogViewer';
import { useConfigStatus } from './hooks/useSetup';
import { logEvent } from './utils/logger';
import './styles/index.css';

function App() {
  const { status, loading, isFirstRun } = useConfigStatus();
  const [showSetup, setShowSetup] = useState(null);
  const [showLogs, setShowLogs] = useState(false);

  useEffect(() => {
    if (!loading && isFirstRun !== null) {
      setShowSetup(isFirstRun);
    }
  }, [loading, isFirstRun]);

  useEffect(() => {
    const handleError = event => {
      logEvent({
        level: 'error',
        source: 'window',
        message: event.message || 'Unhandled error',
        details: event.error?.stack || event.error?.message || event.error,
      });
    };
    const handleRejection = event => {
      logEvent({
        level: 'error',
        source: 'window',
        message: 'Unhandled promise rejection',
        details: event.reason?.stack || event.reason?.message || event.reason,
      });
    };
    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleRejection);
    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleRejection);
    };
  }, []);

  // Show loading while checking config status
  if (loading || showSetup === null) {
    return (
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        background: 'var(--bg-primary)',
        color: 'var(--text-secondary)'
      }}>
        Loading...
      </div>
    );
  }

  // Show setup wizard on first run or when manually opened
  if (showLogs) {
    return (
      <LogViewer onBack={() => setShowLogs(false)} />
    );
  }

  if (showSetup) {
    return (
      <SetupWizard
        onComplete={() => setShowSetup(false)}
        onOpenLogs={() => setShowLogs(true)}
      />
    );
  }

  // Show dashboard with ability to open setup
  return (
    <Dashboard onOpenSetup={() => setShowSetup(true)} />
  );
}

export default App;
