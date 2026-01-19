import React from 'react';
import { useDashboard } from '../hooks/useDashboard';
import { UnifiCard } from './UnifiCard';
import { ProxmoxCard } from './ProxmoxCard';
import { PlexCard } from './PlexCard';
import { DockerCard } from './DockerCard';
import { CalendarCard } from './CalendarCard';

export function Dashboard() {
  const { data, loading, error, lastFetch } = useDashboard();

  const formatTime = (date) => {
    if (!date) return '';
    return date.toLocaleTimeString();
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1 className="dashboard-title">HomeLab Dashboard</h1>
        <div className="dashboard-meta">
          <div className={`refresh-indicator ${loading ? 'loading' : ''}`}>
            {loading ? '⟳ Refreshing...' : `Last refresh: ${formatTime(lastFetch)}`}
          </div>
        </div>
      </header>

      {error && !data && (
        <div className="error-message" style={{ marginBottom: '20px' }}>
          Failed to connect to API: {error}
        </div>
      )}

      <div className="dashboard-grid">
        <UnifiCard data={data?.unifi} />
        <ProxmoxCard data={data?.proxmox} />
        <DockerCard data={data?.docker} />
        <PlexCard data={data?.plex} />
        <CalendarCard data={data?.calendar} />
      </div>
    </div>
  );
}
