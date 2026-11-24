import { gridField, node } from './matrix-input.js';
import { renderResult } from './workspace-results.js';
import { math } from './math-format.js';

const OPTIONS = [
  ['solution','Solución'], ['ranks','Rangos y clasificación'], ['forms','Matrices escalonadas'],
  ['steps','Procedimiento'], ['verify','Comprobación'],
];
const visualFields = {
  'calculo.derivar':['expresion', 'punto'], 'calculo.primitiva':['expresion'],
  'calculo.limite_lateral':['expresion'], 'calculo.derivada_parcial':['expresion'],
  'calculo.sumatoria':['expresion'], 'raices.biseccion':['expresion'], 'raices.falsa_posicion':['expresion'],
  'raices.newton':['expresion', 'derivada'], 'raices.secante':['expresion'],
  'calculo.definida':['expresion', 'inferior', 'superior'], 'calculo.numerica':['expresion'],
  'original.primitiva':['expresion'], 'errores.propagacion':['expresion'], 'calculadora.evaluar':['expresion'],
  'grafica.explicita':['expr'], 'grafica.parametrica':['expr', 'y'], 'funciones.evaluar':['expresion'],
};
const HISTORY_KEY = 'synapsis-historial-escritorio';
const exampleMatrix = [['2','1','-1','8'],['-3','-1','2','-11'],['-2','1','2','-3']];

const GROUP_ICONS = {
  Resolución:'≡', Factorización:'◩', Operaciones:'±', 'Reducción y propiedades':'▥',
  'Determinantes e inversa':'▣', Bloques:'▦', 'Bases y subespacios':'⟡', Transformaciones:'↦',
  'Gráficas':'∿', 'Cálculo':'∫', 'Métodos de intervalo':'〈〉', 'Métodos abiertos':'⋯',
  'Métodos de aproximación':'↻', 'Análisis numérico':'≈', Conversiones:'⇄',
  Conjuntos:'∪', 'Notación y modelos':'⌘',
};
const OP_ICONS = {
  'sistemas.resolver':'G/J', sistema:'⇥', cramer:'∣A∣', inversa:'⁻¹', lu:'LU', plu:'PL', triangular:'◿',
  suma:'+', resta:'−', producto:'×', escalar:'α', transpuesta:'ᵀ', traza:'tr',
  potencia:'ⁿ', analizar:'≡', ref:'◩', rref:'▱', elemental:'⇅', propiedades:'≟',
  calcular:'≈', cofactores:'±', inversa_adjunta:'adj', propiedades_det:'∣∣',
  particionar:'▦', suma_bloques:'⊞', producto_bloques:'⊠', producto_punto:'·',
  producto_cruz:'×', norma:'‖v‖', angulo:'∠', combinacion:'∑', proyeccion:'⊥',
  generado:'⟨v⟩', fundamentales:'⊞', base:'ℬ', interseccion:'∩', coordenadas:'[v]',
  cambio_base:'⇄', desde_imagenes:'↦', componer:'∘', representar:'⊡', relaciones:'≣',
  explicita:'∿', parametrica:'◌', evaluar:'f(x)', derivar:'′', primitiva:'∫',
  definida:'∫ᵇ', numerica:'∑', biseccion:'½', falsa_posicion:'⤡', newton:'∠',
  secante:'╱', jacobi:'J', gauss_seidel:'GS', sor:'ω', romanos:'Ⅻ', enteros:'₂',
  bases:'⇄', operar:'∪', notacion:'aᵢⱼ', ecuaciones:'≡', homogeneo:'0',
  paralelogramo:'◇', taylor:'eˣ', exactitud:'σ', dominancia:'Σ', economia:'¤', balance:'⚖',
  flujos:'⇉', resolver:'⇝', polinomios:'Pₙ', teorema_invertible:'⇔', subespacio:'⊂', formula:'↦', sarrus:'↘', redondeo:'≈', propagacion:'Δ',
  acumulacion:'∑', maquina:'ε', comparar:'≟', parametrico:'λ',
};
function navIcon(symbol) {
  const icon = node('span','ws-nav-icon',symbol);
  icon.setAttribute('aria-hidden','true');
  return icon;
}
function operationIcon(id) {
  return OP_ICONS[id] ?? OP_ICONS[id.split('.')[1]] ?? '◈';
}

