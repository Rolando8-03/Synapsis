import { iterationSelection } from './iteration-selection.js';
import { node } from './matrix-input.js';
import { addPlot } from './plot.js';
import { math, matrixFormula, numericTex, vectorFormula } from './math-format.js';

const LABELS = {
  matrix: 'Matriz resultante', tabla: 'Tabla de iteraciones', rango_A: 'Rango de A',
  rango_aumentada: 'Rango de [A | b]', matriz_rref: 'Forma escalonada reducida',
  matriz_escalonada: 'Forma escalonada', valor: 'Valor', representacion: 'Representación',
  paso: 'Paso', cota_garantizada: 'Cota garantizada', passed: 'Verificación',
  aproximacion_decimal: 'Aproximación decimal', norma_residual: 'Norma del residual',
  verificada: 'Verificación', gauss_jordan: 'Gauss-Jordan', exacta: 'Conversión exacta',
  combinacion: 'Combinación lineal', transformacion: 'Transformación', ecuacion: 'Ecuación',
  valor_funcion: 'Valor de f(x)', pivotes:'Columnas pivote', rref:'Forma escalonada reducida',
  matriz_aumentada:'Matriz aumentada [A | b]', dimension:'Dimensión', incognitas:'Incógnitas',
  clasificacion:'Clasificación', nulidad:'Nulidad', nucleo:'Base del núcleo',
  base_imagen:'Base de la imagen', es_subespacio:'Es subespacio', metodo:'Método',
  error_truncamiento:'Error de truncamiento', error_redondeo:'Error de redondeo', valor_decimal: 'Valor decimal', A: 'A', B: 'B', U: 'U', L: 'L', P: 'P',
};

function title(key) {
  if (Object.hasOwn(LABELS, key)) return LABELS[key];
  const word = key.replaceAll('_',' ');
  return word.charAt(0).toUpperCase() + word.slice(1);
}
const numericFormat = new Intl.NumberFormat('es-NI', { maximumSignificantDigits: 9, useGrouping: false });
function scalar(value) {
  if (value === null || value === undefined) return '—';
  if (typeof value === 'boolean') return value ? 'Sí' : 'No';
  if (typeof value === 'number') return numericFormat.format(value);
  return String(value);
}
function isScalar(value) { return value === null || typeof value !== 'object'; }

const headerFormulas = {
  'xᵣ': 'x_r', 'xₖ': 'x_k', 'xₖ₊₁': 'x_{k+1}', 'f(xᵣ)': 'f(x_r)', 'f′(xₖ)': "f'(x_k)",
  'f(xₖ)': 'f(x_k)', 'f(xₖ₋₁)': 'f(x_{k-1})', 'εₐ (%)': '\\varepsilon_a\\,(\\%)',
  '|f(xₖ₊₁)|': '|f(x_{k+1})|', '‖Ax−b‖': '\\lVert Ax-b\\rVert',
  'Ax': 'Ax', 'f(x)': 'f(x)', 'f(a)': 'f(a)', 'f(b)': 'f(b)',
};
function headerContent(heading) {
  const tex = headerFormulas[heading] ?? (/^x\d+$/.test(heading) ? `x_{${heading.slice(1)}}` : null);
  return tex ? math(tex, heading) : document.createTextNode(heading);
}

function table(headings, rows, caption = '', independent = false, pivots = []) {
  const scroll = node('div', 'ws-table-scroll');
  const data = node('table', `ws-result-table${independent ? ' ws-augmented' : ''}`);
  if (caption) data.append(node('caption', '', caption));
  if (headings?.length) {
    const row = data.createTHead().insertRow();
    for (const heading of headings) {
      const th = node('th');
      th.append(headerContent(heading));
      th.scope = 'col';
      row.append(th);
    }
  }
  const split = independent === true ? rows[0]?.length - 1 : independent;
  if (independent) data.classList.add('ws-augmented');
  for (const header of data.tHead?.rows[0].cells ?? []) {
    if (header.cellIndex === split) header.classList.add('ws-split');
  }
  const pivotCells = new Set(pivots.map(([row, col]) => `${row},${col}`));
  const body = data.createTBody();
  for (const [index, row] of rows.entries()) {
    const rendered = body.insertRow();
    for (const value of row) {
      const cell = rendered.insertCell();
      if (cell.cellIndex === split) cell.classList.add('ws-split');
      if (pivotCells.has(`${index},${cell.cellIndex}`)) {
        cell.classList.add('ws-pivot');
        cell.append(node('span', 'visually-hidden', 'Pivote '));
      }
      if (value == null || typeof value === 'boolean') cell.append(document.createTextNode(scalar(value)));
      else if (isScalar(value)) {
        const exact = typeof value === 'number' ? String(value) : value;
        const tex = numericTex(exact);
        cell.append(tex ? math(tex, exact) : document.createTextNode(scalar(value)));
      } else cell.append(valueView(value));
    }
  }
  scroll.append(data);
  scroll.tabIndex = 0;
  scroll.setAttribute('aria-label', caption || 'Tabla de resultados');
  return scroll;
}

