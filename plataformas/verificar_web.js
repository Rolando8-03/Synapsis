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
  const catalog = await motor.catalog({onProgress:message=>progress.push(message)});
  const startupMs = Math.round(performance.now()-start);
  const answers = [catalog];
  for (const [action,body] of cases.slice(1)) answers.push(await motor[methods[action]](body));
  const abort = new AbortController();
  const interrupted = motor.scene({excentricidad:.96, semieje_b:2.98},{signal:abort.signal});
  abort.abort();
  if (await interrupted.then(()=>false,error=>error.name === 'AbortError') !== true) throw Error('Falló la cancelación.');
  await motor.catalog();

  location.hash='grafica/calculo.derivar';
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
  window.synapsisParity={answers,startupMs,progress,cancellation:true,keyboardAndKatex:true,keplerTime:slider.value};
  document.title='PARIDAD OK';
})().catch(error=>{ document.title='PARIDAD ERROR '+error.message; });
