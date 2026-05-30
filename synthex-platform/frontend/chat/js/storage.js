// Conversation Storage
const Store = {
  CONV_KEY: 'sx_conversations',
  CUR_KEY: 'sx_current_conv',

  getAll() {
    try { return JSON.parse(localStorage.getItem(this.CONV_KEY) || '[]'); } catch { return []; }
  },
  save(convs) { localStorage.setItem(this.CONV_KEY, JSON.stringify(convs.slice(0, 50))); },
  getCurrent() { return localStorage.getItem(this.CUR_KEY); },
  setCurrent(id) { localStorage.setItem(this.CUR_KEY, id); },

  createConv(title) {
    const id = 'conv-' + Date.now();
    const conv = { id, title: title || 'New Chat', messages: [], createdAt: Date.now(), model: SynthexConfig.DEFAULT_MODEL };
    const convs = this.getAll();
    convs.unshift(conv);
    this.save(convs);
    this.setCurrent(id);
    return conv;
  },

  getConv(id) { return this.getAll().find(c => c.id === id); },

  updateConv(id, updates) {
    const convs = this.getAll();
    const idx = convs.findIndex(c => c.id === id);
    if (idx >= 0) { Object.assign(convs[idx], updates); this.save(convs); }
  },

  addMessage(convId, msg) {
    const convs = this.getAll();
    const conv = convs.find(c => c.id === convId);
    if (conv) {
      conv.messages.push(msg);
      // Auto-title from first user message
      if (conv.messages.filter(m => m.role === 'user').length === 1 && msg.role === 'user') {
        conv.title = msg.content.slice(0, 50) + (msg.content.length > 50 ? '...' : '');
      }
      this.save(convs);
    }
  },

  deleteConv(id) {
    const convs = this.getAll().filter(c => c.id !== id);
    this.save(convs);
    if (this.getCurrent() === id) localStorage.removeItem(this.CUR_KEY);
  },
};
