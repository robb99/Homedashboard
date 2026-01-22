import React from 'react';
import { AccordionSection } from './AccordionSection';
import { TestConnectionButton } from './TestConnectionButton';

export function WeatherSetup({
  config,
  updateField,
  onTest,
  testing,
  testResult,
  isConfigured
}) {
  const handleTest = () => {
    onTest('weather', {
      weather_latitude: parseFloat(config.weather_latitude) || 0,
      weather_longitude: parseFloat(config.weather_longitude) || 0,
    });
  };

  return (
    <AccordionSection
      title="Weather"
      icon="&#127780;"
      isConfigured={isConfigured}
    >
      <div className="setup-form">
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Latitude</label>
            <input
              type="number"
              step="0.0001"
              className="form-input"
              placeholder="37.7749"
              value={config.weather_latitude || ''}
              onChange={(e) => updateField('weather_latitude', parseFloat(e.target.value) || 0)}
            />
          </div>
          <div className="form-group">
            <label className="form-label">Longitude</label>
            <input
              type="number"
              step="0.0001"
              className="form-input"
              placeholder="-122.4194"
              value={config.weather_longitude || ''}
              onChange={(e) => updateField('weather_longitude', parseFloat(e.target.value) || 0)}
            />
          </div>
        </div>
        <div className="form-row single">
          <div className="form-checkbox-group">
            <input
              type="checkbox"
              className="form-checkbox"
              id="weather_enabled"
              checked={config.weather_enabled !== false}
              onChange={(e) => updateField('weather_enabled', e.target.checked)}
            />
            <label className="form-checkbox-label" htmlFor="weather_enabled">
              Enable Weather Widget
            </label>
          </div>
        </div>
        <span className="form-hint" style={{ display: 'block', marginTop: '-8px' }}>
          Uses Open-Meteo API (free, no API key required).{' '}
          <a
            href="https://www.latlong.net/"
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'var(--accent)' }}
          >
            Find your coordinates
          </a>
        </span>
        <TestConnectionButton
          onTest={handleTest}
          testing={testing}
          result={testResult}
          disabled={!config.weather_latitude || !config.weather_longitude}
        />
      </div>
    </AccordionSection>
  );
}
