import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

/* =========================
   UTIL
========================= */

function onResize() {
	const container = document.getElementById('viewer');

	camera.aspect = container.clientWidth / container.clientHeight;
	camera.updateProjectionMatrix();

	renderer.setSize(container.clientWidth, container.clientHeight);
	controls.update();
}

function accelToAngles(ax, ay, az) {
	const roll = Math.atan2(ay, az);
	const pitch = Math.atan2(-ax, Math.sqrt(ay * ay + az * az));
	return {
		roll: roll * 180 / Math.PI,
		pitch: pitch * 180 / Math.PI
	};
}

function lerp(a, b, t) {
	return a + (b - a) * t;
}

/* =========================
   STREAM BUFFER
========================= */

// buffer continuo de samples (NO packets)
const samples = [];

// cursor flotante dentro del stream
let cursor = 0;

// velocidad del “reproductor” del stream
const SPEED = 25; // samples por segundo (ajustable)

/* =========================
   INPUT (STREAM FLATTEN)
========================= */

export function onReceiveAccel(packet) {
	const converted = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	// 🔥 append directo al stream
	for (const s of converted) {
		samples.push(s);
	}

	// 🔥 control de memoria + evita delay acumulado
	const MAX = 200;
	if (samples.length > MAX) {
		const remove = samples.length - MAX;
		samples.splice(0, remove);

		// ajustar cursor para no romper continuidad
		cursor = Math.max(0, cursor - remove);
	}
}

/* =========================
   UPDATE (CONTINUOUS INTERPOLATION)
========================= */

function update(dt, object3D) {
	if (samples.length < 2) return;

	// avanzar en el stream continuo
	cursor += dt * SPEED;

	const i = Math.floor(cursor);
	const t = cursor - i;

	const a = samples[i];
	const b = samples[i + 1];

	if (!a || !b) return;

	const roll = lerp(a.roll, b.roll, t);
	const pitch = lerp(a.pitch, b.pitch, t);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;

	// 🔥 limpieza progresiva sin saltos
	if (i > 50) {
		samples.splice(0, i);
		cursor -= i;
	}
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
