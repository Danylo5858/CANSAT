import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* =========================
   THREE
========================= */

let scene, camera, renderer, controls, mesh;

/* =========================
   FLAT BUFFER (CLAVE)
========================= */

const stream = [];
const MIN_BUFFER = 5;

/* cursor continuo */
let index = 0;
let t = 0;

/* velocidad constante (ajustable) */
const SPEED = 1; // puntos por segundo

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
   LERP
========================= */

function lerp(a, b, t) {
	return a + (b - a) * t;
}

/* =========================
   INPUT → FLATTEN STREAM
========================= */

export function onReceiveAccel(packet) {
	const angles = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	// 🔥 flatten inmediato
	for (const a of angles) {
		stream.push(a);
	}

	if (stream.length > 200) {
		stream.splice(0, stream.length - 100);
	}

	if (index > stream.length - 2) {
		index = Math.max(0, stream.length - 2);
	}
}

/* =========================
   HELPERS
========================= */

function canPlay() {
	return stream.length >= MIN_BUFFER;
}

/* =========================
   APPLY ROTATION
========================= */

function apply(a, b, u, object3D) {
	if (!a || !b) return;

	const roll = lerp(a.roll, b.roll, u);
	const pitch = lerp(a.pitch, b.pitch, u);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;

	// 🔒 yaw lock
	object3D.rotation.y = 0;
}

/* =========================
   UPDATE (SMOOTH CONTINUOUS TIME)
========================= */

function update(dt, object3D) {
	if (!canPlay()) return;

	t += dt * SPEED;

	while (t >= 1) {
		t -= 1;
		index++;
	}

	const a = stream[index];
	const b = stream[index + 1];

	apply(a, b, t, object3D);
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
