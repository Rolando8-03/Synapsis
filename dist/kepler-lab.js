import { bindOrbit } from './orbit.js';

const number = new Intl.NumberFormat('es-NI', { maximumFractionDigits: 4, useGrouping: false });
const format = value => number.format(value);
const interval = sector => `${format(sector.inicio_t)} a ${format(sector.fin_t)}`;
const ids = ['A', 'B'];

function attributes(element, values) {
  for (const [name, value] of Object.entries(values)) element.setAttribute(name, value);
}

function diagram(find) {
  const shape = ['a', 'b'].map(id => ({
    track: find(`track-${id}`), focus: find(`focus-${id}`),
    radius: find(`radius-${id}`), planet: find(`planet-${id}`),
  }));
  const model = find('model');
  const sun = find('sun');
  const sectors = [find('sector-current'), find('sector-reference')];
  let project;
  let scales;
  let origin;
  const move = (node, [x,y]) => node.setAttribute('transform', `translate(${x} ${y})`);
  return {
    show(scene) {
      const orbits = ids.map(id => scene[id]);
      const left = Math.min(...orbits.map(orbit => orbit.centro-orbit.a));
      const right = Math.max(...orbits.map(orbit => orbit.centro+orbit.a));
      const height = Math.max(...orbits.map(orbit => orbit.b));
      const scale = Math.min(552/(right-left), 150/height);
      const center = (right+left)/2;
      project = ([x,y]) => [+(320+(x-center)*scale).toFixed(2), +(187-y*scale).toFixed(2)];
      origin = project([0,0]);
      move(sun,origin);
      scales = orbits.map(({a,b}) => [a*scale,b*scale]);
      shape.forEach(({track,focus,radius},i) => {
        const orbit = orbits[i];
        const [cx,cy] = project([orbit.centro, 0]);
        const [rx,ry] = scales[i];
        attributes(track, {cx,cy,rx,ry});
        move(focus,project([orbit.otro_foco,0]));
        focus.toggleAttribute('hidden', orbit.e === 0);
        attributes(radius,{x1:origin[0],y1:origin[1]});
      });
      model.removeAttribute('hidden');
    },
    draw(frame) {
      shape.forEach(({radius,planet},i) => {
        const [x,y] = project(frame[ids[i]].p);
        move(planet,[x,y]);
        attributes(radius,{x2:x,y2:y});
      });
      const [rx,ry] = scales[0];
      [frame.actual, frame.referencia].forEach((sector,i) => {
        const start = project(sector.inicio).join(' ');
        const stop = project(sector.fin).join(' ');
        const large = sector.delta_E > Math.PI ? 1 : 0;
        sectors[i].setAttribute('d', `M${origin.join(' ')}L${start}A${rx} ${ry} 0 ${large} 0 ${stop}Z`);
      });
    },
  };
}

