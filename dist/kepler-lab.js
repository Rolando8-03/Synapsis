import { motor } from './transport.js';
import { bindOrbit } from './orbit.js';

const number = new Intl.NumberFormat('es-NI', { maximumFractionDigits: 4, useGrouping: false });
const format = value => number.format(value);
const interval = sector => `${format(sector.inicio_t)} a ${format(sector.fin_t)}`;
const ids = ['A', 'B'];
const updateText = (element, value) => {
  if (element.textContent !== value) element.textContent = value;
};

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

function orbitalProcedure(find) {
  const element = find('work');
  const stepsA = find('work-a');
  const stepsB = find('work-b');
  const area = find('work-area');
  const time = find('work-time');
  let previous;
  const showLines = (list, lines) => {
    while (list.children.length < lines.length) list.append(document.createElement('li'));
    lines.forEach((line,i) => { list.children[i].textContent = line; });
  };
  function draw(scene, frame) {
    if (!element.open || (previous?.scene === scene && previous.frame === frame)) return;
    previous = {scene,frame};
    time.textContent = `t = ${format(frame.t)} años. Los ángulos se expresan en radianes y se muestran redondeados.`;
    for (const [i,id] of ids.entries()) {
      const {a,b,e,periodo} = scene[id];
      const {M,E,p,r,v} = frame[id];
      showLines(i === 0 ? stepsA : stepsB,[
        `Semieje menor · b = a√(1 − e²) = ${format(a)}√(1 − ${format(e)}²) ≈ ${format(b)} UA.`,
        `Anomalía media · M = (2πt/T) módulo 2π = (2π × ${format(frame.t)}/${format(periodo)}) módulo 2π ≈ ${format(M)} rad.`,
        `Anomalía excéntrica · al resolver E − ${format(e)} sen E = ${format(M)} resulta E ≈ ${format(E)} rad.`,
        `Posición (x, y) · x = a(cos E − e), y = b sen E. Con E ≈ ${format(E)}, (x, y) ≈ (${format(p[0])}, ${format(p[1])}) UA.`,
        `Rapidez · v = √[μ(2/r − 1/a)] ≈ ${format(v)} UA/año con r ≈ ${format(r)} UA.`,
        `Período · T = 2π√(a³/μ) = 2π√(${format(a)}³/${format(scene.mu)}) ≈ ${format(periodo)} años.`,
      ]);
    }
    const {a,b,e} = scene.A;
    showLines(area,[frame.actual,frame.referencia].map(sector => {
      const {E_inicial,E_final,delta_E} = sector;
      return `[${interval(sector)}] años · Área = ab[ΔE − e(sen E₂ − sen E₁)]/2 ≈ ${format(a)} × ${format(b)}/2 × [${format(delta_E)} − ${format(e)}(sen ${format(E_final)} − sen ${format(E_inicial)})] ≈ ${format(sector.area)} UA².`;
    }));
  }
  return {element,draw};
}

