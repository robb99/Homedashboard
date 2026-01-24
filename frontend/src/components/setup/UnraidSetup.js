import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function UnraidSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('unraid', {
      unraid_host: config.unraid_host,
      unraid_username: config.unraid_username,
      unraid_password: config.unraid_password,
      unraid_verify_ssl: config.unraid_verify_ssl,
    });
  };

  return (
    <AccordionSection
      title="UNRAID"
      icon="&#128229;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Host URL</label>
            <input
              type="text"
              className="form-input"
              placeholder="http://192.168.1.50"
              value={config.unraid_host || ''}
              onChange={(e) => updateField('unraid_host', e.target.value)}
            />
            <span className="form-hint">Include http:// or https:// (Unraid 6.12+ required)</span>
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              placeholder="root"
              value={config.unraid_username || ''}
              onChange={(e) => updateField('unraid_username', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="Your Unraid password"
              value={config.unraid_password || ''}
              onChange={(e) => updateField('unraid_password', e.target.value)}
            />
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="unraid_verify_ssl"
              checked={config.unraid_verify_ssl || false}
              onChange={(e) => updateField('unraid_verify_ssl', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="unraid_verify_ssl">
              Verify SSL Certificate
            </label>
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="unraid_enabled"
              checked={config.unraid_enabled !== false}
              onChange={(e) => updateField('unraid_enabled', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="unraid_enabled">
              Enable UNRAID Monitoring
            </label>
          </div>
        </div>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
          disabled={!config.unraid_host || !config.unraid_username || !config.unraid_password}
        />
      </div>
    </AccordionSection>
  );
}
