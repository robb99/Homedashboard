import React from 'react';
import { StatusCard } from './StatusCard';
import { formatRelativeTime } from '../hooks/useDashboard';

function PlexItem({ item }) {
  const getDisplayTitle = () => {
    if (item.type === 'episode' || item.type === 'season') {
      return item.grandparent_title || item.parent_title || item.title;
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

function PlexSessionItem({ session }) {
  const getDisplayTitle = () => {
    if (session.show_title) {
      return `${session.show_title}: ${session.title}`;
    }
    return session.title;
  };

  const getStateIcon = () => {
    return session.state === 'paused' ? '⏸️' : '▶️';
  };

  return (
    <div className="plex-session">
      <span className="session-state">{getStateIcon()}</span>
      <span className="session-user">{session.user}</span>
      <span className="session-title">{getDisplayTitle()}</span>
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
      error={data.error_message}
    >
      <div className="metrics-grid spaced">
        <div className="metric">
          <div className="metric-label">Movies</div>
          <div className="metric-value">{data.movie_count || 0}</div>
        </div>
        <div className="metric">
          <div className="metric-label">TV Shows</div>
          <div className="metric-value">{data.show_count || 0}</div>
        </div>
      </div>

      {data.active_sessions && data.active_sessions.length > 0 && (
        <div className="plex-now-playing">
          <div className="section-label">Now Playing ({data.active_sessions.length})</div>
          {data.active_sessions.map((session, index) => (
            <PlexSessionItem key={index} session={session} />
          ))}
        </div>
      )}

      {data.recent_items && data.recent_items.length > 0 && (
        <div className="item-list">
          {data.recent_items.slice(0, 10).map((item, index) => (
            <PlexItem key={index} item={item} />
          ))}
        </div>
      )}
    </StatusCard>
  );
}