function bindScene(section) {
  const find = id => section.querySelector(`#kepler-${id}`);
  const plot = diagram(find);
  const e = find('e');
  const a = find('a');
  const eValue = find('e-value');
  const aValue = find('a-value');
  const note = find('status');
  const retry = find('retry');
  const measurements = find('measurements');
  const clock = find('clock');
  const time = find('time');
  const timeValue = find('time-value');
  const play = find('play');
  const back = find('back');
  const forward = find('forward');
  const clockStatus = find('clock-status');
  let loading;
  let scene;
  let index = 0;
  let animation = 0;
  let started = null;
  let startTime = 0;
  let playing = false;
  let enabled = false;
  let obscured = false;
  let inView = false;

  function sync() {
    play.textContent = enabled && playing ? 'Pausar' : 'Reproducir';
    play.disabled = !enabled;
    const moving = scene && playing && enabled && inView && !obscured && !document.hidden;
    if (moving && !animation) {
      started = null;
      startTime = scene.frames[index].t;
      animation = requestAnimationFrame(tick);
    } else if (!moving && animation) {
      cancelAnimationFrame(animation);
      animation = 0;
    }
  }

  function show(indexToShow) {
    index = Math.max(0,Math.min(scene.frames.length-1,indexToShow));
    const frame = scene.frames[index];
    const label = `${format(frame.t)} ${frame.t === 1 ? 'año' : 'años'}`;
    time.value = frame.t;
    timeValue.textContent = label;
    time.setAttribute('aria-valuetext',label);
    back.disabled = index === 0;
    forward.disabled = index === scene.frames.length-1;
    draw(frame);
  }

  function tick(now) {
    started ??= now;
    const targetTime = startTime + (now-started)*.00025;
    const nextIndex = Math.floor(targetTime / Number(time.step) + 1e-8);
    if (nextIndex !== index) show(nextIndex);
    if (index === scene.frames.length-1) {
      animation = 0;
      playing = false;
      sync();
      clockStatus.textContent = `Fin de la simulación. ${timeValue.textContent}.`;
    } else {
      animation = requestAnimationFrame(tick);
    }
  }

  function seek(nextIndex, announce = true) {
    if (!scene) return;
    playing = false;
    sync();
    if (nextIndex !== index) show(nextIndex);
    if (announce) clockStatus.textContent = `Tiempo simulado: ${timeValue.textContent}.`;
  }


  function draw(frame) {
    plot.draw(frame);
    for (const id of ids) find(`distance-${id.toLowerCase()}`).textContent = format(frame[id].r);
    for (const [id, sector] of [['current',frame.actual], ['reference',frame.referencia]]) {
      find(`interval-${id}`).textContent = interval(sector);
      find(`area-${id}`).textContent = format(sector.area);
      find(`speed-${id}`).textContent = format(sector.v);
    }
  }

  async function load() {
    loading?.abort();
    playing = false;
    scene = null;
    clock.disabled = true;
    sync();
    const request = new AbortController();
    loading = request;
    eValue.textContent = format(e.valueAsNumber);
    aValue.textContent = `${format(a.valueAsNumber)} UA`;
    note.textContent = 'Cargando las órbitas…';
    retry.hidden = true;
    measurements.hidden = true;
    find('model').setAttribute('hidden','');
    try {
      const response = await fetch('/api/kepler/escena', {
        method:'POST', signal:request.signal, headers:{'Content-Type':'application/json'},
        body: JSON.stringify({excentricidad:e.valueAsNumber, semieje_b:a.valueAsNumber}),
      });
      if (!response.ok) throw new Error('Órbitas no disponibles');
      const result = await response.json();
      if (request.signal.aborted) return;
      scene = result;
      time.max = scene.frames.at(-1).t;
      time.step = scene.frames[1].t;
      clock.disabled = false;
      plot.show(scene);
      for (const id of ids) {
        const key = id.toLowerCase();
        const orbit = scene[id];
        find(`axis-${key}`).textContent = format(orbit.a);
        find(`period-${key}`).textContent = format(orbit.periodo);
        find(`ratio-${key}`).textContent = format(orbit.cociente);
      }
      find('mu').textContent = `μ = ${format(scene.mu)} UA³/año² · 4π²/μ = ${format(scene.cociente_teorico)} años²/UA³`;
      find('sector-duration').textContent = `Duración de cada sector: ${format(scene.duracion_sector)} años.`;
      show(index);
      sync();
      measurements.hidden = false;
      note.textContent = '';
    } catch (error) {
      if (request.signal.aborted) return;
      note.textContent = 'El motor orbital no respondió. Revisá que Synapsis esté abierto desde su lanzador.';
      retry.hidden = false;
    }
  }

  e.addEventListener('input',load);
  a.addEventListener('input',load);
  retry.addEventListener('click',load);
  time.addEventListener('input',() => seek(Math.round(time.valueAsNumber/Number(time.step)),false));
  back.addEventListener('click',() => seek(index-1));
  forward.addEventListener('click',() => seek(index+1));
  find('reset').addEventListener('click',() => seek(0));
  play.addEventListener('click',() => {
    if (!scene || !enabled) return;
    playing = !playing;
    if (playing && index === scene.frames.length-1) show(0);
    if (!playing) clockStatus.textContent = `Pausa en ${timeValue.textContent}.`;
    sync();
  });
  new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    sync();
  }).observe(section.querySelector('.kepler-figure'));
  document.addEventListener('visibilitychange',sync);
  load();
  return {
    setEnabled(value) { enabled = value; sync(); },
    setObscured(value) { obscured = value; sync(); },
  };
}

export function bindKeplerLab(section) {
  const scene = bindScene(section.querySelector('#kepler-scene'));
  const legacy = section.querySelector('.kepler-legacy');
  let experiments;
  let enabled = false;
  let obscured = false;
  const sync = () => {
    scene.setEnabled(enabled);
    scene.setObscured(obscured || legacy.open);
    experiments?.setEnabled(enabled && legacy.open);
    experiments?.setObscured(obscured);
  };
  legacy.addEventListener('toggle', () => {
    if (legacy.open && !experiments) experiments = bindOrbit(legacy);
    sync();
  });
  return {
    setEnabled(value) { enabled = value; sync(); },
    setObscured(value) { obscured = value; sync(); },
  };
}
