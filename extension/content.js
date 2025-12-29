// Create and inject the floating element
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

document.addEventListener('mouseup', (ev) => {
  const sel = window.getSelection().toString().trim();
  if (!sel) {
    hideFloating();
    return;
  }
  
  // Don't show if clicking inside the floating div itself
  if (ev.target.closest('#immersive-translate-floating')) return;

  const x = ev.pageX;
  const y = ev.pageY;
  
  showFloating(x, y, 'Translating...');

  chrome.runtime.sendMessage(
    { action: 'translate', text: sel, target: 'fr' },
    (response) => {
      if (response && response.success) {
        showFloating(x, y, response.text);
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
