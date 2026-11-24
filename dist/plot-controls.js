import { node } from './matrix-input.js';

function button(label, action) {
  const item = node('button', 'secondary', label);
  item.type = 'button';
  item.addEventListener('click', action);
  return item;
}

export function plotPlayback(selection, {label = 'Paso de la gráfica', interval = 250, progress, scrub = true, surface} = {}) {
  const controls = node('div', 'ws-graph-controls');
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const previous = button('Anterior', () => selection.move(-1));
  const next = button('Siguiente', () => selection.move(1));
  const play = button('Reproducir', () => animation ? pause() : start());
  const sliderLabel = node('label', 'ws-graph-slider', label);
  const slider = node('input');
  slider.type = 'range';
  slider.min = 0;
  slider.max = selection.size-1;
  sliderLabel.append(slider);
  const speedLabel = node('label', '', 'Velocidad ');
  const speed = node('select');
  for (const rate of [.5,1,2,4]) speed.add(new Option(rate+'×',rate,false,rate===1));
  speedLabel.append(speed);
  controls.append(previous,play,next,speedLabel);
  if (scrub) controls.append(sliderLabel);
  let animation = 0, started;
  let advancing = false;

  function pause() {
    if (!animation) return;
    cancelAnimationFrame(animation);
    animation = 0;
    document.removeEventListener('visibilitychange', checkVisibility);
    play.textContent = 'Reproducir';
    progress?.(1);
  }
  function visible() {
    if (!controls.isConnected || document.hidden || controls.closest('[hidden]')) return false;
    const rect = (surface ?? controls).getBoundingClientRect();
    return rect.bottom > 0 && rect.top < innerHeight;
  }
  function checkVisibility() { if (!visible()) pause(); }
  function tick(time) {
    if (!visible() || motion.matches) { pause(); return; }
    started ??= time;
    const fraction = Math.min(1,(time-started)*Number(speed.value)/interval);
    progress?.(fraction);
    if (fraction === 1) {
      if (selection.position === selection.size-1) { pause(); return; }
      advancing = true;
      selection.move(1);
      advancing = false;
      progress?.(0);
      started = time;
    }
    animation = requestAnimationFrame(tick);
  }
  function start() {
    if (motion.matches || !visible()) return;
    if (selection.position === selection.size-1) selection.seek(0);
    progress?.(0);
    started = undefined;
    play.textContent = 'Pausar';
    document.addEventListener('visibilitychange',checkVisibility);
    animation = requestAnimationFrame(tick);
  }
  slider.addEventListener('input', () => selection.seek(Number(slider.value)));
  speed.addEventListener('change', () => { started = undefined; });
  selection.subscribe(index => {
    if (!advancing) pause();
    slider.value = selection.position;
    slider.setAttribute('aria-valuetext', String(index));
    previous.disabled = selection.position === 0;
    next.disabled = selection.position === selection.size-1;
  });
  play.disabled = motion.matches || (selection.size <= 1 && !progress);
  if (motion.matches) play.title = 'Usá el avance manual con movimiento reducido.';
  controls.pausePlayback = pause;
  return controls;
}

