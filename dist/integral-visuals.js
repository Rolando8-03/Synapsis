import { node } from './matrix-input.js';
import { addPlot } from './plot.js';
import { math } from './math-format.js';

function framePicker(id, title, description, model) {
  const view = node('div', 'ws-result-stack');
  const label = node('label', '', title);
  label.htmlFor = id;
  const input = node('input');
  input.id = id;
  input.type = 'range';
  input.min = 0;
  input.max = model.cuadros.length - 1;
  input.value = model.inicial;
  const summary = node('output', 'ws-value');
  summary.htmlFor = id;
  summary.setAttribute('aria-live', 'polite');
  view.append(label, input, summary);
  const overlay = {};
  const plot = addPlot({ points: model.curva, names: model.etiquetas, overlay, caption: description });
  view.append(plot);
  const canvas = plot.matches('canvas') ? plot : plot.querySelector('canvas');
  return { view, input, summary, overlay, canvas };
}

export function riemannPlot(model) {
  const { view, input, summary, overlay, canvas } = framePicker('ws-riemann-n', 'Número de rectángulos',
    'Gráfica de la función y los rectángulos de Riemann', model);
  const update = () => {
    const frame = model.cuadros[Number(input.value)];
    const relation = model.exacta ? '=' : '≈';
    summary.textContent = `n = ${frame.n} · Δx = ${frame.ancho} · Primera muestra x₁* = ${frame.primera_muestra} · Sₙ ${relation} ${frame.suma}`;
    input.setAttribute('aria-valuetext', `${frame.n} rectángulos`);
    overlay.rectangles = frame.puntos.map(([x,y], i) => [frame.particion[i],frame.particion[i+1],x,y]);
    canvas.redrawPlot?.();
  };
  input.addEventListener('input', update);
  update();
  return view;
}

export function sectionPlot(model) {
  const { view, input, summary, overlay, canvas } = framePicker('ws-volume-x', 'Posición de la sección',
    'Curvas, eje de giro y sección seleccionada', model);
  const inset = node('canvas', 'plot ws-cross-section');
  inset.width = 240;
  inset.height = 200;
  inset.setAttribute('role', 'img');
  const formula = node('div','ws-frame-formula');
  view.append(inset,formula);
  const context = inset.getContext('2d');
  const largest = Math.max(...model.cuadros.map(frame => Number(frame.radios[0]))) || 1;
  const piText = text => text.replaceAll('pi','π').replaceAll('*','·');
  inset.redrawPlot = () => {
    if (!context || !inset.isConnected) return;
    const { radios } = model.cuadros[Number(input.value)];
    const [outer, inner] = radios.map(radius => 82 * (Number(radius) / largest));
    context.clearRect(0, 0, inset.width, inset.height);
    context.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--plot-series-1').trim();
    context.beginPath();
    context.arc(120, 100, outer, 0, Math.PI * 2);
    if (inner) {
      context.moveTo(120 + inner, 100);
      context.arc(120, 100, inner, 0, Math.PI * 2);
    }
    context.fill('evenodd');
  };
  const update = () => {
    const frame = model.cuadros[Number(input.value)];
    summary.textContent = `x = ${frame.x} · R = ${frame.exterior} · r = ${frame.interior} · A = ${piText(frame.area)}`;
    input.setAttribute('aria-valuetext', `x = ${frame.x}`);
    formula.replaceChildren(math(frame.formula_latex,frame.area,true));
    inset.setAttribute('aria-label', `Sección circular. Radio exterior ${frame.exterior}, radio interior ${frame.interior}.`);
    overlay.section = frame.segmento;
    canvas.redrawPlot?.();
    inset.redrawPlot();
  };
  input.addEventListener('input', update);
  update();
  return view;
}

export function curveFrames(model) {
  const tangent = model.tipo === 'tangente';
  const {view,input,summary,overlay,canvas} = framePicker(
    tangent ? 'ws-tangent-x' : 'ws-area-piece',
    tangent ? 'Punto de tangencia' : 'Tramo entre curvas',
    tangent ? 'Función y recta tangente' : 'Región entre las dos curvas',
    model,
  );
  const formula = node('div','ws-frame-formula');
  view.append(formula);
  function update() {
    const frame = model.cuadros[Number(input.value)];
    const description = tangent ? `x = ${frame.x} · f(x) = ${frame.y} · Pendiente = ${frame.m}`
      : `[${frame.izquierda}, ${frame.derecha}] · Curva superior ${frame.superior}`;
    summary.textContent = description;
    input.setAttribute('aria-valuetext',description);
    formula.replaceChildren(math(frame.formula_latex,frame.formula_latex,true));
    overlay.tangent = frame.tangente?.map(Number);
    overlay.region = frame.banda;
    canvas.redrawPlot?.();
  }
  input.addEventListener('input',update);
  update();
  return view;
}
