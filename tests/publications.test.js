const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const script = fs.readFileSync('assets/publications.js', 'utf8');
function setup() {
  const entries = [
    { textContent: 'MRI recovery Smith Test Journal 10.1/stroke', dataset: { year: '2026', type: 'article' }, hidden: false },
    { textContent: 'MRI networks Jones bioRxiv', dataset: { year: '2025', type: 'preprint' }, hidden: false },
  ];
  const fields = Object.fromEntries(['publication-search', 'publication-year', 'publication-type'].map(id => [id, { value: '' }]));
  fields['publication-results'] = { textContent: '', hidden: true };
  const listeners = {};
  const form = { hidden: true, addEventListener: (name, action) => { listeners[name] = action; } };
  const sections = entries.map(entry => ({ hidden: false, querySelector: () => entry.hidden ? null : entry }));
  const document = {
    querySelector: () => form,
    getElementById: id => fields[id],
    querySelectorAll: selector => selector === '.publication-entry' ? entries : sections,
  };
  vm.runInNewContext(script, { document });
  return { fields, entries, sections, form, update: listeners.input };
}
test('progressive enhancement reveals filters and all entries', () => {
  const s = setup();
  assert.equal(s.form.hidden, false);
  assert.equal(s.fields['publication-results'].textContent, '2 publications shown');
});
test('case-insensitive search supports multiple terms', () => {
  const s = setup(); s.fields['publication-search'].value = 'MRI SMITH'; s.update();
  assert.deepEqual(s.entries.map(e => e.hidden), [false, true]);
  assert.equal(s.fields['publication-results'].textContent, '1 publication shown');
});
test('year and type filters combine with search', () => {
  const s = setup(); s.fields['publication-year'].value = '2025'; s.fields['publication-type'].value = 'preprint'; s.update();
  assert.deepEqual(s.entries.map(e => e.hidden), [true, false]);
  assert.deepEqual(s.sections.map(e => e.hidden), [true, false]);
});
test('empty results are announced and clearing restores entries', () => {
  const s = setup(); s.fields['publication-search'].value = 'no match'; s.update();
  assert.equal(s.fields['publication-results'].textContent, 'No publications match your search.');
  s.fields['publication-search'].value = ''; s.update();
  assert.deepEqual(s.entries.map(e => e.hidden), [false, false]);
});
