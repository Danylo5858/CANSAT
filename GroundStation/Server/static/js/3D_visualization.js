import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

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
   STREAM STATE
========================= */

const queue = [];
const MAX_QUEUE = 2;

let currentPacket = null;
let nextPacket = null;

let segmentIndex = 0;
let t = 0;

/* =========================
   INPUT
========================= */

export function onReceiveAccel(packet) {
	const angles = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	queue.push({
		angles,
		time: packet.time
	});

	// 🔥 evitar delay acumulado
	if (queue.length > MAX_QUEUE) {
		queue.splice(0, queue.length - 1);
	}
}

/* =========================
   PACKET LOADER
========================= */

function loadNext() {
	if (!currentPacket && queue.length > 0) {
		currentPacket = queue.shift();
	}

	nextPacket = queue.length > 0 ? queue[0] : null;

	t = 0;
	segmentIndex = 0;
}

/* =========================
   INTERPOLATION
========================= */

function applyInterp(a0, a1, t, object3D) {
	if (!a0 || !a1) return;

	const roll = lerp(a0.roll, a1.roll, t);
	const pitch = lerp(a0.pitch, a1.pitch, t);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;
}

/* =========================
   UPDATE LOOP
========================= */

function update(dt, object3D) {
	if (!currentPacket) {
		if (queue.length > 0) loadNext();
		return;
	}

	const a = currentPacket;
	const b = nextPacket;

	const segDuration = a.time / 3; // 4 puntos = 3 segmentos
	t += dt;

	const u = Math.min(t / segDuration, 1);

	// ----------------------
	// 1. dentro del packet
	// ----------------------
	if (segmentIndex < 3) {
		const a0 = a.angles[segmentIndex];
		const a1 = a.angles[segmentIndex + 1];

		applyInterp(a0, a1, u, object3D);
	}

	// ----------------------
	// 2. transición entre packets
	// ----------------------
	else if (b) {
		const a3 = a.angles[3];
		const b0 = b.angles[0];

		applyInterp(a3, b0, u, object3D);
	}

	// avanzar tiempo
	if (t >= segDuration) {
		t = 0;
		segmentIndex++;

		// fin del packet
		if (segmentIndex >= 3) {
			currentPacket = nextPacket;
			queue.shift(); // consumimos siguiente
			loadNext();
		}
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
   ANIMATION LOOP
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
