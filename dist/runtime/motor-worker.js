// El trabajador recibe únicamente acciones del contrato y objetos JSON.
const here = new URL('./', self.location.href);
const root = new URL('../../', here);

async function file(url, options) {
  const response = await fetch(url, options);
  if (!response.ok) throw new Error(`No se pudo cargar ${new URL(url, here).pathname.split('/').at(-1)} (${response.status}).`);
  return response;
}

function sri(hex) {
  return 'sha256-' + btoa(String.fromCharCode(...hex.match(/../g).map(pair => Number.parseInt(pair, 16))));
}

const progress = (stage, completedItems, totalItems) => postMessage({type:'progress', stage, completedItems, totalItems});

async function start() {
  progress(0);
  const versions = await (await file(new URL('version.json', here))).json();
  // Un paquete instalado en Android o Pages usa solo recursos internos.
  const packed = await fetch(new URL('empaquetado.json', here), {cache:'no-cache'});
  const local = packed.ok && (packed.headers.get('content-type') || '').includes('json')
    && (await packed.json()).local === true;
  let base = local ? new URL('pyodide/', here).href : `https://cdn.jsdelivr.net/pyodide/v${versions.pyodide}/full/`;
  try {
    importScripts(base + 'pyodide.js');
  } catch (error) {
    if (local) throw error;
    base = new URL('pyodide/', versions.publicRuntime).href;
    importScripts(base + 'pyodide.js');
  }
  const python = await self.loadPyodide({indexURL:base});
  const sourceDir = '/synapsis';
  const wheelsDir = '/synapsis-dependencias';
  const {FS} = python;
  FS.mkdirTree(sourceDir);
  FS.mkdirTree(wheelsDir);

  progress(1,0,versions.wheels.length);
  for (const [i,wheel] of versions.wheels.entries()) {
    const url = new URL(wheel.file, local ? here : versions.publicRuntime);
    const options = {integrity:sri(wheel.sha256)};
    const response = await file(url,options).catch(error => {
      if (local) throw error;
      return file(wheel.url,options);
    });
    python.unpackArchive(await response.arrayBuffer(), 'zip', {extractDir:wheelsDir});
    progress(1,i+1,versions.wheels.length);
  }

  progress(2);
  if (local) {
    const bytes = await (await file(new URL('python.zip', here))).arrayBuffer();
    python.unpackArchive(bytes, 'zip', {extractDir:sourceDir});
  } else {
    const paths = await (await file(new URL('archivos.json', here), {cache:'no-cache'})).json();
    progress(2,0,paths.length);
    for (let offset=0; offset<paths.length; offset+=12) {
      const batch = paths.slice(offset,offset+12);
      await Promise.all(batch.map(async path => {
        if (!/^[a-zA-Z0-9_]+(?:\/[a-zA-Z0-9_]+)*\.py$/.test(path)) throw new Error('Ruta inválida en el manifiesto.');
        const text = await (await file(new URL(path,root))).text();
        const target = sourceDir+'/'+path;
        FS.mkdirTree(target.slice(0,target.lastIndexOf('/')));
        FS.writeFile(target,text);
      }));
      progress(2,offset+batch.length,paths.length);
    }
  }
  progress(3);
  python.runPython(`import sys
sys.path[:0] = ["/synapsis", "/synapsis-dependencias"]
from motor_api import invoke_json
import sympy, mpmath
assert sympy.__version__ == "1.14.0" and mpmath.__version__ == "1.3.0"
`);
  postMessage({type:'ready'});
  return python.globals.get('invoke_json');
}

const engine = start();
engine.catch(error => postMessage({type:'boot-error', message:error.message}));
self.onmessage = async ({data:{id, action, body}}) => {
  try {
    const invoke = await engine;
    const response = JSON.parse(invoke(action, JSON.stringify(body ?? null)));
    postMessage({type:'result', id, ...response});
  } catch (error) {
    postMessage({type:'request-error', id, message:error.message});
  }
};
