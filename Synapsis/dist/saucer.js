import {
  BoxGeometry, CanvasTexture, Group, InstancedMesh, LatheGeometry, Mesh,
  MeshStandardMaterial, Object3D, RepeatWrapping, SphereGeometry, SRGBColorSpace,
  TorusGeometry, Vector2,
} from './vendor/three.js';

function panelTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 256;
  const context = canvas.getContext('2d');
  const image = context.createImageData(canvas.width, canvas.height);
  let state = 313;
  const rnd = () => {
    state = (Math.imul(1664525, state) + 1013904223) >>> 0;
    return state / 4294967296;
  };
  for (let y = 0; y < canvas.height; y++) {
    const brushing = Math.floor(5 * rnd() + 8 * Math.sin(y * .85));
    for (let x = 0; x < canvas.width; x++) {
      const seam = x % 64 < 2 || (y + Math.floor(x / 64) % 2 * 11) % 48 < 2;
      const panel = (Math.floor(x / 64) * 7 + Math.floor(y / 48) * 3) % 19;
      const value = 108 + brushing + panel + rnd() * 33 - (seam ? 51 : 0);
      const index = 4 * (y * canvas.width + x);
      image.data.set([value + 8, value + 2, value + 7, 255], index);
    }
  }
  context.putImageData(image, 0, 0);
  context.fillStyle = '#cbc1c6';
  for (let panel = 1; panel < 16; panel++) {
    for (let row = 1; row < 6; row++) {
      context.fillRect(panel * 64 + 6, row * 43, 2, 2);
      context.fillRect(panel * 64 - 6, row * 43, 2, 2);
    }
  }
  const texture = new CanvasTexture(canvas);
  texture.wrapS = RepeatWrapping;
  texture.colorSpace = SRGBColorSpace;
  return texture;
}

export function makeSaucer() {
  const ship = new Group();
  const patina = panelTexture();
  const hull = new MeshStandardMaterial({ color: '#ac8f9a', map: patina, roughness: .54, metalness: .34 });
  const edge = new MeshStandardMaterial({ color: '#403448', roughness: .42, metalness: .48 });
  const bronze = new MeshStandardMaterial({ color: '#8f6c55', roughness: .43, metalness: .42 });
  const vent = new MeshStandardMaterial({ color: '#211c2a', roughness: .71, metalness: .28 });
  const ceramic = new MeshStandardMaterial({ color: '#c3a3a0', map: patina, roughness: .36, metalness: .36 });
  const windows = new MeshStandardMaterial({ color: '#553959', roughness: .33, metalness: .30, emissive: '#51284e', emissiveIntensity: .62 });
  const amber = new MeshStandardMaterial({ color: '#ffc577', roughness: .33, emissive: '#ff9e27', emissiveIntensity: 2.0 });
  const pearl = new MeshStandardMaterial({ color: '#ffdcb1', roughness: .31, emissive: '#ffcc77', emissiveIntensity: 1.45 });

  const lathe = (profile, material) => {
    const mesh = new Mesh(new LatheGeometry(profile.map(([r, y]) => new Vector2(r, y)), 120), material);
    ship.add(mesh);
  };
  const ring = (radius, tube, height, material) => {
    const mesh = new Mesh(new TorusGeometry(radius, tube, 7, 120), material);
    mesh.rotation.x = Math.PI / 2;
    mesh.position.y = height;
    ship.add(mesh);
  };
  const repeat = (geometry, material, count, place) => {
    const mesh = new InstancedMesh(geometry, material, count);
    const dummy = new Object3D();
    for (let i = 0; i < count; i++) {
      place(dummy, i / count * 2 * Math.PI, i);
      dummy.updateMatrix();
      mesh.setMatrixAt(i, dummy.matrix);
    }
    ship.add(mesh);
  };

  lathe([
    [0, -.57], [.45, -.57], [.57, -.55], [.66, -.48], [.90, -.47],
    [1.03, -.42], [1.38, -.405], [1.55, -.38], [1.80, -.345], [2.13, -.30],
    [2.31, -.24], [2.58, -.18], [2.84, -.11], [3.01, -.068], [3.13, -.026],
    [3.18, .019], [3.17, .073], [3.07, .127], [2.88, .177], [2.54, .231],
    [2.21, .28], [1.89, .317], [1.52, .353], [1.25, .383], [1.14, .405],
    [.89, .415], [0, .418],
  ], hull);
  lathe([[0, .413], [1.18, .413], [1.19, .458], [1.07, .525], [.91,.587],
    [.72, .638], [.44, .671], [.17, .684], [0, .685]], ceramic);
  lathe([[.85, .471], [1.115, .471], [1.079, .503], [1.025, .533], [.967, .55], [.85, .55]], windows);
  lathe([[0,-.629],[.33,-.629],[.43,-.605],[.49,-.564],[.42,-.53],[0,-.53]], bronze);
  lathe([[0,.684],[.039,.684],[.039,.745],[.012,.855],[0,.86]], bronze);
  ring(3.145, .027, .022, bronze);
  ring(3.068, .042, -.068, edge);
  ring(2.89, .018, .166, edge);
  ring(2.18, .020, .286, edge);
  ring(1.28, .024, .391, bronze);
  ring(2.72, .026, -.155, edge);
  ring(2.17, .029, -.288, bronze);
  ring(1.44, .018, -.405, edge);
  ring(.54, .025, -.54, edge);
  ring(.358, .021, -.619, amber);

  repeat(new BoxGeometry(.21,.047,.077), vent, 48, (object, a) => {
    object.position.set(3.117 * Math.sin(a), .038, 3.117 * Math.cos(a));
    object.rotation.y = a;
  });
  repeat(new SphereGeometry(.044, 8, 5), pearl, 30, (object, a) => {
    object.position.set(3.16 * Math.sin(a), .032, 3.16 * Math.cos(a));
    object.scale.set(1, .75, .78);
  });
  repeat(new BoxGeometry(.116,.028,.035), amber, 18, (object, a) => {
    object.position.set(1.085 * Math.sin(a), .504, 1.085 * Math.cos(a));
    object.rotation.y = a;
  });
  repeat(new BoxGeometry(.24,.030,.49), vent, 24, (object, a) => {
    object.position.set(2.35 * Math.sin(a), -.247, 2.35 * Math.cos(a));
    object.rotation.set(-.28, a, 0, 'YXZ');
  });
  repeat(new BoxGeometry(.21,.025,.27), bronze, 12, (object, a) => {
    object.position.set(1.62 * Math.sin(a), -.391, 1.62 * Math.cos(a));
    object.rotation.y = a;
  });
  repeat(new SphereGeometry(.045, 8, 5), amber, 12, (object, a) => {
    object.position.set(.87 * Math.sin(a), -.475, .87 * Math.cos(a));
  });

  return { ship, amber, pearl };
}