function matrixView(rows, caption = '', independent = false, headings = null, pivots = []) {
  return matrixFormula(rows, caption, independent, pivots) ?? table(headings ?? (independent === true ? matrixLabels(rows[0].length - 1) : null), rows, caption, independent, pivots);
}

function valueView(value) {
  if (isScalar(value)) {
    const tex = typeof value === 'string' ? numericTex(value) : null;
    return tex?.startsWith('\\frac') || tex?.startsWith('-\\frac')
      ? math(tex, value) : node('span', 'ws-value', scalar(value));
  }
  if (Array.isArray(value)) {
    if (!value.length) return node('span', 'ws-value', '∅');
    if (value.every(x => Array.isArray(x) && x.every(isScalar))) return matrixView(value);
    if (value.every(isScalar)) return vectorFormula(value) ?? node('span', 'ws-value', `( ${value.map(scalar).join(' · ')} )`);
    if (value.every(x => x && !Array.isArray(x) && typeof x === 'object')) {
      const keys = [...new Set(value.flatMap(Object.keys))];
      return table(keys.map(title), value.map(row => keys.map(key => row[key] ?? null)));
    }
    const list = node('ol', 'ws-tree-list');
    for (const item of value) {
      const entry = node('li');
      entry.append(valueView(item));
      list.append(entry);
    }
    return list;
  }
  const list = node('dl', 'ws-data-list');
  for (const [key, entry] of Object.entries(value)) {
    if (['formula_latex', 'latex_solucion'].includes(key)) continue;
    const term = node('div');
    const valueNode = node('dd');
    if (key === 'formula' && typeof entry === 'string') valueNode.append(math(entry, entry, true));
    else if (['pivotes','pivot_columns'].includes(key) && Array.isArray(entry) && entry.every(Number.isInteger)) {
      valueNode.append(node('span','ws-value',entry.length ? entry.map(i => i+1).join(', ') : 'Ninguna'));
    } else if (['matriz_aumentada','forma_reducida'].includes(key) && Array.isArray(entry)) {
      valueNode.append(matrixView(entry, '', true));
    } else valueNode.append(valueView(entry));
    term.append(node('dt', '', title(key)), valueNode);
    list.append(term);
  }
  return list;
}

function matrixLabels(columns) {
  return [...Array.from({length: columns}, (_, i) => `x${i + 1}`), 'b'];
}

