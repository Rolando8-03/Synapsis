import { iterationSelection } from './iteration-selection.js';
import { math, numericTex } from './math-format.js';
import { node } from './matrix-input.js';
import { addPlot } from './plot.js';
import { printReport, reportSection } from './result-print.js';
import { motor } from './transport.js';

const formula = String.raw`x_{i+1}=x_i-\frac{f(x_i)}{f'(x_i)}`;

function decimal(value, digits = 10) {
  if (value == null) return null;
  const [numerator, denominator] = String(value).split('/');
  const number = Number(numerator) / (denominator ? Number(denominator) : 1);
  return Number.isFinite(number) ? String(Number(number.toPrecision(digits))) : String(value);
}

const numberTex = (value, digits) => numericTex(decimal(value, digits)) ?? String.raw`\text{—}`;

function box(label, tex, fallback) {
  const item = node('article', 'ws-newton-box');
  item.append(node('h3', '', label), math(tex, fallback, true));
  return item;
}

function summary(response) {
  const {result: out, metadata, status} = response;
  const body = node('div', 'ws-newton-summary');
  const last = out.tabla.at(-1);
  const tol = numberTex(out.tolerancia_x);
  const difference = last ? String.raw`E_a \approx ${numberTex(last.error_aproximado_absoluto)}` : '';
  const comparison = last ? String.raw`${difference},\qquad E_a ${last.paso_en_tolerancia ? '\\le' : '>'} \varepsilon= ${tol}`
    : String.raw`\varepsilon=${tol},\qquad E_a:\ \text{sin paso completado}`;
  const exact = out.raiz_exacta;
  body.append(
    box('Función', 'f(x)=' + metadata.funcion_latex, 'f(x) = ' + out.expresion),
    box('Derivada simbólica', metadata.derivada_latex ? "f'(x)=" + metadata.derivada_latex : String.raw`\text{No disponible}`, out.derivada ?? 'No disponible'),
    box('Fórmula de Newton-Raphson', formula, 'x siguiente = x actual − f(x actual) / f′(x actual)'),
    box('Raíz exacta', exact ? 'r=' + exact.latex : String.raw`\text{Sin forma exacta identificada}`, exact?.expresion ?? 'Sin forma exacta identificada'),
    box(status === 'ok' ? 'Raíz aproximada' : 'Último punto calculado', String.raw`x ${status === 'ok' ? '\\approx' : '='} ${numberTex(out.aproximacion)}`, decimal(out.aproximacion)),
    box('Criterio de parada · Error absoluto', comparison, `Tolerancia: ${decimal(out.tolerancia_x)}`),
  );
  const statusText = ({
    ok:'Convergencia alcanzada', breakdown:'Derivada nula o demasiado pequeña',
    iteration_limit:'Máximo de iteraciones alcanzado', cycle_detected:'Se detectó un ciclo',
    stagnated:'Se agotó la precisión de trabajo', domain_error:'Evaluación fuera del dominio',
    non_convergent:'Tolerancia del paso alcanzada con residuo alto',
  })[status] ?? 'Cálculo detenido';
  const report = box(statusText,
    String.raw`${out.iteraciones}\ \text{de} \ ${out.max_iteraciones}\ \text{iteraciones},\qquad |f(x)|\approx${numberTex(out.residual)}`,
    `${out.iteraciones} de ${out.max_iteraciones} iteraciones. Residuo: ${decimal(out.residual)}`);
  report.classList.add('ws-newton-status', status === 'ok' ? 'is-success' : 'is-warning');
  if (status === 'ok' && !last) report.append(node('p', '', 'El residuo en el valor inicial es cero a la precisión de trabajo.'));
  if (response.error?.message) report.append(node('p', '', response.error.message));
  for (const warning of response.warnings ?? []) report.append(node('p', '', warning));
  body.append(report);
  return body;
}

function substitution(template, point) {
  return template?.replaceAll('\\NEWTONPOINT', point);
}