function bindScene(section) {
  const find = id => section.querySelector(`#kepler-${id}`);
  const plot = diagram(find);
  const procedure = orbitalProcedure(find);
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
  const distances = ['a','b'].map(id => find(`distance-${id}`));
  const sectorCells = ['current','reference'].map(id => ({
    interval:find(`interval-${id}`), area:find(`area-${id}`), speed:find(`speed-${id}`),
  }));
  const cache = new Map();
  let loading;
  let delay;
  let pendingKey;
  let activeKey;
  let initialized = false;
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
    updateText(play,enabled && playing ? 'Pausar' : 'Reproducir');
    play.disabled = !enabled;
    play.title = enabled ? '' : 'Activá las animaciones de la página para reproducir.';
    const moving = scene && !clock.disabled && playing && enabled && inView && !obscured && !document.hidden;
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
    procedure.draw(scene,frame);
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
    if (!scene || clock.disabled) return;
    playing = false;
    sync();
    if (nextIndex !== index) show(nextIndex);
    if (announce) clockStatus.textContent = `Tiempo simulado: ${timeValue.textContent}.`;
  }

  function draw(frame) {
    plot.draw(frame);
    ids.forEach((id,i) => updateText(distances[i],format(frame[id].r)));
    [frame.actual,frame.referencia].forEach((sector,i) => {
      const cells = sectorCells[i];
      updateText(cells.interval,interval(sector));
      updateText(cells.area,format(sector.area));
      updateText(cells.speed,format(sector.v));
    });
  }

  function ready() {
    pendingKey = undefined;
    note.textContent = '';
    retry.hidden = true;
    clock.disabled = false;
    measurements.removeAttribute('aria-busy');
    sync();
  }

  function applyScene(key, result) {
    cache.delete(key);
    cache.set(key,result);
    if (cache.size > 6) cache.delete(cache.keys().next().value);
    activeKey = key;
    scene = result;
    time.max = scene.frames.at(-1).t;
    time.step = scene.frames[1].t;
    plot.show(scene);
    for (const id of ids) {
      const field = id.toLowerCase();
      const orbit = scene[id];
      updateText(find(`axis-${field}`),format(orbit.a));
      updateText(find(`period-${field}`),format(orbit.periodo));
      updateText(find(`ratio-${field}`),format(orbit.cociente));
    }
    updateText(find('mu'),`μ = ${format(scene.mu)} UA³/año² · 4π²/μ = ${format(scene.cociente_teorico)} años²/UA³`);
    updateText(find('sector-duration'),`Duración de cada sector: ${format(scene.duracion_sector)} años.`);
    show(index);
    measurements.hidden = false;
    procedure.element.hidden = false;
    ready();
  }

  async function load(key, parameters) {
    const request = new AbortController();
    loading = request;
    try {
      const result = await motor.scene(parameters, {signal:request.signal,
        onProgress(message) { if (!request.signal.aborted && pendingKey === key) updateText(note,message); },
      });
      if (!request.signal.aborted && pendingKey === key) applyScene(key,result);
    } catch (error) {
      if (request.signal.aborted || pendingKey !== key) return;
      note.textContent = scene
        ? 'El motor orbital no respondió. Se muestran los parámetros anteriores.'
        : 'El motor orbital no respondió. Podés reintentar la carga.';
      measurements.removeAttribute('aria-busy');
      retry.hidden = false;
    } finally {
      if (loading === request) loading = undefined;
    }
  }

  function selectOrbits(wait = 0) {
    initialized = true;
    clearTimeout(delay);
    loading?.abort();
    const parameters = {excentricidad:e.valueAsNumber, semieje_b:a.valueAsNumber};
    const key = `${parameters.excentricidad}:${parameters.semieje_b}`;
    updateText(eValue,format(parameters.excentricidad));
    updateText(aValue,`${format(parameters.semieje_b)} UA`);
    e.setAttribute('aria-valuetext',eValue.textContent);
    a.setAttribute('aria-valuetext',aValue.textContent);
    if (key === activeKey) {
      ready();
      return;
    }
    playing = false;
    clock.disabled = true;
    sync();
    pendingKey = key;
    const cached = cache.get(key);
    if (cached) {
      applyScene(key,cached);
      return;
    }
    updateText(note,scene ? 'Actualizando órbitas. Se muestran los parámetros anteriores.' : 'Cargando las órbitas…');
    retry.hidden = true;
    measurements.setAttribute('aria-busy','true');
    if (wait) delay = setTimeout(() => load(key,parameters),wait);
    else load(key,parameters);
  }

  procedure.element.addEventListener('toggle', () => {
    if (scene) procedure.draw(scene,scene.frames[index]);
  });
  e.addEventListener('input',() => selectOrbits(80));
  a.addEventListener('input',() => selectOrbits(80));
  retry.addEventListener('click',() => selectOrbits());
  time.addEventListener('input',() => seek(Math.round(time.valueAsNumber/Number(time.step)),false));
  back.addEventListener('click',() => seek(index-1));
  forward.addEventListener('click',() => seek(index+1));
  find('reset').addEventListener('click',() => seek(0));
  play.addEventListener('click',() => {
    if (!scene || clock.disabled || !enabled) return;
    playing = !playing;
    if (playing && index === scene.frames.length-1) show(0);
    if (!playing) clockStatus.textContent = `Pausa en ${timeValue.textContent}.`;
    sync();
  });
  new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    if (inView && !initialized) selectOrbits();
    sync();
  }).observe(section.querySelector('.kepler-layout'));
  document.addEventListener('visibilitychange',sync);
  window.addEventListener('synapsis:pause', () => { playing = false; sync(); });
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
