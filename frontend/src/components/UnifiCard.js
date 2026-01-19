import React from 'react';
import { StatusCard } from './StatusCard';

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
          <div className="metric-label">Devices Online</div>
          <div className="metric-value">{data.devices_online}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Devices Offline</div>
          <div className="metric-value">{data.devices_offline}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Total Clients</div>
          <div className="metric-value">{data.client_count}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Total Devices</div>
          <div className="metric-value">{data.device_count}</div>
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
