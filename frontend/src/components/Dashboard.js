import React from 'react';
import { useDashboard } from '../hooks/useDashboard';
import { UnifiCard } from './UnifiCard';
import { ProxmoxCard } from './ProxmoxCard';
import { PlexCard } from './PlexCard';
import { DockerCard } from './DockerCard';
import { CalendarCard } from './CalendarCard';
import { DailyByteCard } from './DailyByteCard';
import { WeatherWidget } from './WeatherWidget';
import { NewsWidget } from './NewsWidget';
import { DateTimeWidget } from './DateTimeWidget';
import { RefreshIndicator } from './RefreshIndicator';

export function Dashboard() {
  const { data, loading, error, lastFetch } = useDashboard();

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
        </div>
      </header>

      {error && !data && (
        <div className="error-message" style={{ marginBottom: '20px' }}>
          Failed to connect to API: {error}
        </div>
      )}

      <div className="dashboard-grid">
        {data?.unifi?.status !== 'unknown' && (
          <UnifiCard data={data?.unifi} />
        )}
        {data?.proxmox?.status !== 'unknown' && (
          <ProxmoxCard data={data?.proxmox} />
        )}
        {data?.docker?.status !== 'unknown' && (
          <DockerCard data={data?.docker} />
        )}
        {data?.plex?.status !== 'unknown' && (
          <PlexCard data={data?.plex} />
        )}
        <DailyByteCard />
        {data?.calendar?.status !== 'unknown' && (
          <CalendarCard data={data?.calendar} />
        )}
      </div>

      <RefreshIndicator loading={loading} lastFetch={lastFetch} />
    </div>
  );
}
