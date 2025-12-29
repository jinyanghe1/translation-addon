// --- Cleanup (Handle Extension Reloads) ---
const existingSidebar = document.getElementById('immersive-translate-sidebar');
if (existingSidebar) {
  existingSidebar.remove();
}
const existingFloating = document.getElementById('immersive-translate-floating');
if (existingFloating) {
  existingFloating.remove();
}

// --- Floating Translation (Existing) ---
const floating = document.createElement('div');
floating.id = 'immersive-translate-floating';
document.body.appendChild(floating);

function showFloating(x, y, text) {
  floating.style.left = (x + 8) + 'px';
  floating.style.top = (y + 8) + 'px';
  floating.textContent = text;
  floating.style.display = 'block';
}

function hideFloating() {
  floating.style.display = 'none';
}

// --- Sidebar & Rare Word Detection (New) ---

const sidebar = document.createElement('div');
sidebar.id = 'immersive-translate-sidebar';
document.body.appendChild(sidebar);

// Store added words to handle duplicates. Key: word (lowercase), Value: DOM Element
const sidebarWords = new Map();

function addWordToSidebar(word, translation) {
  const key = word.trim().toLowerCase();
  
  if (sidebarWords.has(key)) {
    // Highlight existing
    const existingEl = sidebarWords.get(key);
    existingEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
    existingEl.classList.add('immersive-highlight');
    setTimeout(() => {
      existingEl.classList.remove('immersive-highlight');
    }, 2000); // Highlight for 2 seconds
    return;
  }

  // Create new item
  const item = document.createElement('div');
  item.className = 'immersive-word-item';
  
  const original = document.createElement('div');
  original.className = 'immersive-word-original';
  original.textContent = word;
  
  const trans = document.createElement('div');
  trans.className = 'immersive-word-translation';
  trans.textContent = translation;
  
  item.appendChild(original);
  item.appendChild(trans);
  
  sidebar.appendChild(item);
  sidebarWords.set(key, item);
  
  // Ensure sidebar is visible if it has content
  if (sidebarWords.size > 0) {
    sidebar.style.display = 'block';
  }
}

document.addEventListener('mouseup', (ev) => {
  const sel = window.getSelection().toString().trim();
  if (!sel) {
    hideFloating();
    return;
  }
  
  if (ev.target.closest('#immersive-translate-floating') || 
      ev.target.closest('#immersive-translate-sidebar')) return;

  const x = ev.pageX;
  const y = ev.pageY;
  
  showFloating(x, y, 'Translating...');

  chrome.runtime.sendMessage(
    { action: 'translate', text: sel, target: 'fr' },
    (response) => {
      if (response && response.success) {
        showFloating(x, y, response.text);
        // Also add to sidebar
        addWordToSidebar(sel, response.text);
      } else {
        showFloating(x, y, '[Error: ' + (response ? response.error : 'Unknown') + ']');
      }
    }
  );
});

document.addEventListener('mousedown', (e) => {
  if (!e.target.closest('#immersive-translate-floating')) {
    hideFloating();
  }
});

function analyzePage() {
  // Get visible text (limit to 5000 chars for prototype safety)
  const text = document.body.innerText.slice(0, 5000);
  
  if (!text.trim()) return;

  fetch('http://127.0.0.1:5000/detect', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text: text })
  })
  .then(response => response.json())
  .then(data => {
    if (data.results && Array.isArray(data.results)) {
      data.results.forEach(item => {
        addWordToSidebar(item.word, item.translation);
      });
    }
  })
  .catch(err => console.error('Error detecting rare words:', err));
}

// Run analysis shortly after load
setTimeout(analyzePage, 1000);