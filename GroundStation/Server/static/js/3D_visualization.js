import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, can;


// =======================
// SETUP
// =======================
function init() {
  const container = document.getElementById('viewer');

  scene = new THREE.Scene();

  camera = new THREE.PerspectiveCamera(
    75,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
  );

  camera.position.set(2, 2, 3);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.enablePan = false;

  const geometry = new THREE.CylinderGeometry(0.5, 0.5, 1.5, 16);
  const material = new THREE.MeshBasicMaterial({
    color: 0x4FD1C5,
    wireframe: true
  });

  can = new THREE.Mesh(geometry, material);
  scene.add(can);

  scene.add(new THREE.AxesHelper(2));

  window.addEventListener('resize', onResize);
}

function onResize() {
  const container = document.getElementById('viewer');

  camera.aspect = container.clientWidth / container.clientHeight;
  camera.updateProjectionMatrix();

  renderer.setSize(container.clientWidth, container.clientHeight);
}


// =======================
// QUATERNION SMOOTH STATE
// =======================
let qA = new THREE.Quaternion();
let qB = new THREE.Quaternion();
let qOut = new THREE.Quaternion();

let hasInit = false;

let segmentStartTime = performance.now();
const segmentDuration = 250; // 4 updates por segundo


// =======================
// INPUT (sensor)
// =======================
export function onReceiveQuats(quats) {
  for (const q of quats) {

    const newQ = new THREE.Quaternion(q[0], q[1], q[2], q[3]);

    // inicialización
    if (!hasInit) {
      qA.copy(newQ);
      qB.copy(newQ);
      hasInit = true;
      segmentStartTime = performance.now();
      continue;
    }

    // mover ventana de interpolación
    qA.copy(qB);
    qB.copy(newQ);
    segmentStartTime = performance.now();

    // evitar flip (shortest path)
    if (qA.dot(qB) < 0) {
      qB.set(-qB.x, -qB.y, -qB.z, -qB.w);
    }
  }
}


// =======================
// RENDER LOOP
// =======================
function animate(time) {
  requestAnimationFrame(animate);

  if (!hasInit) return;

  let alpha = (time - segmentStartTime) / segmentDuration;
  alpha = Math.min(Math.max(alpha, 0), 1);

  // SLERP correcto (API moderna)
  qOut.copy(qA).slerp(qB, alpha);

  can.quaternion.copy(qOut);

  controls.update();
  renderer.render(scene, camera);
}

init();
animate();
