import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function UnifiSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('unifi', {
      unifi_host: config.unifi_host,
      unifi_username: config.unifi_username,
      unifi_password: config.unifi_password,
      unifi_site: config.unifi_site,
      unifi_verify_ssl: config.unifi_verify_ssl,
    });
  };

  return (
    <AccordionSection
      title="UniFi Controller"
      icon="&#128225;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Host URL</label>
            <input
              type="text"
              className="form-input"
              placeholder="https://192.168.1.1"
              value={config.unifi_host || ''}
              onChange={(e) => updateField('unifi_host', e.target.value)}
            />
            <span className="form-hint">Include https:// and port if needed</span>
          </div>
          <div className="form-group">
            <label className="form-label">Site</label>
            <input
              type="text"
              className="form-input"
              placeholder="default"
              value={config.unifi_site || ''}
              onChange={(e) => updateField('unifi_site', e.target.value)}
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Username</label>
            <input
              type="text"
              className="form-input"
              placeholder="admin"
              value={config.unifi_username || ''}
              onChange={(e) => updateField('unifi_username', e.target.value)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="********"
              value={config.unifi_password || ''}
              onChange={(e) => updateField('unifi_password', e.target.value)}
            />
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="unifi_verify_ssl"
              checked={config.unifi_verify_ssl || false}
              onChange={(e) => updateField('unifi_verify_ssl', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="unifi_verify_ssl">
              Verify SSL Certificate
            </label>
          </div>
        </div>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
          disabled={!config.unifi_host || !config.unifi_username || !config.unifi_password}
        />
      </div>
    </AccordionSection>
  );
}
