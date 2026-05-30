// Synthex API Client
const SynthexAPI = {
  get headers() {
    const key = getApiKey();
    return { 'Content-Type': 'application/json', ...(key ? { 'Authorization': `Bearer ${key}` } : {}) };
  },
  get baseUrl() { return SynthexConfig.BACKEND_URL; },

  async ping() {
    try {
      const r = await fetch(`${this.baseUrl}/health`, { signal: AbortSignal.timeout(5000) });
      return r.ok;
    } catch { return false; }
  },

  async *streamMessage(messages, model) {
    const r = await fetch(`${this.baseUrl}/v1/messages`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        model,
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        stream: true,
        max_tokens: 2500,
        language: getLanguage(),
      })
    }).catch(() => { throw new Error('Cannot connect to Synthex backend. Check Settings.'); });

    if (!r.ok) {
      let msg = `Error ${r.status}`;
      try { const d = await r.json(); msg = d?.detail?.error?.message || d?.detail || msg; } catch {}
      throw new Error(msg);
    }

    const reader = r.body.getReader();
    const dec = new TextDecoder();
    let buf = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop() || '';
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const d = line.slice(6);
        if (d === '[DONE]') return;
        try {
          const j = JSON.parse(d);
          const c = j?.choices?.[0]?.delta?.content;
          if (c) yield c;
        } catch {}
      }
    }
  },

  async sendMessage(messages, model) {
    const r = await fetch(`${this.baseUrl}/v1/messages`, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({
        model,
        messages: messages.map(m => ({ role: m.role, content: m.content })),
        stream: false,
        max_tokens: 2500,
        language: getLanguage(),
      })
    }).catch(() => { throw new Error('Cannot connect to Synthex backend. Check Settings.'); });

    if (!r.ok) {
      let msg = `Error ${r.status}`;
      try { const d = await r.json(); msg = d?.detail?.error?.message || d?.detail || msg; } catch {}
      throw new Error(msg);
    }
    const d = await r.json();
    return {
      content: d.choices?.[0]?.message?.content || '',
      model: d.model,
      agents_used: d.agents_used || [],
      agent_traces: d.agent_traces || null,
      usage: d.usage,
    };
  },

  async uploadFile(file, instruction, model) {
    const fd = new FormData();
    fd.append('file', file);
    fd.append('analyze', 'true');
    fd.append('model', model || 'synthex-nova-forge');
    if (instruction) fd.append('instruction', instruction);
    const key = getApiKey();
    const h = key ? { 'Authorization': `Bearer ${key}` } : {};
    const r = await fetch(`${this.baseUrl}/v1/files/upload`, { method: 'POST', headers: h, body: fd });
    if (!r.ok) throw new Error(`File upload failed: ${r.status}`);
    return r.json();
  },

  async createKey(name, email) {
    const r = await fetch(`${this.baseUrl}/v1/keys`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, plan: 'free' })
    });
    if (!r.ok) throw new Error('Could not create API key');
    return r.json();
  },
};
