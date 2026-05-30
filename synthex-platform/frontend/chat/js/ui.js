// UI Utilities
let currentConvId = null;
let currentModel = 'synthex-nova-pro';
let isBengaliMode = false;
let attachedFile = null;
let isStreaming = false;

// Toast
function showToast(msg, type = '') {
  const t = document.getElementById('toast');
  t.textContent = msg;
  t.className = `toast ${type} show`;
  setTimeout(() => t.classList.remove('show'), 3000);
}

// Model dropdown
function toggleModelDropdown() {
  document.getElementById('modelDropdown').classList.toggle('open');
}

document.addEventListener('click', e => {
  if (!e.target.closest('#modelBtn') && !e.target.closest('#modelDropdown')) {
    document.getElementById('modelDropdown')?.classList.remove('open');
  }
});

document.querySelectorAll('.model-opt').forEach(opt => {
  opt.addEventListener('click', () => {
    currentModel = opt.dataset.model;
    document.getElementById('curModelIcon').textContent = opt.dataset.icon;
    document.getElementById('curModelName').textContent = opt.dataset.name;
    document.getElementById('curModelSub').textContent = opt.dataset.sub;
    document.querySelectorAll('.model-opt').forEach(o => o.classList.remove('active'));
    opt.classList.add('active');
    document.getElementById('modelDropdown').classList.remove('open');
    if (currentConvId) Store.updateConv(currentConvId, { model: currentModel });
  });
});

// Sidebar
function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('mobile-open');
}

// Language toggle
function toggleLang() {
  isBengaliMode = !isBengaliMode;
  const toggle = document.getElementById('langToggle');
  toggle.classList.toggle('on', isBengaliMode);
  localStorage.setItem('sx_language', isBengaliMode ? 'bn' : 'auto');
  showToast(isBengaliMode ? 'বাংলা Mode চালু' : 'English Mode', 'success');
}

// Setup modal
function openSetup() {
  document.getElementById('setupBackendUrl').value = localStorage.getItem('sx_backend_url') || 'http://localhost:8000';
  document.getElementById('setupApiKey').value = getApiKey();
  document.getElementById('setupModal').classList.remove('hidden');
}

function saveSetup() {
  const url = document.getElementById('setupBackendUrl').value.trim();
  const key = document.getElementById('setupApiKey').value.trim();
  if (url) localStorage.setItem('sx_backend_url', url.replace(/\/$/, ''));
  if (key) localStorage.setItem('sx_api_key', key);
  document.getElementById('setupModal').classList.add('hidden');
  checkConnection();
  showToast('Settings saved', 'success');
}

// Conversation list
function renderConvList() {
  const list = document.getElementById('convList');
  const convs = Store.getAll();
  if (!convs.length) {
    list.innerHTML = '<div style="font-size:12px;color:var(--text3);padding:8px 10px;">No conversations yet</div>';
    return;
  }
  list.innerHTML = convs.map(c => `
    <div class="conv-item ${c.id === currentConvId ? 'active' : ''}" onclick="loadConv('${c.id}')">
      <svg class="conv-icon" width="12" height="12" viewBox="0 0 12 12" fill="none">
        <path d="M1 1h10v7H7l-3 3V8H1z" stroke="currentColor" stroke-width="1.2" rx="1"/>
      </svg>
      <span class="conv-title">${escHtml(c.title)}</span>
      <div class="conv-actions">
        <button class="icon-btn" style="width:22px;height:22px" onclick="event.stopPropagation();deleteConv('${c.id}')" title="Delete">
          <svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M1 2.5h9M4 2.5V1.5h3v1M2.5 2.5l.5 7h5.5l.5-7" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/></svg>
        </button>
      </div>
    </div>
  `).join('');
}

function loadConv(id) {
  const conv = Store.getConv(id);
  if (!conv) return;
  currentConvId = id;
  Store.setCurrent(id);
  document.getElementById('chatTitle').textContent = conv.title || 'Conversation';
  document.getElementById('emptyState').style.display = 'none';

  const inner = document.getElementById('messagesInner');
  inner.innerHTML = '';
  conv.messages.forEach(m => appendMessage(m.role, m.content, m.agents));
  scrollBottom();
  renderConvList();
  document.getElementById('sidebar').classList.remove('mobile-open');
}

function deleteConv(id) {
  Store.deleteConv(id);
  if (id === currentConvId) {
    currentConvId = null;
    showEmpty();
  }
  renderConvList();
}

function showEmpty() {
  const inner = document.getElementById('messagesInner');
  inner.innerHTML = '';
  inner.insertAdjacentHTML('beforeend', document.getElementById('emptyState').outerHTML.replace('style="display:none"',''));
  document.getElementById('chatTitle').textContent = 'New Chat';
  currentConvId = null;
}

// Messages
function appendMessage(role, content, agents) {
  const emptyState = document.getElementById('emptyState');
  if (emptyState) emptyState.remove();

  const inner = document.getElementById('messagesInner');
  const div = document.createElement('div');
  div.className = `msg ${role}`;

  const avatar = role === 'user'
    ? '<div class="msg-avatar">U</div>'
    : '<div class="msg-avatar">S</div>';

  const agentTags = (agents && agents.length)
    ? `<div class="msg-agents">${agents.map(a => `<span class="agent-tag">${escHtml(a)}</span>`).join('')}</div>`
    : '';

  const now = new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });

  if (role === 'user') {
    div.innerHTML = `
      <div class="msg-body">
        <div class="msg-bubble">${escHtml(content).replace(/\n/g,'<br>')}</div>
        <div class="msg-meta"><span class="msg-time">${now}</span></div>
      </div>
      ${avatar}`;
  } else {
    div.innerHTML = `
      ${avatar}
      <div class="msg-body">
        <div class="msg-bubble markdown" id="msg-${Date.now()}">${renderMarkdown(content)}</div>
        <div class="msg-meta">
          <span class="msg-time">${now}</span>
          ${agentTags}
          <button class="msg-copy icon-btn" style="width:22px;height:22px" onclick="copyMsg(this)" title="Copy">
            <svg width="11" height="11" viewBox="0 0 11 11" fill="none"><rect x="1" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="1.2"/><path d="M3 3V2a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H7" stroke="currentColor" stroke-width="1.2"/></svg>
          </button>
        </div>
      </div>`;
  }

  inner.appendChild(div);
  return div;
}

