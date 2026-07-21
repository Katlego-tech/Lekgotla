const $ = (selector) => document.querySelector(selector);
const getSourceBoxes = () => document.querySelectorAll('.source input');

const sourcesData = {
  '.cursorrules': 'Use pnpm for all dependency operations.\nRun pnpm test before handoff.\nPrefer TypeScript; avoid any.',
  'CLAUDE.md': 'Install packages with npm only.\nFollow conventional commits.',
  'GEMINI.md': 'Never commit secrets or local env files.\nRun npm test before handoff.',
  'copilot-instructions.md': 'Prefer TypeScript; avoid any.\nFollow conventional commits.'
};
let currentManifest = $('#manifest').innerText;
let currentResolutions = {};

function estimateTokens(text) {
  const words = text.trim().match(/\S+/g);
  const count = words ? words.length : 0;
  return Math.max(1, Math.round(count * 1.28));
}

function updateTokens() {
  const total = [...getSourceBoxes()].filter(box => box.checked).reduce((sum, box) => sum + Number(box.dataset.tokens), 0);
  const compact = Math.round(total * 0.318);
  const reduction = total ? Math.round((1 - compact / total) * 100) : 0;
  $('#tokenReadout').textContent = `${total.toLocaleString()} → ${compact.toLocaleString()} tokens`;
  $('#reclaimed').textContent = `${reduction}%`;
  document.querySelectorAll('.source').forEach(label => label.classList.toggle('selected', label.querySelector('input').checked));
}

function getSourceClass(source) {
  const name = source.toLowerCase();
  if (name.includes('cursor')) return 'cursor';
  if (name.includes('claude')) return 'claude';
  if (name.includes('gemini')) return 'gemini';
  return 'source-other';
}

function renderConflicts(conflicts) {
  const container = $('#conflicts');
  container.innerHTML = '';

  conflicts.forEach((conflict, index) => {
    const number = String(index + 1).padStart(2, '0');
    const severityClass = conflict.severity.toLowerCase();
    const severityText = conflict.severity.toUpperCase();

    const article = document.createElement('article');
    article.className = 'conflict';
    if (index === 0) article.classList.add('open');

    let optionsHtml = '';
    let decisionButtonsHtml = '';

    const activeValue = currentResolutions[conflict.key] || conflict.options[0].value;
    currentResolutions[conflict.key] = activeValue;

    conflict.options.forEach(opt => {
      const sourceClass = getSourceClass(opt.source);
      optionsHtml += `
        <div>
          <span class="rule-source ${sourceClass}">${opt.source}</span>
          <p>“${opt.text}”</p>
        </div>
      `;

      const isActive = activeValue === opt.value;
      const activeClass = isActive ? 'active' : '';
      decisionButtonsHtml += `
        <button class="choice ${activeClass}" data-key="${conflict.key}" data-value="${opt.value}">
          Use ${opt.value}
        </button>
      `;
    });

    article.innerHTML = `
      <button class="conflict-head">
        <span class="number">${number}</span>
        <span><b>${conflict.title}</b><small>${conflict.options.length} incompatible instructions detected</small></span>
        <span class="severity ${severityClass}">${severityText}</span>
        <span class="chevron">⌄</span>
      </button>
      <div class="conflict-body">
        ${optionsHtml}
        <div class="decision">
          ${decisionButtonsHtml}
        </div>
      </div>
    `;

    article.querySelector('.conflict-head').addEventListener('click', () => {
      article.classList.toggle('open');
    });

    article.querySelectorAll('.choice').forEach(button => {
      button.addEventListener('click', () => {
        const key = button.dataset.key;
        const val = button.dataset.value;
        currentResolutions[key] = val;
        compileSources();
      });
    });

    container.appendChild(article);
  });
}

