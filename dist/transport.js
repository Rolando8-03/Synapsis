const entry = new URL('./', import.meta.url);
// Python/Qt sirve dist como raíz. Go Live, Pages y Android conservan la carpeta dist.
const staticSite = entry.pathname.endsWith('/dist/');
const aborted = () => new DOMException('Cálculo cancelado.', 'AbortError');

class WebMotor {
  worker = null;
  ready = false;
  queue = [];
  active = null;
  serial = 0;
  timer = null;
  progress = null;

  ask(action, body, {signal, onProgress} = {}) {
    if (signal?.aborted) return Promise.reject(aborted());
    return new Promise((resolve, reject) => {
      const item = {id:++this.serial, action, body, signal, onProgress, resolve, reject};
      item.abort = () => this.cancel(item);
      signal?.addEventListener('abort',item.abort,{once:true});
      this.queue.push(item);
      if (!this.worker) this.start();
      else if (!this.ready) onProgress?.(this.progress);
      this.dispatch();
    });
  }

  start() {
    try {
      const startedAt = performance.now();
      const worker = this.worker = new Worker(new URL('./runtime/motor-worker.js',entry));
      this.report({stage:0, startedAt, stageAt:startedAt});
      this.deadline(120000,'Python tardó demasiado en iniciar. Volvé a intentar.');
      worker.onmessage = ({data}) => {
        if (this.worker !== worker) return;
        switch (data.type) {
          case 'progress':
            if (data.stage > this.progress.stage) {
              this.report({stage:data.stage, startedAt, stageAt:performance.now()});
            }
            break;
          case 'ready':
            clearTimeout(this.timer);
            this.ready = true;
            this.report(null);
            this.dispatch();
            break;
          case 'boot-error':
            this.fail(new Error('No se pudo iniciar Python. '+data.message));
            break;
          case 'result':
          case 'request-error':
            if (this.active?.id !== data.id) return;
            this.finish(data);
            break;
        }
      };
      worker.onerror = () => this.fail(new Error('El trabajador de Python no respondió. Volvé a intentar.'));
      worker.onmessageerror = () => this.fail(new Error('No se pudo leer la respuesta del trabajador.'));
    } catch (error) {
      this.fail(error);
    }
  }

  report(progress) {
    this.progress = progress;
    for (const item of this.queue) item.onProgress?.(progress);
  }

  dispatch() {
    if (!this.ready || this.active || !this.queue.length) return;
    const item = this.active = this.queue.shift();
    this.deadline(180000,'El cálculo superó el tiempo de espera.');
    this.worker.postMessage({id:item.id, action:item.action, body:item.body});
  }

  deadline(ms, message) {
    clearTimeout(this.timer);
    this.timer = setTimeout(() => this.fail(new Error(message)), ms);
  }

  settle(item, result, error) {
    if (error) item.onProgress?.(null);
    item.signal?.removeEventListener('abort',item.abort);
    if (error) item.reject(error);
    else item.resolve(result);
  }

  finish(reply) {
    const item = this.active;
    clearTimeout(this.timer);
    this.active = null;
    this.settle(item, reply, reply.type === 'request-error' ? new Error(reply.message) : null);
    this.dispatch();
  }

  reset() {
    clearTimeout(this.timer);
    this.worker?.terminate();
    this.worker = null;
    this.ready = false;
    this.active = null;
    this.progress = null;
  }

  cancel(item) {
    if (this.active === item) {
      // Terminar el trabajador cancela también en Go Live y Pages, sin SharedArrayBuffer.
      this.reset();
      if (this.queue.length) this.start();
    } else this.queue = this.queue.filter(other => other !== item);
    this.settle(item, null, aborted());
  }

  fail(error) {
    const pending = this.active ? [this.active,...this.queue] : this.queue;
    this.reset();
    this.queue = [];
    for (const item of pending) this.settle(item, null, error);
  }
}

const web = staticSite ? new WebMotor() : null;

async function request(action, body, options = {}) {
  if (web) return web.ask(action,body,options);
  const config = body === undefined ? {} : {
    method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body),
  };
  const response = await fetch('/api/'+action, {...config,signal:options.signal});
  return {status:response.status,data:await response.json()};
}

async function requireSuccess(action, body, options) {
  const {status,data} = await request(action,body,options);
  if (status >= 400) throw new Error(data.error?.message ?? 'El motor de Synapsis no respondió.');
  return data;
}

export const motor = {
  catalog: options => requireSuccess('catalogo',undefined,options),
  calculate: async (body, options) => (await request('calcular',body,options)).data,
  orbit: (body, options) => requireSuccess('kepler',body,options),
  scene: (body, options) => requireSuccess('kepler/escena',body,options),
};
