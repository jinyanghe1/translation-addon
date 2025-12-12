// Frontend JS: selection translation + dynamic rare-word highlighting

const floating = document.getElementById('floating');
const results = document.getElementById('results');

function showFloating(x, y, text) {
  floating.style.left = (x + 8) + 'px';
  floating.style.top = (y + 8) + 'px';
  floating.textContent = text;
  floating.style.display = 'block';
}

function hideFloating() { floating.style.display = 'none'; }

async function translate(text, target='fr') {
  try {
    const res = await fetch('/translate', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({text, target})
    });
    const j = await res.json();
    return j.text || '';
  } catch (e) {
    return '[erreur]';
  }
}

// Handle mouse selection
document.addEventListener('mouseup', async (ev) => {
  const sel = window.getSelection().toString().trim();
  if (!sel) { hideFloating(); return; }
  const x = ev.pageX, y = ev.pageY;
  showFloating(x, y, 'Traduction...');
  const t = await translate(sel, 'fr');
  showFloating(x, y, t);
  // add to sidebar
  const div = document.createElement('div');
  div.innerHTML = '<b>' + escapeHtml(sel) + '</b>: ' + escapeHtml(t);
  results.prepend(div);
});

// Simple escape
function escapeHtml(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

// Dynamic rare-word highlighting (very simple heuristic)
const common = new Set(["the","be","to","of","and","a","in","that","have","I","it","for","not","on","with","he","as","you","do","at"]);
function highlightRareWords() {
  const block = document.getElementById('text-block');
  const text = block.textContent || '';
  const parts = text.split(/(\s+)/);
  const frag = document.createDocumentFragment();
  parts.forEach(p => {
    if (/\s+/.test(p)) { frag.appendChild(document.createTextNode(p)); return; }
    const clean = p.replace(/[^\p{L}'-]/gu,'').toLowerCase();
    if (clean.length >= 7 && !common.has(clean)) {
      const span = document.createElement('span');
      span.className = 'highlight';
      span.textContent = p;
      span.addEventListener('click', async (e) => {
        const w = clean;
        const t = await translate(w, 'zh');
        const d = document.createElement('div'); d.innerHTML = '<i>' + escapeHtml(w) + '</i>: ' + escapeHtml(t);
        results.prepend(d);
      });
      frag.appendChild(span);
    } else {
      frag.appendChild(document.createTextNode(p));
    }
  });
  block.innerHTML = '';
  block.appendChild(frag);
}

highlightRareWords();

// hide floating when clicking elsewhere
document.addEventListener('mousedown', (e)=>{ if (!e.target.closest('#floating')) hideFloating(); });
