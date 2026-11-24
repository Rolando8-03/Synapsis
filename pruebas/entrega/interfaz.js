(async ({cases,algebra,measure}) => {
  const $ = query => document.querySelector(query);
  const all = query => [...document.querySelectorAll(query)];
  const sleep = delay => new Promise(resolve => setTimeout(resolve, delay));
  const check = (condition,message) => {
    if (!condition) throw Error(location.hash + ' · ' + message);
  };
  async function observe(predicate) {
    for (let i=0; i<240; i++) {
      const result=predicate();
      if (result) return result;
      await sleep(25);
    }
    throw Error('No se observó el resultado en ' + location.hash);
  }
  const tab = name => {
    const button=all('#ws-results [role="tab"]').find(item=>item.textContent===name);
    check(button, 'Falta la pestaña '+name);
    button.click();
  };
  const edit = () => $('.ws-result-actions button').click();
  const change = (input,value,event='input') => {
    input.value=value;
    input.dispatchEvent(new Event(event,{bubbles:true}));
  };
  const setDraft = (module,operation,values) => {
    localStorage.setItem('synapsis-historial-escritorio',JSON.stringify([{module,op:operation,date:0,
      draft:{values,options:{steps:true}}}]));
  };
  const read = (body,key) => key.split('.').reduce((value,part)=>value?.[part],body);
  const hardware = {};
  const catalog = await (await fetch('/api/catalogo')).json();
  let last;
  const realFetch = window.fetch.bind(window);
  window.fetch = async (url,options) => {
    if (url!=='/api/calcular') return realFetch(url,options);
    const started=performance.now();
    const response=await realFetch(url,options);
    last={request:JSON.parse(options.body),reply:await response.clone().json(),
      ms:performance.now()-started};
    return response;
  };
  let paints = 0;
  const clear = CanvasRenderingContext2D.prototype.clearRect;
  CanvasRenderingContext2D.prototype.clearRect = function (...rect) {
    if (this.canvas.matches('canvas.plot')) paints++;
    return clear.apply(this,rect);
  };

  async function restore(route, inputs) {
    const [module,operation]=route.split('/');
    if (location.hash !== '#'+route) location.hash=route;
    await observe(()=>$('#ws-operations [aria-current="page"]')?.hash==='#'+route && !$('#workspace').hidden && !$('#ws-history-link').disabled);
    const values={...inputs};
    for (const field of catalog.operations[operation].fields) {
      if (values[field.name] === undefined && field.kind === 'select') values[field.name]=field.default;
      if (values[field.name] === undefined && field.kind === 'boolean') values[field.name]=field.default===true;
      if (['matrix','vector','vectors'].includes(field.kind) && typeof values[field.name]==='string') {
        values[field.name]=values[field.name].split('\n').map(row=>row.split(/\s+/));
      }
    }
    setDraft(module,operation,values);
    if ($('#ws-history-link').getAttribute('aria-pressed')!=='true') $('#ws-history-link').click();
    last=null;
    $('#ws-history-items button').click();
    await observe(()=>!$('#ws-error').hidden || (last?.request.operation===operation && !$('#ws-results').hidden));
    return last?.reply ?? {status:'invalid_input',error:{message:$('#ws-error').textContent}};
  }

  const bisection = 'raices/raices.biseccion';
  const params = {expresion:'x^2-2', inferior:'1',superior:'2', tolerancia_x:'1e-12',criterio:'cota'};

  async function longGraph() {
    const reply = await restore(bisection,params);
    const calculation=last.ms;
    check(reply.status==='ok' && reply.result.tabla.length>=30,'Bisección de referencia');
    check(!$('#ws-results .ws-step-card'),'La traza se volvió a renderizar antes de abrir Procedimiento');
    paints=0;
    const started=performance.now();
    tab('Gráfica');
    const canvas=$('#ws-results canvas.plot');
    check(canvas?.getContext('2d'),'No se pudo abrir la gráfica');
    const firstPaintMs=performance.now()-started;
    const firstPaints=paints;
    const selector=$('.ws-iteration-control select');
    const pixels=canvas.toDataURL();
    canvas.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
    check(selector.value==='2' && canvas.getAttribute('aria-label').includes('iteración 2'),'La flecha de la gráfica no cambió el marcador');
    check(canvas.toDataURL()!==pixels,'El marcador de la gráfica no cambió');
    tab('Iteraciones');
    paints=0;
    const rows=all('#ws-result-content tbody tr');
    rows[29].click();
    check(selector.value==='30' && rows[29].classList.contains('ws-iteration-active'),'La fila 30 no quedó seleccionada');
    const hiddenPaints=paints;
    tab('Gráfica');
    check(canvas.getAttribute('aria-label').includes('iteración 30'),'Gráfica desincronizada');
    change(selector,'1','change');
    tab('Procedimiento');
    const initialSteps=all('#ws-result-content .ws-step-card').length;
    check(initialSteps===18,'El primer lote de pasos debe tener 18 entradas');
    change(selector,'30','change');
    const focused=$('#ws-result-content .ws-iteration-active [data-plain]');
    const step=reply.steps.find(item=>item.data?.iteracion===30);
    check(focused?.dataset.plain===step?.formula,'No coincide la fórmula activa de la iteración 30');
    all('.ws-playback button').find(button=>button.textContent==='Ver paso a paso').click();
    const play=all('.ws-playback button').find(button=>button.textContent==='Reproducir');
    play.click();
    check(play.textContent==='Pausar','No se pudo reproducir');
    play.click();
    check(play.textContent==='Reproducir','No se pudo pausar');
    play.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowRight',bubbles:true}));
    check(selector.value==='31','La flecha del procedimiento no cambió la iteración');
    return {calculation, firstPaintMs,firstPaints,hiddenPaints,initialSteps,totalSteps:reply.steps.length};
  }

  if (measure) {
    hardware.measurements=[];
    for (let i=0;i<5;i++) {
      delete $('#ws-results').dataset.selectedTab;
      hardware.measurements.push(await longGraph());
    }
  } else {
    for (const entry of cases) {
      document.documentElement.dataset.deliveryCase=entry.reference;
      const reply=await restore(entry.route,entry.inputs);
      check(reply.status===entry.status,entry.reference + ' ' + JSON.stringify(reply.error));
      for (const [key,value] of Object.entries(entry.expected)) {
        check(JSON.stringify(read(reply.result,key))===JSON.stringify(value),entry.reference+' · '+key);
      }
      for (const key of entry.absent) check(!(key in reply.result),entry.reference+' · salida innecesaria '+key);
      if (entry.absent.length) check(reply.result.formula_latex.includes('\\int_{0}^{1}'),'El área queda como integral');
      tab('Procedimiento');
      check($('#ws-result-content ol li') || $('#ws-result-content .ws-step-card'),entry.reference+' · sin pasos visibles');
      check(document.documentElement.scrollWidth<=innerWidth, entry.reference+' · desbordamiento horizontal');
    }
    for (const entry of cases.slice(0,algebra)) {
      document.documentElement.dataset.deliveryCase=entry.reference+' · fallo';
      const reply=await restore(entry.route,{...entry.inputs,...entry.failure});
      if (entry.rejected) {
        check(!['ok','infinite'].includes(reply.status) && (!$('#ws-error').hidden || $('#ws-results .result-error, #ws-results .ws-warning')),entry.reference+' · sin diagnóstico de fallo');
      } else {
        for (const [key,value] of Object.entries(entry.invalid)) {
          check(read(reply.result,key)===value,entry.reference+' · caso límite '+key);
        }
      }
    }
    for (const theme of ['light','dark']) {
      location.hash='#modulos';
      await observe(()=>$('#workspace').hidden);
      localStorage.setItem('synapsis-motion','true');
      if (!document.documentElement.classList.contains('serious')) $('#mode').click();
      await observe(()=>document.documentElement.classList.contains('serious'));
      if (document.documentElement.dataset.seriousTheme!==theme) $('#theme').click();
      const reply=await restore(bisection,params);
      check(document.documentElement.dataset.seriousTheme===theme && reply.result.expresion===params.expresion,'Tema o expresión original');
      edit();
      const editor=$('#ws-fields math-field:not([hidden])');
      if (editor) {
        check(editor.value.replace(/[{}\s]/g,'')===params.expresion,'El historial no repuso la expresión');
        editor.setValue('x^{2}-3');
        editor.dispatchEvent(new Event('input',{bubbles:true}));
      } else {
        const text=$('#ws-fields .ws-derivative input[type=text]:not([hidden])');
        check(text?.value===params.expresion,'El historial no repuso la expresión');
        change(text,'x^2-3');
      }
      $('#ws-calculate').focus();
      await sleep(80);
      $('#ws-calculate').click();
      await observe(()=>last?.request.input.expresion==='x^2-3' && !$('#ws-results').hidden);
      const updated=last.reply;
      check($('#ws-results .ws-active-expression').textContent.includes('x^2-3'),'Función antigua en la cabecera');
      tab('Iteraciones');
      check(all('#ws-result-content tbody tr').length===updated.result.tabla.length,'Tabla de otro cálculo');
      const third=updated.result.tabla[2];
      check($('#ws-result-content tbody tr:nth-child(3) td:nth-child(4)').textContent.includes(third.x_decimal),'Fila de otro cálculo');
      tab('Procedimiento');
      check($('#ws-result-content [data-plain]').dataset.plain===updated.steps[0].formula,'Procedimiento de otro cálculo');
      tab('Gráfica');
      const coords=updated.result.grafico_raiz.iteraciones;
      check(coords.length===updated.result.tabla.length,'Gráfica de otro cálculo');
      check(Math.abs(Number(coords[2][1])**2-3-Number(coords[2][2]))<1e-12,'Muestra de otra función');
    }
    delete $('#ws-results').dataset.selectedTab;
    const graph=await longGraph();
    const stopped=await restore('raices/raices.newton',{expresion:'x^2-2',inicial:'0'});
    check(stopped.status==='breakdown' && stopped.result.residual==='2','Newton detenido perdió el residuo');
    check($('#ws-results').textContent.includes('Último punto calculado') && $('#ws-results').textContent.includes('derivada es cero'),'Newton detenido perdió la explicación');
    const riemann=await restore('grafica/calculo.riemann',{expresion:'x^2',inferior:'0',superior:'1',muestra:'medio',n:'4'});
    tab('Resultado');
    const control=$('#ws-riemann-n');
    const render=riemann.result.visual_integral;
    const canvas=$('#ws-result-content canvas');
    const prior=canvas.toDataURL();
    change(control,String(render.inicial+1));
    const frame=render.cuadros[render.inicial+1];
    check($('#ws-result-content output').textContent.includes('n = '+frame.n) &&
      $('#ws-result-content output').textContent.includes(frame.suma) && canvas.toDataURL()!==prior,'Riemann no actualizó suma y rectángulos');
    hardware.verified={examples:cases.length, boundaries:algebra,themes:2,graph};
  }
  document.title='ENTREGA '+JSON.stringify({ok:true,...hardware});
})(globalThis.delivery).catch(error=>{
  document.title='ENTREGA '+JSON.stringify({ok:false,error:error.message,stack:error.stack?.split('\n').slice(0,4)});
});
