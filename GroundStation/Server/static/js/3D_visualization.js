import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

/* =========================
   UTILS
========================= */

function onResize() {
	const container = document.getElementById('viewer');

	camera.aspect = container.clientWidth / container.clientHeight;
	camera.updateProjectionMatrix();

	renderer.setSize(container.clientWidth, container.clientHeight);
	controls.update();
}

/**
 * Accel → quaternion estable
 * Asume que accel representa gravedad aproximada
 */
function accelToQuat(ax, ay, az) {
	const len = Math.hypot(ax, ay, az);
	if (len === 0) return new THREE.Quaternion();

	const x = ax / len;
	const y = ay / len;
	const z = az / len;

	const up = new THREE.Vector3(x, y, z);
	const target = new THREE.Vector3(0, 1, 0);

	return new THREE.Quaternion().setFromUnitVectors(up, target);
}

/* =========================
   STREAM BUFFER
========================= */

const samples = []; // quaternions

let index = 0;
let t = 0;

const SPEED = 10; // velocidad de interpolación

const tmpQuat = new THREE.Quaternion();

/* =========================
   INPUT STREAM
========================= */

export function onReceiveAccel(packet) {
	const quats = packet.accel.map(p => {
		return accelToQuat(p[0], p[1], p[2]);
	});

	for (const q of quats) {
		samples.push(q);
	}

	// 🔥 evitar delay acumulado
	const MAX = 200;
	if (samples.length > MAX) {
		const remove = samples.length - MAX;
		samples.splice(0, remove);
		index = Math.max(0, index - remove);
	}
}

/* =========================
   UPDATE LOOP
========================= */

function update(dt, object3D) {
	if (samples.length < 2) return;

	const a = samples[index];
	const b = samples[index + 1];

	if (!a || !b) return;

	t += dt * SPEED;

	if (t > 1) {
		t = 0;
		index++;

		// clamp seguro
		if (index >= samples.length - 2) {
			index = samples.length - 2;
		}
	}

	// 🔥 interpolación esférica (SIN saltos)
	tmpQuat.copy(a).slerp(b, t);

	object3D.quaternion.copy(tmpQuat);
}

/* =========================
   THREE SETUP
========================= */

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
	renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
	renderer.setSize(container.clientWidth, container.clientHeight);
	container.appendChild(renderer.domElement);

	controls = new OrbitControls(camera, renderer.domElement);
	controls.enableDamping = false;
	controls.rotateSpeed = 0.4;
	controls.enablePan = false;

	const geometry = new THREE.CylinderGeometry(0.5, 0.5, 1.5, 16);
	const material = new THREE.MeshBasicMaterial({
		color: 0x4FD1C5,
		wireframe: true
	});

	mesh = new THREE.Mesh(geometry, material);
	scene.add(mesh);
	scene.add(new THREE.AxesHelper(2));

	window.addEventListener('resize', onResize);
}

/* =========================
   LOOP
========================= */

let lastTime = performance.now();

function animate() {
	requestAnimationFrame(animate);

	const now = performance.now();
	const dt = (now - lastTime) / 1000;
	lastTime = now;

	update(dt, mesh);

	controls.update();
	renderer.render(scene, camera);
}

init();
animate();
