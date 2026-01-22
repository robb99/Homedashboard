import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function ProxmoxSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('proxmox', {
      proxmox_host: config.proxmox_host,
      proxmox_user: config.proxmox_user,
      proxmox_token_name: config.proxmox_token_name,
      proxmox_token_value: config.proxmox_token_value,
      proxmox_node: config.proxmox_node,
      proxmox_verify_ssl: config.proxmox_verify_ssl,
    });
  };

  return (
    <AccordionSection
      title="Proxmox VE"
      icon="&#128187;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Host URL</label>
            <input
              type="text"
              className="form-input"
              placeholder="https://192.168.1.100:8006"
              value={config.proxmox_host || ''}
              onChange={(e) => updateField('proxmox_host', e.target.value)}
            />
            <span className="form-hint">Include https:// and port 8006</span>
          </div>
          <div className="form-group">
            <label className="form-label">Node Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="pve"
              value={config.proxmox_node || ''}
              onChange={(e) => updateField('proxmox_node', e.target.value)}
            />
          </div>
        </div>
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">API User</label>
            <input
              type="text"
              className="form-input"
              placeholder="root@pam"
              value={config.proxmox_user || ''}
              onChange={(e) => updateField('proxmox_user', e.target.value)}
            />
            <span className="form-hint">Format: user@realm (e.g., root@pam)</span>
          </div>
          <div className="form-group">
            <label className="form-label">Token Name</label>
            <input
              type="text"
              className="form-input"
              placeholder="dashboard"
              value={config.proxmox_token_name || ''}
              onChange={(e) => updateField('proxmox_token_name', e.target.value)}
            />
          </div>
        </div>
        <div className="form-row single">
          <div className="form-group">
            <label className="form-label">Token Value</label>
            <input
              type="password"
              className="form-input"
              placeholder="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
              value={config.proxmox_token_value || ''}
              onChange={(e) => updateField('proxmox_token_value', e.target.value)}
            />
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="proxmox_verify_ssl"
              checked={config.proxmox_verify_ssl || false}
              onChange={(e) => updateField('proxmox_verify_ssl', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="proxmox_verify_ssl">
              Verify SSL Certificate
            </label>
          </div>
        </div>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
          disabled={!config.proxmox_host || !config.proxmox_user || !config.proxmox_token_name || !config.proxmox_token_value}
        />
      </div>
    </AccordionSection>
  );
}
