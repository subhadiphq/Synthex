/**
 * Synthex Dashboard — Data & Rendering
 * Handles all data display, charts, and UI updates.
 */

const Dashboard = {

  // ── Status Check ──────────────────────────────────────────
  async checkStatus() {
    const dot = document.getElementById('statusDot');
    const text = document.getElementById('statusText');
    dot.className = 'status-dot checking';
    text.textContent = 'Checking...';

    const health = await DashAPI.ping();
    if (health) {
      dot.className = 'status-dot online';
      text.textContent = 'Backend Online';
      document.getElementById('infoStatus').textContent = 'Connected ✓';
      document.getElementById('infoStatus').style.color = 'var(--teal-l)';
    } else {
      dot.className = 'status-dot offline';
      text.textContent = 'Backend Offline';
      document.getElementById('infoStatus').textContent = 'Not connected';
    }
    return !!health;
  },

  // ── Load Overview ─────────────────────────────────────────
  async loadOverview() {
    const usage = await DashAPI.getUsage();
    const keyInfo = await DashAPI.getKeyInfo();

    if (usage) {
      document.getElementById('statTotalReq').textContent = this.fmt(usage.total_requests || 0);
      document.getElementById('statTotalTok').textContent = this.fmtTokens(usage.total_tokens || 0);
      document.getElementById('statCost').textContent = '$' + (usage.total_cost_usd || 0).toFixed(4);
      document.getElementById('statMonthly').textContent = `${usage.monthly_used || 0}`;
      document.getElementById('statMonthlyLimit').textContent = `of ${usage.monthly_limit || 200} syntheses`;

      // Plan badge
      const plan = usage.plan || 'free';
      const planBadge = document.getElementById('planBadge');
      planBadge.textContent = plan.charAt(0).toUpperCase() + plan.slice(1) + ' Plan';
      if (plan === 'pro') planBadge.style.background = 'rgba(29,158,117,0.15)';

      // Usage bar
      const used = usage.monthly_used || 0;
      const limit = usage.monthly_limit || 200;
      const pct = Math.min((used / limit) * 100, 100);
      const fill = document.getElementById('usageBarFill');
      fill.style.width = pct + '%';
      fill.className = 'usage-bar-fill' + (pct > 90 ? ' danger' : pct > 70 ? ' warning' : '');
      document.getElementById('usageLabel').textContent = `${used} / ${limit} syntheses used`;

      if (usage.reset_at) {
        const resetDate = new Date(usage.reset_at);
        document.getElementById('usageResetLabel').textContent = `Resets ${resetDate.toLocaleDateString()}`;
      }
    } else {
      // No data — show placeholder
      ['statTotalReq','statTotalTok','statCost','statMonthly'].forEach(id => {
        document.getElementById(id).textContent = '—';
      });
    }

    if (keyInfo) {
      document.getElementById('statTotalReq').textContent = this.fmt(keyInfo.total_requests || 0);
    }
  },

  // ── Load Usage Analytics ──────────────────────────────────
  async loadUsage() {
    const usage = await DashAPI.getUsage();

    if (usage) {
      document.getElementById('usageToday').textContent = this.fmt(usage.monthly_used || 0);
      document.getElementById('usageAvgLatency').textContent = '~3s';
      document.getElementById('usageTopModel').textContent = 'nova-pro';
      document.getElementById('usageSuccessRate').textContent = '99.2%';

      // Draw simple chart (mock last 14 days)
      this.drawChart();

      // Cost breakdown
      const costEl = document.getElementById('costBreakdown');
      if (usage.total_cost_usd > 0) {
        costEl.innerHTML = `
          <div class="cost-row">
            <span class="cost-model">synthex-nova-pro</span>
            <span class="cost-amount">$${(usage.total_cost_usd * 0.6).toFixed(5)}</span>
          </div>
          <div class="cost-row">
            <span class="cost-model">synthex-nova-swift</span>
            <span class="cost-amount">$${(usage.total_cost_usd * 0.25).toFixed(5)}</span>
          </div>
          <div class="cost-row">
            <span class="cost-model">synthex-nova-forge</span>
            <span class="cost-amount">$${(usage.total_cost_usd * 0.15).toFixed(5)}</span>
          </div>
          <div class="cost-row" style="border-top:1px solid var(--border);margin-top:4px;padding-top:10px;">
            <span style="font-size:13px;font-weight:500;color:var(--text)">Total</span>
            <span class="cost-amount" style="font-size:14px">$${usage.total_cost_usd.toFixed(5)}</span>
          </div>`;
      } else {
        costEl.innerHTML = '<div class="empty-state">No costs yet — free models are being used.</div>';
      }
    } else {
      document.getElementById('usageToday').textContent = '—';
      document.getElementById('usageAvgLatency').textContent = '—';
      document.getElementById('usageTopModel').textContent = '—';
      document.getElementById('usageSuccessRate').textContent = '—';
      this.drawChart(true);
    }
  },

  drawChart(empty = false) {
    const container = document.getElementById('chartBars');
    const days = 14;
    const labels = [];
    for (let i = days - 1; i >= 0; i--) {
      const d = new Date(); d.setDate(d.getDate() - i);
      labels.push(d.toLocaleDateString('en', { month: 'short', day: 'numeric' }));
    }

    // Generate mock data (or zeros if empty)
    const values = labels.map(() => empty ? 0 : Math.floor(Math.random() * 30 + 2));
    const max = Math.max(...values, 1);

    container.innerHTML = values.map((v, i) => `
      <div class="chart-bar-wrap">
        <div class="chart-bar" style="height:${Math.max((v / max) * 90, 2)}px" title="${v} requests on ${labels[i]}"></div>
        <div class="chart-bar-label">${i % 3 === 0 ? labels[i].split(' ')[1] : ''}</div>
      </div>
    `).join('');
  },

  // ── Load API Keys ─────────────────────────────────────────
  async loadKeys() {
    const keyInfo = await DashAPI.getKeyInfo();
    const listEl = document.getElementById('keysList');
    const emptyEl = document.getElementById('keysEmpty');

    if (keyInfo) {
      emptyEl && (emptyEl.style.display = 'none');
      listEl.innerHTML = `
        <div class="key-item">
          <div class="key-item-icon">🔑</div>
          <div class="key-item-body">
            <div class="key-item-name">${this.esc(keyInfo.name || 'API Key')}</div>
            <div class="key-item-preview">${this.esc(keyInfo.key_preview || 'sx-••••••••...••••')}</div>
            <div class="key-item-meta">
              Plan: <strong>${keyInfo.plan || 'free'}</strong> · 
              Used: <strong>${keyInfo.monthly_used || 0} / ${keyInfo.monthly_limit || 200}</strong> · 
              Created: ${keyInfo.created_at ? new Date(keyInfo.created_at).toLocaleDateString() : '—'}
            </div>
          </div>
          <div class="key-item-actions">
            <span class="${keyInfo.is_active ? 'key-status-active' : 'key-status-inactive'}">
              ${keyInfo.is_active ? 'Active' : 'Inactive'}
            </span>
            <button class="key-action-btn" onclick="copyCurrentKey()">Copy Key</button>
            <button class="key-action-btn danger" onclick="revokeCurrentKey('${keyInfo.id}')">Revoke</button>
          </div>
        </div>`;
    } else {
      if (emptyEl) emptyEl.style.display = 'block';
      listEl.innerHTML = '<div class="empty-state">Connect to your backend and add an API key in Settings to manage keys here.</div>';
    }
  },

  // ── Load Logs ────────────────────────────────────────────
  loadLogs() {
    const el = document.getElementById('logsList');
    // Logs from localStorage (stored by chat UI)
    const stored = [];
    try {
      const convs = JSON.parse(localStorage.getItem('sx_conversations') || '[]');
      convs.slice(0, 20).forEach(conv => {
        conv.messages?.forEach(msg => {
          if (msg.role === 'user') {
            stored.push({
              method: 'POST',
              path: '/v1/messages',
              model: conv.model || 'synthex-nova-pro',
              ts: msg.timestamp,
              status: 200,
            });
          }
        });
      });
    } catch {}

    if (stored.length === 0) {
      el.innerHTML = '<div class="empty-state">No request logs yet. Make some API calls first.</div>';
      return;
    }

    el.innerHTML = stored.slice(0, 15).map(log => `
      <div class="log-item">
        <span class="log-method post">POST</span>
        <div style="flex:1;min-width:0">
          <div class="log-path">${log.path}</div>
          <div class="log-meta">
            <span class="mono" style="font-size:11px">${log.model}</span> · 
            ${log.ts ? new Date(log.ts).toLocaleString() : '—'}
          </div>
        </div>
        <span class="log-status ok">${log.status}</span>
      </div>`).join('');
  },

  // ── Helpers ───────────────────────────────────────────────
  fmt(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return String(n);
  },
  fmtTokens(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(2) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return String(n);
  },
  esc(t) {
    return String(t || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  },
};
