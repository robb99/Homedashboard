import { useState, useEffect, useCallback } from 'react';
import { logEvent } from '../utils/logger';

const API_BASE = '/api/config';

export function useSetup() {
  const [config, setConfig] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saveResult, setSaveResult] = useState(null);
  const [testResults, setTestResults] = useState({});
  const [testingService, setTestingService] = useState(null);

  // Fetch current config on mount
  useEffect(() => {
    fetchConfig();
  }, []);

  const fetchConfig = async () => {
    setLoading(true);
    try {
      const [configRes, statusRes] = await Promise.all([
        fetch(API_BASE),
        fetch(`${API_BASE}/status`),
      ]);

      if (configRes.ok && statusRes.ok) {
        const configData = await configRes.json();
        const statusData = await statusRes.json();
        setConfig(configData);
        setStatus(statusData);
      }
    } catch (error) {
      console.error('Failed to fetch config:', error);
      logEvent({
        level: 'error',
        source: 'useSetup/config',
        message: 'Failed to fetch config/status',
        details: error?.message || error,
      });
    } finally {
      setLoading(false);
    }
  };

  // Update config state for a specific field
  const updateField = useCallback((field, value) => {
    setConfig(prev => ({
      ...prev,
      [field]: value,
    }));
    // Clear any previous save result when user makes changes
    setSaveResult(null);
  }, []);

  // Test connection for a service
  const testConnection = useCallback(async (service, credentials) => {
    setTestingService(service);
    setTestResults(prev => ({ ...prev, [service]: null }));

    try {
      const response = await fetch(`${API_BASE}/test/${service}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(credentials),
      });

      const result = await response.json();
      setTestResults(prev => ({ ...prev, [service]: result }));
      return result;
    } catch (error) {
      const errorResult = {
        success: false,
        message: 'Connection test failed',
        details: error.message,
      };
      setTestResults(prev => ({ ...prev, [service]: errorResult }));
      logEvent({
        level: 'error',
        source: `useSetup/test/${service}`,
        message: 'Connection test failed',
        details: error?.message || error,
      });
      return errorResult;
    } finally {
      setTestingService(null);
    }
  }, []);

  // Save configuration
  const saveConfig = useCallback(async () => {
    setSaving(true);
    setSaveResult(null);

    try {
      const response = await fetch(API_BASE, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config),
      });

      const result = await response.json();

      if (response.ok) {
        setSaveResult({ success: true, message: result.message });
        // Refresh config to get updated status
        await fetchConfig();
        return { success: true };
      } else {
        setSaveResult({ success: false, message: result.detail || 'Save failed' });
        return { success: false };
      }
    } catch (error) {
      setSaveResult({ success: false, message: error.message });
      logEvent({
        level: 'error',
        source: 'useSetup/save',
        message: 'Failed to save configuration',
        details: error?.message || error,
      });
      return { success: false };
    } finally {
      setSaving(false);
    }
  }, [config]);

  // Check if a specific service is configured
  const isServiceConfigured = useCallback((service) => {
    if (!status) return false;
    const serviceStatus = status[service];
    return serviceStatus?.configured && serviceStatus?.has_credentials;
  }, [status]);

  return {
    config,
    status,
    loading,
    saving,
    saveResult,
    testResults,
    testingService,
    updateField,
    testConnection,
    saveConfig,
    isServiceConfigured,
    isFirstRun: status?.is_first_run ?? true,
  };
}

export function useConfigStatus() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then(res => res.json())
      .then(data => {
        setStatus(data);
        setLoading(false);
      })
      .catch(() => {
        setLoading(false);
        logEvent({
          level: 'error',
          source: 'useConfigStatus',
          message: 'Failed to fetch config status',
        });
      });
  }, []);

  return { status, loading, isFirstRun: status?.is_first_run ?? null };
}
