/**
 * Synthex Chat — Configuration
 * NOVA Series model names
 */
const SynthexConfig = {
  get BACKEND_URL() { return localStorage.getItem('sx_backend_url') || 'http://localhost:8000'; },
  DEFAULT_MODEL: 'synthex-nova-pro',
  VERSION: '1.0.0',

  MODELS: {
    'synthex-nova-ultra': {
      name: 'Nova Ultra',
      icon: '🌌',
      tier: 'ultra',
      agents: 5,
      latency: '~8s',
      desc: 'Maximum intelligence · 5 agents',
      plan: 'pro',
      color: '#F5A623',
    },
    'synthex-nova-pro': {
      name: 'Nova Pro',
      icon: '⚡',
      tier: 'pro',
      agents: 3,
      latency: '~3s',
      desc: 'Balanced · Recommended',
      plan: 'free',
      color: '#6C63FF',
    },
    'synthex-nova-swift': {
      name: 'Nova Swift',
      icon: '💫',
      tier: 'swift',
      agents: 1,
      latency: '<1s',
      desc: 'Fastest response · Groq LPU',
      plan: 'free',
      color: '#00D4AA',
    },
    'synthex-nova-forge': {
      name: 'Nova Forge',
      icon: '🔥',
      tier: 'forge',
      agents: 2,
      latency: '~2s',
      desc: 'Code specialist · 480B',
      plan: 'free',
      color: '#FF6B6B',
    },
  },

  USE_STREAMING: true,
  MAX_HISTORY: 30,
  STREAM_CHUNK_DELAY_MS: 8,
};

const getApiKey    = ()  => localStorage.getItem('sx_api_key') || '';
const isConfigured = ()  => !!getApiKey();
const getLanguage  = ()  => localStorage.getItem('sx_language') || 'auto';
const isBengali    = ()  => getLanguage() === 'bn';
const saveConfig   = (url, key) => {
  if (url) localStorage.setItem('sx_backend_url', url.replace(/\/$/, ''));
  if (key) localStorage.setItem('sx_api_key', key);
};
