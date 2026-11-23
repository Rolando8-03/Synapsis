export function node(tag, className = '', text) {
  const element = document.createElement(tag);
  if (className) element.className = className;
  if (text !== undefined) element.textContent = text;
  return element;
}

function dimensions(rowCount, columnCount) {
  return Array.from({ length: rowCount }, () => Array(columnCount).fill(''));
}

function parseGrid(text) {
  const clean = text.trim().replace(/^\[/, '').replace(/\]$/, '');
  if (!clean) return [];
  return clean.split(/\r?\n|;/).map(row => row.trim()
    .replace(/\s*\/\s*/g, '/').replace(/\|/g, ' ').split(/\s+/).filter(Boolean));
}

function sizeSelect(text, limit, value) {
  const label = node('label', 'ws-size', text);
  const select = node('select');
  for (let i = 1; i <= limit; i++) select.add(new Option(i, i, false, i === value));
  label.append(select);
  return [label, select];
}

export function gridField(label, initial, options = {}) {
  const { augmented = false, vector = false, required = false, onChange = () => {} } = options;
  const box = node('fieldset', 'ws-grid-field');
  box.append(node('legend', '', label));
  const bar = node('div', 'ws-grid-bar');
  const limit = augmented ? 12 : 20;
  const [rowsLabel, rowsSelect] = sizeSelect(augmented ? 'Ecuaciones' : 'Filas', limit, augmented ? 3 : 2);
  const [colsLabel, colsSelect] = sizeSelect(augmented ? 'Incógnitas' : vector ? 'Componentes' : 'Columnas', limit, 3);
  if (!vector) bar.append(rowsLabel);
  bar.append(colsLabel);
  const revealPaste = node('button', 'secondary', 'Pegar datos');
  revealPaste.type = 'button';
  revealPaste.setAttribute('aria-expanded', 'false');
  bar.append(revealPaste);
  box.append(bar);
  const pastePanel = node('div', 'ws-grid-paste');
  pastePanel.hidden = true;
  const paste = node('textarea');
  paste.rows = 3;
  paste.placeholder = augmented ? '2  1 | 5\n1 -1 | 1' : '1 2\n3 4';
  paste.setAttribute('aria-label', 'Datos para pegar');
  const apply = node('button', 'secondary', 'Aplicar datos');
  apply.type = 'button';
  const error = node('p', 'result-error');
  error.setAttribute('role', 'status');
  pastePanel.append(paste, apply, error);
  box.append(pastePanel);
  const scrolling = node('div', 'ws-matrix-scroll');
  box.append(scrolling);
  box.append(node('p', 'ws-field-help', 'Admite enteros, decimales con punto y fracciones como 3/4. En sistemas también admite coma decimal.'));

  let rowCount = vector ? 1 : augmented ? 3 : 2;
  let columnCount = augmented ? 4 : 3;
  let cells = [];
  let emptySet = false;

  function draw(data) {
    const table = node('table', augmented ? 'ws-matrix ws-augmented' : 'ws-matrix');
    const head = table.createTHead().insertRow();
    head.append(node('th'));
    for (let j = 0; j < columnCount; j++) {
      const independent = augmented && j === columnCount - 1;
      const title = node('th', independent ? 'ws-independent' : '', augmented ? independent ? 'b' : `x${j + 1}` : `${j + 1}`);
      title.scope = 'col';
      head.append(title);
    }
    const body = table.createTBody();
    cells = Array.from({length: rowCount}, (_, i) => {
      const row = body.insertRow();
      const index = node('th', '', vector ? 'v' : `F${i + 1}`);
      index.scope = 'row';
      row.append(index);
      return Array.from({length: columnCount}, (_, j) => {
        const td = row.insertCell();
        const independent = augmented && j === columnCount - 1;
        if (independent) td.className = 'ws-independent';
        const input = node('input');
        input.type = 'text';
        input.autocomplete = 'off';
        input.spellcheck = false;
        input.maxLength = 80;
        input.placeholder = '0';
        input.value = data[i]?.[j] ?? '';
        input.setAttribute('aria-label', `${label}, fila ${i + 1}, ${independent ? 'término independiente' : `columna ${j + 1}`}`);
        input.addEventListener('input', () => {
          emptySet = false;
          onChange();
        });
        input.addEventListener('paste', event => {
          const text = event.clipboardData.getData('text');
          if (!/[\t\n;|]/.test(text)) return;
          event.preventDefault();
          applyData(text);
        });
        input.addEventListener('keydown', event => {
          const offset = { ArrowUp: [-1, 0], ArrowDown: [1, 0], Enter: [1, 0] }[event.key];
          if (!offset || event.altKey || event.ctrlKey || event.shiftKey || event.metaKey) return;
          const target = cells[i + offset[0]]?.[j + offset[1]];
          if (target) {
            event.preventDefault();
            target.focus();
            target.select();
          }
        });
        td.append(input);
        return input;
      });
    });
    rowsSelect.value = rowCount;
    colsSelect.value = columnCount - Number(augmented);
    scrolling.replaceChildren(table);
  }

  function raw() { return cells.map(row => row.map(cell => cell.value.trim())); }

  function set(data) {
    emptySet = data === '[]';
    const rows = Array.isArray(data) ? data : emptySet ? [] : parseGrid(data || '');
    if (rows.length) {
      if (rows.length > limit || rows[0].length > limit + Number(augmented) ||
          rows[0].length <= Number(augmented) || rows.some(r => r.length !== rows[0].length) ||
          (vector && rows.length !== 1)) {
        throw new Error(augmented ? 'Pegá una matriz rectangular que incluya la columna b.' : 'Los datos pegados deben tener dimensiones válidas y filas del mismo largo.');
      }
      rowCount = rows.length;
      columnCount = rows[0].length;
    }
    draw(rows);
  }

  function applyData(text) {
    try {
      set(text);
      onChange();
      pastePanel.hidden = true;
      revealPaste.setAttribute('aria-expanded', 'false');
      error.textContent = '';
      cells[0][0].focus();
    } catch (err) {
      pastePanel.hidden = false;
      revealPaste.setAttribute('aria-expanded', 'true');
      error.textContent = err.message;
    }
  }

  function resize() {
    const old = raw();
    const oldColumns = columnCount;
    rowCount = vector ? 1 : Number(rowsSelect.value);
    columnCount = Number(colsSelect.value) + Number(augmented);
    const resized = dimensions(rowCount, columnCount);
    resized.forEach((row, i) => row.forEach((_, j) => {
      if (augmented && j === columnCount - 1) row[j] = old[i]?.[oldColumns - 1] ?? '';
      else if (j < oldColumns - Number(augmented)) row[j] = old[i]?.[j] ?? '';
    }));
    emptySet = false;
    draw(resized);
    onChange();
  }

  rowsSelect.addEventListener('change', resize);
  colsSelect.addEventListener('change', resize);
  revealPaste.addEventListener('click', () => {
    pastePanel.hidden = !pastePanel.hidden;
    revealPaste.setAttribute('aria-expanded', String(!pastePanel.hidden));
    if (!pastePanel.hidden) paste.focus();
  });
  apply.addEventListener('click', () => applyData(paste.value));

  set(initial);
  return {
    element: box,
    set,
    raw,
    value() {
      if (emptySet) return '[]';
      const rows = raw();
      const values = rows.flat();
      if (values.every(value => !value)) return augmented ? rows : '';
      if (values.some(value => !value)) throw new Error(`Completá todas las celdas de ${label}.`);
      return augmented ? rows : rows.map(row => row.join(' ')).join('\n');
    },
    ready() { return !required || raw().flat().every(Boolean); },
  };
}
