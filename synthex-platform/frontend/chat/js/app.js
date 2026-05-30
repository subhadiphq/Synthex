// Main App Logic
async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text || isStreaming) return;

  if (!isConfigured()) {
    openSetup();
    showToast('Please configure your API key first', 'error');
    return;
  }

  // Create conv if needed
  if (!currentConvId) {
    const conv = Store.createConv();
    currentConvId = conv.id;
  }

  // User message
  const userMsg = { role: 'user', content: text };
  Store.addMessage(currentConvId, userMsg);
  appendMessage('user', text);

  // Clear input
  input.value = '';
  autoResize(input);
  document.getElementById('sendBtn').disabled = true;

  // Handle file upload
  if (attachedFile) {
    const file = attachedFile;
    removeFile();
    try {
      const result = await SynthexAPI.uploadFile(file, text, currentModel);
      const assistantContent = result.analysis || result.message || 'File processed.';
      Store.addMessage(currentConvId, { role:'assistant', content: assistantContent });
      appendMessage('assistant', assistantContent);
      scrollBottom();
    } catch(err) {
      showToast(err.message, 'error');
    }
    isStreaming = false;
    document.getElementById('sendBtn').disabled = false;
    renderConvList();
    return;
  }

  isStreaming = true;

  // Get conversation history
  const conv = Store.getConv(currentConvId);
  const messages = conv ? conv.messages.slice(-SynthexConfig.MAX_HISTORY) : [userMsg];

  // Show agent activity
  const actDiv = showAgentActivity(currentModel);

  try {
    let fullText = '';

    if (SynthexConfig.USE_STREAMING) {
      // Streaming
      let streamDiv = null;
      let chunkCount = 0;

      for await (const chunk of SynthexAPI.streamMessage(messages, currentModel)) {
        if (chunkCount === 0) {
          removeAgentActivity();
          streamDiv = createStreamMsg();
        }
        fullText += chunk;
        chunkCount++;
        if (chunkCount % 3 === 0) updateStreamMsg(fullText);
      }

      if (fullText) {
        updateStreamMsg(fullText);
        finalizeStreamMsg(fullText, []);
      } else if (!fullText) {
        removeAgentActivity();
        fullText = 'No response received. Please try again.';
        appendMessage('assistant', fullText);
      }
    } else {
      // Non-streaming
      const resp = await SynthexAPI.sendMessage(messages, currentModel);
      removeAgentActivity();
      fullText = resp.content;
      appendMessage('assistant', fullText, resp.agents_used);
    }

    // Store response
    if (fullText) {
      Store.addMessage(currentConvId, { role:'assistant', content: fullText });
    }

    scrollBottom();
    renderConvList();

  } catch(err) {
    removeAgentActivity();
    appendMessage('assistant', `⚠️ ${err.message}`);
    showToast(err.message, 'error');
  }

  isStreaming = false;
  document.getElementById('sendBtn').disabled = false;
  document.getElementById('chatInput').focus();
}

// Init
(function init() {
  // Language
  isBengaliMode = getLanguage() === 'bn';
  document.getElementById('langToggle').classList.toggle('on', isBengaliMode);

  // Responsive
  if (window.innerWidth <= 768) {
    document.getElementById('sidebarToggle').style.display = 'flex';
  }

  // Load conversations
  renderConvList();

  // Load current conv
  const curId = Store.getCurrent();
  if (curId && Store.getConv(curId)) {
    loadConv(curId);
  }

  // Check connection
  checkConnection();
  setInterval(checkConnection, 30000);

  // Show setup if not configured
  if (!isConfigured()) {
    setTimeout(() => {
      document.getElementById('setupModal').classList.remove('hidden');
    }, 500);
  }

  // Input focus
  document.getElementById('chatInput').focus();
})();
