import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function DockerSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('docker', {
      docker_host: config.docker_host,
    });
  };

  return (
    <AccordionSection
      title="Docker"
      icon="&#128051;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row single">
          <div className="form-group">
            <label className="form-label">Docker Host (Optional)</label>
            <input
              type="text"
              className="form-input"
              placeholder="tcp://192.168.1.100:2375 or unix:///var/run/docker.sock"
              value={config.docker_host || ''}
              onChange={(e) => updateField('docker_host', e.target.value)}
            />
            <span className="form-hint">
              Leave empty to use local Docker socket. For remote Docker, use tcp://host:port
            </span>
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="docker_enabled"
              checked={config.docker_enabled !== false}
              onChange={(e) => updateField('docker_enabled', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="docker_enabled">
              Enable Docker Monitoring
            </label>
          </div>
        </div>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
        />
      </div>
    </AccordionSection>
  );
}
