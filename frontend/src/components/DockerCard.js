import React from 'react';
import { StatusCard } from './StatusCard';

export function DockerCard({ data }) {
  if (!data) return null;

  return (
    <StatusCard
      title="Docker"
      icon="🐳"
      status={data.status}
      error={data.error_message}
    >
      <div className="metrics-grid">
        <div className="metric">
          <div className="metric-label">Running</div>
          <div className="metric-value">{data.running_count}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Stopped</div>
          <div className="metric-value">{data.stopped_count}</div>
        </div>
      </div>

      {data.containers && data.containers.length > 0 && (
        <>
          <div style={{ marginTop: '16px', marginBottom: '8px', fontSize: '13px', color: 'var(--text-muted)' }}>
            Containers ({data.total_count})
          </div>
          <div className="item-list">
            {data.containers.map((container, index) => (
              <div key={index} className="list-item">
                <div>
                  <span className="list-item-name">{container.name}</span>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {container.image}
                  </div>
                </div>
                <span className={`list-item-status ${container.state}`}>
                  {container.state}
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </StatusCard>
  );
}
