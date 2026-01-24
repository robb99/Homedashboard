import React from 'react';
import { useSetup } from '../../hooks/useSetup';
import { UnifiSetup } from './UnifiSetup';
import { ProxmoxSetup } from './ProxmoxSetup';
import { PlexSetup } from './PlexSetup';
import { DockerSetup } from './DockerSetup';
import { CalendarSetup } from './CalendarSetup';
import { WeatherSetup } from './WeatherSetup';
import { NewsSetup } from './NewsSetup';
import { UnraidSetup } from './UnraidSetup';
import '../../styles/setup.css';

export function SetupWizard({ onComplete, onOpenLogs }) {
  const {
    config,
    loading,
    saving,
    saveResult,
    testResults,
    testingService,
    updateField,
    testConnection,
    saveConfig,
    isServiceConfigured,
  } = useSetup();

  const handleSave = async () => {
    const result = await saveConfig();
    if (result.success && onComplete) {
      // Give a moment to show success message
      setTimeout(() => onComplete(), 1000);
    }
  };

  if (loading) {
    return (
      <div className="setup-wizard">
        <div className="setup-container">
          <div className="setup-header">
            <h1>Loading...</h1>
          </div>
        </div>
      </div>
    );
  }

  if (!config) {
    return (
      <div className="setup-wizard">
        <div className="setup-container">
          <div className="setup-header">
            <h1>Setup Wizard</h1>
            <p>Unable to load configuration. Please check if the backend is running.</p>
          </div>
          <div className="setup-actions">
            <button className="skip-btn" onClick={onComplete}>
              Continue to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="setup-wizard">
      <div className="setup-container">
        <div className="setup-header">
          <div className="setup-header-row">
            <div>
              <h1>HomeLab Dashboard Setup</h1>
              <p>Configure your services below. You can test each connection before saving.</p>
            </div>
            {onOpenLogs && (
              <button className="log-btn" onClick={onOpenLogs}>
                View Logs
              </button>
            )}
          </div>
        </div>

        {saveResult && (
          <div className={`save-message ${saveResult.success ? 'success' : 'error'}`}>
            {saveResult.message}
          </div>
        )}

        <div className="accordion">
          <UnifiSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'unifi'}
            testResult={testResults.unifi}
            isConfigured={isServiceConfigured('unifi')}
          />

          <ProxmoxSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'proxmox'}
            testResult={testResults.proxmox}
            isConfigured={isServiceConfigured('proxmox')}
          />

          <PlexSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'plex'}
            testResult={testResults.plex}
            isConfigured={isServiceConfigured('plex')}
          />

          <DockerSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'docker'}
            testResult={testResults.docker}
            isConfigured={isServiceConfigured('docker')}
          />

          <CalendarSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'calendar'}
            testResult={testResults.calendar}
            isConfigured={isServiceConfigured('calendar')}
          />

          <WeatherSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'weather'}
            testResult={testResults.weather}
            isConfigured={isServiceConfigured('weather')}
          />

          <NewsSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'news'}
            testResult={testResults.news}
            isConfigured={isServiceConfigured('news')}
          />

          <UnraidSetup
            config={config}
            updateField={updateField}
            onTest={testConnection}
            testing={testingService === 'unraid'}
            testResult={testResults.unraid}
            isConfigured={isServiceConfigured('unraid')}
          />
        </div>

        <div className="setup-actions">
          <button
            className="skip-btn"
            onClick={onComplete}
            disabled={saving}
          >
            Skip for Now
          </button>
          <button
            className={`save-btn ${saving ? 'saving' : ''}`}
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? (
              <>
                <span className="spinner" />
                Saving...
              </>
            ) : (
              'Save Configuration'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
