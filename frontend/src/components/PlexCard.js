import React from 'react';
import { StatusCard } from './StatusCard';
import { formatRelativeTime } from '../hooks/useDashboard';

function PlexItem({ item }) {
  const getDisplayTitle = () => {
    if ((item.type === 'episode' || item.type === 'season') && item.grandparent_title) {
      return item.grandparent_title;
    }
    return item.title;
  };

  const getSubtitle = () => {
    if (item.type === 'episode' || item.type === 'season') {
      return item.title;
    }
    if (item.year) {
      return `${item.type} (${item.year})`;
    }
    return item.type;
  };

  const getTypeIcon = () => {
    switch (item.type) {
      case 'movie':
        return '🎬';
      case 'episode':
        return '📺';
      case 'track':
        return '🎵';
      default:
        return '📁';
    }
  };

  return (
    <div className="plex-item">
      <div className="plex-thumb">
        {item.thumb ? (
          <img src={item.thumb} alt={item.title} className="plex-poster" />
        ) : (
          getTypeIcon()
        )}
      </div>
      <div className="plex-info">
        <div className="plex-title">{getDisplayTitle()}</div>
        <div className="plex-subtitle">{getSubtitle()}</div>
        <div className="plex-added">Added {formatRelativeTime(item.added_at)}</div>
      </div>
    </div>
  );
}

export function PlexCard({ data }) {
  if (!data) return null;

  return (
    <StatusCard
      title="Plex"
      icon="🎬"
      status={data.status}
      lastUpdated={data.last_updated}
      error={data.error_message}
    >
      <div className="metrics-grid" style={{ marginBottom: '16px' }}>
        <div className="metric">
          <div className="metric-label">Libraries</div>
          <div className="metric-value">{data.library_count}</div>
        </div>
        <div className="metric">
          <div className="metric-label">Recent Items</div>
          <div className="metric-value">{data.recent_items?.length || 0}</div>
        </div>
      </div>

      {data.recent_items && data.recent_items.length > 0 && (
        <div className="item-list">
          {data.recent_items.slice(0, 5).map((item, index) => (
            <PlexItem key={index} item={item} />
          ))}
        </div>
      )}
    </StatusCard>
  );
}
