for (const figure of document.querySelectorAll('.tools-video')) {
  const image = figure.querySelector('.tools-animation img');
  const button = figure.querySelector('.animation-toggle');
  if (!image || !button) continue;
  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  function syncPreference() {
    button.hidden = motion.matches;
    button.setAttribute('aria-pressed', 'false');
    button.textContent = 'Pause animation';
    image.src = image.dataset.animationSrc;
  }
  button.addEventListener('click', () => {
    const paused = button.getAttribute('aria-pressed') !== 'true';
    image.src = paused ? image.dataset.posterSrc : image.dataset.animationSrc;
    button.setAttribute('aria-pressed', String(paused));
    button.textContent = paused ? 'Resume animation' : 'Pause animation';
  });
  motion.addEventListener('change', syncPreference);
  syncPreference();
}
