(() => {
  const form = document.querySelector('.publication-filters');
  if (!form) return;
  const search = document.getElementById('publication-search');
  const year = document.getElementById('publication-year');
  const type = document.getElementById('publication-type');
  const status = document.getElementById('publication-results');
  const entries = [...document.querySelectorAll('.publication-entry')].map(element => ({
    element, text: element.textContent.toLocaleLowerCase(),
  }));
  function update() {
    const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    for (const { element, text } of entries) {
      const matches = terms.every(term => text.includes(term)) &&
        (!year.value || element.dataset.year === year.value) &&
        (!type.value || element.dataset.type === type.value);
      element.hidden = !matches;
      if (matches) count++;
    }
    for (const section of document.querySelectorAll('.publication-year')) {
      section.hidden = !section.querySelector('.publication-entry:not([hidden])');
    }
    status.textContent = count ? `${count} publication${count === 1 ? '' : 's'} shown` : 'No publications match your search.';
  }
  form.hidden = false;
  status.hidden = false;
  form.addEventListener('input', update);
  form.addEventListener('change', update);
  update();
})();
