import React, { useState } from 'react';

export function AccordionSection({
  title,
  icon,
  isConfigured,
  children,
  defaultExpanded = false
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  return (
    <div className={`accordion-section ${expanded ? 'expanded' : ''}`}>
      <button
        className="accordion-header"
        onClick={() => setExpanded(!expanded)}
        type="button"
      >
        <div className="accordion-header-left">
          <span className="accordion-icon">{icon}</span>
          <span className="accordion-title">{title}</span>
        </div>
        <div className="accordion-header-right">
          <span className={`config-status ${isConfigured ? 'configured' : 'not-configured'}`}>
            {isConfigured ? 'Configured' : 'Not configured'}
          </span>
          <span className="accordion-chevron">&#9660;</span>
        </div>
      </button>
      {expanded && (
        <div className="accordion-content">
          {children}
        </div>
      )}
    </div>
  );
}
