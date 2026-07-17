const $ = (selector) => document.querySelector(selector);
const sourceBoxes = document.querySelectorAll('.source input');
const fixtures = {
  '.cursorrules': 'Use pnpm for all dependency operations.\nRun pnpm test before handoff.\nPrefer TypeScript; avoid any.',
  'CLAUDE.md': 'Install packages with npm only.\nFollow conventional commits.',
  'GEMINI.md': 'Never commit secrets or local env files.\nRun npm test before handoff.',
  'copilot-instructions.md': 'Prefer TypeScript; avoid any.\nFollow conventional commits.'
};
let currentManifest = $('#manifest').innerText;
let currentResolutions = { packageManager: 'pnpm' };

function updateTokens() {
  const total = [...sourceBoxes].filter(box => box.checked).reduce((sum, box) => sum + Number(box.dataset.tokens), 0);
  const compact = Math.round(total * 0.318);
  const reduction = total ? Math.round((1 - compact / total) * 100) : 0;
  $('#tokenReadout').textContent = `${total.toLocaleString()} → ${compact.toLocaleString()} tokens`;
  $('#reclaimed').textContent = `${reduction}%`;
  document.querySelectorAll('.source').forEach(label => label.classList.toggle('selected', label.querySelector('input').checked));
}
async function compileSources() {
  const sources = [...sourceBoxes].filter(box => box.checked).map(box => {
    const name = box.closest('.source').querySelector('b').textContent;
    return { name, content: fixtures[name] };
  });
  try {
    const response = await fetch('/api/compile', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ sources, resolutions: currentResolutions }) });
    if (!response.ok) throw new Error('Compilation failed');
    const result = await response.json();
    currentManifest = result.manifest;
    $('#manifest').textContent = result.manifest;
    $('#tokenReadout').textContent = `${result.inputTokens.toLocaleString()} → ${result.outputTokens.toLocaleString()} tokens`;
    $('#reclaimed').textContent = `${result.reclaimed}%`;
    $('#conflictStat').textContent = result.conflicts.length;
  } catch (error) {
    console.warn('Lekgotla API unavailable; retaining local demo state.', error);
  }
}
sourceBoxes.forEach(box => box.addEventListener('change', () => { updateTokens(); compileSources(); }));

document.querySelectorAll('.conflict-head').forEach(head => head.addEventListener('click', () => head.closest('.conflict').classList.toggle('open')));
document.querySelectorAll('.choice').forEach(choice => choice.addEventListener('click', () => {
  const group = choice.closest('.decision');
  group.querySelectorAll('.choice').forEach(button => button.classList.remove('active'));
  choice.classList.add('active');
  if (choice.dataset.rule) {
    currentResolutions.packageManager = choice.dataset.rule;
    compileSources();
  }
}));

const routeData = {
  ui: ['Build checkout UI', '4 rules · 514 tokens', 'components · design system · test rules', '84% less context than the full manifest'],
  api: ['Fix orders API timeout', '5 rules · 642 tokens', 'API contracts · database · test rules', '80% less context than the full manifest'],
  review: ['Review payment PR', '3 rules · 376 tokens', 'commit rules · security · test rules', '88% less context than the full manifest']
};
document.querySelectorAll('.task').forEach(button => button.addEventListener('click', async () => {
  document.querySelectorAll('.task').forEach(tab => tab.classList.remove('active'));
  button.classList.add('active');
  const [name, count, text, note] = routeData[button.dataset.task];
  $('#taskName').textContent = name; $('#bundleCount').textContent = count; $('#bundleText').textContent = text; $('#routeNote').innerHTML = `<span>↗</span> ${note}`;
  try {
    const response = await fetch('/api/context', { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ manifest: currentManifest, task: button.dataset.task }) });
    if (!response.ok) throw new Error('Context routing failed');
    const bundle = await response.json();
    $('#taskName').textContent = bundle.task;
    $('#bundleCount').textContent = `${bundle.rules} rules · ${bundle.tokens} tokens`;
    $('#bundleText').textContent = bundle.areas;
    $('#routeNote').innerHTML = `<span>↗</span> ${bundle.reduction}% less context than the full manifest`;
  } catch (error) { console.warn('Lekgotla API unavailable; retaining local route state.', error); }
}));

$('#copyManifest').addEventListener('click', async () => {
  await navigator.clipboard.writeText(currentManifest);
  $('#copyManifest').textContent = 'Copied!';
  setTimeout(() => $('#copyManifest').textContent = 'Copy', 1500);
});

$('#downloadManifest').addEventListener('click', () => {
  const blob = new Blob([currentManifest], {type: 'text/markdown'});
  const link = Object.assign(document.createElement('a'), {href: URL.createObjectURL(blob), download: 'AGENTS.md'});
  link.click(); URL.revokeObjectURL(link.href);
});

$('#addSource').addEventListener('click', () => alert('Drop a config file or repository folder here to add it to the compilation.'));
updateTokens();
compileSources();
