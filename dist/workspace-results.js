import { iterationSelection } from './iteration-selection.js';
import { node } from './matrix-input.js';
import { bookControl, bookScene } from './book-scenes.js';
import { addPlot } from './plot.js';
import { printReport, reportSection } from './result-print.js';
import { curveFrames, riemannPlot, sectionPlot } from './integral-visuals.js';
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
  residual: 'Residuo', ultimo_punto: 'Último punto', origen_derivada: 'Origen de la derivada',
  motivo_parada: 'Motivo de parada', tecnica_elegida:'Técnica', metodo_elegido:'Método elegido',
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

function systemResult(out, choices, steps, printing = false) {
  const headings = matrixLabels(out.numero_variables);
  if (out.objetivo === 'escalonada') {
    const panels = [['Forma escalonada', matrixView(out.matriz_escalonada, 'Forma escalonada · Gauss', true, headings)]];
    if (steps?.length) panels.push(['Procedimiento', () => procedureView(steps, null, printing)]);
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

  if (choices.steps && steps?.length) panels.push(['Procedimiento', () => procedureView(steps, null, printing)]);

  if (choices.verify && out.comprobaciones) {
    const proofs = node('div', 'ws-result-stack');
    proofs.append(table(['Ecuación','Ax','b','Coincide'],
      out.comprobaciones.map((row, i) => [`F${i+1}`, row.resultado,row.esperado,row.cumple]), 'Sustitución de la solución particular'));
    if (out.comprobaciones_direcciones?.length) {
      proofs.append(valueView({'Producto Av de cada dirección': out.comprobaciones_direcciones}));
    }
    panels.push(['Comprobación', proofs]);
  }
  return panels;
}

function procedureView(entries, selection, printing = false) {
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
    for (const step of entries.slice(shown,printing ? entries.length : shown+18)) {
      const item = node('li');
      const body = node('div','ws-step-card');
      body.append(node('h3','',step.description));
      if (step.formula) body.append(math(step.formula,step.formula,true));
      if (step.data?.iteracion !== undefined && selection) {
        byIteration.set(step.data.iteracion, item);
        item.addEventListener('click', () => selection.select(step.data.iteracion));
      }
      const {matriz, antes, separador, formula, desarrollo, teorema, ...remainder} = step.data ?? {};
      if (matriz) {
        const split = separador && separador < matriz[0]?.length ? separador : false;
        if (antes) body.append(matrixView(antes, 'Antes', split));
        body.append(matrixView(matriz, antes ? 'Después' : 'Matriz', split));
      }
      if (teorema) {
        const card = node('details', 'ws-step-data ws-theorem-card');
        card.append(node('summary', '', 'Ficha del teorema'), node('h4', '', 'Enunciado'),
          math(teorema.enunciado, teorema.enunciado, true), node('h4', '', 'Hipótesis'),
          node('p', '', teorema.hipotesis), node('h4', '', 'Evidencia'),
          valueView(teorema.evidencia), node('h4', '', 'Conclusión'), node('p', '', teorema.conclusion));
        card.open = printing;
        body.append(card);
      }
      if (Object.keys(remainder).length) {
        const data = node('details','ws-step-data');
        data.append(node('summary','','Ver cálculos y datos de este paso'));
        data.open = printing || (!matriz && !step.formula);
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
  stack.append(list);
  appendSteps();
  if (printing) return stack;
  stack.append(more);
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

function rootColumns(row) {
  return row.a !== undefined
    ? ['k','a','b','xᵣ','f(a)','f(b)','f(xᵣ)','Signo f(a)f(xᵣ)','εₐ (%)','Cota']
    : ['k','xₖ','f(xₖ)',row.derivada_x !== undefined ? 'f′(xₖ)' : 'f(xₖ₋₁)','xₖ₊₁','εₐ (%)','Error absoluto','|f(xₖ₊₁)|'];
}
function rootCells(row) {
  return row.a !== undefined
    ? [row.iteracion,row.a,row.b,row.x_decimal,row.fa,row.fb,row.fx,row.signo_fa_por_fx,row.error_porcentual,row.cota_intervalo]
    : [row.iteracion,row.x_anterior,row.f_anterior_actual,row.derivada_x ?? row.f_anterior,
      row.x_decimal,row.error_porcentual,row.error_aproximado_absoluto,row.residual];
}
function rootGraph(graph, rows, selection) {
  const view = node('div','ws-result-stack');
  const chart = addPlot({...graph, selection, playback:false});
  const explanation = node('div','ws-frame-formula');
  const byIndex = new Map(rows.map(row=>[row.iteracion,row]));
  const byFrame = new Map(graph.cuadros?.map(frame=>[frame.iteracion,frame]));
  selection?.subscribe(index => {
    const row = byIndex.get(index);
    const frame = byFrame.get(index);
    explanation.dataset.iteration = index;
    const summary = [frame?.tipo_recta, frame?.corte_decimal ? 'Corte con el eje x ≈ '+frame.corte_decimal : '',
      frame?.decision].filter(Boolean).join(' · ');
    const essential = row.a !== undefined ? 7 : 5;
    const active = table(rootColumns(row).slice(0,essential),[rootCells(row).slice(0,essential)],'Fila de la iteración '+index);
    active.querySelector('tbody tr').classList.add('ws-iteration-active');
    explanation.replaceChildren(math(frame?.formula ?? row.desarrollo,row.desarrollo,true),active);
    if (summary) explanation.prepend(node('p','ws-muted',summary));
  });
  view.append(chart,explanation);
  view.pausePlayback = chart.pausePlayback;
  return view;
}

function connectRows(grid, selection, indices) {
  const rows = [...grid.querySelectorAll('tbody tr')];
  const key = i => indices?.[i] ?? i;
  rows.forEach((row,i) => {
    row.tabIndex = 0;
    const select = () => selection.select(key(i));
    row.addEventListener('click',select);
    row.addEventListener('keydown',event=>{
      if (!['Enter',' '].includes(event.key)) return;
      event.preventDefault();
      select();
    });
  });
  selection.subscribe(index => rows.forEach((row,i) => {
    const active = key(i) === index;
    row.classList.toggle('ws-iteration-active',active);
    row.setAttribute('aria-current',active ? 'step' : 'false');
  }));
}

function genericResult(response, recalculate, camera, {printing = false, showSteps = true} = {}) {
  const output = response.result;
  const main = node('div', 'ws-result-stack');
  const panels = [['Resultado', main]];
  const {points, parametric, muestras, parametros, tabla, encabezados, formula_latex, series, diagrama_vectores, grafico_raiz, visual_integral, visual_libro, control_libro, ...general} = output;
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
  if (general.metodo === 'newton') general.metodo = 'Newton-Raphson';
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
    const lead = node('div', 'ws-result-lead');
    const stopped = response.status !== 'ok';
    if (stopped) lead.append(node('p', 'ws-feature', 'Último punto calculado'));
    const value = output.aproximacion_decimal;
    const exactDisplay = output.error_redondeo_decimal === '0';
    const sign = exactDisplay ? '=' : '\\approx';
    lead.append(math(`x${sign}${numericTex(value) ?? value}`, `x ${exactDisplay ? '=' : '≈'} ${value}`, true));
    if (stopped && output.residual !== undefined) {
      const residual = numericTex(output.residual);
      lead.append(residual ? math(`|f(x)|=${residual}`, `|f(x)| = ${output.residual}`, true)
        : node('p', 'ws-value', `Residuo: ${output.residual}`));
      const reasons = {
        derivada_nula_o_demasiado_pequena: 'La derivada es cero o demasiado pequeña para dividir.',
        denominador_secante_nulo: 'Las dos ordenadas de la secante coinciden.',
        denominador_falsa_posicion_nulo: 'Los valores en los extremos coinciden a la precisión de trabajo.',
        maximo_de_iteraciones: 'Se alcanzó el máximo de iteraciones.',
        precision_agotada: 'El nuevo punto coincide con el anterior a la precisión de trabajo.',
      };
      if (reasons[output.motivo_parada]) lead.append(node('p', 'ws-muted', reasons[output.motivo_parada]));
    }
    main.append(lead);
  }
  if (control_libro && !printing) main.append(bookControl(control_libro,recalculate));
  if (visual_libro) main.append(bookScene(visual_libro,response,recalculate,camera));
  const seriesTimeline = series?.points?.length && encabezados && tabla?.length === series.points.length
    ? iterationSelection(series.points.map((_,i)=>i),series.points.length-1) : null;
  if (series?.points?.length) {
    const xLabel = seriesTimeline && encabezados[0] === 'Período' ? 'Período' :
      ['iterativos.comparar','libros.markov','libros.svd'].includes(response.operation_id) ? 'k' : 'x';
    main.append(addPlot({...series,sampleTimeline:seriesTimeline,axisLabels:[xLabel, 'Valor']}));
    if (seriesTimeline) {
      const active = node('div','ws-frame-formula');
      seriesTimeline.subscribe(index => active.replaceChildren(table(encabezados,[tabla[index]],'Datos de la muestra')));
      main.append(active);
    }
  }
  const indices = grafico_raiz?.iteraciones?.map(([index]) => index);
  const selection = indices?.length ? iterationSelection(indices) : null;
  if (grafico_raiz?.points?.length) panels.push(['Gráfica', () => rootGraph(grafico_raiz,tabla,selection)]);
  if (diagrama_vectores?.length) main.append(addPlot({diagram:diagrama_vectores}));
  if (formula_latex) {
    main.append(math(formula_latex, formula_latex, true));
    if (output.primitiva) delete general.primitiva;
  }
  if (visual_integral?.tipo === 'riemann') main.append(riemannPlot(visual_integral));
  if (visual_integral?.tipo === 'seccion') main.append(sectionPlot(visual_integral));
  if (['area','tangente'].includes(visual_integral?.tipo)) main.append(curveFrames(visual_integral));
  if (points?.length) {
    main.append(addPlot({points, parametric, parametros}), table(parametric ? ['t', 'x(t)', 'y(t)'] : ['x','f(x)'],
      muestras.map(row => parametric ? row : row.slice(1)), 'Puntos de referencia'));
  }
  if (response.operation_id === 'calculo.derivar' && response.metadata?.formulas_derivada) {
    for (const {latex, texto} of response.metadata.formulas_derivada) {
      main.append(latex ? math(latex, texto, true) : node('p', 'ws-value', texto));
    }
  } else if (Object.keys(general).length) main.append(valueView(general));
  if (tabla?.length) panels.push([encabezados ? 'Tabla' : 'Iteraciones', () => {
    if (encabezados) {
      const grid = table(encabezados,tabla);
      if (seriesTimeline) connectRows(grid,seriesTimeline);
      return grid;
    }
    const first = tabla[0];
    const body = node('div','ws-result-stack');
    if (first.x_decimal !== undefined) {
      const formatDecimal = value => {
        if (value == null) return null;
        const number = Number(value);
        if (!printing || !Number.isFinite(number)) return String(value);
        const magnitude = Math.abs(number);
        return magnitude !== 0 && (magnitude < .01 || magnitude >= 1e5)
          ? number.toExponential(4) : String(Number(number.toPrecision(7)));
      };
      const iterations = table(rootColumns(first),tabla.map(row=>rootCells(row).map(formatDecimal)));
      body.append(iterations);
      if (selection) connectRows(iterations,selection,tabla.map(row=>row.iteracion));
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
    if (printing) {
      if (!showSteps || !response.steps?.length) {
        exact.open = true;
        exact.append(valueView(tabla));
        body.append(exact);
      }
    } else body.append(exact);
    return body;
  }]);
  if (showSteps && response.steps?.length) panels.push(['Procedimiento', () => procedureView(response.steps, selection, printing)]);
  if (selection) panels.selection = selection;
  if (response.verification && Object.keys(response.verification).length) {
    panels.push(['Comprobación', valueView(response.verification)]);
  }
  return panels;
}

function summaryCards(response) {
  const out = response.result;
  const cards = node('div','ws-summary-cards');
  const items = [
    ['Clasificación', out.clasificacion], ['Método', out.metodo_elegido ?? out.tecnica_elegida],
    ['Aproximación', out.aproximacion_decimal], ['Iteraciones', out.iteraciones],
    ['Residuo', out.residual == null ? null : Number(out.residual).toPrecision(5)],
    ['Rango de A', out.rango_A], ['Rango de [A | b]', out.rango_aumentada],
    ['Incógnitas', out.incognitas ?? out.numero_variables],
    ['Dimensión del dominio', out.dimension_dominio], ['Nulidad', out.nulidad],
    ['Valor', out.valor], ['Primitiva', out.primitiva], ['En el dominio', typeof out.dominio === 'string' ? out.dominio : null],
    ['Comprobación', typeof response.verification?.passed === 'boolean'
      ? (response.verification.passed ? 'Verificada' : 'Revisar') : null],
  ].filter(([,value]) => value != null && value !== 'NaN').slice(0,4);
  if (!items.length) return null;
  for (const [label,value] of items) {
    const card = node('article','ws-summary-card');
    card.append(node('h3','',label),label === 'Primitiva' && out.formula_latex
      ? math(out.formula_latex,value) : valueView(value));
    cards.append(card);
  }
  return cards;
}

function exportResult(target, response, original, camera, report) {
  const content = [];
  const cards = summaryCards(response);
  if (cards) content.push(cards);
  const messages = [...target.querySelectorAll(':scope > :is(.ws-warning,.result-error)')];
  content.push(...messages.map(message => message.cloneNode(true)));
  if (Object.keys(report.input).length) content.push(reportSection('Datos del ejercicio',valueView(report.input)));
  const panels = original
    ? systemResult(response.result,{ranks:true,solution:true,forms:true,steps:true,verify:true},response.steps,true)
    : genericResult(response, () => {}, {...camera}, {printing:true});
  for (const [name, build] of panels) {
    const view = typeof build === 'function' ? build() : build;
    const current = name === 'Gráfica' && target.querySelector('#ws-result-content canvas');
    if (current) {
      const image = node('img','pdf-graph');
      image.alt = 'Gráfica en el momento de exportar';
      try {
        const snapshot = node('canvas');
        snapshot.width = current.width;
        snapshot.height = current.height;
        const ctx = snapshot.getContext('2d');
        ctx.fillStyle = getComputedStyle(current).backgroundColor;
        ctx.fillRect(0,0,snapshot.width,snapshot.height);
        ctx.drawImage(current,0,0);
        image.src = snapshot.toDataURL('image/png');
      }
      catch { /* El gráfico reconstruido queda disponible. */ }
      content.push(reportSection(name, image.src ? image : view));
    } else content.push(reportSection(name,view));
  }
  if (original && response.verification && Object.keys(response.verification).length) {
    content.push(reportSection('Verificación del cálculo', valueView(response.verification)));
  }
  return printReport(report.title,content);
}

function pauseGraphs(content) {
  content?.firstElementChild?.pausePlayback?.();
  content?.querySelectorAll('.ws-graph-controls').forEach(controls=>controls.pausePlayback?.());
}

export function renderResult(target, response, choices, originalSystem, onEdit, recalculate, camera, report) {
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
    pauseGraphs(target.querySelector('#ws-result-content'));
    onEdit();
  });
  actions.append(edit);
  header.append(heading, actions);
  target.append(header);
  if (response.result?.expresion && response.operation_id !== 'calculo.derivar') {
    const expression = node('p','ws-active-expression');
    expression.append(node('strong','','Función '),node('code','',response.result.expresion));
    if (response.result.derivada) {
      const derivative = response.metadata?.derivada_latex;
      expression.append(node('strong', '', ' Derivada '),
        derivative ? math(derivative, response.result.derivada) : node('code', '', response.result.derivada));
    }
    target.append(expression);
  }
  if (response.status !== 'ok' && !originalSystem) {
    const status = ({iteration_limit:'Máximo de iteraciones alcanzado', stagnated:'El método se estancó',
      infinite:'Infinitas soluciones', inconsistent:'Sistema incompatible', not_applicable:'Método no aplicable',
      cycle_detected:'Se detectó un ciclo', domain_error:'Evaluación fuera del dominio', breakdown:'El método se detuvo', singular:'Matriz singular',
    })[response.status];
    if (status) target.append(node('p','ws-warning',status));
  }
  if (response.error) target.append(node('p', 'result-error', response.error.message));
  for (const warning of response.warnings ?? []) target.append(node('p', 'ws-warning', isScalar(warning) ? scalar(warning) : warning.message ?? JSON.stringify(warning)));
  if (!response.result) return;
  const cards = summaryCards(response);
  if (cards) target.append(cards);
  if (report) {
    const button = node('button','secondary','Exportar PDF');
    button.type = 'button';
    button.addEventListener('click', () => exportResult(target,response,originalSystem,camera,report));
    actions.append(button);
  }
  const panels = originalSystem ? systemResult(response.result, choices, response.steps) : genericResult(response, recalculate, camera, {showSteps:choices.steps});
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
    pauseGraphs(content);
    content.replaceChildren(panelContent(i));
    content.querySelectorAll("canvas.plot, canvas.ws-book-canvas").forEach(canvas => canvas.redrawPlot?.());
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
