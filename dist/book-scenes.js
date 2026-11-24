import { math } from './math-format.js';
import { node } from './matrix-input.js';
import { iterationSelection } from './iteration-selection.js';
import { plotCamera, plotPlayback } from './plot-controls.js';

const asText = (value, places=3) => String(Number(value.toFixed(places)));

function button(label, action) {
  const control = node('button','secondary',label);
  control.type = 'button';
  control.addEventListener('click', action);
  return control;
}

function input(label, value, type='text') {
  const container = node('label','ws-field',label);
  const field = node('input');
  field.type = type;
  field.value = value;
  field.inputMode = 'decimal';
  field.setAttribute('aria-label',label);
  container.append(field);
  return [container,field];
}

function imagePair(scene, update) {
  const body = node('div','ws-result-stack');
  const canvas = node('canvas','ws-book-canvas');
  canvas.width=670;
  canvas.height=360;
  canvas.setAttribute('role','img');
  canvas.setAttribute('aria-label','Imagen original y reconstrucción de rango '+scene.rango);
  const original = scene.original;
  const h = original.length, w = original[0].length;
  const sources = [original,scene.truncada].map(pixels => {
    const source = node('canvas');
    source.width = w;
    source.height = h;
    const context = source.getContext('2d');
    const image = context.createImageData(w,h);
    pixels.forEach((row,y)=>row.forEach((level,x)=>{
      const offset = (y*w+x)*4;
      image.data.set([level,level,level,255],offset);
    }));
    context.putImageData(image,0,0);
    return source;
  });
  const context=canvas.getContext('2d');
  const {controls,view}=plotCamera(canvas,()=>canvas.redrawPlot());
  const rows = Array.from({length:Math.min(h,40)},(_,i)=>Math.ceil((i+1)*h/Math.min(h,40)));
  const timeline=iterationSelection(rows,rows.length-1);
  const player=plotPlayback(timeline,{label:'Filas reconstruidas',interval:115,surface:canvas});
  const readout=node('output','ws-graph-reading');
  let row;
  canvas.redrawPlot=()=>{
    if (!canvas.isConnected) return;
    const scale=Math.min(288/w,275/h);
    const width=w*scale,height=h*scale;
    context.clearRect(0,0,canvas.width,canvas.height);
    context.save();
    context.translate(335+view.x,180+view.y);
    context.scale(view.zoom,view.zoom);
    context.translate(-335,-180);
    context.imageSmoothingEnabled=false;
    context.font='17px system-ui';
    context.fillStyle=getComputedStyle(canvas).getPropertyValue('--text').trim();
    context.fillText('Original',28,28);
    context.fillText('Reconstrucción · rango '+scene.rango,350,28);
    context.drawImage(sources[0],28,44,width,height);
    context.drawImage(sources[1],0,0,w,row,350,44,width,row*scale);
    context.restore();
  };
  timeline.subscribe(index=>{
    row=index;
    readout.textContent=index+' de '+h+' filas reconstruidas';
    canvas.redrawPlot();
  });
  body.append(player,readout,canvas,controls);
  const [label,slider] = input('Rango de compresión',scene.rango,'range');
  slider.min = 0;
  slider.max = scene.maximo;
  slider.addEventListener('change', () => update({rango:slider.value}));
  body.append(label);
  return body;
}

export function bookControl({campo,etiqueta,valor}, recalculate) {
  const wrap = node('div','ws-book-controls');
  const [label,field] = input(etiqueta,valor);
  const status = node('p','ws-field-help');
  status.setAttribute('role','status');
  wrap.append(label,button('Volver a calcular',async () => {
    status.textContent = 'Actualizando…';
    status.textContent = await recalculate({[campo]:field.value}) || '';
  }),status);
  return wrap;
}

