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
// BUFFER TEMPORAL
// ======================================================

const buffer = [];

// ======================================================
// INPUT
// ======================================================

export function onReceiveAccel(packet) {

	const angles = packet.accel.map(p => accelToAngles(p[0], p[1], p[2]));

	buffer.push({
		time: packet.time, // IMPORTANTE: timestamp del sensor
		angles
	});

	// evitar crecimiento infinito
	if (buffer.length > 200) buffer.shift();
}

// ======================================================
// BUSCAR INTERPOLACIÓN POR TIEMPO
// ======================================================

function sampleAtTime(t) {

	if (buffer.length < 2) return null;

	for (let i = 0; i < buffer.length - 1; i++) {

		const a = buffer[i];
		const b = buffer[i + 1];

		if (t >= a.time && t <= b.time) {

			const alpha = (t - a.time) / (b.time - a.time);

			return { a, b, alpha };
		}
	}

	return null;
}

// ======================================================
// UPDATE (FLUIDO REAL)
// ======================================================

function update(_, object3D) {

	const t = performance.now() / 1000;

	const s = sampleAtTime(t);
	if (!s) return;

	const a0 = s.a.angles[0];
	const a1 = s.b.angles[0];

	const roll = a0.roll + (a1.roll - a0.roll) * s.alpha;
	const pitch = a0.pitch + (a1.pitch - a0.pitch) * s.alpha;

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;

	// yaw libre (NO bloqueado)
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

function animate() {
	requestAnimationFrame(animate);

	update(null, mesh);

	controls.update();
	renderer.render(scene, camera);
}

// ======================================================
// START
// ======================================================

init();
animate();
