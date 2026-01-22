import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function PlexSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('plex', {
      plex_url: config.plex_url,
      plex_token: config.plex_token,
    });
  };

  return (
    <AccordionSection
      title="Plex Media Server"
      icon="&#127916;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Server URL</label>
            <input
              type="text"
              className="form-input"
              placeholder="http://192.168.1.100:32400"
              value={config.plex_url || ''}
              onChange={(e) => updateField('plex_url', e.target.value)}
            />
            <span className="form-hint">Include http:// and port 32400</span>
          </div>
          <div className="form-group">
            <label className="form-label">Plex Token</label>
            <input
              type="password"
              className="form-input"
              placeholder="Your Plex token"
              value={config.plex_token || ''}
              onChange={(e) => updateField('plex_token', e.target.value)}
            />
            <span className="form-hint">
              <a
                href="https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'var(--accent)' }}
              >
                How to find your token
              </a>
            </span>
          </div>
        </div>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
          disabled={!config.plex_url || !config.plex_token}
        />
      </div>
    </AccordionSection>
  );
}
