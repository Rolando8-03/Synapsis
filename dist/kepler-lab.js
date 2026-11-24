import { printReport, reportSection } from './result-print.js';
import { math } from './math-format.js';
import { loadingProgress, renderingProgress } from './loading-progress.js';
import { motor } from './transport.js';
import { orbitalDiagram } from './kepler-camera.js';

const number = new Intl.NumberFormat('es-NI', { maximumFractionDigits: 4, useGrouping: false });
const format = value => number.format(value);
const interval = sector => `${format(sector.inicio_t)} a ${format(sector.fin_t)}`;
const ids = ['A', 'B'];
const EPOCH = Date.UTC(2000, 0, 3);
const YEAR_MS = 365.25 * 86400000;
const dateAt = time => new Date(EPOCH + time * YEAR_MS).toISOString().slice(0,10);
const updateText = (element, value) => {
  if (element.textContent !== value) element.textContent = value;
};

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
  const plot = orbitalDiagram(find);
  const procedure = orbitalProcedure(find);
  const e = find('e');
  const a = find('a');
  const eValue = find('e-value');
  const aValue = find('a-value');
  const note = find('status');
  const progress = loadingProgress(find('loading'));
  const retry = find('retry');
  const measurements = find('measurements');
  const clock = find('clock');
  const time = find('time');
  const timeValue = find('time-value');
  const play = find('play');
  const date = find('date');
  const exportButton = find('export');
  const figure = find('figure');
  const settings = exportButton.closest('details');
  const fullscreen = find('fullscreen');
  const rate = find('rate');
  const back = find('back');
  const forward = find('forward');
  const clockStatus = find('clock-status');
  const distances = ['a','b'].map(id => find(`distance-${id}`));
  const foci = ['a','b'].map(id => find(`focal-${id}`));
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
    date.value = dateAt(frame.t);
    time.setAttribute('aria-valuetext',label);
    back.disabled = index === 0;
    forward.disabled = index === scene.frames.length-1;
    draw(frame);
    procedure.draw(scene,frame);
  }

  function tick(now) {
    started ??= now;
    const targetTime = startTime + (now-started)*.00025*Number(rate.value);
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
    ids.forEach((id,i) => {
      updateText(distances[i],format(frame[id].r));
      updateText(foci[i],format(frame[id].suma_focal));
    });
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
    progress(null);
    retry.hidden = true;
    clock.disabled = false;
    date.disabled = false;
    exportButton.disabled = false;
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
    date.max = dateAt(Number(time.max));
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
      const result = await motor.scene(parameters, {signal:request.signal});
      if (!request.signal.aborted && pendingKey === key) applyScene(key,result);
    } catch (error) {
      if (request.signal.aborted || pendingKey !== key) return;
      note.textContent = scene
        ? 'No se pudo actualizar la órbita. Se muestran los parámetros anteriores.'
        : 'No se pudo cargar la órbita.';
      progress(null);
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
    progress(null);
    const parameters = {excentricidad:.0167, semieje_b:a.valueAsNumber, excentricidad_b:e.valueAsNumber};
    const key = `${parameters.excentricidad_b}:${parameters.semieje_b}`;
    updateText(eValue,format(parameters.excentricidad_b));
    updateText(aValue,`${format(parameters.semieje_b)} UA`);
    e.setAttribute('aria-valuetext',eValue.textContent);
    a.setAttribute('aria-valuetext',aValue.textContent);
    if (key === activeKey) {
      ready();
      return;
    }
    playing = !scene && !matchMedia('(prefers-reduced-motion: reduce)').matches;
    clock.disabled = true;
    date.disabled = true;
    exportButton.disabled = true;
    sync();
    pendingKey = key;
    const cached = cache.get(key);
    if (cached) {
      applyScene(key,cached);
      return;
    }
    note.textContent = '';
    if (motor.isReady()) progress(renderingProgress('Actualizando las órbitas'));
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
  find('reset').addEventListener('click',() => { plot.reset(); seek(0); });
  date.addEventListener('change',() => {
    if (date.value && date.validity.valid) seek(Math.round((date.valueAsNumber-EPOCH)/YEAR_MS/Number(time.step)));
    if (scene) date.value = dateAt(scene.frames[index].t);
  });
  function syncFullscreen() {
    const expanded = document.fullscreenElement === figure || figure.classList.contains('kepler-expanded');
    fullscreen.textContent = expanded ? 'Salir de pantalla completa' : 'Pantalla completa';
    fullscreen.setAttribute('aria-pressed',String(expanded));
  }
  function setExpanded(expanded) {
    figure.classList.toggle('kepler-expanded',expanded);
    document.documentElement.classList.toggle('kepler-immersive',expanded);
    syncFullscreen();
  }
  fullscreen.addEventListener('click',async () => {
    if (document.fullscreenElement === figure) await document.exitFullscreen();
    else if (figure.classList.contains('kepler-expanded')) setExpanded(false);
    else {
      try {
        if (!document.fullscreenEnabled) throw Error();
        await figure.requestFullscreen();
      } catch { setExpanded(true); }
    }
    settings.open = false;
    find('chart').focus();
  });
  document.addEventListener('fullscreenchange',syncFullscreen);
  figure.addEventListener('keydown',event => {
    if (event.key === 'Escape' && figure.classList.contains('kepler-expanded')) setExpanded(false);
  });
  window.addEventListener('hashchange',() => setExpanded(false));
  rate.addEventListener('change',() => {
    if (animation) {
      started = null;
      startTime = scene.frames[index].t;
    }
  });
  play.addEventListener('click',() => {
    if (!scene || clock.disabled || !enabled) return;
    playing = !playing;
    if (playing && index === scene.frames.length-1) show(0);
    if (!playing) clockStatus.textContent = `Pausa en ${timeValue.textContent}.`;
    sync();
  });
  exportButton.addEventListener('click', async () => {
    if (!scene || clock.disabled) return;
    playing = false;
    sync();
    const wasOpen = procedure.element.open;
    procedure.element.open = true;
    procedure.draw(scene,scene.frames[index]);
    const steps = procedure.element.cloneNode(true);
    procedure.element.open = wasOpen;
    steps.querySelector('summary').remove();
    if (document.fullscreenElement === figure) await document.exitFullscreen();
    if (figure.classList.contains('kepler-expanded')) setExpanded(false);
    settings.open = false;
    const graph = find('chart').cloneNode(true);
    graph.removeAttribute('tabindex');
    graph.classList.add('pdf-graph');
    const capture = document.createElement('div');
    const instant = document.createElement('p');
    instant.textContent = `Tiempo simulado: ${timeValue.textContent} · Fecha del modelo: ${date.value}`;
    capture.append(instant,graph);
    const formulas = document.createElement('div');
    formulas.append(
      math('d_1+d_2=2a', 'Suma de distancias a los focos', true),
      math('A_1=A_2\\quad(\\Delta t_1=\\Delta t_2)', 'Áreas iguales en tiempos iguales', true),
      math('T^2/a^3=4\\pi^2/\\mu', 'Relación entre período y semieje', true),
    );
    printReport('Laboratorio de Kepler', [
      reportSection('Tres leyes de Kepler', formulas),
      reportSection('Gráfica orbital', capture),
      reportSection('Mediciones y comprobación', measurements.cloneNode(true)),
      reportSection('Procedimiento del instante', steps),
    ]);
  });
  new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    if (inView && !initialized) selectOrbits();
    sync();
  }).observe(find('chart'));
  document.addEventListener('visibilitychange',sync);
  window.addEventListener('synapsis:pause', () => { playing = false; sync(); });
  return {
    setEnabled(value) { enabled = value; sync(); },
    setObscured(value) { obscured = value; sync(); },
  };
}

export function bindKeplerLab(section) {
  return bindScene(section.querySelector('#kepler-scene'));
}
