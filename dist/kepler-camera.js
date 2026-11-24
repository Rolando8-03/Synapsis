// The model's coordinates stay in AU. Only the orthographic camera applies zoom and rotation.
const tau = 2 * Math.PI;
const clamp = (value, min, max) => Math.max(min, Math.min(max, value));

export function orbitalDiagram(find) {
  const chart = find('chart');
  const bodies = find('bodies');
  const sun = find('sun');
  const shape = ['a', 'b'].map(id => ({
    track: find(`track-${id}`), focus: find(`focus-${id}`),
    radius: find(`radius-${id}`), planet: find(`planet-${id}`),
  }));
  const sectors = [find('sector-current'), find('sector-reference')];
  let yaw, pitch, zoom, span, orbits, frame, project;
  const valid = point => point.slice(0, 2).map(value => value.toFixed(2));
  const move = (node, point) => node.setAttribute('transform', `translate(${valid(point).join(' ')})`);
  const path = (points, closed = false) => `M${points.map(point => valid(project(point)).join(',')).join('L')}${closed ? 'Z' : ''}`;
  const ellipse = ({a, b, centro}, angle) => [centro + a * Math.cos(angle), b * Math.sin(angle)];
  const arc = (orbit, start, size, divisions) => Array.from({length: divisions + 1},
    (_, index) => ellipse(orbit, start + size * index / divisions));

  function draw(next) {
    frame = next;
    const origin = project([0, 0]);
    const order = [[sun, origin]];
    shape.forEach(({radius, planet}, i) => {
      const point = project(frame[i === 0 ? 'A' : 'B'].p);
      move(planet, point);
      const [x1, y1] = valid(origin), [x2, y2] = valid(point);
      for (const [name,value] of Object.entries({x1,y1,x2,y2})) radius.setAttribute(name,value);
      order.push([planet, point]);
    });
    order.sort((a,b) => a[1][2] - b[1][2]);
    order.forEach(([node], i) => {
      if (bodies.children[i] !== node) bodies.insertBefore(node,bodies.children[i]);
    });
    [frame.actual, frame.referencia].forEach((sector,i) => {
      const points = arc(orbits[0], sector.E_inicial, sector.delta_E, 28);
      points[0] = sector.inicio;
      points[points.length - 1] = sector.fin;
      sectors[i].setAttribute('d', path([[0,0], ...points], true));
    });
  }

  function repaint() {
    if (!orbits) return;
    const cy = Math.cos(yaw), sy = Math.sin(yaw);
    const cp = Math.cos(pitch), sp = Math.sin(pitch);
    const scale = 174 * zoom / span;
    project = ([x,y,z = 0]) => {
      const across = x * cy - y * sy;
      const along = x * sy + y * cy;
      return [360 + across * scale, 210 - (along * cp + z * sp) * scale, z * cp - along * sp];
    };
    const grid = [];
    const bound = span * 1.15;
    for (let index = -5; index <= 5; index++) {
      const line = index * bound / 5;
      grid.push(path([[line,-bound], [line,bound]]), path([[-bound,line], [bound,line]]));
    }
    find('grid').setAttribute('d', grid.join(''));
    const zenith = [0,0,span * .55];
    find('axis-z').setAttribute('d', path([[0,0],zenith]));
    move(find('axis-label'), project(zenith));
    move(sun,project([0,0]));
    shape.forEach(({track,focus},i) => {
      const orbit = orbits[i];
      track.setAttribute('d', path(arc(orbit,0,tau,120),true));
      move(focus,project([orbit.otro_foco,0]));
      focus.toggleAttribute('hidden', orbit.e === 0);
    });
    if (frame) draw(frame);
  }

  function rotate(dx,dy) {
    yaw = (yaw + dx * .009) % tau;
    pitch = clamp(pitch + dy * .008, -.15, 1.40);
    repaint();
  }

  function magnify(factor) {
    zoom = clamp(zoom * factor, .55, 4);
    repaint();
  }

  function reset() {
    yaw = -.36;
    pitch = .92;
    zoom = 1;
    repaint();
  }

  const pointers = new Map();
  const separation = () => {
    const [a,b] = pointers.values();
    return Math.hypot(a[0] - b[0], a[1] - b[1]);
  };
  chart.addEventListener('pointerdown', event => {
    if (event.button !== 0 || pointers.size >= 2) return;
    chart.setPointerCapture(event.pointerId);
    pointers.set(event.pointerId,[event.clientX,event.clientY]);
    chart.classList.add('dragging');
  });
  chart.addEventListener('pointermove', event => {
    const last = pointers.get(event.pointerId);
    if (!last) return;
    const distance = pointers.size === 2 ? separation() : 0;
    pointers.set(event.pointerId,[event.clientX,event.clientY]);
    if (distance > 1) magnify(separation() / distance);
    else if (pointers.size === 1) rotate(event.clientX - last[0],event.clientY - last[1]);
  });
  for (const type of ['pointerup','pointercancel','lostpointercapture']) {
    chart.addEventListener(type,event => {
      pointers.delete(event.pointerId);
      if (!pointers.size) chart.classList.remove('dragging');
    });
  }
  chart.addEventListener('wheel',event => {
    if (!orbits || !event.deltaY) return;
    event.preventDefault();
    const dy = event.deltaY * (event.deltaMode === 0 ? 1 : event.deltaMode === 1 ? 16 : 160);
    magnify(Math.exp(clamp(-dy * .002, -.7, .7)));
  },{passive:false});
  chart.setAttribute('tabindex','0');
  chart.addEventListener('keydown',event => {
    const rotations = {ArrowLeft:[-18,0], ArrowRight:[18,0], ArrowUp:[0,-18], ArrowDown:[0,18]};
    if (Object.hasOwn(rotations,event.key)) rotate(...rotations[event.key]);
    else if (event.key === '+' || event.key === '=') magnify(1.18);
    else if (event.key === '-') magnify(1/1.18);
    else if (event.key === 'Home') reset();
    else return;
    event.preventDefault();
  });
  reset();
  return {
    show(scene) {
      orbits = [scene.A, scene.B];
      span = Math.max(...orbits.map(orbit => orbit.a * (1 + orbit.e)));
      frame = undefined;
      repaint();
      find('model').removeAttribute('hidden');
    },
    draw,
    reset,
  };
}
