import React from 'react';
import { StatusCard } from './StatusCard';
import { formatUptime, getProgressClass } from '../hooks/useDashboard';

function ResourceBar({ label, value, unit = '%' }) {
  const progressClass = getProgressClass(value);

  return (
    <div className="resource-bar">
      <div className="resource-label">
        <span className="resource-name">{label}</span>
        <span className="resource-value">{value.toFixed(1)}{unit}</span>
      </div>
      <div className="progress-bar">
        <div
          className={`progress-fill ${progressClass}`}
          style={{ width: `${Math.min(value, 100)}%` }}
        />
      </div>
    </div>
  );
}

export function ProxmoxCard({ data }) {
  if (!data) return null;

  const allItems = [...(data.containers || []), ...(data.vms || [])];

  return (
    <StatusCard
      title="Proxmox"
      icon="🖥️"
      status={data.status}
      lastUpdated={data.last_updated}
      error={data.error_message}
    >
      {data.node && (
        <div className="node-info">
          <div className="node-name">
            {data.node.name} - {formatUptime(data.node.uptime)}
          </div>
          <div className="resource-bars">
            <ResourceBar label="CPU" value={data.node.cpu_usage} />
            <ResourceBar label="Memory" value={data.node.memory_usage} />
          </div>
        </div>
      )}

      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Running</div>
          <div className="metric-value">{data.total_running}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Stopped</div>
          <div className="metric-value">{data.total_stopped}</div>
        </div>
      </div>

      {allItems.length > 0 && (
        <>
          <div style={{ marginTop: '16px', marginBottom: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
            Containers & VMs
          </div>
          <div className="item-list">
            {allItems.map((item, index) => (
              <div key={index} className="list-item">
                <div>
                  <span className="list-item-name">{item.name}</span>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {item.type.toUpperCase()} {item.vmid}
                    {item.status === 'running' && item.cpu_usage !== undefined && (
                      <> | CPU: {item.cpu_usage.toFixed(1)}% | Mem: {item.memory_usage.toFixed(1)}%</>
                    )}
                  </div>
                </div>
                <span className={`list-item-status ${item.status}`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </StatusCard>
  );
}
