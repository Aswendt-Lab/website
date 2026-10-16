// Native details/summary provides touch and keyboard toggles without JavaScript.
// Mouse hover additionally reveals each profile without requiring a click.
for (const tile of document.querySelectorAll('.team-tile')) {
  tile.addEventListener('pointerenter', event => {
    if (event.pointerType === 'mouse') tile.open = true;
  });
  tile.addEventListener('pointerleave', event => {
    if (event.pointerType === 'mouse') tile.open = false;
  });
  tile.addEventListener('focusout', event => {
    if (!tile.contains(event.relatedTarget)) tile.open = false;
  });
  tile.querySelector('.team-close').addEventListener('click', () => {
    tile.open = false;
    tile.querySelector('summary').focus();
  });
  tile.addEventListener('keydown', event => {
    if (event.key === 'Escape') tile.open = false;
  });
}
