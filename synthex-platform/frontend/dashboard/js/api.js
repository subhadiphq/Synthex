/**
 * Synthex Dashboard — API Layer
 * All backend communication for dashboard data.
 */
const DashAPI = {
  async ping() {
    try {
      const r = await fetch(`${DashConfig.backendUrl}/health`, { signal: AbortSignal.timeout(5000) });
      if (!r.ok) return null;
      return await r.json();
    } catch { return null; }
  },

  async getUsage() {
    try {
      const r = await fetch(`${DashConfig.backendUrl}/v1/usage`, { headers: DashConfig.headers });
      if (!r.ok) return null;
      return await r.json();
    } catch { return null; }
  },

  async getKeyInfo() {
    try {
      const r = await fetch(`${DashConfig.backendUrl}/v1/keys/me`, { headers: DashConfig.headers });
      if (!r.ok) return null;
      return await r.json();
    } catch { return null; }
  },

  async createKey(name, email) {
    const r = await fetch(`${DashConfig.backendUrl}/v1/keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, plan: 'free' }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err?.detail || `Error ${r.status}`);
    }
    return r.json();
  },

  async revokeKey(keyId) {
    const r = await fetch(`${DashConfig.backendUrl}/v1/keys/${keyId}`, {
      method: 'DELETE',
      headers: DashConfig.headers,
    });
    return r.ok;
  },

  async getModels() {
    try {
      const r = await fetch(`${DashConfig.backendUrl}/v1/models`);
      if (!r.ok) return null;
      return await r.json();
    } catch { return null; }
  },
};
