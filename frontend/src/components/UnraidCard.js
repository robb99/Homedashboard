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

  // Normalize status to lowercase for comparison
  const statusLower = (array.status || '').toLowerCase();
  const parityLower = (array.parity_status || '').toLowerCase();

  // Determine parity display class - valid/syncing are ok, invalid is error
  const parityClass = parityLower === 'valid' ? 'valid' :
                      parityLower === 'syncing' ? 'syncing' :
                      parityLower === 'checking' ? 'syncing' :
                      parityLower === 'invalid' ? 'invalid' : 'valid';

  // Check for disk health issues
  const diskWithErrors = array.disks?.filter(d =>
    d.num_errors > 0 || d.smart_status === 'failed'
  ).length || 0;

  return (
    <div className="unraid-section">
      <div className="section-label">Array Status</div>
      <div className="array-info">
        <div className="array-status-row">
          <span className={`array-state ${statusLower === 'started' ? 'running' : 'stopped'}`}>
            {statusLower === 'started' ? 'Started' : array.status}
          </span>
          {array.parity_status && (
            <span className={`parity-status ${parityClass}`}>
              Parity: {array.parity_status}
              {array.parity_progress !== null && (parityLower === 'syncing' || parityLower === 'checking') &&
                ` (${array.parity_progress.toFixed(1)}%)`
              }
              {array.parity_errors > 0 && (
                <span className="parity-errors"> ({array.parity_errors} errors)</span>
              )}
            </span>
          )}
        </div>
        <div className="array-stats">
          <div className="array-stat">
            <span className="stat-label">Disks</span>
            <span className="stat-value">
              {array.disks?.length || 0}
              {diskWithErrors > 0 && (
                <span className="disk-warning" title={`${diskWithErrors} disk(s) with errors`}> ⚠</span>
              )}
            </span>
          </div>
          <div className="array-stat">
            <span className="stat-label">Free</span>
            <span className="stat-value">{formatBytes(array.free_size)}</span>
          </div>
          <div className="array-stat">
            <span className="stat-label">Used</span>
            <span className="stat-value">{formatBytes(array.used_size)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function getTempClass(temp, type = 'disk') {
  // Temperature thresholds: disk (50/60), CPU (80/95)
  const warnThreshold = type === 'cpu' ? 80 : 50;
  const critThreshold = type === 'cpu' ? 95 : 60;

  if (temp >= critThreshold) return 'temp-critical';
  if (temp >= warnThreshold) return 'temp-warning';
  return 'temp-normal';
}

function SystemSection({ system }) {
  if (!system) return null;

  const hasUptime = system.uptime > 0;
  const hasCpuTemp = system.cpu_temp !== null && system.cpu_temp !== undefined;

  return (
    <div className="unraid-section">
      <div className="section-label">System Info</div>
      <div className="system-info">
        {/* Server header with uptime (Proxmox style) */}
        <div className="node-name">
          UNRAID{hasUptime && ` - ${formatUptime(system.uptime)}`}
        </div>

        {/* CPU/RAM bars (always show, even if 0%) */}
        <div className="resource-bars">
          <ResourceBar label="CPU" value={system.cpu_usage || 0} />
          <ResourceBar label="Memory" value={system.memory_percent || 0} />
        </div>

        {/* Additional stats row */}
        {(hasCpuTemp || system.version) && (
          <div className="system-stats">
            {hasCpuTemp && (
              <div className="system-stat">
                <span className="stat-label">CPU Temp</span>
                <span className={`stat-value ${getTempClass(system.cpu_temp, 'cpu')}`}>
                  {system.cpu_temp}°C
                </span>
              </div>
            )}
            {system.version && (
              <div className="system-stat">
                <span className="stat-label">Version</span>
                <span className="stat-value">{system.version}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ContainersSection({ containers, containerRunning, containerCount }) {
  if (!containers || containers.length === 0) return null;

  // Sort containers: running first, then stopped
  const sortedContainers = [...containers].sort((a, b) => {
    const aRunning = (a.status || '').toLowerCase() === 'running';
    const bRunning = (b.status || '').toLowerCase() === 'running';
    if (aRunning && !bRunning) return -1;
    if (!aRunning && bRunning) return 1;
    return a.name.localeCompare(b.name);
  });

  return (
    <div className="unraid-section">
      <div className="section-label">
        Containers ({containerRunning} of {containerCount} running)
      </div>
      <div className="item-list compact">
        {sortedContainers.slice(0, 8).map((container, index) => {
          const statusLower = (container.status || '').toLowerCase();
          const statusClass = statusLower === 'running' ? 'running' : 'stopped';
          return (
            <div key={index} className="list-item">
              <span className="list-item-name">{container.name}</span>
              <span className={`list-item-status ${statusClass}`}>
                {statusLower === 'running' ? '●' : '○'}
              </span>
            </div>
          );
        })}
        {sortedContainers.length > 8 && (
          <div className="list-item more">
            +{sortedContainers.length - 8} more
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
        {vms.map((vm, index) => {
          const statusLower = (vm.status || '').toLowerCase();
          const statusClass = statusLower === 'running' ? 'running' : 'stopped';
          return (
            <div key={index} className="list-item">
              <div>
                <span className="list-item-name">{vm.name}</span>
                {statusLower === 'running' && vm.vcpus > 0 && (
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                    {vm.vcpus} vCPU | {formatBytes(vm.memory)}
                  </div>
                )}
              </div>
              <span className={`list-item-status ${statusClass}`}>
                {statusLower === 'running' ? '●' : '○'}
              </span>
            </div>
          );
        })}
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
