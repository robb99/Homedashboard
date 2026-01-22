import React from 'react';

export function TestConnectionButton({
  onTest,
  testing,
  result,
  disabled = false
}) {
  const getButtonClass = () => {
    if (testing) return 'test-btn testing';
    if (result?.success) return 'test-btn success';
    if (result && !result.success) return 'test-btn error';
    return 'test-btn';
  };

  const getButtonText = () => {
    if (testing) return 'Testing...';
    if (result?.success) return 'Connected';
    if (result && !result.success) return 'Test Failed';
    return 'Test Connection';
  };

  return (
    <div className="test-connection-container">
      <button
        type="button"
        className={getButtonClass()}
        onClick={onTest}
        disabled={disabled || testing}
      >
        {testing && <span className="spinner" />}
        {getButtonText()}
      </button>
      {result && (
        <div className={`test-result ${result.success ? 'success' : 'error'}`}>
          <span>{result.message}</span>
          {result.details && (
            <span className="test-result-details">({result.details})</span>
          )}
        </div>
      )}
    </div>
  );
}
