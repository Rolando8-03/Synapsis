export const landscapeVertex = /* glsl */ `
varying vec2 screen;
void main() {
  screen = vec2(uv.x, 1.0 - uv.y);
  gl_Position = vec4(position.xy, 0.0, 1.0);
}
`;

export const landscapeFragment = /* glsl */ `
varying vec2 screen;
uniform sampler2D landscape;
uniform sampler2D terrainMap;
uniform vec4 crop;
uniform vec3 cameraMotion;
uniform vec3 beam;
uniform float time;
uniform float aspect;

vec2 uv(vec2 topLeft) { return vec2(topLeft.x, 1.0 - topLeft.y); }

float random(vec2 cell) {
  vec3 p = fract(vec3(cell.xyx) * .1031);
  p += dot(p, p.yzx + 33.33);
  return fract((p.x + p.y) * p.z);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  f = f * f * (3.0 - 2.0 * f);
  return mix(mix(random(i), random(i + vec2(1,0)), f.x),
             mix(random(i + vec2(0,1)), random(i + 1.0), f.x), f.y);
}

float clouds(vec2 p) {
  return .56 * noise(p) + .28 * noise(p * 2.08 + 21.7)
    + .11 * noise(p * 4.03 - 17.0);
}

float starField(vec2 p, float scale, float seed) {
  vec2 grid = p * vec2(scale * 2.0, scale) + seed;
  vec2 cell = floor(grid);
  float rnd = random(cell + seed);
  vec2 pos = vec2(random(cell + 13.1), random(cell + 91.4)) * .62 + .18;
  float d = length(fract(grid) - pos);
  float point = 1.0 - smoothstep(.017, .057, d);
  float flicker = .42 + .56 * pow(.5 + .5 * sin(time * (1.2 + rnd * 2.1) + rnd * 67.0), 2.0);
  return point * flicker * smoothstep(.85, .97, rnd);
}

float meteor(vec2 p) {
  float phase = mod(time + .8, 8.8) / 1.32;
  vec2 head = vec2(.52, .155) + vec2(.29, -.128) * phase;
  vec2 orient = normalize(vec2(.29, -.128) * vec2(aspect, 1));
  vec2 delta = (p - head) * vec2(aspect, 1);
  float back = -dot(delta, orient);
  float crossTrack = abs(dot(delta, vec2(orient.y, -orient.x)));
  float streak = exp(-crossTrack * crossTrack * 900000.0) * exp(-back * 40.0) * step(0.0, back);
  return streak * smoothstep(0.0, .13, phase) * (1.0 - smoothstep(.73, 1.0, phase)) * .76;
}

void main() {
  vec2 place = crop.xy + screen * crop.zw;
  float z = texture2D(terrainMap, uv(place)).g;
  float parallax = .11 + z * .9;
  vec2 p = place - cameraMotion.xy * parallax - (place - vec2(.66,.66)) * cameraMotion.z;
  vec3 land = texture2D(landscape, uv(p)).rgb;
  float water = texture2D(terrainMap, uv(p)).r;
  vec2 lunar = (p - vec2(.745,.469)) * vec2(2.0,1.0);
  float face = (1.0 - smoothstep(.39,.465,length(lunar))) * (1.0 - smoothstep(.40,.465,p.y));
  vec2 driftOnDisk = vec2(.0062 * sin(time*.33 + lunar.y*2.9), .0032 * sin(time*.21 + lunar.x));
  vec3 lunarSurface = texture2D(landscape, uv(p + driftOnDisk)).rgb;
  float lunarGlow = .034 * sin(time * .46 - lunar.y*2.6 + lunar.x*3.2);
  land = mix(land, lunarSurface * (1.0 + lunarGlow), face * .62);

  // A perspective-compressed set of traveling waves. Their slopes distort
  // reflected color and light at different scales.
  if (water > .005) {
    float reach = clamp((p.y - .75) * 4.0, 0.0, 1.0);
    vec2 w = vec2(p.x * 28.0, (1.0 - exp(-4.8 * max(0.0, p.y - .73))) * 57.0);
    float streakNoise = noise(vec2(w.x * 1.28 + time * .52, w.y * .34));
    float a = w.y * 1.71 + w.x * .57 - time * 2.9 + 1.8 * streakNoise;
    float b = w.y * 3.28 - w.x * .76 + time * 3.6;
    float c = w.y * .78 + w.x * 1.42 - time * 1.7;
    float slopeX = .56*cos(a) - .33*cos(b) + .23*cos(c);
    float slopeY = .46*cos(a) + .34*cos(b) + .17*cos(c);
    vec2 distorted = p + vec2(slopeX * .009, slopeY * .0036) * (.66 + reach);
    vec3 reflection = texture2D(landscape, uv(distorted)).rgb;
    float paths = max(exp(-pow((p.x - .842 + slopeX * .023) * 13.5, 2.0)) * .86,
                      exp(-pow((p.x - .637 + slopeX * .034) * 10.2, 2.0)) * .38);
    float brokenMirror = pow(max(0.0, slopeY * .54 + .49), 5.0) * (.25 + .75 * streakNoise);
    float foam = pow(max(0.0, cos(b + .65 * sin(c))), 14.0) * .12;
    vec3 reflectedLight = vec3(1.0,.60,.41) * paths * (brokenMirror * .45 + foam * reach);
    reflection = mix(reflection * vec3(.88,.86,1.04), reflection * 1.2, .4 + slopeY * .29);
    land = mix(land, reflection + reflectedLight, water * .87);
  }

  float mantle = 1.0 - smoothstep(.42,.56,p.y);
  float night = 1.0 - smoothstep(.15,.34,max(max(land.r,land.g),land.b));
  float stars = starField(p + vec2(time*.0004,0), 84.0, 7.0)
    + starField(p, 151.0, 113.0) * .52;
  land += vec3(1.0,.84,.73) * stars * mantle * night * .63;
  land += vec3(1.0,.75,.49) * meteor(screen) * mantle;

  // Separate air currents move between the ridgeline and the foreground.
  float farBand = exp(-pow((p.y - .665 - sin(p.x*7.0)*.019) * 17.0, 2.0));
  float nearBand = exp(-pow((p.y - .803 + sin(p.x*5.4)*.025) * 13.2, 2.0));
  if (farBand + nearBand > .019) {
    float hardRidge = smoothstep(.16,.38,z) * (1.0 - smoothstep(.66,.75,p.y));
    vec2 stream = vec2(p.x * 7.6 - time * .33, p.y * 31.0 + sin(p.x*8.0 + time*.36)*.38);
    float farAir = smoothstep(.29,.73, clouds(stream)) * farBand * (.36 + .64*smoothstep(.14,.83,p.x));
    vec2 drift = vec2(p.x * 5.8 + time*.24, p.y * 42.0 - time*.12);
    float nearAir = smoothstep(.34,.74, clouds(drift)) * nearBand;
    land = mix(land, vec3(.66,.42,.62), farAir * (.46 - hardRidge * .26));
    land = mix(land, vec3(.60,.38,.54), nearAir * .29 * (1.0 - water*.6));
  }

  float moonLight = exp(-pow((p.x - .83)*2.9, 2.0)) * smoothstep(.46,.60,p.y);
  land *= 1.0 + moonLight * (.027 * sin(time * .38) + .014 * noise(p*10.0 + time*.12));

  // The projected engine follows the camera and lights both air and water.
  float below = screen.y - beam.y;
  if (below > -.02 && beam.z > .005) {
    float live = beam.z * smoothstep(-.02,.03,below);
    float dx = (screen.x - beam.x) * aspect;
    float cone = .015 + .129 * max(below, 0.0);
    float lit = exp(-pow(dx/max(cone,.001),2.0) * 1.7) * exp(-max(below,0.0)*4.4);
    float dust = .61 + .39 * noise(vec2(dx*58.0,below*24.0 - time*1.6));
    float core = exp(-pow(dx/max(.007 + below*.032,.006),2.0)) * exp(-max(below,0.0)*6.4);
    land += vec3(.87,.55,.23) * (lit*dust*.40 + core*.35) * live;
    land += vec3(1.0,.72,.37) * lit * water * (1.1 + sin(p.y*580.0-time*4.3)*.36) * live * .21;
  }
  land = clamp(land, 0.0, 1.0);
  gl_FragColor = vec4(land, 1.0);
}
`;