function systemResult(out, choices, steps) {
  const headings = matrixLabels(out.numero_variables);
  if (out.objetivo === 'escalonada') {
    const panels = [['Forma escalonada', matrixView(out.matriz_escalonada, 'Forma escalonada · Gauss', true, headings)]];
    if (steps?.length) panels.push(['Procedimiento', () => procedureView(steps)]);
    return panels;
  }
  const summary = node('div', 'ws-result-stack');
  summary.append(node('p', 'ws-feature', out.clasificacion), node('p', 'ws-muted', out.conclusion));
  const panels = [['Resumen', summary]];

  if (choices.ranks) {
    const ranks = {
      rango_A: out.rango_A, rango_aumentada: out.rango_aumentada, incógnitas: out.numero_variables,
      'Naturaleza del sistema': out.naturaleza_sistema,
      'Columnas pivote': out.columnas_pivote.map(i => `x${i+1}`),
      'Variables libres': out.variables_libres.map(i => `x${i+1}`),
    };
    const details = valueView(ranks);
    details.classList.add('ws-rank-grid');
    summary.append(details);
    if (out.fila_contradiccion_datos) {
      summary.append(table(headings, [out.fila_contradiccion_datos], `Contradicción en F${out.fila_contradiccion + 1}`, true));
    }
  }

  if (choices.solution && out.expresiones_rref) {
    const content = node('div', 'ws-result-stack');
    const variables = out.expresiones_rref.map(({ constante, terminos }, i) => {
      const parts = Object.entries(terminos).filter(([, coefficient]) => coefficient !== '0');
      const expression = [constante, ...parts.map(([v, coef]) => `${coef.startsWith('-') ? '−' : '+'} ${coef.replace(/^-/, '')}·t${out.variables_libres.indexOf(Number(v)) + 1}`)];
      return [`x${i+1}`, expression.join(' ')];
    });
    if (out.latex_solucion) {
      const formula = math(out.latex_solucion, variables.map(row => row.join(' = ')).join('\n'), true);
      formula.classList.add('ws-result-lead');
      content.append(formula);
    } else content.append(table(['Variable', 'Valor exacto'], variables, 'Sistema resuelto'));
    if (out.variables_libres.length) {
      content.append(valueView({
        'Parámetros reales': out.variables_libres.map((v, i) => `t${i+1} = x${v+1}`),
        'Solución particular': out.solucion_particular,
        'Direcciones del espacio de soluciones': out.direcciones,
      }));
    }
    panels.push(['Solución', content]);
  }

  if (choices.forms) {
    const forms = node('div', 'ws-result-stack');
    forms.append(matrixView(out.matriz_inicial, 'Matriz aumentada original [A | b]', true, headings),
      matrixView(out.matriz_escalonada, 'Forma escalonada · Gauss', true, headings),
      matrixView(out.matriz_rref, 'Forma reducida · Gauss-Jordan · pivotes recuadrados', true, headings, out.posiciones_pivote));
    panels.push(['Matrices', forms]);
  }

  if (choices.steps && steps?.length) panels.push(['Procedimiento', () => procedureView(steps)]);

  if (choices.verify && out.comprobaciones) {
    panels.push(['Comprobación', table(['Ecuación','Ax','b','Coincide'],
      out.comprobaciones.map((row, i) => [`F${i+1}`, row.resultado,row.esperado,row.cumple]), 'Sustitución de la solución particular')]);
  }
  return panels;
}

