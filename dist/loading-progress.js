const stages = [
  'Iniciando Python',
  'Cargando dependencias matemáticas',
  'Cargando las operaciones',
  'Inicializando las bibliotecas',
  'Verificando el catálogo',
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
  track.setAttribute('aria-label','Avance de carga');
  const timing = document.createElement('p');
  timing.className = 'loading-timing';
  const remaining = document.createElement('p');
  remaining.className = 'loading-remaining';
  element.replaceChildren(header,track,timing,remaining);
  let state, timer, reveal;

  function tick() {
    const {startedAt, stageAt, completedItems, totalItems} = state;
    const now = performance.now();
    const elapsed = Math.max(0, Math.floor((now-startedAt)/1000));
    const spent = Math.max(0,(now-stageAt)/1000);
    let estimate = '';
    if (totalItems) {
      track.max = totalItems;
      track.value = completedItems;
      percent.textContent = `${completedItems}/${totalItems}`;
      if (completedItems > 0 && completedItems < totalItems && spent >= 1) {
        estimate = ` · ≈ ${duration(Math.ceil(spent*(totalItems-completedItems)/completedItems))} para esta etapa`;
      }
    } else {
      track.removeAttribute('value');
      percent.textContent = '';
    }
    timing.textContent = `${duration(elapsed)} transcurridos${estimate}`;
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
    state = next;
    const {stage, task, viewOnly, totalItems, completedItems, cachedItems} = next;
    const label = (viewOnly ? '' : `Paso ${stage+1} de ${stages.length} · `)+(task ?? stages[stage]);
    if (text.textContent !== label) text.textContent = label;
    const pending = totalItems ? totalItems-completedItems : 0;
    const details = [pending ? `${pending} ${pending === 1 ? 'recurso pendiente' : 'recursos pendientes'}` : '',
      cachedItems ? `${cachedItems} desde la caché` : '',
      stage < renderStage ? `Sigue: ${stages[stage+1].toLowerCase()}` : ''].filter(Boolean).join(' · ');
    remaining.textContent = details;
    remaining.hidden = !details;
    if (!element.hidden || !viewOnly) {
      clearTimeout(reveal);
      show();
    } else reveal ??= setTimeout(show,120);
  };
}
