import {
  AmbientLight, CanvasTexture, Color, DirectionalLight, LinearFilter, Mesh, OrthographicCamera,
  PerspectiveCamera, PlaneGeometry, Scene, ShaderMaterial, Texture, Vector3, Vector4, WebGLRenderer,
} from './vendor/three.js';
import { landscapeMap } from './terrain.js';
import { landscapeFragment, landscapeVertex } from './landscape-shader.js';
import { makeSaucer } from './saucer.js';

export function createWebGL(canvas, photo) {
  const renderer = new WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: 'low-power' });
  renderer.autoClear = false;
  renderer.setClearColor(new Color('#161f2d'), 1);
  const landscape = new Texture(photo);
  landscape.minFilter = LinearFilter;
  landscape.generateMipmaps = false;
  landscape.needsUpdate = true;
  const terrainMap = new CanvasTexture(landscapeMap());
  terrainMap.minFilter = LinearFilter;
  terrainMap.generateMipmaps = false;

  const uniforms = {
    landscape: { value: landscape },
    terrainMap: { value: terrainMap },
    crop: { value: new Vector4() },
    cameraMotion: { value: new Vector3() },
    beam: { value: new Vector3() },
    time: { value: 0 },
    aspect: { value: 1 },
  };
  const environment = new Scene();
  const plane = new Mesh(new PlaneGeometry(2, 2), new ShaderMaterial({
    uniforms,
    depthTest: false,
    depthWrite: false,
    vertexShader: landscapeVertex,
    fragmentShader: landscapeFragment,
  }));
  plane.frustumCulled = false;
  environment.add(plane);
  const screen = new OrthographicCamera(-1, 1, 1, -1, 0, 2);

  const objects = new Scene();
  const camera = new PerspectiveCamera(36, 1, .1, 80);
  camera.position.set(0, 0, 22);
  const light = new DirectionalLight('#f7d6df', 2.33);
  const cool = new DirectionalLight('#83dce0', 1.02);
  const glow = new DirectionalLight('#ffb06b', .54);
  light.position.set(2.8, 4.8, 5.8);
  cool.position.set(-4, 1.2, -4);
  glow.position.set(1.3, -4, 5);
  objects.add(new AmbientLight('#baccdf', .95), light, cool, glow);
  const { ship, amber, pearl } = makeSaucer();
  objects.add(ship);
  const engine = new Vector3();

  renderer.compile(environment, screen);
  renderer.compile(objects, camera);

  let width = 0;
  let height = 0;
  return {
    kind: 'webgl',
    render(frame) {
      if (width !== frame.pixelWidth || height !== frame.pixelHeight) {
        width = frame.pixelWidth;
        height = frame.pixelHeight;
        renderer.setSize(width, height, false);
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
      }
      const { time, view, craft } = frame;
      const layout = frame.crop;
      uniforms.time.value = time;
      uniforms.aspect.value = camera.aspect;
      uniforms.crop.value.set(-layout.x / layout.w, -layout.y / layout.h, frame.width / layout.w, frame.height / layout.h);
      uniforms.cameraMotion.value.set(view.x, view.y, view.push);
      const viewHeight = 2 * camera.position.z * Math.tan(Math.PI * camera.fov / 360);
      const viewWidth = viewHeight * camera.aspect;
      ship.position.set((craft.x - .5) * viewWidth, (.5 - craft.y) * viewHeight, -craft.flight * 4);
      ship.scale.setScalar(viewWidth * craft.width / 6.4);
      ship.rotation.set(-.28 + craft.pitch, time * .12 + craft.yaw, craft.roll, 'ZXY');
      ship.updateMatrixWorld();
      engine.set(0, -.58, 0);
      ship.localToWorld(engine).project(camera);
      uniforms.beam.value.set((engine.x + 1) * .5, (1 - engine.y) * .5, craft.beam);
      amber.emissiveIntensity = 1.45 + craft.beam * .8 + Math.sin(time * 3.3) * .19;
      pearl.emissiveIntensity = 1.5 + Math.sin(time * 5.7) * .23;

      renderer.clear();
      renderer.render(environment, screen);
      renderer.clearDepth();
      renderer.render(objects, camera);
    },
    dispose() {
      const materials = new Set();
      const geometries = new Set();
      for (const scene of [environment, objects]) {
        scene.traverse(object => {
          if (object.geometry) geometries.add(object.geometry);
          if (object.material) materials.add(object.material);
        });
      }
      for (const material of materials) {
        material.map?.dispose();
        material.dispose();
      }
      for (const geometry of geometries) geometry.dispose();
      landscape.dispose();
      terrainMap.dispose();
      renderer.dispose();
    },
  };
}
