import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function CalendarSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('calendar', {
      google_credentials_path: config.google_credentials_path,
    });
  };

  return (
    <AccordionSection
      title="Google Calendar"
      icon="&#128197;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row single">
          <div className="form-group">
            <label className="form-label">Credentials File Path</label>
            <input
              type="text"
              className="form-input"
              placeholder="/path/to/credentials.json"
              value={config.google_credentials_path || ''}
              onChange={(e) => updateField('google_credentials_path', e.target.value)}
            />
            <span className="form-hint">
              Path to your Google service account or OAuth credentials JSON file
            </span>
          </div>
        </div>
        <div className="form-row single">
          <div className="form-group">
            <label className="form-label">Calendar IDs</label>
            <input
              type="text"
              className="form-input"
              placeholder="primary, work@group.calendar.google.com"
              value={config.google_calendar_ids || ''}
              onChange={(e) => updateField('google_calendar_ids', e.target.value)}
            />
            <span className="form-hint">
              Comma-separated list of calendar IDs. Use "primary" for your main calendar
            </span>
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="calendar_enabled"
              checked={config.calendar_enabled !== false}
              onChange={(e) => updateField('calendar_enabled', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="calendar_enabled">
              Enable Calendar Widget
            </label>
          </div>
        </div>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
          disabled={!config.google_credentials_path}
        />
      </div>
    </AccordionSection>
  );
}
