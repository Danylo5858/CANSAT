import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

// ======================================================
// RESIZE (TU FUNCIÓN EXACTA)
// ======================================================

function onResize() {
	const container = document.getElementById('viewer');

	camera.aspect = container.clientWidth / container.clientHeight;
	camera.updateProjectionMatrix();

	renderer.setSize(container.clientWidth, container.clientHeight);
	controls.update();
}

// ======================================================
// ACCEL -> ANGLES (OPTIMIZADO SIN GC)
// ======================================================

const tmpAnglesA = { roll: 0, pitch: 0 };
const tmpAnglesB = { roll: 0, pitch: 0 };

function accelToAngles(ax, ay, az, out) {
	const roll = Math.atan2(ay, az);
	const pitch = Math.atan2(-ax, Math.sqrt(ay * ay + az * az));

	out.roll = roll * 180 / Math.PI;
	out.pitch = pitch * 180 / Math.PI;
}

// ======================================================
// LERP
// ======================================================

function lerp(a, b, t) {
	return a + (b - a) * t;
}

// ======================================================
// REALTIME STATE (SIN COLA)
// ======================================================

const state = {
	prev: null,
	next: null,
	t: 0,
	blendTime: 0.12 // más bajo = más responsivo (menos lag visual)
};

// ======================================================
// RECEPCIÓN DE PACKET
// ======================================================

export function onReceiveAccel(packet) {

	// reutilizamos buffers (NO objetos nuevos por frame crítico)
	const angles = [];

	for (let i = 0; i < packet.accel.length; i++) {
		const p = packet.accel[i];

		const out = i === 0 ? tmpAnglesA : tmpAnglesB;

		accelToAngles(p[0], p[1], p[2], out);

		angles.push({
			roll: out.roll,
			pitch: out.pitch
		});
	}

	const newState = {
		angles,
		time: packet.time
	};

	state.prev = state.next;
	state.next = newState;

	state.t = 0;
}

// ======================================================
// UPDATE LOOP
// ======================================================

function update(dt, object3D) {

	if (!state.prev || !state.next) return;

	state.t += dt / state.blendTime;

	const t = Math.min(state.t, 1);

	const a0 = state.prev.angles[0];
	const a1 = state.next.angles[0];

	if (!a0 || !a1) return;

	const roll = lerp(a0.roll, a1.roll, t);
	const pitch = lerp(a0.pitch, a1.pitch, t);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;

	// 🚨 BLOQUEO TOTAL DE YAW
	object3D.rotation.y = 0;
}

// ======================================================
// INIT (TU FUNCIÓN EXACTA)
// ======================================================

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

// ======================================================
// ANIMATION LOOP
// ======================================================

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

// ======================================================
// START
// ======================================================

init();
animate();
