import { node } from './matrix-input.js';
import { addPlot } from './plot.js';
import { math, matrixFormula, numericTex } from './math-format.js';

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

function table(headings, rows, caption = '', independent = false) {
  const scroll = node('div', 'ws-table-scroll');
  const data = node('table', `ws-result-table${independent ? ' ws-augmented' : ''}`);
  if (caption) data.append(node('caption', '', caption));
  if (headings?.length) {
    const row = data.createTHead().insertRow();
    for (const heading of headings) {
      const th = node('th', '', heading);
      th.scope = 'col';
      row.append(th);
    }
  }
  const body = data.createTBody();
  for (const row of rows) {
    const rendered = body.insertRow();
    for (const value of row) {
      const cell = rendered.insertCell();
      if (Array.isArray(value) && value.every(isScalar)) cell.textContent = value.map(scalar).join(' · ');
      else if (isScalar(value)) cell.textContent = scalar(value);
      else cell.append(valueView(value));
    }
  }
  scroll.append(data);
  scroll.tabIndex = 0;
  scroll.setAttribute('aria-label', caption || 'Tabla de resultados');
  return scroll;
}

function matrixView(rows, caption = '', independent = false, headings = null, pivots = []) {
  return matrixFormula(rows, caption, independent, pivots) ?? table(headings, rows, caption, independent);
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
    if (value.every(isScalar)) return node('span', 'ws-value', `( ${value.map(scalar).join(' · ')} )`);
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

function systemResult(out, choices) {
  const headings = matrixLabels(out.numero_variables);
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

  if (choices.steps && out.pasos_gauss) panels.push(['Procedimiento', () => {
    const trace = node('div', 'ws-result-stack');
    for (const [name, steps] of [['Eliminación de Gauss',out.pasos_gauss], ['Reducción de Gauss-Jordan',out.pasos_jordan]]) {
      trace.append(node('h3', '', name));
      const list = node('ol', 'ws-step-list');
      for (const step of steps ?? []) {
        const item = node('li');
        item.append(node('p', '', step.titulo));
        if (step.formula_latex) item.append(math(step.formula_latex, step.formula_latex, true));
        if (step.mostrar_matriz) item.append(matrixView(step.matriz, '', true, headings));
        list.append(item);
      }
      trace.append(list);
    }
    if (out.pasos_sustitucion?.length) {
      trace.append(node('h3','','Sustitución regresiva'));
      for (const step of out.pasos_sustitucion) {
        const variable = `x${step.variable + 1}`;
        const {constante, terminos} = step.expresion;
        const terms = Object.entries(terminos).filter(([, coef]) => coef !== '0').map(([key,coef]) => `${coef}·x${Number(key)+1}`);
        trace.append(node('p','ws-value', `${variable} = ${[constante, ...terms].join(' + ').replaceAll('+ -','− ')}`));
      }
    }
    return trace;
  }]);

  if (choices.verify && out.comprobaciones) {
    panels.push(['Comprobación', table(['Ecuación','Ax','b','Coincide'],
      out.comprobaciones.map((row, i) => [`F${i+1}`, row.resultado,row.esperado,row.cumple]), 'Sustitución de la solución particular')]);
  }
  return panels;
}

function procedureView(entries) {
  const stack = node('div','ws-result-stack');
  const list = node('ol','ws-step-list ws-detailed-steps');
  const more = node('button','secondary','Ver los siguientes pasos');
  more.type = 'button';
  let shown = 0;
  function appendSteps() {
    const added = document.createDocumentFragment();
    const start = shown;
    for (const step of entries.slice(shown,shown+18)) {
      const item = node('li');
      const body = node('div','ws-step-card');
      body.append(node('h3','',step.description));
      if (step.formula) body.append(math(step.formula,step.formula,true));
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
    if (start) {
      const item = list.children[start];
      item.tabIndex = -1;
      item.focus();
    }
  }
  more.addEventListener('click',appendSteps);
  stack.append(list,more);
  appendSteps();
  return stack;
}

function genericResult(response) {
  const output = response.result;
  const main = node('div', 'ws-result-stack');
  const panels = [['Resultado', main]];
  const {points, parametric, muestras, tabla, encabezados, formula_latex, series, diagrama_vectores, grafico_raiz, ...general} = output;
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
  if (grafico_raiz?.points?.length) panels.push(['Gráfica', () => addPlot(grafico_raiz)]);
  if (diagrama_vectores?.length) main.append(addPlot({diagram:diagrama_vectores}));
  if (formula_latex) main.append(math(formula_latex, formula_latex, true));
  if (points?.length) {
    main.append(addPlot({points, parametric}), table(parametric ? ['t', 'x(t)', 'y(t)'] : ['x','f(x)'],
      muestras.map(row => parametric ? row : row.slice(1)), 'Puntos de referencia'));
  }
  if (Object.keys(general).length) main.append(valueView(general));
  if (tabla?.length) panels.push([encabezados ? 'Tabla' : 'Iteraciones', () => {
    if (encabezados) return table(encabezados, tabla);
    const first = tabla[0];
    const body = node('div','ws-result-stack');
    if (first.x_decimal !== undefined) {
      const bracket = first.a !== undefined;
      const formatDecimal = value => value == null ? null : (typeof value === 'string' && value.includes('/') ? value : scalar(value));
      const cols = bracket
        ? ['k','a','b','xᵣ','f(a)','f(b)','f(xᵣ)','Signo f(a)f(xᵣ)','εₐ (%)','Cota']
        : ['k','xₖ','f(xₖ)',first.derivada_x !== undefined ? 'f′(xₖ)' : 'f(xₖ₋₁)','xₖ₊₁','εₐ (%)','Error absoluto','|f(xₖ₊₁)|'];
      body.append(table(cols, tabla.map(row => (bracket
        ? [row.iteracion,row.a,row.b,row.x_decimal,row.fa,row.fb,row.fx,row.signo_fa_por_fx,row.error_porcentual,row.cota_intervalo]
        : [row.iteracion,row.x_anterior,row.f_anterior_actual,row.derivada_x ?? row.f_anterior,
          row.x_decimal,row.error_porcentual,row.error_aproximado_absoluto,row.residual]).map(formatDecimal))));
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
  if (response.steps?.length) panels.push(['Procedimiento', () => procedureView(response.steps)]);
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
  edit.addEventListener('click', onEdit);
  actions.append(edit);
  header.append(heading, actions);
  target.append(header);
  if (response.result?.expresion) {
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
  const panels = originalSystem ? systemResult(response.result, choices) : genericResult(response);
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
    content.replaceChildren(panelContent(i));
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
  results.append(tabs, content);
  target.append(results);
  const initial = selectedTab || (originalSystem && choices.solution ? 'Solución' : 'Resultado');
  select(Math.max(0, panels.findIndex(([label]) => label === initial)));
  if (navigator.clipboard?.writeText) {
    const copy = node('button','secondary','Copiar pestaña');
    copy.type = 'button';
    copy.addEventListener('click', async () => {
      try {
        const clone = content.cloneNode(true);
        clone.querySelectorAll('[data-plain]').forEach(item => {
          item.replaceWith(node('span','', item.dataset.plain + '\n'));
        });
        clone.querySelectorAll('tr').forEach(row => {
          row.replaceWith(node('div','', [...row.cells].map(cell => cell.textContent).join('\t') + '\n'));
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