function copyMsg(btn) {
  const text = btn.closest('.msg').querySelector('.msg-bubble').textContent;
  navigator.clipboard.writeText(text).then(() => showToast('Copied', 'success'));
}

// Agent activity
function showAgentActivity(model) {
  const inner = document.getElementById('messagesInner');
  const emptyState = document.getElementById('emptyState');
  if (emptyState) emptyState.remove();

  const div = document.createElement('div');
  div.className = 'msg assistant';
  div.id = 'agentActivity';

  const agentNames = {
    'synthex-nova-ultra': ['α Reasoning', 'δ Research', 'β Reflection', 'ρ Debate', 'λ Synthesis'],
    'synthex-nova-pro':   ['α Reasoning', 'δ Research', 'λ Synthesis'],
    'synthex-nova-swift': ['μ Flash'],
    'synthex-nova-forge': ['ε Coding', 'β Review'],
  };
  const agents = agentNames[model] || ['α Reasoning', 'λ Synthesis'];

  div.innerHTML = `
    <div class="msg-avatar">S</div>
    <div class="msg-body">
      <div class="agent-activity visible">
        <div class="activity-dots"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        <span class="activity-text">Processing</span>
        <div class="activity-agents">${agents.map(a=>`<span class="act-agent">${a}</span>`).join('')}</div>
      </div>
    </div>`;
  inner.appendChild(div);
  scrollBottom();
  return div;
}

function removeAgentActivity() {
  document.getElementById('agentActivity')?.remove();
}

// Streaming message
function createStreamMsg() {
  const inner = document.getElementById('messagesInner');
  const div = document.createElement('div');
  div.className = 'msg assistant';
  div.innerHTML = `
    <div class="msg-avatar">S</div>
    <div class="msg-body">
      <div class="msg-bubble markdown" id="streamBubble"></div>
    </div>`;
  inner.appendChild(div);
  return div;
}

function updateStreamMsg(text) {
  const bubble = document.getElementById('streamBubble');
  if (bubble) {
    bubble.innerHTML = renderMarkdown(text);
    scrollBottom();
  }
}

function finalizeStreamMsg(text, agents) {
  const div = document.getElementById('streamBubble')?.closest('.msg');
  if (!div) return;
  const now = new Date().toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
  const agentTags = (agents && agents.length)
    ? `<div class="msg-agents">${agents.map(a=>`<span class="agent-tag">${escHtml(a)}</span>`).join('')}</div>`
    : '';
  const body = div.querySelector('.msg-body');
  body.insertAdjacentHTML('beforeend', `
    <div class="msg-meta">
      <span class="msg-time">${now}</span>
      ${agentTags}
      <button class="msg-copy icon-btn" style="width:22px;height:22px" onclick="copyMsg(this)">
        <svg width="11" height="11" viewBox="0 0 11 11" fill="none"><rect x="1" y="3" width="7" height="7" rx="1" stroke="currentColor" stroke-width="1.2"/><path d="M3 3V2a1 1 0 011-1h4a1 1 0 011 1v5a1 1 0 01-1 1H7" stroke="currentColor" stroke-width="1.2"/></svg>
      </button>
    </div>`);
  div.querySelector('.msg-bubble').id = '';
}

function scrollBottom() {
  const wrap = document.getElementById('messagesWrap');
  requestAnimationFrame(() => { wrap.scrollTop = wrap.scrollHeight; });
}

// Input resize
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  document.getElementById('sendBtn').disabled = !el.value.trim() || isStreaming;
  const len = el.value.length;
  document.getElementById('charCount').textContent = len > 100 ? `${len}` : '';
}

function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function useSuggestion(el) {
  const text = el.querySelector('.suggestion-text').textContent;
  const input = document.getElementById('chatInput');
  input.value = text;
  autoResize(input);
  input.focus();
}

// File handling
function handleFileSelect(input) {
  const file = input.files[0];
  if (!file) return;
  attachedFile = file;
  const preview = document.getElementById('filePreview');
  preview.style.display = 'flex';
  preview.innerHTML = `
    <div class="file-chip">
      📎 ${escHtml(file.name)} (${(file.size/1024).toFixed(1)} KB)
      <button onclick="removeFile()">×</button>
    </div>`;
}

function removeFile() {
  attachedFile = null;
  document.getElementById('filePreview').style.display = 'none';
  document.getElementById('fileInput').value = '';
}

// Connection status
async function checkConnection() {
  const dot = document.getElementById('statusDot');
  const label = document.getElementById('statusLabel');
  dot.style.background = 'var(--amber)';
  dot.style.boxShadow = 'none';
  label.textContent = 'Connecting...';
  const ok = await SynthexAPI.ping();
  if (ok) {
    dot.style.background = 'var(--green)';
    dot.style.boxShadow = '0 0 6px rgba(16,185,129,.5)';
    label.textContent = 'Connected';
  } else {
    dot.style.background = 'var(--red)';
    dot.style.boxShadow = 'none';
    label.textContent = isConfigured() ? 'Offline' : 'Not configured';
  }
}

function escHtml(str) {
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
