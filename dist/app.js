import { bindWorkspace } from './workspace.js';
import { bindHero } from './hero-motion.js';
import { bindOrbit } from './orbit.js';

const page = document.documentElement;
const hero = document.querySelector('.hero');
const cover = document.querySelector('#portada');
const menu = document.querySelector('#modulos');
const orbit = document.querySelector('#orbita');
const topbar = document.querySelector('.topbar');
const mode = document.querySelector('#mode');
const theme = document.querySelector('#theme');
const themeColor = document.querySelector('meta[name="theme-color"]');
const seriousTitle = document.querySelector('#serious-title');
const brands = [...document.querySelectorAll('.brand')];
const motion = document.querySelector('#motion');
const preference = matchMedia('(prefers-reduced-motion: reduce)');
const systemTheme = matchMedia('(prefers-color-scheme: dark)');
const nav = [...document.querySelectorAll('.topbar nav a')];
const clamp = (value, min = 0, max = 1) => Math.max(min, Math.min(max, value));
const scenery = bindHero(cover, topbar);
const orbitalLab = bindOrbit(orbit);

function read(key) {
  try { return localStorage.getItem(key); } catch { return null; }
}
function store(key, value) {
  try { localStorage.setItem(key, value); } catch { /* The current view still applies. */ }
}

let stopped = read('synapsis-motion');
const spaceAnchors = new Set(['#portada', '#orbita']);
let serious = read('synapsis-serio') === 'true' && !spaceAnchors.has(location.hash);
let savedTheme = read('synapsis-tema');
let active = false;
let switching = false;
let spatialPosition = { hash: '#portada', top: 0 };

function applyTheme() {
  const selected = savedTheme === 'dark' || savedTheme === 'light'
    ? savedTheme : systemTheme.matches ? 'dark' : 'light';
  page.dataset.seriousTheme = selected;
  const next = selected === 'dark' ? 'claro' : 'oscuro';
  theme.querySelector('span').textContent = `Tema ${next}`;
  theme.setAttribute('aria-label', `Cambiar al tema ${next}`);
  theme.title = theme.getAttribute('aria-label');
  themeColor.content = getComputedStyle(page).getPropertyValue('--browser-color').trim();
  document.querySelectorAll('canvas.plot').forEach(canvas => canvas.redrawPlot?.());
}
function applyView() {
  const paused = stopped === null ? preference.matches : stopped === 'true';
  active = !paused && !serious;
  page.classList.toggle('serious', serious);
  page.classList.toggle('still', paused);
  page.classList.toggle('motion-on', active);
  page.classList.toggle('motion-override', stopped === 'false');
  theme.hidden = !serious;
  seriousTitle.hidden = !serious;
  menu.setAttribute('aria-labelledby', serious ? seriousTitle.id : 'modules-title');
  for (const brand of brands) {
    brand.href = serious ? '#modulos' : '#portada';
    brand.setAttribute('aria-label', serious ? 'Synapsis, menú principal' : 'Synapsis, portada');
  }
  applyTheme();
  mode.setAttribute('aria-pressed', String(serious));
  const modeLabel = serious ? 'Modo espacial' : 'Modo serio';
  mode.querySelector('span').textContent = modeLabel;
  mode.setAttribute('aria-label', modeLabel);
  mode.title = modeLabel;
  const label = paused ? 'Activar animaciones' : 'Pausar animaciones';
  motion.setAttribute('aria-pressed', String(paused));
  motion.setAttribute('aria-label', label);
  motion.title = label;
  scenery.setEnabled(active);
  orbitalLab.setEnabled(active);
}

applyView();
preference.addEventListener('change', applyView);

systemTheme.addEventListener('change', applyTheme);
theme.addEventListener('click', () => {
  savedTheme = page.dataset.seriousTheme === 'dark' ? 'light' : 'dark';
  store('synapsis-tema', savedTheme);
  applyTheme();
});

function goToView(next, position) {
  serious = next;
  store('synapsis-serio', serious);
  applyView();
  const hash = serious ? '#modulos' : position.hash;
  history.replaceState(history.state, '', hash || location.pathname + location.search);
  scrollTo({ top: serious ? 0 : position.top, behavior: 'instant' });
  scheduleNav();
}

