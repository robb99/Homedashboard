import React from 'react';
import { useDashboard } from '../hooks/useDashboard';
import { UnifiCard } from './UnifiCard';
import { ProxmoxCard } from './ProxmoxCard';
import { PlexCard } from './PlexCard';
import { DockerCard } from './DockerCard';
import { CalendarCard } from './CalendarCard';
import { DailyByteCard } from './DailyByteCard';
import { UnraidCard } from './UnraidCard';
import { WeatherWidget } from './WeatherWidget';
import { NewsWidget } from './NewsWidget';
import { DateTimeWidget } from './DateTimeWidget';
import { RefreshIndicator } from './RefreshIndicator';
import '../styles/setup.css';

export function Dashboard({ onOpenSetup }) {
  const { data, config, loading, error, lastFetch } = useDashboard();

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1 className="dashboard-title">HomeLab Dashboard</h1>
        <div className="dashboard-meta">
          <div className="header-widgets">
            <WeatherWidget />
            <NewsWidget />
            <DateTimeWidget />
          </div>
          {onOpenSetup && (
            <button className="settings-btn" onClick={onOpenSetup} title="Settings">
              &#9881; Settings
            </button>
          )}
        </div>
      </header>

      {error && !data && (
        <div className="error-message" style={{ marginBottom: '20px' }}>
          Failed to connect to API: {error}
        </div>
      )}

      <div className="dashboard-grid">
        {config?.unifi_enabled && data?.unifi?.status !== 'unknown' && (
          <UnifiCard data={data?.unifi} />
        )}
        {config?.proxmox_enabled && data?.proxmox?.status !== 'unknown' && (
          <ProxmoxCard data={data?.proxmox} />
        )}
        {config?.docker_enabled && data?.docker?.status !== 'unknown' && (
          <DockerCard data={data?.docker} />
        )}
        {config?.unraid_enabled && data?.unraid && (
          <UnraidCard data={data?.unraid} />
        )}
        {config?.plex_enabled && data?.plex?.status !== 'unknown' && (
          <PlexCard data={data?.plex} />
        )}
        <DailyByteCard />
        {config?.calendar_enabled && data?.calendar?.status !== 'unknown' && (
          <CalendarCard data={data?.calendar} />
        )}
      </div>

      <RefreshIndicator loading={loading} lastFetch={lastFetch} />
    </div>
  );
}
