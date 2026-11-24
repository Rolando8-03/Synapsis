import { node } from './matrix-input.js';
import { addPlot } from './plot.js';

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
  const plot = addPlot({ points: model.curva, overlay, caption: description });
  view.append(plot);
  return { view, input, summary, overlay, plot };
}

export function riemannPlot(model) {
  const { view, input, summary, overlay, plot } = framePicker('ws-riemann-n', 'Número de rectángulos',
    'Gráfica de la función y los rectángulos de Riemann', model);
  const update = () => {
    const frame = model.cuadros[Number(input.value)];
    const relation = model.exacta ? '=' : '≈';
    summary.textContent = `n = ${frame.n} · Δx = ${frame.ancho} · Primera muestra x₁* = ${frame.primera_muestra} · Sₙ ${relation} ${frame.suma}`;
    input.setAttribute('aria-valuetext', `${frame.n} rectángulos`);
    overlay.rectangles = frame.puntos.map(([x,y], i) => [frame.particion[i],frame.particion[i+1],x,y]);
    plot.redrawPlot();
  };
  input.addEventListener('input', update);
  update();
  return view;
}
