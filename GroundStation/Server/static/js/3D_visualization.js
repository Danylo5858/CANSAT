import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ======================================================
// THREE SETUP
// ======================================================

let scene, camera, renderer, controls, mesh;

// ======================================================
// ACCEL -> ANGLES
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
// LERP
// ======================================================

function lerp(a, b, t) {
	return a + (b - a) * t;
}

// ======================================================
// REAL-TIME STATE (SIN COLA)
// ======================================================

const state = {
	prev: null,   // último estado estable
	next: null,   // nuevo packet

	t: 0,         // interpolación local
	blendTime: 0.15 // suavizado (segundos)
};

// ======================================================
// RECEPCIÓN DE PACKET (RADIO)
// ======================================================

export function onReceiveAccel(packet) {

	const angles = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	const newState = {
		angles,
		time: packet.time,
		timestamp: performance.now() / 1000
	};

	// desplazar estados
	state.prev = state.next;
	state.next = newState;

	// reset interpolación
	state.t = 0;
}

// ======================================================
// UPDATE (FRAME LOOP)
// ======================================================

function update(dt, object3D) {

	if (!state.prev || !state.next) return;

	// acumulamos tiempo local de transición
	state.t += dt / state.blendTime;

	const t = Math.min(state.t, 1);

	// usamos SOLO primeros 2 puntos del segmento actual (stream real-time)
	const a0 = state.prev.angles[0];
	const a1 = state.next.angles[0];

	if (!a0 || !a1) return;

	const roll = lerp(a0.roll, a1.roll, t);
	const pitch = lerp(a0.pitch, a1.pitch, t);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;
}

// ======================================================
// INIT THREE
// ======================================================

function init() {

	scene = new THREE.Scene();

	camera = new THREE.PerspectiveCamera(
		75,
		window.innerWidth / window.innerHeight,
		0.1,
		1000
	);

	camera.position.set(2, 2, 3);

	renderer = new THREE.WebGLRenderer({ antialias: true });
	renderer.setSize(window.innerWidth, window.innerHeight);
	document.body.appendChild(renderer.domElement);

	controls = new OrbitControls(camera, renderer.domElement);
	controls.enableDamping = true;

	const geometry = new THREE.CylinderGeometry(0.5, 0.5, 1.5, 16);
	const material = new THREE.MeshNormalMaterial({ wireframe: true });

	mesh = new THREE.Mesh(geometry, material);

	scene.add(mesh);
	scene.add(new THREE.AxesHelper(2));

	window.addEventListener('resize', () => {
		camera.aspect = window.innerWidth / window.innerHeight;
		camera.updateProjectionMatrix();
		renderer.setSize(window.innerWidth, window.innerHeight);
	});
}

// ======================================================
// ANIMATE LOOP
// ======================================================

let last = performance.now();

function animate() {

	requestAnimationFrame(animate);

	const now = performance.now();
	const dt = (now - last) / 1000;
	last = now;

	update(dt, mesh);

	controls.update();
	renderer.render(scene, camera);
}

// ======================================================
// START
// ======================================================

init();
animate();
