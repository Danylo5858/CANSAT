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
// ACCEL -> ANGLES (SIN OBJETOS NUEVOS)
// ======================================================

function accelToAngles(ax, ay, az) {
	const roll = Math.atan2(ay, az);
	const pitch = Math.atan2(-ax, Math.sqrt(ay * ay + az * az));

	return {
		roll: roll * 180 / Math.PI,
		pitch: pitch * 180 / Math.PI
	};
}

// ======================================================
// STATE (PIPELINE ESTABLE)
// ======================================================

const queue = [];

const state = {
	current: null,
	next: null,
	t: 0,
	segmentDuration: 0.12 // estabilidad (clave)
};

// ======================================================
// INPUT
// ======================================================

export function onReceiveAccel(packet) {

	const angles = packet.accel.map(p => {
		return accelToAngles(p[0], p[1], p[2]);
	});

	queue.push({
		angles
	});
}

// ======================================================
// CONSUMO DE COLA (ESTABILIZA TIMING)
// ======================================================

function consumeQueue() {

	if (!state.current && queue.length > 0) {
		state.current = queue.shift();
	}

	if (!state.next && queue.length > 0) {
		state.next = queue.shift();
		state.t = 0;
	}
}

// ======================================================
// LERP
// ======================================================

function lerp(a, b, t) {
	return a + (b - a) * t;
}

// ======================================================
// UPDATE (FLUIDO REAL)
// ======================================================

function update(dt, object3D) {

	consumeQueue();

	if (!state.current || !state.next) return;

	state.t += dt / state.segmentDuration;

	const t = Math.min(state.t, 1);

	const a0 = state.current.angles[0];
	const a1 = state.next.angles[0];

	if (!a0 || !a1) return;

	const roll = lerp(a0.roll, a1.roll, t);
	const pitch = lerp(a0.pitch, a1.pitch, t);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;

	// 🚨 YAW BLOQUEADO
	object3D.rotation.y = 0;

	// avanzar segmento
	if (state.t >= 1) {
		state.current = state.next;
		state.next = null;
		state.t = 0;
	}
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
// LOOP
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
