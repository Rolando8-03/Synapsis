import { node } from './matrix-input.js';

const page = document.documentElement;
const clamp = (value, lower, upper) => Math.min(upper, Math.max(lower, value));
const tickFormat = new Intl.NumberFormat('es-NI', { maximumSignificantDigits: 3, useGrouping: false });

export function addPlot({ points = [], parametric = false, names = [], diagram, tangents = [], markers = [], iteraciones = [], selection, caption, overlay }) {
  const numericPoint = point => point.map(value => value === null ? null : Number(value));
  points = points.map(numericPoint);
  const arrows = diagram?.map(([label,start,end]) => [label,numericPoint(start),numericPoint(end)]);
  const canvas = node('canvas', 'plot');
  const width = 670;
  const height = 420;
  const padding = 48;
  canvas.width = width;
  canvas.height = height;
  canvas.setAttribute('role', 'img');
  canvas.setAttribute('aria-label', caption || (arrows ? 'Paralelogramo de los vectores y su suma' : names.length ? 'Comparación de ' + names.join(' y ') : parametric ? 'Gráfica de la curva paramétrica' : 'Gráfica de la función'));
  const context = canvas.getContext('2d');
  if (!context) return canvas;

  const finite = arrows ? arrows.flatMap(([,start,end]) => [start,end]) : points.flatMap(([x,...ys]) => ys.filter(y => Number.isFinite(x) && Number.isFinite(y)).map(y => [x,y]));
  if (overlay && !names.length) finite.push([finite[0][0],0]);
  const range = (index, trim) => {
    const values = finite.map(point => point[index]).sort((a, b) => a - b);
    const skip = trim ? Math.floor(values.length * .025) : 0;
    return [values[skip], values[values.length - 1 - skip]].map(value => clamp(value, -1e100, 1e100));
  };
  let [xmin, xmax] = range(0, parametric);
  let [ymin, ymax] = range(1, !overlay);
  const padded = (min, max) => {
    const gap = max > min ? (max - min) * .09 : Math.max(1, Math.abs(max) * .09);
    return [min - gap, max + gap];
  };
  [xmin, xmax] = padded(xmin, xmax);
  [ymin, ymax] = padded(ymin, ymax);
  const w = width - padding * 2;
  const h = height - padding * 2;
  if (parametric || arrows) {
    const units = Math.max((xmax - xmin) / w, (ymax - ymin) / h);
    const cx = (xmin + xmax) / 2;
    const cy = (ymin + ymax) / 2;
    [xmin, xmax, ymin, ymax] = [cx - units * w / 2, cx + units * w / 2, cy - units * h / 2, cy + units * h / 2];
  }
  const xPixel = x => padding + (x - xmin) * w / (xmax - xmin);
  const yPixel = y => height - padding - (y - ymin) * h / (ymax - ymin);
  const line = (x1, y1, x2, y2, color) => {
    context.strokeStyle = color;
    context.beginPath();
    context.moveTo(x1, y1);
    context.lineTo(x2, y2);
    context.stroke();
  };
  const tick = value => Math.abs(value) >= 10000 || (value && Math.abs(value) < .01)
    ? value.toExponential(1) : tickFormat.format(value);
  const legends = [];
  let selectedPoint;
  canvas.redrawPlot = () => {
    // La pestaña vuelve a dibujar al montar el lienzo. Evitar trabajo fuera del documento.
    if (!canvas.isConnected) return;
    context.clearRect(0, 0, width, height);
    context.lineWidth = 1;
    const palette = getComputedStyle(page);
    const color = name => palette.getPropertyValue(name).trim();
    const graphGrid = color('--plot-grid');
    const graphAxis = color('--plot-axis');
    const colors = [1, 2, 3].map(index => color('--plot-series-' + index));
    context.font = '20px system-ui';
    context.fillStyle = color('--muted');
    for (let i = 0; i <= 4; i++) {
      const x = padding + w * i / 4;
      const y = padding + h * i / 4;
      line(x, padding, x, height - padding, graphGrid);
      line(padding, y, width - padding, y, graphGrid);
      context.textAlign = 'center';
      context.fillText(tick(xmin + (xmax - xmin) * i / 4), x, height - padding + 26);
      context.textAlign = 'right';
      context.fillText(tick(ymax - (ymax - ymin) * i / 4), padding - 7, y + 5, padding - 8);
    }
    if (xmin <= 0 && xmax >= 0) line(xPixel(0), padding, xPixel(0), height - padding, graphAxis);
    if (ymin <= 0 && ymax >= 0) line(padding, yPixel(0), width - padding, yPixel(0), graphAxis);
    context.save();
    context.beginPath();
    context.rect(padding, padding, w, h);
    context.clip();
    if (arrows) {
      arrows.forEach(([label,start,end],index) => {
        const from = [xPixel(start[0]),yPixel(start[1])];
        const to = [xPixel(end[0]),yPixel(end[1])];
        const color = colors[index % 3];
        context.setLineDash(label ? [] : [6,6]);
        context.lineWidth = label ? 3 : 1.5;
        line(...from, ...to, color);
        if (!label) return;
        const angle = Math.atan2(to[1]-from[1],to[0]-from[0]);
        context.fillStyle = color;
        context.beginPath();
        context.arc(...to, 3, 0, Math.PI*2);
        context.fill();
        if (Math.hypot(to[0]-from[0],to[1]-from[1]) < 10) return;
        context.beginPath();
        context.moveTo(...to);
        context.lineTo(to[0]-13*Math.cos(angle-.43),to[1]-13*Math.sin(angle-.43));
        context.lineTo(to[0]-13*Math.cos(angle+.43),to[1]-13*Math.sin(angle+.43));
        context.fill();
      });
    }
    if (!arrows) {
      context.lineWidth = 1.2;
      context.setLineDash([5,5]);
      tangents.forEach(([[x1,y1],[x2,y2]]) => line(xPixel(x1),yPixel(y1),xPixel(x2),yPixel(y2),colors[2]));
      context.setLineDash([]);
      markers.forEach(([x,y]) => {
        context.beginPath();
        context.arc(xPixel(x),yPixel(y),4,0,Math.PI*2);
        context.fillStyle = colors[1];
        context.fill();
      });
    }
    if (overlay?.rectangles) {
      const baseline = yPixel(0);
      context.fillStyle = colors[1];
      context.strokeStyle = colors[1];
      overlay.rectangles.forEach(([left,right,x,y]) => {
        const top = yPixel(y);
        const start = xPixel(left);
        const width = xPixel(right) - start;
        context.globalAlpha = .24;
        context.fillRect(start, top, width, baseline - top);
        context.globalAlpha = .9;
        context.strokeRect(start, top, width, baseline - top);
        context.beginPath();
        context.arc(xPixel(x), top, 3, 0, Math.PI * 2);
        context.fill();
      });
      context.globalAlpha = 1;
    }
    if (overlay?.region?.length) {
      const band = overlay.region;
      context.beginPath();
      context.moveTo(xPixel(band[0][0]),yPixel(band[0][1]));
      for (const [x,y] of band) context.lineTo(xPixel(x),yPixel(y));
      for (let i=band.length-1; i>=0; i--) context.lineTo(xPixel(band[i][0]),yPixel(band[i][2]));
      context.closePath();
      context.fillStyle = color('--highlight');
      context.globalAlpha = .35;
      context.fill();
      context.globalAlpha = 1;
    }
    const series = names.length || 1;
    for (let index = 0; index < series; index++) {
      context.beginPath();
      context.strokeStyle = colors[index];
      context.lineWidth = index ? 3 : 3.6;
      context.setLineDash(index ? [7,4] : []);
      let last = null;
      for (const point of points) {
        const [x,y] = [point[0],point[index+1]];
        if (!Number.isFinite(x) || !Number.isFinite(y)) {
          last = null;
          continue;
        }
        const next = [clamp(xPixel(x), -width, width * 2), clamp(yPixel(y), -height, height * 2)];
        if (!last || (!names.length && Math.hypot(next[0] - last[0], next[1] - last[1]) > h * .65)) context.moveTo(...next);
        else context.lineTo(...next);
        last = next;
      }
      context.stroke();
      if (points.length === 1 && last) {
        context.beginPath();
        context.arc(...last, 5, 0, Math.PI * 2);
        context.fillStyle = colors[index];
        context.fill();
      }
    }
    if (overlay?.tangent) {
      const [x,y,m] = overlay.tangent;
      context.setLineDash([]);
      context.lineWidth = 2.5;
      line(xPixel(xmin),yPixel(y+m*(xmin-x)),xPixel(xmax),yPixel(y+m*(xmax-x)),color('--highlight'));
      context.beginPath();
      context.arc(xPixel(x),yPixel(y),6,0,Math.PI*2);
      context.fillStyle = color('--highlight');
      context.fill();
    }
    if (overlay?.section) {
      const [x, y0, y1] = overlay.section;
      context.setLineDash([]);
      context.lineWidth = 5;
      line(xPixel(x), yPixel(y0), xPixel(x), yPixel(y1), color('--text'));
    }
    if (selectedPoint) {
      const [,x,y] = selectedPoint;
      context.beginPath();
      context.arc(xPixel(x), yPixel(y), 8, 0, Math.PI*2);
      context.strokeStyle = color('--text');
      context.lineWidth = 3;
      context.stroke();
    }
    context.restore();

    legends.forEach((legend, i) => legend.style.setProperty('--series-color', colors[i]));
  };
  if (selection && iteraciones.length) {
    canvas.tabIndex = 0;
    canvas.addEventListener('keydown', event => {
      if (!['ArrowLeft', 'ArrowRight'].includes(event.key)) return;
      event.preventDefault();
      selection.move(event.key === 'ArrowLeft' ? -1 : 1);
    });
    canvas.addEventListener('click', event => {
      const rect = canvas.getBoundingClientRect();
      const x = (event.clientX - rect.left) * width / rect.width;
      const y = (event.clientY - rect.top) * height / rect.height;
      let closest;
      let distance = 18;
      for (const [index, px, py] of iteraciones) {
        const candidate = Math.hypot(xPixel(px) - x, yPixel(py) - y);
        if (candidate < distance) {
          closest = index;
          distance = candidate;
        }
      }
      if (closest !== undefined) selection.select(closest);
    });
    selection.subscribe(index => {
      selectedPoint = iteraciones.find(([iteration]) => iteration === index);
      canvas.setAttribute('aria-label', `${caption || 'Gráfica'} · iteración ${index}. Usá las flechas para cambiar.`);
      canvas.redrawPlot();
    });
  }
  if (arrows) names = arrows.map(([name]) => name).filter(Boolean);
  if (!names.length) {
    canvas.redrawPlot();
    return canvas;
  }
  const figure = node('figure','ws-plot-figure');
  const legendCaption = node('figcaption','ws-plot-key');
  names.forEach(name => {
    const legend = node('span','ws-plot-legend',name);
    legends.push(legend);
    legendCaption.append(legend);
  });
  figure.append(canvas,legendCaption);
  canvas.redrawPlot();
  return figure;
}

