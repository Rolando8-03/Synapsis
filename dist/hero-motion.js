import { fitLandscape } from './terrain.js';
import { createCanvasScene } from './scene-canvas.js';

const TAU = Math.PI * 2;
const clamp = (value, lower = 0, upper = 1) => Math.max(lower, Math.min(upper, value));
const ease = value => {
  const t = clamp(value);
  return t * t * (3 - 2 * t);
};
const replaySeconds = 7.4;

export function bindHero(cover, header) {
  const hero = cover.querySelector('.hero');
  const scene = hero.querySelector('.scene');
  const photo = hero.querySelector('.land img');
  const replay = hero.querySelector('#flight-replay');
  const label = replay.querySelector('span');
  const compactView = matchMedia('(max-width: 660px)');
  let canvas = scene.querySelector('canvas');
  let renderer = null;
  let startup;
  let enabled = false;
  let visible = true;
  let obscured = false;
  let painting = 0;
  let lastPaint = 0;
  let lastTick = 0;
  let time = 0;
  let replayStart = null;
  let width = 0;
  let height = 0;
  let sectionTop = 0;
  let travel = 1;
  let pointerX = 0;
  let pointerY = 0;
  let cameraX = 0;
  let cameraY = 0;
  let scrollProgress = 0;
  let manualFlight = 0;
  let crop;

  function resetCanvas() {
    const replacement = canvas.cloneNode(false);
    canvas.replaceWith(replacement);
    canvas = replacement;
    return replacement;
  }

  async function loadScene() {
    try {
      await photo.decode();
    } catch {
      return;
    }
    try {
      // Probe the actual canvas before loading the 3D renderer. If the browser
      // denies WebGL, the independent 2D renderer can reuse this canvas.
      if (canvas.getContext('webgl2', { antialias: true, alpha: false, powerPreference: 'low-power' })) {
        const { createWebGL } = await import('./scene-webgl.js');
        renderer = createWebGL(canvas, photo);
        canvas.addEventListener('webglcontextlost', event => {
          event.preventDefault();
          renderer?.dispose();
          renderer = createCanvasScene(resetCanvas(), photo);
          paint();
          sync();
        }, { once: true });
      }
    } catch {
      resetCanvas();
    }
    renderer ??= createCanvasScene(canvas, photo);
    paint();
    sync();
  }

  function measure() {
    width = hero.clientWidth;
    height = hero.clientHeight;
    sectionTop = cover.getBoundingClientRect().top + scrollY - header.offsetHeight;
    travel = Math.max(1, cover.offsetHeight - height);
    if (width && height) crop = fitLandscape(width, height, compactView.matches);
    if (enabled) sync();
  }

  function setReplay(start) {
    replayStart = start;
    replay.setAttribute('aria-pressed', String(start !== null));
    label.textContent = start === null ? 'Ver despegue' : 'Volver a la vista';
  }

  function paint() {
    if (!enabled || !width || !height || !crop) return;
    const compact = compactView.matches;
    const targetScroll = clamp((scrollY - sectionTop) / travel);
    scrollProgress += (targetScroll - scrollProgress) * .17;
    const clip = replayStart === null ? 0 : time - replayStart;
    if (clip >= replaySeconds) setReplay(null);
    const targetFlight = ease(clip / 2.8) * (1 - ease((clip - 4.4) / 3.0));
    manualFlight += (targetFlight - manualFlight) * .18;
    const ascent = manualFlight;
    const flight = Math.max(ease((scrollProgress - .08) / .9), ascent);
    cameraX += (pointerX - cameraX) * .075;
    cameraY += (pointerY - cameraY) * .075;
    const orbit = time * TAU / 10.5;
    const drive = Math.sin(flight * Math.PI);
    const craft = {
      x: (compact ? .635 : .75) + .014 * Math.cos(orbit) + .126 * flight + cameraX * .015,
      y: (compact ? .639 : .438) + .026 * Math.sin(orbit * 1.13) - .605 * flight - cameraY * .014,
      width: (compact ? .70 : clamp(.405, 300 / width, 710 / width)) * (1 - .24 * flight),
      pitch: .065 * Math.sin(orbit * .8) - .19 * drive + .067 * cameraY,
      yaw: cameraX * .28 + flight * .61,
      roll: .042 * Math.sin(orbit * 1.09) + .22 * drive,
      beam: Math.max(0, (.48 + .46 * drive + .085 * Math.sin(time * 1.5)) * (1 - .68 * flight)),
      flight,
    };
    if (renderer?.kind !== 'webgl') {
      const styles = {
        '--craft-x': `${craft.x * 100}%`,
        '--craft-y': `${craft.y * 100}%`,
        '--craft-w': `${craft.width * 100}%`,
        '--craft-roll': `${craft.roll}rad`,
        '--craft-lean': `${Math.sin(time * .91) * 8 + cameraX * 13}deg`,
        '--charge': craft.beam,
      };
      for (const [name, value] of Object.entries(styles)) hero.style.setProperty(name, value);
    }

    if (!renderer) return;
    const pixelBudget = compact ? 410000 : 1180000;
    const pixelRatio = Math.min(1.3, devicePixelRatio || 1, Math.sqrt(pixelBudget / (width * height)));
    renderer.render({
      time, width, height, crop, craft,
      pixelWidth: Math.max(1, Math.round(width * pixelRatio)),
      pixelHeight: Math.max(1, Math.round(height * pixelRatio)),
      view: {
        x: .018 * Math.sin(orbit * .56) + cameraX * .035 - .072 * ease(scrollProgress) - .019 * ascent,
        y: .011 * Math.sin(orbit * .69) + cameraY * .024 + .051 * ease(scrollProgress),
        push: .015 * Math.sin(orbit * .46) + .112 * ease(scrollProgress) + .081 * ascent,
      },
    });
    if (scene.dataset.render !== renderer.kind) scene.dataset.render = renderer.kind;
  }

  function tick(now) {
    const delta = lastTick ? Math.min((now - lastTick) / 1000, .15) : 0;
    lastTick = now;
    time += delta;
    if (!lastPaint || now - lastPaint >= (compactView.matches ? 30 : 22)) {
      paint();
      lastPaint = now;
    }
    painting = requestAnimationFrame(tick);
  }

  function sync() {
    const run = enabled && visible && !obscured && !document.hidden && Boolean(width && height);
    if (run && !painting) {
      lastTick = 0;
      lastPaint = 0;
      painting = requestAnimationFrame(tick);
    } else if (!run && painting) {
      cancelAnimationFrame(painting);
      painting = 0;
    }
  }

  const observer = new IntersectionObserver(([entry]) => {
    visible = entry.isIntersecting;
    sync();
  });
  observer.observe(hero);
  new ResizeObserver(measure).observe(hero);
  document.addEventListener('visibilitychange', sync);
  hero.addEventListener('pointermove', event => {
    if (event.pointerType !== 'mouse') return;
    const position = hero.getBoundingClientRect();
    pointerX = clamp((event.clientX - position.left) / width * 2 - 1, -1, 1);
    pointerY = clamp((event.clientY - position.top) / height * 2 - 1, -1, 1);
  }, { passive: true });
  hero.addEventListener('pointerleave', () => { pointerX = 0; pointerY = 0; });
  replay.addEventListener('click', () => setReplay(replayStart === null ? time : null));

  return {
    setEnabled(value) {
      enabled = value;
      replay.hidden = !enabled;
      if (!enabled) setReplay(null);
      measure();
      sync();
      if (enabled && !startup) startup = loadScene();
    },
    setObscured(value) {
      obscured = value;
      sync();
    },
  };
}
