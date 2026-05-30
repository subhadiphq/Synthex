/**
 * Synthex Dashboard — Main App
 * Navigation, event handlers, page management.
 */

// ── State ──────────────────────────────────────────────────
let currentPage = 'overview';
let newKeyData = null;

// ── Init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Populate settings fields
  document.getElementById('settingBackendUrl').value = DashConfig.backendUrl;
  document.getElementById('settingApiKey').value = DashConfig.apiKey;
  document.getElementById('configUrl').value = DashConfig.backendUrl;
  document.getElementById('configKey').value = DashConfig.apiKey;
  document.getElementById('backendUrl') && (document.getElementById('backendUrl').value = DashConfig.backendUrl);

  // Show config modal if not configured
  if (!DashConfig.isConfigured() && !localStorage.getItem('sx_skip_config')) {
    setTimeout(() => {
      document.getElementById('configModal').style.display = 'flex';
    }, 600);
  }

  // Check backend status
  Dashboard.checkStatus().then(online => {
    if (online) loadPage('overview');
  });

  // Event: nav items
  document.querySelectorAll('.nav-item[data-page]').forEach(el => {
    el.addEventListener('click', (e) => {
      e.preventDefault();
      navigate(el.dataset.page);
    });
  });

  // Event: top bar Configure button
  document.getElementById('settingsBtn').addEventListener('click', () => navigate('settings'));

  // Event: mobile sidebar
  document.getElementById('mobileMenuBtn')?.addEventListener('click', () => {
    document.getElementById('sidebar').classList.toggle('open');
  });

  // Event: Create Key button
  document.getElementById('createKeyBtn').addEventListener('click', () => {
    const form = document.getElementById('createKeyForm');
    form.style.display = form.style.display === 'none' ? 'block' : 'none';
    document.getElementById('newKeyDisplay').style.display = 'none';
  });

  // Close sidebar on outside click (mobile)
  document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const menuBtn = document.getElementById('mobileMenuBtn');
    if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !menuBtn?.contains(e.target)) {
      sidebar.classList.remove('open');
    }
  });

  // Load initial page
  loadPage('overview');
});

// ── Navigation ─────────────────────────────────────────────
function navigate(page) {
  currentPage = page;

  // Update nav items
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });

  // Update breadcrumb
  const labels = {
    overview: 'Overview', usage: 'Usage & Analytics',
    keys: 'API Keys', logs: 'Request Logs',
    billing: 'Billing & Plan', settings: 'Settings',
  };
  document.getElementById('breadcrumbPage').textContent = labels[page] || page;

  // Show/hide pages
  document.querySelectorAll('.page').forEach(el => {
    el.classList.toggle('active', el.id === `page-${page}`);
  });

  // Load data for page
  loadPage(page);

  // Close mobile sidebar
  document.getElementById('sidebar').classList.remove('open');
}

async function loadPage(page) {
  switch (page) {
    case 'overview': await Dashboard.loadOverview(); break;
    case 'usage':    await Dashboard.loadUsage(); break;
    case 'keys':     await Dashboard.loadKeys(); break;
    case 'logs':     Dashboard.loadLogs(); break;
    case 'settings': break; // Settings are pre-populated
  }
}

function loadLogs() { Dashboard.loadLogs(); }

// ── API Key Management ─────────────────────────────────────
async function createKey() {
  const name = document.getElementById('newKeyName').value.trim();
  const email = document.getElementById('newKeyEmail').value.trim();

  if (!name || !email) {
    showToast('Please fill in name and email', 'error'); return;
  }

  const btn = event.target;
  btn.textContent = 'Creating...'; btn.disabled = true;

  try {
    const result = await DashAPI.createKey(name, email);
    newKeyData = result;

    document.getElementById('newKeyValue').textContent = result.key;
    document.getElementById('createKeyForm').style.display = 'none';
    document.getElementById('newKeyDisplay').style.display = 'block';

    // Auto-save key to settings
    DashConfig.save(DashConfig.backendUrl, result.key);
    document.getElementById('settingApiKey').value = result.key;

    showToast('API key created! Save it now — shown only once.', 'success');
    await Dashboard.loadKeys();
  } catch (err) {
    showToast('Failed to create key: ' + err.message, 'error');
  } finally {
    btn.textContent = 'Generate Key'; btn.disabled = false;
  }
}

function copyNewKey() {
  const key = document.getElementById('newKeyValue').textContent;
  navigator.clipboard.writeText(key).then(() => {
    showToast('API key copied to clipboard ✓', 'success');
  });
}

function copyCurrentKey() {
  const key = DashConfig.apiKey;
  if (!key) { showToast('No API key configured', 'error'); return; }
  navigator.clipboard.writeText(key).then(() => showToast('API key copied ✓', 'success'));
}

async function revokeCurrentKey(keyId) {
  if (!confirm('Revoke this API key? This cannot be undone.')) return;
  const ok = await DashAPI.revokeKey(keyId);
  if (ok) {
    localStorage.removeItem('sx_api_key');
    showToast('API key revoked', 'success');
    await Dashboard.loadKeys();
    await Dashboard.checkStatus();
  } else {
    showToast('Failed to revoke key', 'error');
  }
}

// ── Settings ───────────────────────────────────────────────
function saveAllSettings() {
  const url = document.getElementById('settingBackendUrl').value.trim().replace(/\/$/, '');
  const key = document.getElementById('settingApiKey').value.trim();
  DashConfig.save(url, key);
  showToast('Settings saved ✓', 'success');
  Dashboard.checkStatus();
}

async function testConnection() {
  const btn = event.target;
  const result = document.getElementById('connectionResult');
  btn.textContent = 'Testing...'; btn.disabled = true;
  result.textContent = '';

  // Temporarily use the input values for test
  const oldUrl = localStorage.getItem('sx_backend_url');
  const testUrl = document.getElementById('settingBackendUrl').value.trim().replace(/\/$/, '');
  localStorage.setItem('sx_backend_url', testUrl);

  const health = await DashAPI.ping();
  localStorage.setItem('sx_backend_url', oldUrl || '');

  if (health) {
    result.textContent = '✓ Connected — backend is running';
    result.style.color = 'var(--teal-l)';
    showToast('Backend connected ✓', 'success');
  } else {
    result.textContent = '✗ Cannot reach backend — check URL';
    result.style.color = 'var(--coral-l)';
    showToast('Cannot connect to backend', 'error');
  }

  btn.textContent = 'Test Connection'; btn.disabled = false;
}

// ── Config Modal ───────────────────────────────────────────
function saveConfig() {
  const url = document.getElementById('configUrl').value.trim().replace(/\/$/, '');
  const key = document.getElementById('configKey').value.trim();
  DashConfig.save(url, key);

  if (document.getElementById('settingBackendUrl')) {
    document.getElementById('settingBackendUrl').value = url;
    document.getElementById('settingApiKey').value = key;
  }

  closeModal();
  showToast('Connected to Synthex backend ✓', 'success');
  Dashboard.checkStatus().then(() => loadPage(currentPage));
}

function closeModal() {
  document.getElementById('configModal').style.display = 'none';
  localStorage.setItem('sx_skip_config', '1');
}

// ── Toast Notifications ────────────────────────────────────
function showToast(message, type = 'success') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}