async function switchView() {
  if (switching) return;
  const next = !serious;
  if (next) spatialPosition = { hash: location.hash, top: scrollY };
  if (preference.matches || page.classList.contains('still')) {
    goToView(next, spatialPosition);
    return;
  }

  switching = true;
  const rect = mode.getBoundingClientRect();
  page.style.setProperty('--transition-x', `${rect.left + rect.width / 2}px`);
  page.style.setProperty('--transition-y', `${rect.top + rect.height / 2}px`);
  page.dataset.modeTransition = next ? 'serious' : 'space';
  let applied = false;
  const update = () => {
    goToView(next, spatialPosition);
    applied = true;
  };
  try {
    if (typeof document.startViewTransition === 'function') {
      const transition = document.startViewTransition(update);
      transition.ready.catch(() => {});
      await transition.finished;
    } else {
      update();
      const main = document.querySelector('main');
      await main.animate(
        [{ opacity: .35, transform: `translateY(${next ? 9 : -9}px)` }, { opacity: 1, transform: 'translateY(0)' }],
        { duration: 360, easing: 'ease-out' },
      ).finished;
    }
  } catch {
    if (!applied) update();
  } finally {
    delete page.dataset.modeTransition;
    page.style.removeProperty('--transition-x');
    page.style.removeProperty('--transition-y');
    switching = false;
  }
}
mode.addEventListener('click', switchView);

addEventListener('hashchange', () => {
  if (!serious || !spaceAnchors.has(location.hash)) return;
  const hash = location.hash;
  serious = false;
  store('synapsis-serio', false);
  applyView();
  document.querySelector(hash).scrollIntoView({ behavior: 'instant' });
  scheduleNav();
});
motion.addEventListener('click', () => {
  const position = cover.getBoundingClientRect();
  const withinCover = position.top <= topbar.offsetHeight && position.bottom > topbar.offsetHeight;
  stopped = String(!page.classList.contains('still'));
  store('synapsis-motion', stopped);
  applyView();
  if (withinCover && stopped === 'true' && scrollY > hero.offsetHeight / 2) {
    scrollTo({ top: Math.min(scrollY, hero.offsetHeight / 2), behavior: 'instant' });
  }
});
let navFrame = 0;
function markSection() {
  navFrame = 0;
  const marker = topbar.offsetHeight + Math.min(innerHeight * .27, 240);
  const id = serious ? '#modulos' : orbit.getBoundingClientRect().top <= marker ? '#orbita'
    : menu.getBoundingClientRect().top <= marker ? '#modulos' : '#portada';
  for (const link of nav) {
    if (link.hash === id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  }
}
function scheduleNav() {
  if (!navFrame) navFrame = requestAnimationFrame(markSection);
}
addEventListener('scroll', scheduleNav, { passive: true });
addEventListener('resize', scheduleNav);
markSection();
const cardObserver = new IntersectionObserver(entries => {
  for (const { isIntersecting, target } of entries) {
    if (!isIntersecting) continue;
    if (active) target.classList.add('revealed');
    cardObserver.unobserve(target);
  }
}, { threshold: .23 });
for (const card of document.querySelectorAll('[data-reveal]')) {
  cardObserver.observe(card);
  card.addEventListener('pointermove', event => {
    if (!active || event.pointerType !== 'mouse') return;
    const box = card.getBoundingClientRect();
    const x = clamp((event.clientX - box.left) / box.width);
    const y = clamp((event.clientY - box.top) / box.height);
    card.setAttribute('data-engaged', '');
    card.style.setProperty('--art-x', `${(x - .5) * 11}px`);
    card.style.setProperty('--art-y', `${(y - .5) * 9}px`);
    card.style.setProperty('--art-rx', `${(.5 - y) * 12}deg`);
    card.style.setProperty('--art-ry', `${(x - .5) * 15}deg`);
    card.style.setProperty('--glint-x', `${x * 100}%`);
    card.style.setProperty('--glint-y', `${y * 100}%`);
  }, { passive: true });
  card.addEventListener('pointerleave', () => card.removeAttribute('data-engaged'));
}


bindWorkspace(open => {
  scenery.setObscured(open);
  orbitalLab.setObscured(open);
});