function iterationSteps(row, response) {
  const {metadata, result} = response;
  // Conserva cifras suficientes para distinguir los dos puntos de la resta.
  const current = numericTex(row.puntos_desarrollo?.[0]) ?? numberTex(row.x_anterior);
  const next = numericTex(row.puntos_desarrollo?.[1]) ?? numberTex(row.x);
  const fx = numberTex(row.f_anterior_actual);
  const slope = numberTex(row.derivada_x);
  const error = numberTex(row.error_aproximado_absoluto);
  const tolerance = numberTex(result.tolerancia_x);
  const k = row.iteracion;
  const lines = node('ol', 'ws-newton-steps');
  function step(label, tex) {
    const item = node('li');
    item.append(node('strong', '', label), math(tex, tex, true));
    lines.append(item);
  }
  step('Evaluar la función',
    String.raw`f(x_{${k-1}})\approx f(${current})=${substitution(metadata.funcion_sustitucion,current)}\approx ${fx}`);
  step('Evaluar la derivada',
    String.raw`f'(x_{${k-1}})\approx f'(${current})=${substitution(metadata.derivada_sustitucion,current)}\approx ${slope}`);
  step('Comprobar el denominador',
    String.raw`|f'(x_{${k-1}})|\approx |${slope}|>10^{-16}|f(x_{${k-1}})|\approx 10^{-16}|${fx}|`);
  step('Calcular la nueva aproximación',
    String.raw`x_{${k}}\approx ${current}-\frac{\left(${fx}\right)}{\left(${slope}\right)}\approx ${next}`);
  step('Calcular el error absoluto',
    String.raw`E_a=|x_{${k}}-x_{${k-1}}|\approx\left|\left(${next}\right)-\left(${current}\right)\right|\approx${error}`);
  step('Calcular el error porcentual', row.error_porcentual == null
    ? String.raw`x_{${k}}=0\quad\Longrightarrow\quad E_a(\%)\ \text{indefinido. Se usa el error absoluto.}`
    : String.raw`E_a(\%)=\frac{E_a}{|x_{${k}}|}\cdot100\%\approx\frac{${error}}{|${next}|}\cdot100\%\approx${numberTex(row.error_porcentual)}\%`);
  step('Comparar el error absoluto con la tolerancia',
    String.raw`E_a\approx${error},\qquad E_a${row.paso_en_tolerancia ? '\\le' : '>'}\varepsilon=${tolerance}`);
  step('Comprobar el residuo en la función original',
    String.raw`|f(x_{${k}})|\approx\left|${substitution(metadata.funcion_sustitucion,next)}\right|\approx\left|${numberTex(row.fx)}\right|\approx${numberTex(row.residual)}`);
  return lines;
}

function newtonTable(response, table) {
  const rows = response.result.tabla;
  const headings = ['Iteración i','x actual','f(x)','f′(x)','x siguiente','Error absoluto (Eₐ)','Error porcentual (Eₐ %)'];
  const fields = ['x_anterior','f_anterior_actual','derivada_x','x','error_aproximado_absoluto','error_porcentual'];
  return table(headings, rows.map(row => [row.iteracion, ...fields.map(key => decimal(row[key]))]), 'Tabla de iteraciones');
}

function procedures(response, printing = false) {
  const body = node('div', 'ws-result-stack');
  const {tabla, fallo_derivada: failure} = response.result;
  if (!tabla.length) body.append(node('p', '', 'No se completaron iteraciones.'));
  else body.append(node('p', 'ws-muted', 'Las sustituciones se muestran redondeadas. Los errores se calculan con la precisión del motor.'));
  for (const row of tabla) {
    const item = node(printing ? 'section' : 'details', 'ws-step-card ws-newton-iteration');
    item.append(node(printing ? 'h3' : 'summary', '', `Iteración ${row.iteracion}`), iterationSteps(row, response));
    body.append(item);
  }
  if (failure) {
    body.append(box(`Detención al evaluar la derivada en la iteración ${failure.iteracion}`,
      String.raw`f'(${numberTex(failure.x)})\approx ${numberTex(failure.valor)}`, 'División cancelada'));
  }
  return body;
}