export function bookScene(scene, response, recalculate, view) {
  const body = node('section','ws-book-scene');
  const status = node('p','ws-field-help');
  status.setAttribute('role','status');
  async function update(fields) {
    status.textContent = 'Actualizando…';
    const error = await recalculate(fields);
    status.textContent = error || '';
  }
  if (scene.tipo === 'imagen') {
    body.append(imagePair(scene,update),status);
    return body;
  }

  // El contrato HTTP envía las magnitudes como texto. El lienzo usa coordenadas numéricas.
  scene = {...scene};
  const numericPoint = point => point.map(Number);
  for (const key of ['punto','direccion','particular']) {
    if (Array.isArray(scene[key])) scene[key] = numericPoint(scene[key]);
  }
  for (const key of ['puntos','vertices']) {
    if (scene[key]) scene[key] = scene[key].map(numericPoint);
  }
  for (const key of ['lineas','planos']) {
    if (scene[key]) scene[key] = scene[key].map(polyline=>polyline.map(numericPoint));
  }
  if (scene.vectores) scene.vectores = scene.vectores.map(([label,p])=>[label,numericPoint(p)]);

  const controls = node('div','ws-book-controls');
  const legend = node('p','ws-field-help',scene.etiqueta || '');
  const canvas = node('canvas','ws-book-canvas');
  canvas.width = 670;
  canvas.height = 390;
  canvas.setAttribute('role','img');
  canvas.setAttribute('aria-label',scene.etiqueta || `Visualización de ${scene.tipo}`);
  const ctx = canvas.getContext('2d');
  const style = () => getComputedStyle(document.documentElement);
  const palette = () => {
    const css = style();
    return [1,2,3].map(i=>css.getPropertyValue('--plot-series-'+i).trim());
  };
  const showPlanes = scene.tipo === 'planos';
  const config = scene.control;
  const handle = config?.eje === 'intercepto' ? config.punto.map(Number) : null;

  let yaw = -.58, pitch = .6, toPixel, fromPixel;
  let preview, drag, paint = 0;
  const axes = scene.tipo !== 'grafo';
  const route = response.result?.camino ?? [];
  const pathEdges = route.slice(1).map((end,i)=>scene.aristas?.find(edge=>edge[0]===route[i]-1 && edge[1]===end-1));
  const edges = pathEdges.length ? [...scene.aristas.filter(edge=>!edge[3]),...pathEdges] : scene.aristas ?? [];
  const lines = scene.lineas ?? [];
  const visibleSegments = scene.tipo === 'contorno' ? lines[0].length-1 : 0;
  const poses = [
    ...Array.from({length:visibleSegments || lines.length},(_,i)=>['line',i]),
    ...(scene.planos ?? []).map((_,i)=>['plane',i]),
    ...(scene.vectores ?? []).map((_,i)=>['vector',i]),
    ...edges.map((_,i)=>['edge',i]),
    ['result',0],
  ];
  const selection=iterationSelection(poses.map((_,i)=>i),poses.length-1);
  const player=plotPlayback(selection,{label:'Construcción de la escena',interval:visibleSegments>8 ? 85 : 320,surface:canvas});
  const readout=node('output','ws-graph-reading');
  let active=poses.length-1;
  selection.subscribe(index=>{
    active=index;
    const [part,i]=poses[index];
    const label={line:'Trazo',plane:'Plano',vector:scene.vectores?.[i]?.[0],edge:'Arista',result:'Construcción completa'}[part];
    readout.textContent = part==='edge' ? label+' '+scene.etiquetas[edges[i][0]]+' → '+scene.etiquetas[edges[i][1]]+' · '+edges[i][2]
      : ['line','plane'].includes(part) ? label+' '+(i+1) : label;
    redraw();
  });
  const count = kind => poses.slice(0,active+1).filter(([key])=>key===kind).length;
  function redraw() {
    if (!paint) paint = requestAnimationFrame(() => {
      paint = 0;
      if (canvas.isConnected) draw();
    });
  }
  const camera = ([x,y,z]) => [
    x*Math.cos(yaw)-y*Math.sin(yaw),
    (x*Math.sin(yaw)+y*Math.cos(yaw))*Math.sin(pitch)+z*Math.cos(pitch),
  ];

  function draw() {
    const {width,height} = canvas;
    const lineData = scene.lineas ?? [];
    const planes = showPlanes ? scene.planos.map(poly=>poly.map(camera)) : [];
    const origin = [0,0];
    const marks = showPlanes ? (scene.punto ? [camera(scene.punto)] : []) :
      (scene.puntos ?? (scene.punto ? [scene.punto] : []));
    const vectors = scene.vectores ?? [];
    const extra = [...marks,...vectors.map(([,p])=>p),...(scene.vertices ?? [])];
    let spatialIntersection = [];
    if (showPlanes && scene.direccion) {
      const size = Math.max(...scene.direccion.map(Math.abs));
      spatialIntersection = [-4,4].map(t=>camera(scene.particular.map((v,i)=>v+t*scene.direccion[i]/size)));
    }
    const vertices = [origin,...lineData.flat(),...planes.flat(),...extra,...spatialIntersection];
    const extent = Math.max(1,...vertices.map(p=>Math.max(Math.abs(p[0]),Math.abs(p[1]))));
    const bound = view.bound ??= extent;
    const scale = (height/2-27)/bound*view.zoom;
    const centerX = width/2+view.x, centerY = height/2+view.y;
    toPixel = ([x,y]) => [centerX+x*scale,centerY-y*scale];
    fromPixel = ([x,y]) => [(x-centerX)/scale,(centerY-y)/scale];
    const colors = palette();
    const ink = style().getPropertyValue('--muted').trim();
    function stroke(points,color,fill='') {
      if (points.length<2) return;
      ctx.beginPath();
      ctx.moveTo(...toPixel(points[0]));
      for (const p of points.slice(1)) ctx.lineTo(...toPixel(p));
      if (fill) { ctx.fillStyle=fill;ctx.fill(); }
      ctx.strokeStyle=color;ctx.stroke();
    }
    function dot(point,color,label='') {
      const [x,y] = toPixel(point);
      ctx.beginPath();
      ctx.arc(x,y,5,0,Math.PI*2);
      ctx.fillStyle=color;
      ctx.fill();
      if (label) {
        ctx.fillStyle=ink;
        ctx.textAlign='center';
        ctx.fillText(label,x,y-12);
      }
    }
    ctx.clearRect(0,0,width,height);
    ctx.font = '15px system-ui';
    ctx.textAlign = 'start';
    ctx.lineWidth = 1;
    if (axes) {
      const axes = showPlanes ? [[bound,0,0],[0,bound,0],[0,0,bound]].map(camera)
        : [[bound,0],[0,bound]];
      const axisInk = style().getPropertyValue('--plot-axis').trim();
      for (const [i,end] of axes.entries()) {
        stroke([end.map(v=>-v),end],axisInk);
        const [x,y] = toPixel(end);
        ctx.fillStyle=ink;
        ctx.fillText('xyz'[i],x+9,y);
      }
    }
    ctx.lineWidth = 2.3;
    planes.slice(0,count('plane')).forEach((poly,i) => {
      const color = colors[i%3];
      ctx.globalAlpha = .32;
      stroke([...poly,poly[0]],color,color);
      ctx.globalAlpha = 1;
      ctx.textAlign='center';
      const center = toPixel(poly.reduce(([x,y],[a,b])=>[x+a/4,y+b/4],[0,0]));
      ctx.fillStyle=ink;ctx.fillText(`Plano ${i+1}`,...center);
    });
    if (active === poses.length-1) stroke(spatialIntersection,ink);
    const shown = visibleSegments ? (count('line') ? [lineData[0].slice(0,count('line')+1)] : []) : lineData.slice(0,count('line'));
    shown.forEach((line,i)=>{
      const isHandleLine = handle && i===1;
      if (isHandleLine && preview) {
        const normal = config.normal.map(Number);
        const size = Math.hypot(...normal);
        const [nx,ny] = normal.map(value=>value/size);
        const shift = (preview[0]-handle[0])*nx+(preview[1]-handle[1])*ny;
        line = line.map(([x,y])=>[x+shift*nx,y+shift*ny]);
      }
      stroke(line,isHandleLine ? style().getPropertyValue('--highlight').trim() : colors[scene.tramos?.[i].color ?? i%3]);
    });
    vectors.slice(0,count('vector')).forEach(([label,p],i)=>{stroke([origin,p],colors[i%3]);dot(p,colors[i%3],label);});
    if (active === poses.length-1 || scene.tipo === 'regresion') marks.forEach(p=>dot(p,ink));
    if (scene.tipo==='grafo') {
      const pairs = new Set(scene.aristas.map(([i,j])=>`${i},${j}`));
      for (const [i,j,label,selected] of edges.slice(0,count('edge'))) {
        const a = scene.vertices[i], b = scene.vertices[j];
        const color = selected ? colors[1] : colors[0];
        const dx = b[0]-a[0], dy = b[1]-a[1];
        const mag = Math.hypot(dx,dy);
        const offset = scene.dirigido && pairs.has(`${j},${i}`) ? .09 : 0;
        const offsetX = -offset*dy/mag, offsetY = offset*dx/mag;
        const lift = ([x,y])=>[x+offsetX,y+offsetY];
        stroke([lift(a),lift(b)],color);
        const [x,y] = toPixel(lift([(a[0]+b[0])/2,(a[1]+b[1])/2]));
        ctx.textAlign='center';
        ctx.fillStyle=ink;ctx.fillText(label,x,y-8);
        if (scene.dirigido) {
          const [endX,endY] = toPixel(lift(b));
          const angle = Math.atan2(-dy,dx);
          const ax=endX-12*Math.cos(angle), ay=endY-12*Math.sin(angle);
          ctx.beginPath(); ctx.moveTo(ax,ay);
          ctx.lineTo(ax-11*Math.cos(angle-.48),ay-11*Math.sin(angle-.48));
          ctx.lineTo(ax-11*Math.cos(angle+.48),ay-11*Math.sin(angle+.48));
          ctx.closePath();ctx.fillStyle=color;ctx.fill();
        }
      }
      scene.vertices.forEach((p,i)=>dot(p,ink,scene.etiquetas[i]));
    }
    if (handle) dot(preview ?? handle,style().getPropertyValue('--highlight').trim(),'Mover');
    else if (preview) dot(preview, colors[1]);
  }

  const navigation = plotCamera(canvas,()=>canvas.redrawPlot(),{
    view,
    captures: (event,pixel) => Boolean(config) && !event.shiftKey &&
      (!handle || Math.hypot(...toPixel(handle).map((value,i)=>value-pixel[i]))<=29),
    onPinch() { drag=null; preview=null; redraw(); },
    resetView() {
      yaw=-.58; pitch=.6;
      if (turns) turns.forEach(([slider,value])=>{slider.value=value;});
    },
  });
  navigation.controls.classList.add('ws-book-view');
  let turns;
  if (config) canvas.style.cursor='crosshair';
  if (showPlanes) {
    const [h,azimuth] = input('Giro horizontal','-33','range');
    const [v,elevation] = input('Elevación','34','range');
    azimuth.min=-180;azimuth.max=180;azimuth.value=-33;
    elevation.min=-90;elevation.max=90;elevation.value=34;
    azimuth.addEventListener('input',()=>{yaw=Number(azimuth.value)*Math.PI/180;redraw();});
    elevation.addEventListener('input',()=>{pitch=Number(elevation.value)*Math.PI/180;redraw();});
    turns=[[azimuth,-33],[elevation,34]];
    controls.append(h,v);
  } else if (scene.selector) {
    const [name,label,values,current] = scene.selector;
    const wrap = node('label','ws-field',label);
    const select = node('select');
    for (const [key,title] of values) select.add(new Option(title,key,false,key===current));
    select.addEventListener('change',()=>update({[name]:select.value}));
    wrap.append(select);controls.append(wrap);
  } else if (config) {
    const list = config.valores;
    let index = config.indice ?? 0;
    let original = list ? list[index] : config.valor;
    let fieldX, fieldY, pointSelect;
    const selectPoint = i => {
      index = i;
      original = list[index];
      pointSelect.value = index;
      [fieldX.value,fieldY.value] = original;
    };
    if (list) {
      const wrap = node('label','ws-field','Punto a modificar');
      const select = node('select');
      list.forEach((p,i)=>select.add(new Option(`Punto ${i+1} (${p.join(', ')})`,i)));
      pointSelect = select;
      select.addEventListener('change',()=>selectPoint(Number(select.value)));
      wrap.append(select);controls.append(wrap);
    }
    const [xLabel,xInput] = input(Array.isArray(original)?'Coordenada x':config.etiqueta,Array.isArray(original)?original[0]:original);
    fieldX=xInput;
    controls.append(xLabel);
    if (Array.isArray(original)) {
      const [yLabel,yInput] = input('Coordenada y',original[1]);
      fieldY=yInput;controls.append(yLabel);
    }
    const apply = () => {
      const field = config.campo;
      const point = [fieldX.value,fieldY?.value];
      if (config.eje === 'intercepto') {
        const b = Array.isArray(response.input.b) ? response.input.b.flat() : response.input.b.trim().split(/\s+/);
        b[index]=point[0];update({b});
      } else if (config.eje === 'columna') {
        const A = Array.isArray(response.input.A) ? response.input.A.map(row=>row.slice()) : response.input.A.trim().split(/\n|;/).map(row=>row.trim().split(/\s+/));
        A[0][index] = point[0];A[1][index] = point[1];update({A});
      } else if (list) {
        const data=list.map(p=>p.slice()); data[index]=point; update({[field]:data});
      } else update({[field]:point});
    };
    controls.append(button('Aplicar a la gráfica',apply));
    for (const field of [fieldX,fieldY].filter(Boolean)) {
      field.addEventListener('keydown',event=>{
        if (event.key === 'Enter') { event.preventDefault(); apply(); }
      });
    }
    function pickPoint() {
      let nearest = 0;
      let distance = Infinity;
      scene.puntos.forEach(([x,y],i)=>{
        const separation = Math.hypot(x-preview[0],y-preview[1]);
        if (separation < distance) { nearest=i; distance=separation; }
      });
      selectPoint(nearest);
    }
    canvas.addEventListener('pointerdown',event=>{
      if (event.button !== 0 || drag || event.shiftKey || navigation.dragged()) return;
      const pixel = navigation.pixel(event);
      if (handle && Math.hypot(...toPixel(handle).map((value,i)=>value-pixel[i])) > 29) return;
      drag = {id:event.pointerId};
      preview=fromPixel(pixel);
      if (list) pickPoint();
      redraw();
    });
    canvas.addEventListener('pointermove',event=>{
      if (drag?.id !== event.pointerId) return;
      preview=fromPixel(navigation.pixel(event));
      redraw();
    });
    canvas.addEventListener('lostpointercapture',()=>{drag=null;preview=null;redraw();});
    canvas.addEventListener('pointerup',event=>{
      if (drag?.id !== event.pointerId || navigation.dragged()) return;
      const [x,y] = fromPixel(navigation.pixel(event));
      preview=null;
      if (handle) fieldX.value=asText(x*config.normal[0]+y*config.normal[1],2);
      else {
        fieldX.value=asText(x,2);fieldY.value=asText(y,2);
      }
      redraw();apply();
    });
    canvas.style.touchAction='none';
    legend.textContent = handle
      ? 'Arrastrá el punto ámbar para mover la recta. Arrastrá el fondo o usá las flechas para mover la vista. También podés editar el término y pulsar Enter.'
      : 'Arrastrá para mover el punto. Para desplazar la vista, usá Mayús y arrastrá o usá las flechas.';
  }
  if (scene.leyenda) legend.textContent=scene.leyenda.join(' · ');
  if (scene.enlace) {
    const link=node('a','',scene.enlace[1]);link.href=scene.enlace[0];legend.append(' ',link);
  }
  canvas.redrawPlot = () => { if (canvas.isConnected) draw(); };
  body.append(player,readout,canvas,navigation.controls,legend,controls,status);
  if (scene.ecuaciones) {
    const equations = node('div','ws-book-equations');
    for (const value of scene.ecuaciones) equations.append(math(value,value,true));
    const classification = {unica:'Un cruce',infinitas:'Rectas coincidentes',incompatible:'Sin cruce'};
    equations.append(node('p','ws-field-help',classification[response.result.clasificacion] || response.result.clasificacion));
    body.append(equations);
  }
  return body;
}
