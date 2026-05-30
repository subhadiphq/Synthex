/**
 * Synthex Dashboard — Configuration
 */
const DashConfig = {
  get backendUrl() {
    return localStorage.getItem('sx_backend_url') || 'http://localhost:8000';
  },
  get apiKey() {
    return localStorage.getItem('sx_api_key') || '';
  },
  get headers() {
    const key = this.apiKey;
    return {
      'Content-Type': 'application/json',
      ...(key ? { 'Authorization': `Bearer ${key}` } : {}),
    };
  },
  save(url, key) {
    if (url) localStorage.setItem('sx_backend_url', url.replace(/\/$/, ''));
    if (key) localStorage.setItem('sx_api_key', key);
  },
  isConfigured() {
    return !!this.apiKey;
  },
};
