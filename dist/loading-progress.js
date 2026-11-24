const stages = [
  ['Iniciando el motor', .47],
  ['Preparando las herramientas matemáticas', .24],
  ['Cargando las operaciones', .15],
  ['Verificando el motor', .08],
  ['Abriendo la vista', .06],
];
const renderStage = stages.length - 1;
const duration = whole => whole < 60 ? `${whole} s` : `${Math.floor(whole / 60)} min ${whole % 60} s`;

export function renderingProgress(task, previous) {
  const now = performance.now();
  return {stage:renderStage, task, startedAt:previous?.startedAt ?? now,
    stageAt:previous?.stage === renderStage ? previous.stageAt : now, viewOnly:previous?.viewOnly ?? !previous};
}

export function loadingProgress(element) {
  const header = document.createElement('div');
  header.className = 'loading-header';
  const text = document.createElement('p');
  text.className = 'loading-stage';
  text.setAttribute('role','status');
  const percent = document.createElement('span');
  percent.className = 'loading-percent';
  percent.setAttribute('aria-hidden','true');
  header.append(text,percent);
  const track = document.createElement('progress');
  track.max = 100;
  track.setAttribute('aria-label','Avance estimado de carga');
  const timing = document.createElement('p');
  timing.className = 'loading-timing';
  const remaining = document.createElement('p');
  remaining.className = 'loading-remaining';
  element.replaceChildren(header,track,timing,remaining);
  let state, timer, reveal, shown = 0;

  function tick() {
    const {stage, startedAt, stageAt, viewOnly, completedItems, totalItems} = state;
    const now = performance.now();
    const completed = viewOnly ? 0 : stages.slice(0,stage).reduce((sum,[,weight]) => sum+weight,0);
    const weight = viewOnly ? 1 : stages[stage][1];
    const baseline = viewOnly ? 1.2 : completed ? Math.max(2,(stageAt-startedAt)/1000/completed) : 7;
    const spent = Math.max(0,(now-stageAt)/1000);
    const expected = baseline*weight;
    const estimated = .98*spent/(spent+expected*.6);
    const confirmed = totalItems ? Math.min(.98,completedItems/totalItems) : 0;
    const value = Math.floor(100*(completed+weight*Math.max(confirmed,estimated)));
    shown = Math.max(shown,Math.min(99,value));
    track.value = shown;
    percent.textContent = `${shown} %`;
    const elapsed = duration(Math.max(0,Math.floor((now-startedAt)/1000)));
    const left = Math.max(.2,expected*(1-confirmed)-spent)+baseline*Math.max(0,1-completed-weight);
    const estimate = spent > 2*expected && confirmed < .98
      ? 'recalculando el tiempo restante' : `≈ ${duration(Math.ceil(left))} restantes`;
    timing.textContent = `${elapsed} transcurridos · ${estimate}`;
  }

  function show() {
    reveal = undefined;
    if (!state) return;
    element.hidden = false;
    tick();
    timer ??= setInterval(tick,125);
  }

  return next => {
    if (!next) {
      clearTimeout(reveal);
      clearInterval(timer);
      reveal = timer = state = undefined;
      element.hidden = true;
      return;
    }
    if (!state || state.startedAt !== next.startedAt) shown = 0;
    state = next;
    const {stage, task, viewOnly, totalItems, completedItems} = next;
    const label = (viewOnly ? '' : `Paso ${stage+1} de ${stages.length} · `)+(task ?? stages[stage][0]);
    if (text.textContent !== label) text.textContent = label;
    const pending = totalItems ? totalItems-completedItems : 0;
    const details = [pending ? `${pending} ${pending === 1 ? 'recurso pendiente' : 'recursos pendientes'}` : '',
      stage < renderStage ? `Sigue: ${stages[stage+1][0].toLowerCase()}` : ''].filter(Boolean).join(' · ');
    remaining.textContent = details;
    remaining.hidden = !details;
    if (!element.hidden || !viewOnly) {
      clearTimeout(reveal);
      show();
    } else reveal ??= setTimeout(show,120);
  };
}
