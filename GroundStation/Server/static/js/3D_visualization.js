import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

/* =========================
   BUFFER CONTROLADO
========================= */

const buffer = [];
const MAX_BUFFER = 3; // 🔥 CLAVE: buffer ultra corto (evita lag)

let currentIndex = 0;
let segmentIndex = 0;
let t = 0;

/* =========================
   ACCEL
========================= */

function accelToAngles(ax, ay, az) {
	const roll = Math.atan2(ay, az);
	const pitch = Math.atan2(-ax, Math.sqrt(ay * ay + az * az));

	return {
		roll: roll * 180 / Math.PI,
		pitch: pitch * 180 / Math.PI
	};
}

/* =========================
   INPUT
========================= */

export function onReceiveAccel(packet) {
	const angles = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	buffer.push({
		angles,
		time: packet.time
	});

	// 🔥 mantener buffer FIJO (no crecimiento)
	if (buffer.length > MAX_BUFFER) {
		buffer.shift();

		// 🔥 IMPORTANTÍSIMO: evitar que el índice se quede atrás
		if (currentIndex > 0) currentIndex--;
	}
}

/* =========================
   LERP
========================= */

function lerp(a, b, t) {
	return a + (b - a) * t;
}

/* =========================
   APPLY (QUAT + YAW LOCK)
========================= */

const qA = new THREE.Quaternion();
const qB = new THREE.Quaternion();
const qOut = new THREE.Quaternion();

const eA = new THREE.Euler();
const eB = new THREE.Euler();

function applyInterp(a0, a1, u, object3D) {
	if (!a0 || !a1) return;

	eA.set(a0.pitch, 0, a0.roll, 'XYZ');
	eB.set(a1.pitch, 0, a1.roll, 'XYZ');

	qA.setFromEuler(eA);
	qB.setFromEuler(eB);

	qOut.copy(qA).slerp(qB, u);

	object3D.quaternion.copy(qOut);
	object3D.rotation.y = 0;
}

/* =========================
   UPDATE (FIXED SEGMENT FLOW)
========================= */

function update(dt, object3D) {
	if (buffer.length < 2) return;

	const a = buffer[currentIndex];
	const b = buffer[currentIndex + 1];

	if (!a || !b) return;

	const segDuration = 0.016; // 🔥 FIX: constante (~60fps stable)
	t += dt;

	const u = Math.min(t / segDuration, 1);

	applyInterp(
		a.angles[segmentIndex],
		a.angles[segmentIndex + 1],
		u,
		object3D
	);

	if (t >= segDuration) {
		t = 0;
		segmentIndex++;

		// 🔥 salto de packet SOLO cuando termina ciclo completo
		if (segmentIndex >= 3) {
			segmentIndex = 0;
			currentIndex++;

			// 🔥 anti-lag catch-up (clave)
			if (currentIndex > buffer.length - 2) {
				currentIndex = buffer.length - 2;
			}
		}
	}
}

/* =========================
   THREE
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
