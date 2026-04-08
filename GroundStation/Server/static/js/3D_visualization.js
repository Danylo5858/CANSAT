import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* =========================
   THREE GLOBALS
========================= */

let scene, camera, renderer, controls, mesh;

/* =========================
   BUFFER SYSTEM
========================= */

const buffer = [];
const MIN_BUFFER = 2; // siempre 1 packet de delay

let currentIndex = 0;
let segmentIndex = 0;
let t = 0;

/* =========================
   RESIZE
========================= */

function onResize() {
	const container = document.getElementById('viewer');

	camera.aspect = container.clientWidth / container.clientHeight;
	camera.updateProjectionMatrix();

	renderer.setSize(container.clientWidth, container.clientHeight);
}

/* =========================
   ACCEL -> ANGLES
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
   LERP
========================= */

function lerp(a, b, t) {
	return a + (b - a) * t;
}

/* =========================
   INPUT STREAM
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

	// limitar crecimiento
	if (buffer.length > 10) {
		buffer.shift();
	}

	// reset safe si se desincroniza todo
	if (currentIndex > buffer.length - 3) {
		currentIndex = Math.max(0, buffer.length - 3);
	}
}

/* =========================
   BUFFER CHECK
========================= */

function canPlay() {
	return buffer.length >= MIN_BUFFER;
}

function getPacket(i) {
	return buffer[i] || null;
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
	if (!canPlay()) return;

	const a = getPacket(currentIndex);
	const b = getPacket(currentIndex + 1);

	if (!a || !b) return;

	const segDuration = a.time / 3;
	t += dt;

	const u = Math.min(t / segDuration, 1);

	// ----------------------
	// dentro del packet
	// ----------------------
	if (segmentIndex < 3) {
		applyInterp(
			a.angles[segmentIndex],
			a.angles[segmentIndex + 1],
			u,
			object3D
		);
	}

	// ----------------------
	// transición entre packets
	// ----------------------
	else {
		applyInterp(
			a.angles[3],
			b.angles[0],
			u,
			object3D
		);
	}

	// avance controlado
	if (t >= segDuration) {
		t = 0;
		segmentIndex++;

		if (segmentIndex >= 3) {
			segmentIndex = 0;
			currentIndex++;
		}
	}
}

/* =========================
   THREE INIT
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

/* =========================
   START
========================= */

init();
animate();
