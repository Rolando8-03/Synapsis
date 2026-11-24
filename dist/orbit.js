import { motor } from './transport.js';
const CENTER_Y = 174;
const TIME_LIMIT = 12;
const decimal = new Intl.NumberFormat('es-NI', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
const years = value => `${decimal.format(value)} ${value === 1 ? 'año' : 'años'}`;

const laws = {
  1: {
    name: 'Primera ley de Kepler',
    formula: 'd₁ + d₂ = 2a',
    note: 'La órbita es una elipse y la estrella ocupa uno de sus focos. Cambiá la excentricidad para ver cómo se separan los focos.',
    chart: 'Órbita elíptica con la estrella en uno de sus dos focos. Las líneas indican la distancia a cada foco.',
    readouts: ['Distancia d₁ / a', 'Distancia d₂ / a', 'Suma de distancias / a'],
  },
  2: {
    name: 'Segunda ley de Kepler',
    formula: 'Áreas iguales · tiempos iguales',
    note: 'Los dos sectores corresponden al mismo intervalo de tiempo. Observá cómo el planeta se mueve más rápido cerca de la estrella.',
    chart: 'Órbita con dos sectores de igual área que representan intervalos de tiempo iguales.',
    readouts: ['Distancia r / a', 'Rapidez relativa', 'Área de cada sector'],
  },
  3: {
    name: 'Tercera ley de Kepler',
    formula: 'P² ∝ a³',
    note: 'Compará dos órbitas circulares alrededor de una estrella como el Sol. La órbita A tiene un semieje de 1 UA. Cambiá el de B y compará cuánto tardan en dar una vuelta.',
    chart: 'Dos órbitas circulares alrededor de la misma estrella. A es dorada y B es violeta.',
    readouts: ['Período A', 'Período B', 'P² / a³ (años² / UA³)'],
  },
};

function move(element, x, y) {
  element.setAttribute('transform', `translate(${x.toFixed(2)} ${y.toFixed(2)})`);
}

function connect(line, x1, x2, y2) {
  line.setAttribute('x1', x1.toFixed(2));
  line.setAttribute('y1', CENTER_Y);
  line.setAttribute('x2', x2.toFixed(2));
  line.setAttribute('y2', y2.toFixed(2));
}

export function bindOrbit(section) {
  const select = id => section.querySelector(`#orbit-${id}`);
  const tabs = [...section.querySelectorAll('[role="tab"]')];
  const panel = section.querySelector('[role="tabpanel"]');
  const heading = select('law-title');
  const formula = select('formula');
  const note = select('intro');
  const graph = select('chart');
  const shape = select('shape');
  const phase = select('phase');
  const shapeValue = select('shape-value');
  const phaseValue = select('phase-value');
  const shapeLabel = select('shape-label');
  const phaseLabel = select('phase-label');
  const ellipseModel = select('ellipse-model');
  const periodModel = select('period-model');
  const areaMarkers = select('area-markers');
  const foci = select('foci');
  const ellipse = select('ellipse');
  const liveArc = select('sector-live');
  const earlierArc = select('sector-reference');
  const focus = select('focus');
  const focusLabel = select('focus-label');
  const secondFocus = select('second-focus');
  const planet = select('planet');
  const vector = select('vector');
  const secondVector = select('second-vector');
  const trackB = select('track-b');
  const planetA = select('planet-a');
  const planetB = select('planet-b');
  const captions = [...section.querySelectorAll('.orbit-readouts dt')];
  const readouts = [...section.querySelectorAll('.orbit-readouts dd')];
  const play = select('play');
  const reset = select('reset');

  const experiments = [
    { shape: .55, time: .14 },
    { shape: .55, time: .14 },
    { shape: 2.25, time: .64 },
  ];
  let law = 1;
  let current = experiments[0];
  let allowed = false;
  let running = true;
  let inView = false;
  let obscured = false;
  let animation = 0;
  let lastTime = 0;
  let lastDraw = 0;

  let buffer;
  let request;
  let delay;
  const cache = new Map();

  function draw() {
    const period = law === 3;
    phase.value = String(current.time);
    const time = period ? years(current.time) : `${Math.round(current.time * 100)} %`;
    const size = `${decimal.format(current.shape)}${period ? ' UA' : ''}`;
    phaseValue.textContent = time;
    phase.setAttribute('aria-valuetext', time);
    shapeValue.textContent = size;
    shape.setAttribute('aria-valuetext', size);
    if (!buffer) return;
    const last = buffer.frames.length - 1;
    const index = Math.min(last, Math.round(current.time / buffer.duration * last));
    const frame = buffer.frames[index];
    const [x,y] = frame;
    let values;
    if (period) {
      trackB.setAttribute('r',buffer.radius);
      move(planetA,x,y);
      move(planetB,frame[2],frame[3]);
      values = [years(1), years(buffer.period), decimal.format(buffer.ratio)];
    } else {
      ellipse.setAttribute('ry', buffer.minor.toFixed(2));
      move(focus,buffer.focus,CENTER_Y);
      move(planet,x,y);
      connect(vector,buffer.focus,x,y);
      if (law === 1) {
        foci.toggleAttribute('hidden',current.shape === 0);
        focusLabel.textContent = current.shape === 0 ? 'Focos coincidentes' : 'F₁ · estrella';
        move(secondFocus,buffer.other,CENTER_Y);
        connect(secondVector,buffer.other,x,y);
        values = frame.slice(2).map(value => decimal.format(value));
      } else {
        focusLabel.textContent = 'Estrella';
        liveArc.setAttribute('d',frame[4]);
        earlierArc.setAttribute('d',frame[5]);
        values = [decimal.format(frame[2]), `${decimal.format(frame[3])}×`, `${buffer.area_percent} %`];
      }
    }
    readouts.forEach((readout,i) => {
      if (readout.textContent !== values[i]) readout.textContent = values[i];
    });
  }

  async function prepare() {
    clearTimeout(delay);
    request?.abort();
    const key = `${law}:${current.shape}`;
    buffer = cache.get(key);
    if (buffer) {
      draw();
      sync();
      return;
    }
    const controller = new AbortController();
    request = controller;
    const previousMessage = note.textContent;
    try {
      const result = await motor.orbit({ley:law, forma:current.shape}, {signal:controller.signal});
      if (controller.signal.aborted) return;
      if (cache.size >= 12) cache.delete(cache.keys().next().value);
      cache.set(key,result);
      buffer = result;
      draw();
      sync();
    } catch (error) {
      if (!controller.signal.aborted) note.textContent = `${previousMessage} El motor de órbitas no respondió.`;
    }
  }

  function tick(now) {
    if (lastTime) {
      const delta = Math.min(now - lastTime, 70);
      if (law === 3) {
        current.time = Math.min(TIME_LIMIT, current.time + delta / 5900);
        if (current.time >= TIME_LIMIT) {
          animation = 0;
          running = false;
          draw();
          sync();
          return;
        }
      } else {
        current.time = (current.time + delta / 13300) % 1;
      }
    }
    lastTime = now;
    if (now - lastDraw > 40) {
      draw();
      lastDraw = now;
    }
    animation = requestAnimationFrame(tick);
  }

  function sync() {
    const moving = Boolean(buffer) && allowed && running && inView && !obscured && !document.hidden;
    const label = allowed && running ? 'Pausar' : 'Reproducir';
    play.textContent = `${label} ${law === 3 ? 'órbitas' : 'órbita'}`;
    play.disabled = !allowed;
    play.title = allowed ? '' : 'Activá las animaciones de la página para reproducir.';
    if (moving && !animation) {
      lastTime = 0;
      animation = requestAnimationFrame(tick);
    } else if (!moving && animation) {
      cancelAnimationFrame(animation);
      animation = 0;
    }
  }

  function showLaw(next) {
    law = next;
    current = experiments[law - 1];
    const period = law === 3;
    const config = laws[law];
    for (const tab of tabs) {
      const selected = Number(tab.dataset.law) === law;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
      if (selected) panel.setAttribute('aria-labelledby', tab.id);
    }
    heading.textContent = config.name;
    formula.textContent = config.formula;
    note.textContent = config.note;
    graph.setAttribute('aria-label', config.chart);
    captions.forEach((caption, i) => { caption.textContent = config.readouts[i]; });
    ellipseModel.toggleAttribute('hidden', period);
    periodModel.toggleAttribute('hidden', !period);
    areaMarkers.toggleAttribute('hidden', law !== 2);
    foci.toggleAttribute('hidden', law !== 1);
    shapeLabel.textContent = period ? 'Semieje mayor de B' : 'Excentricidad';
    phaseLabel.textContent = period ? 'Tiempo simulado' : 'Tiempo orbital';
    shape.min = period ? '.60' : '0';
    shape.max = period ? '3' : '.88';
    shape.value = String(current.shape);
    phase.max = period ? String(TIME_LIMIT) : '1';
    phase.step = period ? '.01' : '.001';
    buffer = null;
    lastTime = 0;
    if (period && current.time >= TIME_LIMIT) running = false;
    draw();
    prepare();
    sync();
  }

  for (const tab of tabs) {
    tab.addEventListener('click', () => showLaw(Number(tab.dataset.law)));
    tab.addEventListener('keydown', event => {
      const index = tabs.indexOf(tab);
      const next = {
        ArrowRight: (index + 1) % tabs.length,
        ArrowLeft: (index - 1 + tabs.length) % tabs.length,
        Home: 0,
        End: tabs.length - 1,
      }[event.key];
      if (next === undefined) return;
      event.preventDefault();
      showLaw(next + 1);
      tabs[next].focus();
    });
  }
  shape.addEventListener('input', () => {
    current.shape = Number(shape.value);
    request?.abort();
    buffer = null;
    clearTimeout(delay);
    draw();
    sync();
    delay = setTimeout(prepare, 75);
  });
  phase.addEventListener('input', () => {
    current.time = Number(phase.value);
    running = false;
    sync();
    draw();
  });
  play.addEventListener('click', () => {
    if (!running && law === 3 && current.time >= TIME_LIMIT) current.time = 0;
    running = !running;
    sync();
    draw();
  });
  reset.addEventListener('click', () => {
    current.time = 0;
    running = false;
    sync();
    draw();
  });
  new IntersectionObserver(([entry]) => {
    inView = entry.isIntersecting;
    sync();
  }, { threshold: .16 }).observe(section.querySelector('.orbit-visual'));
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('synapsis:pause', () => { running = false; sync(); });
  showLaw(1);

  return {
    setEnabled(value) { allowed = value; sync(); },
    setObscured(value) { obscured = value; sync(); },
  };
}
