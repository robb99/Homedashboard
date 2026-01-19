import React from 'react';

function formatEventTime(event) {
  if (event.all_day) {
    return 'All day';
  }

  const start = new Date(event.start);
  const end = new Date(event.end);

  const timeOptions = { hour: 'numeric', minute: '2-digit' };
  const startTime = start.toLocaleTimeString(undefined, timeOptions);
  const endTime = end.toLocaleTimeString(undefined, timeOptions);

  return `${startTime} - ${endTime}`;
}

function EventCard({ event }) {
  const startDate = new Date(event.start);
  const day = startDate.getDate();
  const month = startDate.toLocaleDateString(undefined, { month: 'short' });

  return (
    <div className="event-card">
      <div className="event-card-date">
        <div className="event-card-day">{day}</div>
        <div className="event-card-month">{month}</div>
      </div>
      <div className="event-card-title">{event.summary}</div>
      <div className="event-card-time">{formatEventTime(event)}</div>
      {event.location && (
        <div className="event-card-location">📍 {event.location}</div>
      )}
    </div>
  );
}

export function CalendarCard({ data }) {
  if (!data) return null;

  // Sort events by start date (soonest first)
  const sortedEvents = [...(data.events || [])].sort(
    (a, b) => new Date(a.start) - new Date(b.start)
  );

  return (
    <div className="card calendar-card">
      <div className="card-header">
        <h2 className="card-title">
          <span className="card-icon">📅</span>
          Calendar
        </h2>
        <div className="card-status status-healthy">
          <span className="status-dot"></span>
          {data.event_count} events
        </div>
      </div>
      <div className="card-body">
        {data.error_message ? (
          <div className="error-message">{data.error_message}</div>
        ) : sortedEvents.length > 0 ? (
          <div className="event-cards-row">
            {sortedEvents.map((event, index) => (
              <EventCard key={index} event={event} />
            ))}
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
            No upcoming events
          </div>
        )}
      </div>
      {data.last_updated && (
        <div className="card-footer">
          Next 7 days
        </div>
      )}
    </div>
  );
}
