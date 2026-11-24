(async () => {
  const {motor} = await import(new URL('./transport.js', location.href));
  const methods = {'catalogo':'catalog', 'calcular':'calculate', 'kepler':'orbit', 'kepler/escena':'scene'};
  const cases = __CASOS__;
  const until = async (predicate,message) => {
    for (let i=0; i<400; i++) {
      const value = predicate();
      if (value) return value;
      await new Promise(resolve=>setTimeout(resolve,40));
    }
    throw Error(message);
  };
  const start = performance.now();
  const progress = [];
  const unsubscribe = motor.observeStartup(update => {
    if (typeof update?.stage === 'number') progress.push(update.stage);
  });
  const pendingCatalog = motor.catalog();
  const loading = document.querySelector('#engine-loading');
  await until(() => !loading.hidden || motor.isReady(), 'El motor no informó su estado de arranque.');
  if (/SymPy|mpmath/.test(loading.textContent)) throw Error('La barra debe usar lenguaje claro.');
  location.hash='grafica/calculo.derivar';
  const catalog = await pendingCatalog;
  await until(()=>document.querySelector('#ws-fields math-field'), 'No se abrió el editor después del arranque');
  await until(()=>loading.hidden, 'La barra global quedó visible después del arranque');
  if (document.querySelector('#ws-message').textContent.trim()) throw Error('Quedó un aviso tras abrir la calculadora.');
  unsubscribe();
  if (!motor.isReady()) throw Error('Falta la verificación final del catálogo.');
  const startupMs = Math.round(performance.now()-start);
  const answers = [catalog];
  for (const [action,body] of cases.slice(1)) answers.push(await motor[methods[action]](body));
  const abort = new AbortController();
  const interrupted = motor.scene({excentricidad:.96, semieje_b:2.98},{signal:abort.signal});
  abort.abort();
  if (await interrupted.then(()=>false,error=>error.name === 'AbortError') !== true) throw Error('Falló la cancelación.');
  await motor.catalog();

  const editor=await until(()=>document.querySelector('#ws-fields math-field'), 'No cargó MathLive');
  editor.focus();
  for (const label of ['x','Exponente','3']) {
    const key=[...document.querySelectorAll('.ws-power-keys button')].find(button=>
      button.textContent === label || button.getAttribute('aria-label') === label);
    if (!key) throw Error('Falta la tecla '+label);
    key.click();
  }
  document.querySelector('#ws-calculate').focus();
  await new Promise(resolve=>setTimeout(resolve,90));
  document.querySelector('#ws-calculate').click();
  await until(()=>!document.querySelector('#ws-results').hidden && document.querySelector('#ws-result-content math'),
    'No se mostró el resultado con KaTeX. '+document.querySelector('#ws-message')?.textContent);
  if (!loading.hidden || document.querySelector('#ws-message').textContent.trim()) {
    throw Error('Quedó un aviso técnico al volver a usar la calculadora.');
  }
  location.hash='orbita';
  const chart=await until(()=>document.querySelector('#kepler-chart'), 'No hay gráfica orbital');
  chart.scrollIntoView();
  const clock=await until(()=>{
    const control=document.querySelector('#kepler-clock');
    return !control?.disabled && control;
  },'No se activó el reloj común. '+document.querySelector('#kepler-status')?.textContent);
  const slider=clock.querySelector('#kepler-time');
  const before=chart.querySelector('#kepler-sector-current').getAttribute('d');
  slider.value='.50';
  slider.dispatchEvent(new Event('input',{bubbles:true}));
  if (chart.querySelector('#kepler-sector-current').getAttribute('d') === before) throw Error('La escena no avanzó.');
  const label = id => document.querySelector('#kepler-' + id).textContent.trim();
  const track = document.querySelector('#kepler-track-a');
  const angle = track.getAttribute('d');
  chart.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
  if (track.getAttribute('d') === angle || slider.valueAsNumber !== .5) throw Error('La cámara no gira de forma independiente.');
  const rotated = track.getAttribute('d');
  chart.dispatchEvent(new WheelEvent('wheel',{deltaY:-120,bubbles:true,cancelable:true}));
  if (track.getAttribute('d') === rotated || slider.valueAsNumber !== .5) throw Error('La cámara no amplió el instante.');
  if (label('axis-a') !== '1' || label('focal-a') !== '2' || label('area-current') !== label('area-reference')
      || label('ratio-a') !== label('ratio-b')) throw Error('Las mediciones de las tres leyes no coinciden.');
  if (!document.querySelector('#kepler-loading').hidden || document.querySelector('#kepler-status').textContent.trim()) {
    throw Error('Quedó un aviso después de abrir Kepler.');
  }
  window.synapsisParity={answers,loadingDismissed:true,startupMs,progress,cancellation:true,keyboardAndKatex:true,keplerTime:slider.value};
  document.title='PARIDAD OK';
})().catch(error=>{ document.title='PARIDAD ERROR '+error.message; });
