import { paths, terrainHeight, terrainWidth } from './terrain.js';

const sine = Math.sin;
const point = (i, salt) => {
  const n = Math.sin(i * 197.57 + salt * 312.85) * 45131.23;
  return n - Math.floor(n);
};

function createHaze() {
  const texture = document.createElement('canvas');
  texture.width = 768;
  texture.height = 108;
  const ctx = texture.getContext('2d');
  for (let i = 0; i < 20; i++) {
    ctx.save();
    const x = point(i, 1) * texture.width;
    const y = 35 + point(i, 2) * 38;
    const radius = 23 + point(i, 3) * 20;
    ctx.translate(x, y);
    ctx.scale(2.9 + point(i, 5) * 2.5, .42 + point(i, 6) * .25);
    const halo = ctx.createRadialGradient(0, 0, 0, 0, 0, radius);
    halo.addColorStop(0, 'rgba(116,201,203,.31)');
    halo.addColorStop(.43, 'rgba(69,135,172,.19)');
    halo.addColorStop(1, 'rgba(69,135,172,0)');
    ctx.fillStyle = halo;
    ctx.fillRect(-radius, -radius, radius * 2, radius * 2);
    ctx.restore();
  }
  return texture;
}

export function createCanvasScene(canvas, photo) {
  const context = canvas.getContext('2d', { alpha: false });
  if (!context) return null;
  const { water, ridge, foreground } = paths();
  const haze = createHaze();
  const starPoints = Array.from({ length: 95 }, (_, i) => [
    point(i, 1), point(i, 2) * .47, point(i, 3), point(i, 4) * 38,
  ]);
  const drawPhoto = (x = 0, y = 0, zoom = 0) => {
    context.drawImage(photo, x - zoom / 2, y - zoom / 4, terrainWidth + zoom, terrainHeight + zoom / 2);
  };
  const naturalWidth = photo.naturalWidth;
  const naturalHeight = photo.naturalHeight;

  return {
    kind: 'canvas',
    render(frame) {
      const { time, crop, view, craft } = frame;
      if (canvas.width !== frame.pixelWidth || canvas.height !== frame.pixelHeight) {
        canvas.width = frame.pixelWidth;
        canvas.height = frame.pixelHeight;
      }
      const ratio = canvas.width / frame.width;
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      context.globalAlpha = 1;
      context.fillStyle = '#121c2b';
      context.fillRect(0, 0, frame.width, frame.height);
      context.translate(crop.x, crop.y);
      context.scale(crop.w / terrainWidth, crop.h / terrainHeight);
      const surge = view.push * 55;
      drawPhoto(view.x * 210, view.y * 113, surge);

      // Illumination rolls across the cratered disk independently of the camera.
      context.save();
      context.beginPath();
      context.ellipse(744, 227, 226, 221, 0, Math.PI, 2 * Math.PI);
      context.clip();
      const moonLight = context.createRadialGradient(819, 109, 0, 819, 109, 197);
      moonLight.addColorStop(0, 'rgba(255,194,164,.22)');
      moonLight.addColorStop(1, 'transparent');
      context.fillStyle = moonLight;
      context.globalCompositeOperation = 'screen';
      context.globalAlpha = .42 + .30 * sine(time * .61);
      context.fillRect(517, 6, 460, 225);
      context.restore();

      context.save();
      context.clip(ridge);
      context.globalAlpha = .64;
      drawPhoto(view.x * 415, view.y * 184, surge * 1.14);
      context.restore();

      context.save();
      context.clip(water);
      context.globalCompositeOperation = 'source-over';
      context.globalAlpha = .78;
      for (let y = 373; y < terrainHeight; y += 2.3) {
        const distance = (y - 373) / 127;
        const spread = 2.5 + distance * 7.2;
        const slide = (sine(y * .33 + time * 2.85) + sine(y * .945 - time * 3.43) * .59) * spread;
        const sourceY = Math.min(497, Math.max(372, y + sine(y * .51 - time * 2.9) * (1 + distance)));
        context.drawImage(photo, 0, sourceY * naturalHeight / 500, naturalWidth,
          2.8 * naturalHeight / 500, slide - 9, y, terrainWidth + 20, 2.8);
      }
      context.globalCompositeOperation = 'screen';
      for (let i = 0; i < 73; i++) {
        const y = 380 + point(i, 8) * 120;
        const strength = (.5 + .5 * sine(i * 6.83 - time * (2.1 + point(i, 9) * 2))) ** 4;
        const spread = 42 + (y - 380) * .8;
        const x = 827 + (point(i, 10) - .5) * spread + sine(time * .92 + i * 7) * 10;
        context.globalAlpha = strength * .56;
        context.fillStyle = i % 4 ? '#e19878' : '#f7c7ad';
        context.fillRect(x, y, 6 + point(i, 11) * 24, .45 + point(i, 4) * .8);
      }
      const beamCenter = (craft.x * frame.width - crop.x) * terrainWidth / crop.w;
      for (let i = 0; i < 34; i++) {
        const y = 383 + point(i, 19) * 113;
        const x = beamCenter + (point(i, 17) - .5) * 63 + sine(time * 2.5 + i * 1.8) * 9;
        const glint = (.5 + .5 * sine(time * 4.2 + i * 2.9)) ** 3;
        context.globalAlpha = glint * craft.beam * .48;
        context.fillStyle = '#ffcd8e';
        context.fillRect(x, y, 4 + point(i, 23) * 18, .72);
      }
      context.restore();

      context.save();
      context.globalCompositeOperation = 'screen';
      for (const [x, y, size, offset] of starPoints) {
        if (x > .62 && y < .47) continue;
        const shimmer = (.5 + .5 * sine(time * (1.3 + size * 2.2) + offset)) ** 2;
        context.globalAlpha = shimmer * (.44 + size * .54);
        context.fillStyle = '#ffdfbb';
        context.beginPath();
        context.arc(x * 1000, y * 500, .36 + size * .58, 0, 2 * Math.PI);
        context.fill();
      }
      const meteor = ((time + .8) % 8.8) / 1.32;
      if (meteor < 1) {
        const lead = [530 + meteor * 300, 114 - meteor * 60];
        const tail = [lead[0] - 61, lead[1] + 15];
        const trail = context.createLinearGradient(...tail, ...lead);
        trail.addColorStop(0, 'transparent');
        trail.addColorStop(1, '#ffe0ae');
        context.globalAlpha = Math.sin(meteor * Math.PI);
        context.strokeStyle = trail;
        context.lineWidth = 1.1;
        context.beginPath();
        context.moveTo(...tail);
        context.lineTo(...lead);
        context.stroke();
      }
      context.restore();

      for (const [y, speed, opacity] of [[276, 24, .78], [341, -32, .61]]) {
        const x = ((time * speed) % 1000 + 1000) % 1000;
        context.globalAlpha = opacity;
        context.drawImage(haze, x, y + sine(time * .43) * 6, 1000, 106);
        context.drawImage(haze, x - 1000, y + sine(time * .43) * 6, 1000, 106);
      }
      context.globalAlpha = 1;
      context.save();
      context.clip(foreground);
      context.globalAlpha = .59;
      drawPhoto(view.x * 550, view.y * 264, surge * 1.28);
      context.restore();

      // Engine light is drawn in viewport space so it follows the ship
      // even when the camera crop changes on narrow screens.
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
      const engineX = craft.x * frame.width + 2;
      const engineY = craft.y * frame.height + craft.width * frame.width * .145;
      const reach = frame.height * (.35 + .09 * sine(time * .9));
      const spread = reach * .19;
      const light = context.createLinearGradient(0, engineY, 0, engineY + reach);
      light.addColorStop(0, 'rgba(255,219,153,.60)');
      light.addColorStop(.32, 'rgba(255,178,108,.23)');
      light.addColorStop(1, 'rgba(255,167,104,0)');
      context.save();
      context.globalCompositeOperation = 'screen';
      context.globalAlpha = craft.beam * .83;
      context.filter = 'blur(4px)';
      context.fillStyle = light;
      context.beginPath();
      context.moveTo(engineX - 6, engineY);
      context.lineTo(engineX + 6, engineY);
      context.lineTo(engineX + spread, engineY + reach);
      context.lineTo(engineX - spread, engineY + reach);
      context.fill();
      context.filter = 'none';
      context.fillStyle = '#ffd699';
      for (let i = 0; i < 18; i++) {
        const fall = (point(i, 22) + time * (.21 + point(i, 24) * .12)) % 1;
        const x = engineX + (point(i, 25) - .5) * spread * (fall + .12) * 1.7;
        const y = engineY + fall * reach;
        context.globalAlpha = Math.sin(fall * Math.PI) * craft.beam * .67 * (1 - .53 * fall);
        context.beginPath();
        context.arc(x, y, .48 + point(i, 26) * .89, 0, 2 * Math.PI);
        context.fill();
      }
      context.restore();
    },
    dispose() {},
  };
}
