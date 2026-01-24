import React from 'react';
import { StatusCard } from './StatusCard';
import { formatUptime, formatBytes, getProgressClass } from '../hooks/useDashboard';

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

function ArraySection({ array }) {
  if (!array) return null;

  const usedPercent = array.total_size > 0
    ? (array.used_size / array.total_size) * 100
    : 0;

  return (
    <div className="unraid-section">
      <div className="section-label">Array Status</div>
      <div className="array-info">
        <div className="array-status-row">
          <span className={`array-state ${array.status === 'started' ? 'running' : 'stopped'}`}>
            {array.status === 'started' ? 'Started' : array.status}
          </span>
          {array.parity_status && (
            <span className={`parity-status ${array.parity_status}`}>
              Parity: {array.parity_status}
              {array.parity_progress !== null && array.parity_status === 'syncing' &&
                ` (${array.parity_progress.toFixed(1)}%)`
              }
            </span>
          )}
        </div>
        <div className="array-stats">
          <div className="array-stat">
            <span className="stat-label">Disks</span>
            <span className="stat-value">{array.disks?.length || 0}</span>
          </div>
          <div className="array-stat">
            <span className="stat-label">Free</span>
            <span className="stat-value">{formatBytes(array.free_size)}</span>
          </div>
          <div className="array-stat">
            <span className="stat-label">Used</span>
            <span className="stat-value">{usedPercent.toFixed(0)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function SystemSection({ system }) {
  if (!system) return null;

  return (
    <div className="unraid-section">
      <div className="section-label">System Resources</div>
      <div className="system-info">
        <div className="resource-bars">
          <ResourceBar label="CPU" value={system.cpu_usage} />
          <ResourceBar label="RAM" value={system.memory_percent} />
        </div>
        <div className="system-stats">
          <div className="system-stat">
            <span className="stat-label">Uptime</span>
            <span className="stat-value">{formatUptime(system.uptime)}</span>
          </div>
          {system.version && (
            <div className="system-stat">
              <span className="stat-label">Version</span>
              <span className="stat-value">{system.version}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ContainersSection({ containers, containerRunning, containerCount }) {
  if (!containers || containers.length === 0) return null;

  return (
    <div className="unraid-section">
      <div className="section-label">
        Containers ({containerRunning} of {containerCount} running)
      </div>
      <div className="item-list compact">
        {containers.slice(0, 6).map((container, index) => (
          <div key={index} className="list-item">
            <span className="list-item-name">{container.name}</span>
            <span className={`list-item-status ${container.status}`}>
              {container.status}
            </span>
          </div>
        ))}
        {containers.length > 6 && (
          <div className="list-item more">
            +{containers.length - 6} more
          </div>
        )}
      </div>
    </div>
  );
}

function VMsSection({ vms, vmRunning, vmCount }) {
  if (!vms || vms.length === 0) return null;

  return (
    <div className="unraid-section">
      <div className="section-label">
        VMs ({vmRunning} of {vmCount} running)
      </div>
      <div className="item-list compact">
        {vms.map((vm, index) => (
          <div key={index} className="list-item">
            <div>
              <span className="list-item-name">{vm.name}</span>
              {vm.status === 'running' && (
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                  {vm.vcpus} vCPU | {formatBytes(vm.memory)}
                </div>
              )}
            </div>
            <span className={`list-item-status ${vm.status}`}>
              {vm.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function UnraidCard({ data }) {
  if (!data) return null;

  return (
    <StatusCard
      title="UNRAID"
      icon="&#128229;"
      status={data.status}
      error={data.error_message}
    >
      <div className="unraid-grid">
        <div className="unraid-top-row">
          <ArraySection array={data.array} />
          <SystemSection system={data.system} />
        </div>
        <div className="unraid-bottom-row">
          <ContainersSection
            containers={data.containers}
            containerRunning={data.container_running}
            containerCount={data.container_count}
          />
          <VMsSection
            vms={data.vms}
            vmRunning={data.vm_running}
            vmCount={data.vm_count}
          />
        </div>
      </div>
    </StatusCard>
  );
}