export function plotCamera(canvas, redraw, {
  view = {x:0,y:0,zoom:1}, captures = () => false, onPinch, resetView, fixed = false
} = {}) {
  const controls = node('div', 'ws-graph-controls');
  const status = node('span', 'ws-field-help');
  status.setAttribute('role','status');
  const pointers = new Map();
  let paint = 0, dragging = false;
  const pixel = event => {
    const bounds = canvas.getBoundingClientRect();
    return [(event.clientX-bounds.left)*canvas.width/bounds.width,
      (event.clientY-bounds.top)*canvas.height/bounds.height];
  };
  function schedule() {
    if (!paint) paint = requestAnimationFrame(() => { paint = 0; redraw(); });
  }
  function pan(x,y) { view.x += x; view.y += y; schedule(); }
  function zoom(factor, x = canvas.width/2, y = canvas.height/2) {
    const scale = Math.max(.25,Math.min(50,view.zoom*factor));
    const ratio = scale/view.zoom;
    view.x = ratio*(view.x+canvas.width/2-x)+x-canvas.width/2;
    view.y = ratio*(view.y+canvas.height/2-y)+y-canvas.height/2;
    view.zoom = scale;
    schedule();
  }
  function reset() {
    Object.assign(view,{x:0,y:0,zoom:1,bound:undefined});
    resetView?.();
    schedule();
  }
  async function save() {
    try {
      canvas.redrawPlot?.();
      const image = node('canvas');
      image.width = canvas.width;
      image.height = canvas.height;
      const context = image.getContext('2d');
      const background = getComputedStyle(canvas).backgroundColor;
      context.fillStyle = background === 'rgba(0, 0, 0, 0)' ? '#fff' : background;
      context.fillRect(0,0,image.width,image.height);
      context.drawImage(canvas,0,0);
      if (window.SynapsisPrint?.savePng) {
        window.SynapsisPrint.savePng(image.toDataURL('image/png').split(',')[1]);
        return;
      }
      const link = node('a');
      link.href = image.toDataURL('image/png');
      link.download = 'synapsis-grafica.png';
      link.click();
    } catch {
      status.textContent = 'No se pudo guardar la imagen.';
    }
  }
  canvas.tabIndex = 0;
  if (fixed) {
    controls.append(button('Guardar imagen',save),status);
    return {view, controls, pixel, dragged:() => false};
  }
  controls.append(button('Acercar',()=>zoom(1.25)),button('Alejar',()=>zoom(.8)),
    button('Restablecer vista',reset),button('Guardar imagen',save),status);
  canvas.style.touchAction = 'none';
  canvas.addEventListener('wheel', event => {
    event.preventDefault();
    zoom(Math.exp(Math.max(-1,Math.min(1,-event.deltaY*.002))),...pixel(event));
  },{passive:false});
  canvas.addEventListener('keydown', event => {
    const delta = {ArrowLeft:[-24,0],ArrowRight:[24,0],ArrowUp:[0,-24],ArrowDown:[0,24]}[event.key];
    if (delta && (event.shiftKey || !canvas.dataset.sampleKeys)) pan(...delta);
    else if (event.key === '+' || event.key === '=') zoom(1.25);
    else if (event.key === '-') zoom(.8);
    else if (event.key === 'Home') reset();
    else return;
    event.preventDefault();
  });
  canvas.addEventListener('pointerdown', event => {
    if (event.button !== 0) return;
    const point = pixel(event);
    if (!pointers.size) dragging = false;
    pointers.set(event.pointerId,{point,start:point,pan:!captures(event,point)});
    canvas.setPointerCapture(event.pointerId);
    if (pointers.size === 2) {
      dragging = true;
      onPinch?.();
    }
  });
  canvas.addEventListener('pointermove', event => {
    const item = pointers.get(event.pointerId);
    if (!item) return;
    const previous = item.point;
    const point = item.point = pixel(event);
    if (pointers.size === 2) {
      const other = [...pointers.values()].find(p => p !== item).point;
      const before = Math.hypot(previous[0]-other[0],previous[1]-other[1]);
      const after = Math.hypot(point[0]-other[0],point[1]-other[1]);
      if (before && after) zoom(after/before,(point[0]+other[0])/2,(point[1]+other[1])/2);
      pan((point[0]-previous[0])/2,(point[1]-previous[1])/2);
    } else if (item.pan) {
      dragging ||= Math.hypot(point[0]-item.start[0],point[1]-item.start[1]) > 1;
      if (dragging) pan(point[0]-previous[0],point[1]-previous[1]);
    }
  });
  for (const event of ['pointerup','pointercancel','lostpointercapture']) {
    canvas.addEventListener(event, e => pointers.delete(e.pointerId));
  }
  return {controls,view,pixel,dragged:()=>dragging};
}
