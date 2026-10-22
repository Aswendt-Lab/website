// Only Info opens a biography. Mouse leave and outside taps close it.
for (const tile of document.querySelectorAll('.team-tile')) {
  const details = tile.querySelector('.team-details');
  const summary = details.querySelector('summary');

  details.addEventListener('toggle', () => {
    summary.tabIndex = details.open ? -1 : 0;
    if (details.open) {
      // Focus the scroll container so keyboard users can read long biographies.
      details.tabIndex = 0;
      details.focus({ preventScroll: true });
    } else {
      details.removeAttribute('tabindex');
    }
  });
  tile.addEventListener('pointerleave', event => {
    if (event.pointerType === 'mouse') details.open = false;
  });
  tile.addEventListener('focusout', event => {
    if (!tile.contains(event.relatedTarget)) details.open = false;
  });
  tile.addEventListener('keydown', event => {
    if (event.key === 'Escape' && details.open) {
      details.open = false;
      summary.tabIndex = 0;
      summary.focus({ preventScroll: true });
    }
  });
}

document.addEventListener('pointerdown', event => {
  for (const details of document.querySelectorAll('.team-details[open]')) {
    if (!details.closest('.team-tile').contains(event.target)) details.open = false;
  }
});