function historyEntries() {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) ?? []; }
  catch { return []; }
}

function optionLabel(value) {
  return ({'-':'Izquierda (−)', '+':'Derecha (+)', x:'x', y:'y', ambos:'Ambos lados', plantear:'Solo plantear', resolver:'Resolver', completo:'Análisis completo', escalonada:'Solo escalonada (Gauss)',
    gauss_jordan:'Gauss-Jordan', gauss:'Gauss', falsa_posicion:'Falsa posición',
    gauss_seidel:'Gauss-Seidel', residual_y_paso:'Residual y paso', rref:'RREF',
    infinito:'Norma ∞', uno:'Norma 1', dos:'Norma 2 (euclidiana)', lu:'LU', plu:'PLU', sarrus:'Sarrus',
    reduccion:'Reducción por filas', cofactores:'Expansión por cofactores', cota:'Cota del intervalo',
    relativo:'Cambio relativo entre iterados', residual:'Residual', ambos:'Cota y residual',
    paso_y_residual:'Paso y residual', paso_absoluto:'Cambio absoluto',
    relativo_vectorial:'Cambio relativo vectorial', porcentaje_por_componente:'Cambio porcentual en cada componente',
    relativo_y_residual:'Cambio relativo y residual', solo_residual:'Solo el residual', proporcion:'Proporción', porcentaje:'Porcentaje',
    
  })[value] ?? value.replaceAll('_', ' ');
}

