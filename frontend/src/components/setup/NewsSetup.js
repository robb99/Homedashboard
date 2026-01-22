import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function NewsSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('news', {
      news_api_key: config.news_api_key,
    });
  };

  return (
    <AccordionSection
      title="News"
      icon="&#128240;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">NewsAPI Key</label>
            <input
              type="password"
              className="form-input"
              placeholder="Your NewsAPI.org API key"
              value={config.news_api_key || ''}
              onChange={(e) => updateField('news_api_key', e.target.value)}
            />
            <span className="form-hint">
              Get a free API key at{' '}
              <a
                href="https://newsapi.org/register"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: 'var(--accent)' }}
              >
                newsapi.org
              </a>
            </span>
          </div>
          <div className="form-group">
            <label className="form-label">Country Code</label>
            <input
              type="text"
              className="form-input"
              placeholder="us"
              maxLength={2}
              value={config.news_country || ''}
              onChange={(e) => updateField('news_country', e.target.value.toLowerCase())}
            />
            <span className="form-hint">2-letter country code (e.g., us, gb, de)</span>
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="news_enabled"
              checked={config.news_enabled !== false}
              onChange={(e) => updateField('news_enabled', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="news_enabled">
              Enable News Widget
            </label>
          </div>
        </div>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
          disabled={!config.news_api_key}
        />
      </div>
    </AccordionSection>
  );
}