function graph(response) {
  const out = response.result;
  const original = out.grafico_raiz;
  const view = node('div', 'ws-result-stack ws-newton-graph');
  const range = node('form', 'ws-newton-range');
  const inputs = ['Desde x', 'Hasta x'].map(label => {
    const field = node('label', 'ws-field', label);
    const input = node('input');
    input.required = true;
    input.inputMode = 'decimal';
    field.append(input);
    range.append(field);
    return input;
  });
  const apply = node('button', 'secondary', 'Aplicar rango');
  apply.type = 'submit';
  range.append(apply);
  const notice = node('p', 'ws-field-help');
  notice.setAttribute('role', 'status');
  const chart = node('div');
  let figure;
  function draw(points, bounds) {
    const indices = original?.iteraciones.map(([i]) => i) ?? [];
    const selection = indices.length ? iterationSelection(indices, Number(figure?.querySelector('select')?.selectedIndex ?? 0)) : null;
    const base = original ?? {caption:'Gráfica de la función'};
    figure = addPlot({...base, points, selection, playback:false, xRange:bounds,
      cuadros:selection ? base.cuadros : undefined,
      markers:selection ? base.markers : [[decimal(out.aproximacion), decimal(out.valor_funcion)]]});
    chart.replaceChildren(figure);
    figure.querySelector('canvas')?.redrawPlot?.();
    if (!selection) figure.querySelector('.ws-graph-controls')?.before(node('p', 'ws-muted', 'Iteraciones completadas: 0'));
  }
  const min = Number(original?.points[0]?.[0]);
  const max = Number(original?.points.at(-1)?.[0]);
  const initial = Number(decimal(out.aproximacion));
  const bounds = Number.isFinite(min) && Number.isFinite(max) && min < max ? [min,max]
    : [initial-1,initial+1].every(v => Math.abs(v) <= 1e7) ? [initial-1,initial+1] : [-2,2];
  inputs.forEach((input, i) => { input.value = String(bounds[i]); });
  view.append(range, notice, chart);
  if (original?.points.some(([,y]) => y != null)) draw(original.points, bounds);
  else notice.textContent = 'Elegí el rango donde querés graficar la función.';
  range.addEventListener('submit', async event => {
    event.preventDefault();
    const limits = inputs.map(input => Number(input.value.trim()));
    if (inputs.some(input => !input.value.trim()) || !limits.every(Number.isFinite) || limits[0] >= limits[1]) {
      notice.textContent = 'Ingresá dos límites numéricos. El inferior debe ser menor que el superior.';
      return;
    }
    apply.disabled = true;
    notice.textContent = '';
    try {
      const answer = await motor.calculate({operation:'grafica.explicita',input:{
        expr:out.expresion,from:String(limits[0]),to:String(limits[1]),
      },steps:false});
      if (!answer.result?.points) throw new Error(answer.error?.message ?? 'No se pudo graficar el rango.');
      draw(answer.result.points, limits);
    } catch (error) {
      notice.textContent = error.message;
    } finally {
      apply.disabled = false;
    }
  });
  return view;
}

export function newtonViews(response, table) {
  return [
    ['Resumen', () => summary(response)],
    ['Procedimiento', () => {
      const content = procedures(response);
      if (response.result.tabla.length) content.prepend(newtonTable(response,table));
      return content;
    }],
    ['Gráfica', () => graph(response)],
  ];
}

export function newtonExport(response, table) {
  return printReport('Newton-Raphson', [
    reportSection('Resumen', summary(response)),
    ...(response.result.tabla.length ? [reportSection('Tabla de iteraciones', newtonTable(response,table))] : []),
    reportSection('Procedimiento por iteración', procedures(response, true)),
  ]);
}

export async function warnNewtonDerivative(response) {
  const failure = response.result?.fallo_derivada;
  if (!failure) return;
  const {default: Swal} = await import('./vendor/sweetalert2/sweetalert2.esm.all.min.js');
  const zero = Number(failure.valor.split(/[eE]/)[0]) === 0;
  return Swal.fire({
    icon:'warning',
    title:zero ? 'La derivada es 0' : 'La derivada es demasiado pequeña',
    text:zero
      ? 'Newton-Raphson se detuvo antes de dividir entre cero. Debés cambiar la función para volver a resolver.'
      : 'Newton-Raphson se detuvo antes de dividir. Revisá la función o el valor inicial.',
    confirmButtonText:'Entendido',
  });
}
