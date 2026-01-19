import React from 'react';
import { StatusCard } from './StatusCard';

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

function EventItem({ event }) {
  const startDate = new Date(event.start);
  const day = startDate.getDate();
  const month = startDate.toLocaleDateString(undefined, { month: 'short' });
  const weekday = startDate.toLocaleDateString(undefined, { weekday: 'short' });

  return (
    <div className="event-item">
      <div className="event-date">
        <div className="event-day">{day}</div>
        <div className="event-month">{month}</div>
      </div>
      <div className="event-details">
        <div className="event-title">{event.summary}</div>
        <div className="event-time">
          {weekday} {formatEventTime(event)}
        </div>
        {event.location && (
          <div className="event-location">📍 {event.location}</div>
        )}
      </div>
    </div>
  );
}

function groupEventsByDay(events) {
  const groups = {};

  events.forEach(event => {
    const date = new Date(event.start).toDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(event);
  });

  return groups;
}

export function CalendarCard({ data }) {
  if (!data) return null;

  const eventsByDay = groupEventsByDay(data.events || []);
  const sortedDays = Object.keys(eventsByDay).sort(
    (a, b) => new Date(a) - new Date(b)
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
        ) : data.events && data.events.length > 0 ? (
          <div className="event-list">
            {sortedDays.map(day => (
              <React.Fragment key={day}>
                {eventsByDay[day].map((event, index) => (
                  <EventItem key={`${day}-${index}`} event={event} />
                ))}
              </React.Fragment>
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
