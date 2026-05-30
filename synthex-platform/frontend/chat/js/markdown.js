// Markdown Renderer with syntax highlighting
(function(){
  if (typeof marked === 'undefined') return;
  marked.setOptions({ breaks: true, gfm: true });

  const renderer = new marked.Renderer();

  renderer.code = function(code, lang) {
    const language = lang || 'plaintext';
    let highlighted = code;
    try {
      if (hljs && hljs.getLanguage(language)) {
        highlighted = hljs.highlight(code, { language }).value;
      } else {
        highlighted = hljs.highlightAuto(code).value;
      }
    } catch(e) {}
    return `<div class="code-block">
      <div class="code-header">
        <span class="code-lang">${language}</span>
        <button class="code-copy" onclick="copyCode(this)">Copy</button>
      </div>
      <div class="code-body"><pre><code class="hljs">${highlighted}</code></pre></div>
    </div>`;
  };

  renderer.codespan = function(code) {
    return `<code>${code}</code>`;
  };

  marked.use({ renderer });
})();

function renderMarkdown(text) {
  if (typeof marked === 'undefined') return text.replace(/\n/g,'<br>');
  try { return marked.parse(text); } catch(e) { return text.replace(/\n/g,'<br>'); }
}

function copyCode(btn) {
  const code = btn.closest('.code-block').querySelector('code').textContent;
  navigator.clipboard.writeText(code).then(() => {
    btn.textContent = 'Copied!';
    btn.classList.add('copied');
    setTimeout(() => { btn.textContent = 'Copy'; btn.classList.remove('copied'); }, 2000);
  });
}
