import React from 'react';
import { StatusCard } from './StatusCard';
import { formatBytes } from '../hooks/useDashboard';

export function UnifiCard({ data }) {
  if (!data) return null;

  return (
    <StatusCard
      title="Network"
      icon="🌐"
      status={data.status}
      lastUpdated={data.last_updated}
      error={data.error_message}
    >
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Wireless Clients</div>
          <div className="metric-value">{data.wireless_clients}</div>
        </div>
        <div className="metric">
          <div className="metric-label">WAN Latency</div>
          <div className="metric-value">{data.wan_latency?.toFixed(1)} ms</div>
        </div>
        <div className="metric">
          <div className="metric-label">Total Clients</div>
          <div className="metric-value">{data.client_count}</div>
        </div>
        <div className="metric">
          <div className="metric-label">24h Data Usage</div>
          <div className="metric-value">{formatBytes(data.data_usage_24h)}</div>
        </div>
      </div>

      {data.devices && data.devices.length > 0 && (
        <>
          <div style={{ marginTop: '16px', marginBottom: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
            Devices
          </div>
          <div className="item-list">
            {data.devices.map((device, index) => (
              <div key={index} className="list-item">
                <span className="list-item-name">{device.name}</span>
                <span className={`list-item-status ${device.status}`}>
                  {device.status}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </StatusCard>
  );
}