async function compileSources() {
  const sources = [...getSourceBoxes()].filter(box => box.checked).map(box => {
    const name = box.closest('.source').querySelector('b').textContent;
    return { name, content: sourcesData[name] };
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
    $('#signalText').innerHTML = `Rules grouped into <b>${result.directives} directives</b>. ${result.conflicts.length} contradictions need your call before compilation.`;
    renderConflicts(result.conflicts);
  } catch (error) {
    console.warn('Lekgotla API unavailable; retaining local demo state.', error);
  }
}

getSourceBoxes().forEach(box => box.addEventListener('change', () => { updateTokens(); compileSources(); }));

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

$('#addSource').addEventListener('click', () => {
  $('#fileInput').click();
});

function addSource(name, content, tokensCount) {
  if (sourcesData[name]) {
    sourcesData[name] = content;
    const labels = document.querySelectorAll('.source');
    for (const label of labels) {
      if (label.querySelector('b').textContent === name) {
        const input = label.querySelector('input');
        input.dataset.tokens = tokensCount;
        label.querySelector('small').textContent = `${tokensCount.toLocaleString()} tokens · loaded`;
        input.checked = true;
        updateTokens();
        compileSources();
        return;
      }
    }
  }

  sourcesData[name] = content;
  const colors = ['violet', 'orange', 'lime', 'blue'];
  const randomColor = colors[Math.floor(Math.random() * colors.length)];

  const label = document.createElement('label');
  label.className = 'source selected';
  label.innerHTML = `
    <input type="checkbox" checked data-tokens="${tokensCount}" />
    <span class="file-icon ${randomColor}">✦</span>
    <span><b>${name}</b><small>${tokensCount.toLocaleString()} tokens · loaded</small></span>
    <i>↗</i>
  `;

  label.querySelector('input').addEventListener('change', () => {
    updateTokens();
    compileSources();
  });

  $('#sourceList').appendChild(label);
  updateTokens();
  compileSources();
}

async function handleFiles(filesOrEntries) {
  const results = [];

  const readFileAsText = (file) => {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve({ name: file.name, content: e.target.result });
      reader.onerror = () => resolve(null);
      reader.readAsText(file);
    });
  };

  const traverseEntry = async (entry) => {
    if (entry.isFile) {
      const file = await new Promise((resolve) => entry.file(resolve));
      const res = await readFileAsText(file);
      if (res) results.push(res);
    } else if (entry.isDirectory) {
      const reader = entry.createReader();
      const readEntriesBatch = () => {
        return new Promise((resolve) => {
          reader.readEntries(resolve);
        });
      };
      
      let entries = await readEntriesBatch();
      while (entries.length > 0) {
        for (const child of entries) {
          await traverseEntry(child);
        }
        entries = await readEntriesBatch();
      }
    }
  };

  for (const item of filesOrEntries) {
    if (item.webkitGetAsEntry) {
      const webkitEntry = item.webkitGetAsEntry();
      if (webkitEntry) {
        await traverseEntry(webkitEntry);
      }
    } else if (item instanceof File) {
      const res = await readFileAsText(item);
      if (res) results.push(res);
    }
  }

  for (const res of results) {
    const isConfig = res.name.startsWith('.') || 
                     res.name.endsWith('.md') || 
                     res.name.endsWith('.txt') || 
                     res.name.endsWith('.json') || 
                     res.name.endsWith('.yaml') || 
                     res.name.endsWith('.yml');
    
    if (isConfig && res.content) {
      const tokens = estimateTokens(res.content);
      addSource(res.name, res.content, tokens);
    }
  }
}

const dropzone = $('#dropzone');
const fileInput = $('#fileInput');

dropzone.addEventListener('click', (e) => {
  if (e.target !== fileInput) {
    fileInput.click();
  }
});

fileInput.addEventListener('change', async (e) => {
  const files = [...e.target.files];
  await handleFiles(files);
});

dropzone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
  dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', async (e) => {
  e.preventDefault();
  dropzone.classList.remove('dragover');
  const items = e.dataTransfer.items ? [...e.dataTransfer.items] : [...e.dataTransfer.files];
  await handleFiles(items);
});

updateTokens();
compileSources();