export function bindWorkspace(setOpen) {
  const get = id => document.querySelector(`#${id}`);
  const workspace = get('workspace');
  const sidebar = get('ws-operations');
  const sections = get('ws-module');
  const page = document.documentElement;
  const form = get('ws-form');
  const fields = get('ws-fields');
  const header = get('ws-title');
  const status = get('ws-message');
  const results = get('ws-results');
  const operations = get('ws-operation');
  const historyView = get('ws-history');
  const toggle = get('ws-sidebar-toggle');
  const compactToggle = get('ws-compact-toggle');
  const cards = new Map([...document.querySelectorAll('.card-open')].map(link => {
    const card = link.closest('.card');
    return [link.dataset.module, { link, name:card.querySelector('h3').textContent }];
  }));
  for (const [id, card] of cards) sections.add(new Option(card.name,id));

  let expressionField;
  let savedFactors;
  let catalogPromise;
  let catalog;
  let state;
  let opener;
  let generation = 0;
  let request;
  let automatic;
  let view = 'form';
  const drafts = new Map();
  const responses = new Map();
  let controls = new Map();
  let choiceControls = new Map();

  function getCatalog() {
    if (!catalogPromise) catalogPromise = fetch('/api/catalogo').then(response => {
      if (!response.ok) throw new Error('El catálogo de Python no está disponible.');
      return response.json();
    }).catch(error => {
      catalogPromise = null;
      throw error;
    });
    return catalogPromise;
  }

  function snapshot() {
    const values = {};
    for (const [name, control] of controls) values[name] = control.raw();
    const options = Object.fromEntries([...choiceControls].map(([key, element]) => [key, element.checked]));
    const draft = {values, options};
    if (savedFactors && state.op === 'factorizacion.resolver'
        && values.metodo === savedFactors.method && JSON.stringify(values.A) === savedFactors.matrix) {
      draft.savedFactors = savedFactors;
    }
    return draft;
  }

  function remember() {
    if (state && controls.size) drafts.set(state.op, snapshot());
  }

  function showView(next) {
    view = next;
    operations.hidden = next === 'history' || next === 'course';
    historyView.hidden = next !== 'history';
    get('ws-course').hidden = next !== 'course';
    form.hidden = next === 'result';
    results.hidden = next !== 'result';
    for (const name of ['history', 'course']) {
      get(`ws-${name}-link`).setAttribute('aria-pressed', String(next === name));
    }
    status.textContent = '';
    setError('');
  }

  function setError(message) {
    const error = get('ws-error');
    error.hidden = !message;
    error.textContent = message;
  }

  function edit() {
    showView('form');
    (fields.querySelector('math-field:not([hidden]), input[type="text"]:not([hidden]), textarea, select') ?? get('ws-calculate')).focus();
  }

  function displayResult(response, draft, original, updateResult = false) {
    renderResult(results, response, draft.options, original, edit, async values => {
      try {
        for (const [key, value] of Object.entries(values)) {
          const control = controls.get(key);
          control.set(control.definition.kind === 'vector' && Array.isArray(value) ? [value] : value);
        }
      } catch (error) {
        return error.message;
      }
      return calculate(true, true);
    });
    if (['factorizacion.lu', 'factorizacion.plu'].includes(state.op) && response.verification?.passed) {
      const {L, U, P} = response.result;
      const method = state.op.split('.')[1];
      const button = node('button', 'secondary', 'Resolver con estos factores');
      button.type = 'button';
      button.addEventListener('click', async () => {
        history.pushState(history.state, '', '#sistemas/factorizacion.resolver');
        await sync({restore: {values: {A: draft.values.A, metodo: method}, options: draft.options,
          savedFactors: {method, matrix: JSON.stringify(draft.values.A), factors: {L, U, P}}}});
        controls.get('b')?.element.querySelector('input')?.focus();
      });
      results.querySelector('.ws-result-actions').append(button);
    }
    showView('result');
    if (updateResult) results.querySelector('.ws-book-controls :is(input,select)')?.focus({preventScroll:true});
    else {
      get('ws-result-title').focus({preventScroll:true});
      window.scrollTo({top:0,behavior:'instant'});
    }
  }

  function historyScreen() {
    clearTimeout(automatic);
    request?.abort();
    showView('history');
    const list = get('ws-history-items');
    list.replaceChildren();
    const entries = historyEntries().filter(x => x.module === state.module);
    if (!entries.length) list.append(node('p','ws-muted','Todavía no hay cálculos guardados en este módulo.'));
    for (const entry of entries) {
      const button = node('button','ws-history-item');
      button.type = 'button';
      const date = new Intl.DateTimeFormat('es-NI',{dateStyle:'medium',timeStyle:'short'}).format(new Date(entry.date));
      button.append(node('strong','',catalog.operations[entry.op]?.title ?? entry.op),node('span','',date));
      button.addEventListener('click', () => {
        drafts.set(entry.op, entry.draft);
        responses.delete(entry.op);
        if (entry.op === state.op) {
          renderForm(catalog.operations[entry.op]);
          showView('form');
          calculate();
        } else {
          history.replaceState(history.state, '', `#${entry.module}/${entry.op}`);
          sync({compute:true, restore:entry.draft});
        }
      });
      list.append(button);
    }
  }

  function record(draft) {
    const entries = historyEntries().filter(entry => entry.op !== state.op || JSON.stringify(entry.draft) !== JSON.stringify(draft));
    entries.unshift({module:state.module,op:state.op,draft,date:Date.now()});
    try { localStorage.setItem(HISTORY_KEY,JSON.stringify(entries.slice(0,40))); } catch { /* El cálculo sigue disponible. */ }
  }

  function queueAutomatic() {
    clearTimeout(automatic);
    request?.abort();
    get('ws-calculate').disabled = false;
    status.textContent = '';
    if (!state || view !== 'form') return;
    setError('');
    remember();
    responses.delete(state.op);
    if (state.op === 'original.sistema' && controls.get('matrix')?.ready()) {
      automatic = setTimeout(() => calculate(false), 360);
    }
  }

  function setConditions() {
    const values = snapshot().values;
    if (state.op === 'original.sistema') {
      const partial = values.objetivo === 'escalonada';
      fields.querySelector('.ws-options').hidden = partial;
      fields.querySelector('.ws-theorem').hidden = partial;
    }
    for (const [,control] of controls) {
      control.updateNotation?.(values);
      const condition = control.definition?.when;
      const enabled = !condition || Object.entries(condition).every(([name, allowed]) => allowed.includes(values[name]));
      control.element.hidden = !enabled;
    }
  }

  function elementField(definition, value) {
    const {name, label, kind, choices} = definition;
    if (definition.visual || visualFields[state.op]?.includes(name)) {
      return expressionField(definition, value, queueAutomatic, {
        differential: state.op === 'calculo.primitiva' ? 'x' : null,
        variables: state.op === 'grafica.parametrica' ? ['t']
          : state.op === 'calculo.derivada_implicita' ? ['x', 'y'] : undefined,
      });
    }
    if (state.op === 'calculo.primitiva' && name === 'variable') {
      // La plantilla muestra dx. Enviá esa misma variable también al recuperar un historial antiguo.
      const input = node('input');
      input.type = 'hidden';
      const set = () => { input.value = definition.default; };
      set();
      return {definition, element:input, set, raw:() => input.value, value:() => input.value};
    }
    if (['matrix','vector','vectors'].includes(kind)) {
      const control = gridField(label,value,{vector:kind === 'vector',required:definition.required,onChange:queueAutomatic});
      return {...control,definition};
    }
    const wrap = node('label', 'ws-field', label);
    const select = kind === 'select';
    const multiline = kind === 'set' || kind === 'multiline';
    const input = node(select ? 'select' : multiline ? 'textarea' : 'input');
    if (select) {
      for (const choice of choices) input.add(new Option(definition.choice_labels?.[choice] ?? optionLabel(String(choice)), choice));
    } else if (kind === 'boolean') {
      input.type = 'checkbox';
      wrap.classList.add('ws-field-checkbox');
    } else if (multiline) {
      input.rows = 4;
      input.maxLength = 4000;
      input.spellcheck = false;
      wrap.classList.add('ws-full-field');
    } else {
      input.type = 'text';
      input.inputMode = kind === 'integer' || kind === 'index' ? 'numeric' : 'text';
      input.autocomplete = 'off';
      input.spellcheck = false;
      input.maxLength = 500;
    }
    if (kind === 'expression') wrap.classList.add('ws-full-field');
    function set(next) {
      if (kind === 'boolean') input.checked = next === true || next === 'true';
      else input.value = next ?? '';
    }
    function raw() { return kind === 'boolean' ? input.checked : input.value.trim(); }
    set(value);
    if (!select && kind !== 'boolean' && definition.default !== '') input.placeholder = definition.default;
    input.addEventListener('input', () => { setConditions(); queueAutomatic(); });
    wrap.append(input);
    return {definition,element:wrap,raw,set,value:raw,name};
  }

  function renderForm(definition) {
    const saved = drafts.get(state.op);
    savedFactors = saved?.savedFactors;
    const original = state.op === 'original.sistema';
    controls = new Map();
    choiceControls = new Map();
    fields.replaceChildren();
    get('ws-engine').textContent = state.op.startsWith('original.') ? 'Motor original · Python' : 'Motor Python';
    if (original) {
      const editor = gridField('Matriz aumentada [A | b]',saved?.values.matrix ?? '',{
        augmented:true,required:true,onChange:queueAutomatic,
      });
      controls.set('matrix',editor);
      fields.append(editor.element);
    }
    for (const definitionField of definition.fields) {
      const {name, kind} = definitionField;
      const initial = saved?.values[name] ?? (kind === 'select' || kind === 'boolean' || !definitionField.required
        ? definitionField.default : '');
      const control = elementField(definitionField,initial);
      controls.set(name,control);
      fields.append(control.element);
    }
    const checks = node('fieldset','ws-options');
    checks.append(node('legend','',original ? '¿Qué querés calcular o ver?' : 'Presentación'));
    if (original) {
      for (const [key,label] of OPTIONS) {
        const element = node('input');
        element.type = 'checkbox';
        element.checked = saved?.options[key] ?? true;
        choiceControls.set(key,element);
        const row = node('label');
        row.append(element,document.createTextNode(label));
        element.addEventListener('change', queueAutomatic);
        checks.append(row);
      }
      const theorem = node('details','ws-theorem');
      theorem.append(node('summary','','Teorema de Rouché–Capelli'),
        node('p','','Si los rangos de A y [A | b] difieren, el sistema no tiene solución. Si coinciden con el número de incógnitas, la solución es única. Si coinciden pero son menores, hay infinitas soluciones.'));
      fields.append(checks,theorem);
    } else {
      const checkbox = node('input');
      checkbox.type = 'checkbox';
      checkbox.checked = saved?.options.steps ?? true;
      choiceControls.set('steps',checkbox);
      checkbox.addEventListener('change',queueAutomatic);
      const label = node('label');
      label.append(checkbox,document.createTextNode('Mostrar procedimiento'));
      checks.append(label);
      fields.append(checks);
    }
    setConditions();

  }

  function operationsSidebar(module, selected) {
    const menu = document.createDocumentFragment();
    for (const [group, ids] of catalog.modules[module]) {
      const details = node('details','ws-nav-group');
      details.open = ids.includes(selected);
      const summary = node('summary');
      summary.title = group;
      summary.append(navIcon(GROUP_ICONS[group] ?? '◈'), node('span','ws-nav-label',group));
      details.append(summary);
      for (const id of ids) {
        const label = catalog.operations[id].title;
        const link = node('a','ws-op-link');
        link.title = label;
        link.append(navIcon(operationIcon(id)), node('span','ws-nav-label',label));
        link.href = `#${module}/${id}`;
        if (id === selected) link.setAttribute('aria-current','page');
        details.append(link);
      }
      menu.append(details);
    }
    sidebar.replaceChildren(menu);
  }

  async function calculate(reveal = true, updateResult = false) {
    clearTimeout(automatic);
    const button = get('ws-calculate');
    if (!state || !controls.size || (view !== 'form' && !updateResult)) return;
    request?.abort();
    const controller = new AbortController();
    request = controller;
    const operation = state.op;
    const original = operation === 'original.sistema';
    const draft = snapshot();
    const cached = responses.get(operation);
    if (reveal && cached?.key === JSON.stringify(draft)) {
      record(draft);
      displayResult(cached.response, draft, original, updateResult);
      return;
    }
    setError('');
    try {
      const input = {};
      for (const [name,control] of controls) {
        if (control.element.hidden) continue;
        if (operation === 'factorizacion.resolver' && name === 'b' && !control.ready()) {
          setError('Completá el vector b para resolver Ax=b, o factorizá la matriz que ya ingresaste.');
          const method = draft.values.metodo;
          const action = node('button', 'secondary', `Solo factorizar con ${method.toUpperCase()}`);
          action.type = 'button';
          action.addEventListener('click', () => {
            history.pushState(history.state, '', `#${state.module}/factorizacion.${method}`);
            sync({compute:true, restore:{values:{A:draft.values.A}, options:draft.options}});
          });
          get('ws-error').append(' ', action);
          control.element.querySelector('.ws-matrix input:placeholder-shown')?.focus();
          return;
        }
        const value = control.value();
        const def = control.definition ?? {};
        const augmented = original && name === 'matrix';
        const isRequired = augmented || def.required || (def.required_when && Object.entries(def.required_when)
          .every(([k,v]) => v.includes(draft.values[k])));
        if ((value === '' || (augmented && !control.ready())) && isRequired) {
          throw new Error(augmented ? 'Completá todas las celdas de la matriz aumentada, incluido b. Ingresá 0 cuando corresponda.' : `Completá «${def.label}».`);
        }
        if (value !== '') input[name] = value;
      }
      if (draft.savedFactors) input.factores = draft.savedFactors.factors;
      button.disabled = reveal;
      status.textContent = 'Calculando…';
      const http = await fetch('/api/calcular',{method:'POST',signal:controller.signal,headers:{'Content-Type':'application/json'},
        body:JSON.stringify({operation,input,steps:input.objetivo === 'escalonada' || draft.options.steps})});
      const response = await http.json();
      if (controller.signal.aborted || state?.op !== operation) return;
      status.textContent = '';
      if (!response.result) throw new Error(response.error?.message ?? 'El motor no devolvió un resultado.');
      responses.set(operation, {key:JSON.stringify(draft), response});
      if (reveal) {
        record(draft);
        displayResult(response, draft, original, updateResult);
      } else status.textContent = 'Cálculo listo. Presioná Resolver para ver el resultado.';
    } catch (error) {
      if (controller.signal.aborted) return;
      status.textContent = '';
      const message = error instanceof SyntaxError ? 'El servicio local de Python no respondió correctamente.' : error.message;
      if (updateResult) return message;
      setError(message);
    } finally {
      if (request === controller) button.disabled = false;
    }
  }

  function example(override = {}) {
    if (!state) return;
    if (state.op === 'original.sistema') controls.get('matrix').set(override.matrix ?? exampleMatrix);
    for (const f of catalog.operations[state.op].fields) {
      if (state.op === 'original.sistema' && f.name === 'objetivo' && override.objetivo === undefined) continue;
      controls.get(f.name).set(override[f.name] ?? f.default);
    }
    setConditions();
    remember();
    calculate();
  }

  function courseScreen() {
    clearTimeout(automatic);
    request?.abort();
    showView('course');
    const list = get('ws-course-items');
    list.replaceChildren(node('p','ws-course-controls','Elegí una sesión y probá sus operaciones con datos editables.'));
    for (const [course, units] of catalog.calculus_courses ?? []) {
      const section = node('details', 'ws-course-session');
      section.append(node('summary', '', course));
      for (const [name, operations] of units) {
        const unit = node('div', 'ws-course-session');
        unit.append(node('h3', '', name));
        for (const op of operations) {
          const link = node('a', '', catalog.operations[op].title);
          link.href = `#grafica/${op}`;
          link.addEventListener('click', event => {
            if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
            event.preventDefault();
            history.pushState(history.state, '', link.hash);
            sync();
          });
          unit.append(link);
        }
        section.append(unit);
      }
      list.append(section);
    }
    for (const session of catalog.sessions) {
      const item = node('details','ws-course-session');
      const [number, name, description, formula, tools] = session;
      item.append(node('summary','',`${number}. ${name}`), node('p','',description));
      if (formula) item.append(math(formula, formula, true));
      for (const [module, op, input] of tools) {
        const link = node('a','',catalog.operations[op].title);
        link.href = `#${module}/${op}`;
        link.addEventListener('click', async event => {
          if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
          event.preventDefault();
          history.pushState(history.state,'',link.hash);
          await sync();
          if (state?.op === op && input) example(input);
        });
        item.append(link);
      }
      list.append(item);
    }
    get('ws-course-title').focus({preventScroll:true});
  }

  function setCompact(compact) {
    workspace.classList.toggle('ws-compact', compact);
    const label = compact ? 'Expandir barra lateral' : 'Minimizar barra lateral';
    compactToggle.title = label;
    compactToggle.setAttribute('aria-expanded', String(!compact));
    compactToggle.querySelector('.ws-nav-icon').textContent = compact ? '»' : '«';
    compactToggle.querySelector('.ws-nav-label').textContent = label;
  }

  async function sync({focus = true, compute = false, restore = null} = {}) {
    const [module, requested] = location.hash.slice(1).split('/');
    const revision = ++generation;
    clearTimeout(automatic);
    request?.abort();
    if (!cards.has(module)) {
      const wasOpen = !workspace.hidden;
      remember();
      state = null;
      controls.clear();
      workspace.hidden = true;
      page.classList.remove('workspace-open');
      if (wasOpen) {
        setOpen(false);
        const anchor = Array.from(document.querySelectorAll('main > section')).find(item => `#${item.id}` === location.hash);
        if (anchor) requestAnimationFrame(() => anchor.scrollIntoView({behavior:'instant'}));
      }
      if (wasOpen && focus && opener) {
        const target = opener;
        opener = null;
        requestAnimationFrame(() => target.focus({preventScroll:true}));
      }
      return;
    }

    remember();
    const newModule = state?.module !== module;
    workspace.hidden = false;
    page.classList.add('workspace-open');
    setOpen(true);
    get('ws-history-link').disabled = true;
    get('ws-course-link').disabled = true;
    status.textContent = 'Cargando herramientas…';
    try {
      catalog = await getCatalog();
    } catch (error) {
      if (revision !== generation) return;
      status.textContent = error.message;
      status.append(' Abrí el proyecto con el lanzador de Synapsis.');
      operations.hidden = true;
      historyView.hidden = true;
      return;
    }
    if (revision !== generation) return;
    const ids = catalog.modules[module].flatMap(([, ids]) => ids);
    const op = ids.includes(requested) ? requested : ids[0];
    if ((visualFields[op] || catalog.operations[op].fields.some(field => field.visual)) && !expressionField) {
      try {
        ({expressionField} = await import('./derivative-field.js'));
      } catch {
        if (revision === generation) status.textContent = 'No se pudo abrir el editor matemático. Volvé a abrir la operación.';
        return;
      }
      if (revision !== generation) return;
    }
    if (state?.op !== op) delete results.dataset.selectedTab;
    state = {module,op};
    const card = cards.get(module);
    sections.value = module;
    if (newModule || !sidebar.querySelector('[aria-current]')) operationsSidebar(module,op);
    for (const link of sidebar.querySelectorAll('.ws-op-link')) {
      if (link.hash === `#${module}/${op}`) {
        link.setAttribute('aria-current','page');
        link.closest('details').open = true;
      } else link.removeAttribute('aria-current');
    }
    if (matchMedia('(max-width: 760px)').matches) {
      toggle.setAttribute('aria-expanded','false');
      toggle.textContent = 'Ver operaciones';
    }
    showView('form');
    if (restore) drafts.set(op, restore);
    const definition = catalog.operations[op];
    get('ws-category').textContent = card.name;
    header.textContent = definition.title;
    get('ws-description').textContent = definition.description || 'Ingresá los datos para resolver la operación y revisar su procedimiento.';
    status.textContent = '';
    get('ws-calculate').disabled = false;
    renderForm(definition);
    get('ws-history-link').disabled = false;
    get('ws-course-link').disabled = false;
    scrollTo({top:0,behavior:'instant'});
    if (focus) header.focus({preventScroll:true});
    if (compute) calculate();
  }

  sections.addEventListener('change', () => {location.hash = sections.value;});
  toggle.addEventListener('click', () => {
    const expanded = toggle.getAttribute('aria-expanded') === 'true';
    toggle.setAttribute('aria-expanded',String(!expanded));
    toggle.textContent = expanded ? 'Ver operaciones' : 'Ocultar operaciones';
  });
  get('ws-history-link').addEventListener('click', () => view === 'history' ? edit() : historyScreen());
  get('ws-course-link').addEventListener('click', () => view === 'course' ? edit() : courseScreen());
  get('ws-example').addEventListener('click', () => example());
  try { setCompact(localStorage.getItem('synapsis-sidebar-compact') === 'true'); } catch { setCompact(false); }
  compactToggle.addEventListener('click', () => {
    const compact = !workspace.classList.contains('ws-compact');
    setCompact(compact);
    try { localStorage.setItem('synapsis-sidebar-compact', String(compact)); } catch { /* Preferencia local opcional. */ }
  });
  sidebar.addEventListener('click', event => {
    const link = event.target.closest('a');
    if (link?.hash === location.hash && view !== 'form') edit();
  });
  get('ws-clear').addEventListener('click', () => {
    for (const [key, control] of controls) {
      const def = control.definition;
      if (key === 'matrix' || ['matrix','vector','vectors'].includes(def?.kind)) control.set('');
      else if (def) control.set(def.kind === 'select' || def.kind === 'boolean' ? def.default : '');
    }
    setConditions();
    queueAutomatic();
  });
  form.addEventListener('submit', event => {event.preventDefault(); calculate();});
  document.querySelectorAll('[data-module]').forEach(link => link.addEventListener('click', async event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    opener = link;
    const hash = `#${link.dataset.module}`;
    history.pushState(history.state,'',hash);
    await sync();
    if (location.hash === hash && link.hasAttribute('data-example') && state) example();
  }));
  addEventListener('hashchange', () => sync());
  workspace.addEventListener('keydown', event => {
    if (event.key !== 'Escape' || event.defaultPrevented) return;
    if (view !== 'form') edit();
    else location.hash = '#modulos';
  });
  sync({focus:false});
}
