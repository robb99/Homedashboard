import React, { useState, useEffect } from 'react';
import { Dashboard } from './components/Dashboard';
import { SetupWizard } from './components/setup/SetupWizard';
import { useConfigStatus } from './hooks/useSetup';
import './styles/index.css';

function App() {
  const { status, loading, isFirstRun } = useConfigStatus();
  const [showSetup, setShowSetup] = useState(null);

  useEffect(() => {
    if (!loading && isFirstRun !== null) {
      setShowSetup(isFirstRun);
    }
  }, [loading, isFirstRun]);

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
  if (showSetup) {
    return (
      <SetupWizard onComplete={() => setShowSetup(false)} />
    );
  }

  // Show dashboard with ability to open setup
  return (
    <Dashboard onOpenSetup={() => setShowSetup(true)} />
  );
}

export default App;
