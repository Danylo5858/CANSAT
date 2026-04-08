import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

/* =========================
   STREAM (with timestamps)
========================= */

const stream = [];
const MAX_BUFFER = 300;

let startTime = null;

/* =========================
   QUATERNIONS
========================= */

const qA = new THREE.Quaternion();
const qB = new THREE.Quaternion();
const qOut = new THREE.Quaternion();

const eA = new THREE.Euler();
const eB = new THREE.Euler();

/* =========================
   ACCEL
========================= */

function accelToAngles(ax, ay, az) {
	const roll = Math.atan2(ay, az);
	const pitch = Math.atan2(-ax, Math.sqrt(ay * ay + az * az));

	return {
		roll,
		pitch
	};
}

/* =========================
   INPUT
========================= */

export function onReceiveAccel(packet) {
	const now = performance.now();

	const angles = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	for (const a of angles) {
		stream.push({
			...a,
			t: now
		});
	}

	if (stream.length > MAX_BUFFER) {
		stream.splice(0, stream.length - 200);
	}

	if (!startTime) startTime = now;
}

/* =========================
   FIND NEIGHBORS BY TIME
========================= */

function getSurroundingPoints(t) {
	for (let i = 0; i < stream.length - 1; i++) {
		const a = stream[i];
		const b = stream[i + 1];

		if (a.t <= t && b.t >= t) {
			const u = (t - a.t) / (b.t - a.t);
			return { a, b, u };
		}
	}

	return null;
}

/* =========================
   UPDATE (NO DRIFT)
========================= */

function update(object3D) {
	if (stream.length < 2) return;

	const now = performance.now();

	const sample = getSurroundingPoints(now);
	if (!sample) return;

	const { a, b, u } = sample;

	eA.set(a.pitch, 0, a.roll, 'XYZ');
	eB.set(b.pitch, 0, b.roll, 'XYZ');

	qA.setFromEuler(eA);
	qB.setFromEuler(eB);

	qOut.copy(qA).slerp(qB, u);

	object3D.quaternion.copy(qOut);
	object3D.rotation.y = 0; // lock yaw
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
	renderer.setSize(container.clientWidth, container.clientHeight);
	container.appendChild(renderer.domElement);

	controls = new OrbitControls(camera, renderer.domElement);

	const geometry = new THREE.CylinderGeometry(0.5, 0.5, 1.5, 16);
	const material = new THREE.MeshBasicMaterial({ wireframe: true });

	mesh = new THREE.Mesh(geometry, material);
	scene.add(mesh);

	scene.add(new THREE.AxesHelper(2));

	window.addEventListener('resize', onResize);
}

function onResize() {
	const container = document.getElementById('viewer');

	camera.aspect = container.clientWidth / container.clientHeight;
	camera.updateProjectionMatrix();

	renderer.setSize(container.clientWidth, container.clientHeight);
}

/* =========================
   LOOP
========================= */

function animate() {
	requestAnimationFrame(animate);

	update(mesh);

	controls.update();
	renderer.render(scene, camera);
}

init();
animate();
