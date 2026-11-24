import { node } from './matrix-input.js';
import { iterationSelection } from './iteration-selection.js';
import { plotCamera, plotPlayback } from './plot-controls.js';

const clamp = (value, lower, upper) => Math.min(upper, Math.max(lower, value));
const tickFormat = new Intl.NumberFormat('es-NI', { maximumSignificantDigits: 3, useGrouping: false });

export function addPlot({ points = [], parametric = false, names = [], diagram, tangents = [], markers = [], iteraciones = [], selection, caption, overlay, cuadros, parametros, playback = true, axisLabels, sampleTimeline }) {
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
  if ((overlay || cuadros) && finite.length) finite.push([finite[0][0],0]);
  if (!finite.length) finite.push([0,0]);
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
  const base = [xmin,xmax,ymin,ymax];
  const samples = points.flatMap(([x,...ys],i) => Number.isFinite(x) && ys.some(Number.isFinite) ? [i] : []);
  const stride = Math.max(1,Math.ceil(samples.length/100));
  const sampled = samples.filter((_,i) => i%stride===0 || i===samples.length-1);
  const arrowsSteps = arrows ? [...new Set([1,2,arrows.length].filter(i=>i<=arrows.length))] : [];
  const indices = arrows ? arrowsSteps : sampled;
  const timeline = selection ?? sampleTimeline ?? (playback && indices.length ? iterationSelection(indices,indices.length-1) : null);
  const frames = new Map(cuadros?.map(frame => [frame.iteracion,frame]));
  let active, fraction = 1;
  const camera = plotCamera(canvas, () => canvas.redrawPlot());
  const readout = node('output','ws-graph-reading');
  const chartLabel = canvas.getAttribute('aria-label');
  const axes = axisLabels ?? (arrows || parametric ? ['x','y'] : ['x', names.length ? 'Valor' : 'f(x)']);
  const pointLabel = ([x,y]) => '('+tick(Number(x))+', '+tick(Number(y))+')';
  function dot(point, color, label, offset = -10) {
    const [x,y] = [xPixel(point[0]),yPixel(point[1])];
    context.beginPath();
    context.arc(x,y,5,0,Math.PI*2);
    context.fillStyle = color;
    context.fill();
    if (label) {
      context.font = '16px system-ui';
      context.textAlign = x > width/2 ? 'right' : 'left';
      context.fillText(label,x+(x>width/2 ? -7 : 7),y+offset);
    }
  }
  canvas.redrawPlot = () => {
    // La pestaña vuelve a dibujar al montar el lienzo. Evitar trabajo fuera del documento.
    if (!canvas.isConnected) return;
    const {x,y,zoom} = camera.view;
    const xScale = (base[1]-base[0])/zoom;
    const yScale = (base[3]-base[2])/zoom;
    const midX = (base[0]+base[1])/2-x*xScale/w;
    const midY = (base[2]+base[3])/2+y*yScale/h;
    [xmin,xmax,ymin,ymax] = [midX-xScale/2,midX+xScale/2,midY-yScale/2,midY+yScale/2];
    context.clearRect(0, 0, width, height);
    context.lineWidth = 1;
    const palette = getComputedStyle(canvas);
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
    context.textAlign = 'right';
    context.fillText(axes[0], width-padding, height-4);
    context.textAlign = 'left';
    context.fillText(axes[1], padding+3, padding-15);
    context.save();
    context.beginPath();
    context.rect(padding, padding, w, h);
    context.clip();
    if (arrows) {
      arrows.slice(0, active ?? arrows.length).forEach(([label,start,end],index) => {
        const from = [xPixel(start[0]),yPixel(start[1])];
        const to = [xPixel(end[0]),yPixel(end[1])];
        const color = colors[index % 3];
        context.setLineDash(label ? [] : [6,6]);
        context.lineWidth = label ? 3 : 1.5;
        line(...from, ...to, color);
        if (!label) return;
        dot(end,color,label);
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
    if (!arrows && !cuadros) {
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
      let last = null, previous = null;
      const limit = !arrows && timeline && !cuadros && !selection ? active : points.length-1;
      for (let i=0; i<=limit; i++) {
        const [x,...ys] = points[i];
        const y = ys[index];
        if (!Number.isFinite(x) || !Number.isFinite(y)) {
          last = previous = null;
          continue;
        }
        const next = [clamp(xPixel(x), -width, width * 2), clamp(yPixel(y), -height, height * 2)];
        if (!last || (!names.length && Math.abs(y-previous) > (base[3]-base[2])*.65)) context.moveTo(...next);
        else context.lineTo(...next);
        last = next;
        previous = y;
      }
      context.stroke();
      if (limit === 0 && last) {
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
    context.setLineDash([]);
    const frame = frames.get(active);
    if (frame) {
      const accent = color('--highlight');
      if (frame.intervalo) {
        const [left,right] = frame.intervalo.map(Number);
        const [start,end] = frame.intervalo_siguiente.map(Number);
        for (const [a,b,alpha] of [[left,right,.15],[start,end,.3*fraction]]) {
          context.globalAlpha = alpha;
          context.fillStyle = accent;
          context.fillRect(xPixel(a),padding,xPixel(b)-xPixel(a),h);
        }
        context.globalAlpha = 1;
        frame.extremos.forEach((p,i) => dot(p,colors[1],i ? 'b' : 'a'));
      }
      if (frame.recta) {
        const [[x,y],[cross]] = frame.recta.map(numericPoint);
        const t = Math.min(1,fraction/.78);
        context.lineWidth = 3;
        line(xPixel(x),yPixel(y),xPixel(x+t*(cross-x)),yPixel(y*(1-t)),accent);
        if (!frame.intervalo) dot([x,y],accent,'Punto inicial');
        if (t === 1) dot([cross,0],accent,Number(frame.siguiente)===cross ? 'Corte = siguiente' : 'Corte',24);
      }
      if (fraction >= .78) {
        const [x,y] = frame.punto.map(Number);
        context.lineWidth = 1.3;
        context.setLineDash([4,4]);
        line(xPixel(x),yPixel(0),xPixel(x),yPixel(y),colors[1]);
        dot([x,y],accent,frame.intervalo ? 'f(xᵣ)' : Math.abs(yPixel(y)-yPixel(0)) >= 24 ? 'Siguiente punto' : '');
        if (!frame.recta || Number(frame.recta[1][0]) !== x) dot([x,0],accent,frame.intervalo ? 'xᵣ' : 'x siguiente',24);
      }
    } else if (timeline && !selection && !arrows) {
      points[active]?.slice(1).forEach((y,i) => {
        if (Number.isFinite(y)) dot([points[active][0],y],colors[i%3]);
      });
    }
    context.restore();

    legends.forEach((legend, i) => legend.style.setProperty('--series-color', colors[i]));
  };
  if (timeline) {
    canvas.dataset.sampleKeys = 'true';
    canvas.addEventListener('keydown', event => {
      if (event.shiftKey || !['ArrowLeft','ArrowRight'].includes(event.key)) return;
      event.preventDefault();
      timeline.move(event.key==='ArrowLeft' ? -1 : 1);
    });
    canvas.addEventListener('click', event => {
      if (camera.dragged() || arrows) return;
      const [x,y] = camera.pixel(event);
      const candidates = selection ? iteraciones : (sampleTimeline ? samples : sampled).flatMap(i=>
        points[i].slice(1).filter(Number.isFinite).map(value => [i,points[i][0],value]));
      let closest, distance = 20;
      for (const [index,px,py] of candidates) {
        const gap = Math.hypot(xPixel(px)-x,yPixel(py)-y);
        if (gap < distance) { closest = index; distance = gap; }
      }
      if (closest !== undefined) timeline.select(closest);
    });
    timeline.subscribe(index => {
      active = index;
      fraction = 1;
      canvas.dataset.frame = String(index);
      if (selection) {
        canvas.setAttribute('aria-label',chartLabel+' · iteración '+index);
      } else if (arrows) {
        readout.textContent = arrows.slice(0,index).filter(([name])=>name)
          .map(([name,,end])=>name+' = '+pointLabel(end)).join(' · ');
      } else {
        const [x,...ys] = points[index];
        readout.textContent = (parametros ? 't = '+tick(Number(parametros[index]))+' · ' : '')+
          ys.flatMap((y,i)=>Number.isFinite(y) ? [(names[i] ? names[i]+' ' : '')+pointLabel([x,y])] : []).join(' · ');
      }
      canvas.redrawPlot();
    });
  }
  if (arrows) names = arrows.map(([name]) => name).filter(Boolean);
  const figure = node('figure','ws-plot-figure');
  if (timeline) {
    const player = plotPlayback(timeline,{
      label: selection ? 'Iteración del método' : arrows ? 'Construcción de vectores' : 'Recorrer muestras',
      interval: selection ? 950 : arrows ? 700 : 85, surface:canvas,
      progress: selection && cuadros ? value => { fraction = value; canvas.redrawPlot(); } : undefined,
    });
    figure.append(player);
    figure.pausePlayback = player.pausePlayback;
    if (!selection) figure.append(readout);
  }
  figure.append(canvas,camera.controls);
  if (names.length) {
    const captions = node('figcaption','ws-plot-key');
    names.forEach(name => {
      const legend = node('span','ws-plot-legend',name);
      legends.push(legend);
      captions.append(legend);
    });
    figure.append(captions);
  }
  return figure;
}