function procedureView(entries, selection) {
  const stack = node('div','ws-result-stack');
  const list = node('ol','ws-step-list ws-detailed-steps');
  const more = node('button','secondary','Ver los siguientes pasos');
  more.type = 'button';
  let shown = 0;
  const byIteration = new Map();
  let active;
  let showIteration;
  function appendSteps(focus = false) {
    const added = document.createDocumentFragment();
    const start = shown;
    for (const step of entries.slice(shown,shown+18)) {
      const item = node('li');
      const body = node('div','ws-step-card');
      body.append(node('h3','',step.description));
      if (step.formula) body.append(math(step.formula,step.formula,true));
      if (step.data?.iteracion !== undefined && selection) {
        byIteration.set(step.data.iteracion, item);
        item.addEventListener('click', () => selection.select(step.data.iteracion));
      }
      const {matriz, antes, separador, formula, desarrollo, ...remainder} = step.data ?? {};
      if (matriz) {
        const split = separador && separador < matriz[0]?.length ? separador : false;
        if (antes) body.append(matrixView(antes, 'Antes', split));
        body.append(matrixView(matriz, antes ? 'Después' : 'Matriz', split));
      }
      if (Object.keys(remainder).length) {
        const data = node('details','ws-step-data');
        data.append(node('summary','','Ver cálculos y datos de este paso'));
        data.open = !matriz && !step.formula;
        if (data.open) data.append(valueView(remainder));
        data.addEventListener('toggle', () => {
          if (data.open && data.childElementCount === 1) data.append(valueView(remainder));
        });
        body.append(data);
      }
      item.append(body);
      added.append(item);
      shown++;
    }
    list.append(added);
    more.hidden = shown >= entries.length;
    if (start && focus) {
      const item = list.children[start];
      item.tabIndex = -1;
      item.focus();
    }
  }
  more.addEventListener('click', () => appendSteps(true));
  stack.append(list,more);
  appendSteps();
  if (selection) selection.subscribe(index => {
    if (!entries.some(step => step.data?.iteracion === index)) return;
    while (!byIteration.has(index) && shown < entries.length) appendSteps();
    active?.classList.remove('ws-iteration-active');
    active = byIteration.get(index);
    active?.classList.add('ws-iteration-active');
    showIteration?.(index);
  });
  const controls = node('div', 'ws-playback');
  const mode = node('button', 'secondary', 'Ver paso a paso');
  const previous = node('button', 'secondary', 'Anterior');
  const next = node('button', 'secondary', 'Siguiente');
  const play = node('button', 'secondary', 'Reproducir');
  const counter = node('span', 'ws-muted');
  counter.setAttribute('role', 'status');
  for (const button of [mode, previous, next, play]) button.type = 'button';
  controls.append(mode, previous, next, play, counter);
  stack.prepend(controls);
  let index = 0;
  let single = false;
  let timer = null;
  let synchronizing = false;

  function pause() {
    clearInterval(timer);
    timer = null;
    play.textContent = 'Reproducir';
  }

  function update() {
    while (single && index >= shown) appendSteps();
    for (const item of list.children) item.hidden = single && item !== list.children[index];
    list.start = single ? index + 1 : 1;
    more.hidden = single || shown >= entries.length;
    for (const control of [previous, next, play, counter]) control.hidden = !single;
    previous.disabled = index === 0;
    next.disabled = play.disabled = index === entries.length - 1;
    counter.textContent = `Paso ${index + 1} de ${entries.length}`;
    if (next.disabled) pause();
  }

  function move(offset) {
    index = Math.max(0, Math.min(entries.length - 1, index + offset));
    const iteration = entries[index].data?.iteracion;
    if (iteration !== undefined && selection) {
      synchronizing = true;
      selection.select(iteration);
      synchronizing = false;
    }
    update();
  }

  showIteration = iteration => {
    if (synchronizing) return;
    index = entries.findIndex(step => step.data?.iteracion === iteration);
    pause();
    update();
  };
  if (active) index = [...list.children].indexOf(active);
  mode.addEventListener('click', () => {
    pause();
    single = !single;
    mode.textContent = single ? 'Ver lista de pasos' : 'Ver paso a paso';
    update();
  });
  previous.addEventListener('click', () => { pause(); move(-1); });
  next.addEventListener('click', () => { pause(); move(1); });
  play.addEventListener('click', () => {
    if (timer !== null) { pause(); return; }
    play.textContent = 'Pausar';
    timer = setInterval(() => {
      if (!stack.isConnected || stack.closest('[hidden]')) { pause(); return; }
      move(1);
    }, 1300);
  });
  controls.addEventListener('keydown', event => {
    if (!single || !['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
    event.preventDefault();
    pause();
    move(event.key === 'ArrowLeft' ? -1 : 1);
  });
  stack.pausePlayback = pause;
  update();
  return stack;
}

function genericResult(response) {
  const output = response.result;
  const main = node('div', 'ws-result-stack');
  const panels = [['Resultado', main]];
  const {points, parametric, muestras, tabla, encabezados, formula_latex, series, diagrama_vectores, grafico_raiz, ...general} = output;
  if (response.operation_id === 'sistemas.resolver') {
    general.metodo = output.metodo === 'gauss' ? 'Gauss' : 'Gauss-Jordan';
    main.append(matrixView(output.matrix, `[A | b] después de ${general.metodo}`, true, matrixLabels(output.dimension_dominio)));
    delete general.matrix;
    if (output.certificado) {
      general.certificado = {...output.certificado, fila: output.certificado.fila + 1};
      delete general.variables_libres;
    } else {
      general.variables_libres = output.variables_libres.map(i => `x${i + 1}`);
    }
  }
  if (output.convencion && output.L && output.U) {
    main.append(math(output.convencion, output.convencion, true));
    const factors = node('div','ws-factors');
    for (const key of output.convencion === 'PA=LU' ? ['P','L','U'] : ['L','U']) {
      factors.append(matrixView(output[key], key));
    }
    main.append(factors);
    for (const key of ['P','L','U','convencion']) delete general[key];
  }
  if (output.aproximacion_decimal) {
    const lead = math(`x\\approx${numericTex(output.aproximacion_decimal) ?? output.aproximacion_decimal}`,
      `x ≈ ${output.aproximacion_decimal}`, true);
    lead.classList.add('ws-result-lead');
    main.append(lead);
  }
  if (series?.points?.length) main.append(addPlot(series));
  const indices = grafico_raiz?.iteraciones?.map(([index]) => index);
  const selection = indices?.length ? iterationSelection(indices) : null;
  if (grafico_raiz?.points?.length) panels.push(['Gráfica', () => addPlot({...grafico_raiz, selection})]);
  if (diagrama_vectores?.length) main.append(addPlot({diagram:diagrama_vectores}));
  if (formula_latex) main.append(math(formula_latex, formula_latex, true));
  if (points?.length) {
    main.append(addPlot({points, parametric}), table(parametric ? ['t', 'x(t)', 'y(t)'] : ['x','f(x)'],
      muestras.map(row => parametric ? row : row.slice(1)), 'Puntos de referencia'));
  }
  if (response.operation_id === 'calculo.derivar' && response.metadata?.formulas_derivada) {
    for (const {latex, texto} of response.metadata.formulas_derivada) {
      main.append(latex ? math(latex, texto, true) : node('p', 'ws-value', texto));
    }
  } else if (Object.keys(general).length) main.append(valueView(general));
  if (tabla?.length) panels.push([encabezados ? 'Tabla' : 'Iteraciones', () => {
    if (encabezados) return table(encabezados, tabla);
    const first = tabla[0];
    const body = node('div','ws-result-stack');
    if (first.x_decimal !== undefined) {
      const bracket = first.a !== undefined;
      const formatDecimal = value => value == null ? null : String(value);
      const cols = bracket
        ? ['k','a','b','xᵣ','f(a)','f(b)','f(xᵣ)','Signo f(a)f(xᵣ)','εₐ (%)','Cota']
        : ['k','xₖ','f(xₖ)',first.derivada_x !== undefined ? 'f′(xₖ)' : 'f(xₖ₋₁)','xₖ₊₁','εₐ (%)','Error absoluto','|f(xₖ₊₁)|'];
      const iterations = table(cols, tabla.map(row => (bracket
        ? [row.iteracion,row.a,row.b,row.x_decimal,row.fa,row.fb,row.fx,row.signo_fa_por_fx,row.error_porcentual,row.cota_intervalo]
        : [row.iteracion,row.x_anterior,row.f_anterior_actual,row.derivada_x ?? row.f_anterior,
          row.x_decimal,row.error_porcentual,row.error_aproximado_absoluto,row.residual]).map(formatDecimal)));
      body.append(iterations);
      if (selection) {
        const rows = [...iterations.querySelectorAll('tbody tr')];
        rows.forEach((row, i) => row.addEventListener('click', () => selection.select(tabla[i].iteracion)));
        selection.subscribe(index => rows.forEach((row, i) => row.classList.toggle('ws-iteration-active', tabla[i].iteracion === index)));
      }
    } else if (first.vector_decimal) {
      body.append(table(['k','xₖ · aproximado','‖Ax−b‖','Cambio absoluto','Cambio relativo','Error por componente (%)'],
        tabla.map(row => [row.iteracion,row.vector_decimal,row.norma_residual_decimal,
          row.error_aproximado_absoluto,row.error_aproximado_relativo,row.error_por_componente_pct])));
    } else return valueView(tabla);
    const exact = node('details');
    exact.append(node('summary','','Ver todos los datos exactos'));
    exact.addEventListener('toggle', () => {
      if (exact.open && exact.childElementCount === 1) exact.append(valueView(tabla));
    });
    body.append(exact);
    return body;
  }]);
  if (response.steps?.length) panels.push(['Procedimiento', () => procedureView(response.steps, selection)]);
  if (selection) panels.selection = selection;
  if (response.verification && Object.keys(response.verification).length) {
    panels.push(['Comprobación', valueView(response.verification)]);
  }
  return panels;
}

export function renderResult(target, response, choices, originalSystem, onEdit) {
  const selectedTab = target.dataset.selectedTab;
  target.replaceChildren();
  const header = node('div', 'ws-panel-heading');
  const heading = node('h2', '', 'Resultados');
  heading.id = 'ws-result-title';
  heading.tabIndex = -1;
  const actions = node('div','ws-result-actions');
  const edit = node('button','secondary','Editar datos');
  edit.type = 'button';
  edit.addEventListener('click', () => {
    target.querySelector('#ws-result-content')?.firstElementChild?.pausePlayback?.();
    onEdit();
  });
  actions.append(edit);
  header.append(heading, actions);
  target.append(header);
  if (response.result?.expresion && response.operation_id !== 'calculo.derivar') {
    const expression = node('p','ws-active-expression');
    expression.append(node('strong','','Función '),node('code','',response.result.expresion));
    if (response.result.derivada) expression.append(node('strong','',' Derivada '),node('code','',response.result.derivada));
    target.append(expression);
  }
  if (response.status !== 'ok' && !originalSystem) {
    const status = ({iteration_limit:'Máximo de iteraciones alcanzado', stagnated:'El método se estancó',
      infinite:'Infinitas soluciones', inconsistent:'Sistema incompatible', not_applicable:'Método no aplicable',
      cycle_detected:'Se detectó un ciclo', breakdown:'El método se detuvo', singular:'Matriz singular',
    })[response.status];
    if (status) target.append(node('p','ws-warning',status));
  }
  if (response.error) target.append(node('p', 'result-error', response.error.message));
  for (const warning of response.warnings ?? []) target.append(node('p', 'ws-warning', isScalar(warning) ? scalar(warning) : warning.message ?? JSON.stringify(warning)));
  if (!response.result) return;
  const panels = originalSystem ? systemResult(response.result, choices, response.steps) : genericResult(response);
  const results = node('div', 'ws-result-body');
  const tabs = node('div', 'ws-result-tabs');
  tabs.setAttribute('role', 'tablist');
  tabs.setAttribute('aria-label', 'Vistas del resultado');
  const content = node('div', 'ws-result-content');
  content.id = 'ws-result-content';
  content.setAttribute('role', 'tabpanel');
  content.tabIndex = 0;
  const panelContent = i => {
    if (typeof panels[i][1] === 'function') panels[i][1] = panels[i][1]();
    return panels[i][1];
  };
  const buttons = panels.map(([label], i) => {
    const button = node('button', '', label);
    button.type = 'button';
    button.id = `ws-result-tab-${i}`;
    button.setAttribute('role', 'tab');
    button.setAttribute('aria-controls', content.id);
    return button;
  });
  const select = i => {
    target.dataset.selectedTab = panels[i][0];
    buttons.forEach((button, index) => {
      button.setAttribute('aria-selected', String(i === index));
      button.tabIndex = i === index ? 0 : -1;
    });
    content.setAttribute('aria-labelledby', buttons[i].id);
    content.firstElementChild?.pausePlayback?.();
    content.replaceChildren(panelContent(i));
    content.querySelectorAll("canvas.plot").forEach(canvas => canvas.redrawPlot?.());
  };
  buttons.forEach((button, i) => {
    button.addEventListener('click', () => select(i));
    button.addEventListener('keydown', event => {
      const index = {ArrowRight:(i + 1) % buttons.length, ArrowLeft:(i - 1 + buttons.length) % buttons.length, Home:0, End:buttons.length-1}[event.key];
      if (index === undefined) return;
      event.preventDefault();
      select(index);
      buttons[index].focus();
    });
    tabs.append(button);
  });
  results.append(tabs);
  if (panels.selection) results.append(panels.selection.controls());
  results.append(content);
  target.append(results);
  const initial = selectedTab || (originalSystem && choices.solution ? 'Solución' : 'Resultado');
  select(Math.max(0, panels.findIndex(([label]) => label === initial)));
  if (navigator.clipboard?.writeText) {
    const copy = node('button','secondary','Copiar pestaña');
    copy.type = 'button';
    copy.addEventListener('click', async () => {
      try {
        const clone = content.cloneNode(true);
        clone.querySelectorAll('[hidden]').forEach(item => item.remove());
        clone.querySelectorAll('[data-plain]').forEach(item => {
          const separator = item.closest('td, th') ? '' : '\n';
          item.replaceWith(document.createTextNode(item.dataset.plain + separator));
        });
        clone.querySelectorAll('tr').forEach(row => {
          row.replaceWith(node('div','', [...row.cells].map(cell => {
            cell.querySelector('.visually-hidden')?.remove();
            return cell.textContent;
          }).join('\t') + '\n'));
        });
        await navigator.clipboard.writeText(clone.innerText || clone.textContent.trim());
        copy.textContent = 'Copiado';
      } catch {
        copy.textContent = 'No se pudo copiar';
      }
    });
    actions.append(copy);
  }
}
