import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* =========================
   THREE
========================= */

let scene, camera, renderer, controls, mesh;

/* =========================
   STREAM
========================= */

const stream = [];
const MIN_BUFFER = 2;

let index = 0;
let t = 0;

const SPEED = 1;

/* =========================
   QUATERNIONS
========================= */

const qA = new THREE.Quaternion();
const qB = new THREE.Quaternion();
const qOut = new THREE.Quaternion();

const eulerA = new THREE.Euler();
const eulerB = new THREE.Euler();

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

	return { roll, pitch };
}

/* =========================
   INPUT STREAM
========================= */

export function onReceiveAccel(packet) {
	const angles = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	for (const a of angles) {
		stream.push(a);
	}

	// 🔥 recorte ligero (sin saltos grandes)
	if (stream.length > 80) {
		stream.shift();
	}

	// 🔥 mantener índice siempre válido
	if (index > stream.length - 2) {
		index = Math.max(0, stream.length - 2);
		t = 1;
	}
}

/* =========================
   UPDATE
========================= */

function update(dt, object3D) {
	if (stream.length < MIN_BUFFER) return;

	t += dt * SPEED;

	const maxIndex = stream.length - 2;

	// 🔥 CLAVE: siempre seguir el "presente"
	if (index < maxIndex - 1) {
		index = maxIndex - 1;
		t = 1;
	}

	if (t >= 1) {
		t = 0;
		index = Math.max(0, stream.length - 2);
	}

	const a = stream[index];
	const b = stream[index + 1];

	if (!a || !b) return;

	// Euler -> Quaternion
	eulerA.set(a.pitch, 0, a.roll, 'XYZ');
	eulerB.set(b.pitch, 0, b.roll, 'XYZ');

	qA.setFromEuler(eulerA);
	qB.setFromEuler(eulerB);

	// Smooth interpolation
	qOut.copy(qA).slerp(qB, t);

	object3D.quaternion.copy(qOut);
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

/* =========================
   START
========================= */

init();
animate();
