// Los hitos llegan del trabajador. La barra estima el avance dentro del hito actual.
const stages = [
  ['Preparando el entorno de cálculo', .55],
  ['Preparando las herramientas matemáticas', .27],
  ['Cargando las operaciones de Synapsis', .1],
  ['Comprobando que todo esté listo', .08],
];
const duration = seconds => {
  const whole = Math.max(0, Math.ceil(seconds));
  return whole < 60 ? `${whole} s` : `${Math.floor(whole / 60)} min ${whole % 60} s`;
};

export function loadingProgress(element) {
  const text = document.createElement('p');
  text.className = 'loading-stage';
  text.setAttribute('role','status');
  const track = document.createElement('progress');
  track.max = 100;
  track.setAttribute('aria-label','Avance estimado de carga');
  const timing = document.createElement('p');
  timing.className = 'loading-timing';
  element.replaceChildren(text,track,timing);
  let state, timer, shown = 0;

  function tick() {
    const {stage, startedAt, stageAt} = state;
    const now = performance.now();
    const completed = stages.slice(0,stage).reduce((sum,[,weight]) => sum + weight,0);
    const weight = stages[stage][1];
    const baseline = completed > 0 ? Math.max(2, (stageAt-startedAt)/1000/completed) : 7;
    const spent = Math.max(0,(now-stageAt)/1000);
    const expected = baseline*weight;
    const fraction = spent < expected ? .83*spent/expected : .98-.15*expected/spent;
    shown = Math.max(shown,Math.min(99,100*(completed+weight*fraction)));
    track.value = shown;
    const left = Math.max(.6,expected-spent,spent*.35) + baseline*(1-completed-weight);
    timing.textContent = `${duration((now-startedAt)/1000)} transcurridos · ≈ ${duration(left)} restantes`;
  }

  return next => {
    if (!next) {
      clearInterval(timer);
      timer = undefined;
      state = undefined;
      element.hidden = true;
      return;
    }
    if (!state || state.startedAt !== next.startedAt) shown = 0;
    state = next;
    element.hidden = false;
    const label = `${state.stage+1} de ${stages.length} · ${stages[state.stage][0]}`;
    if (text.textContent !== label) text.textContent = label;
    tick();
    timer ??= setInterval(tick,200);
  };
}
