// Only the Info summary toggles details; portraits and hover never open them.
// Native details/summary also provides the close control, touch and keyboard support.
for (const tile of document.querySelectorAll('.team-tile')) {
  const details = tile.querySelector('.team-details');
  const summary = details.querySelector('summary');
  tile.addEventListener('focusout', event => {
    if (!tile.contains(event.relatedTarget)) details.open = false;
  });
  tile.addEventListener('keydown', event => {
    if (event.key === 'Escape' && details.open) {
      details.open = false;
      summary.focus();
    }
  });
}
