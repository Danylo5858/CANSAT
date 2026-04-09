import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* =========================
   THREE
========================= */

let scene, camera, renderer, controls, mesh;

/* =========================
   STREAM TARGET
========================= */

const targetQuat = new THREE.Quaternion();
const currentQuat = new THREE.Quaternion();

const euler = new THREE.Euler();

/* smoothing factor (clave del sistema) */
const SMOOTHING = 0.12;

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
   INPUT (TARGET ONLY)
========================= */

export function onReceiveAccel(packet) {
	// solo nos quedamos con el ÚLTIMO estado
	const last = packet.accel[packet.accel.length - 1];

	const { roll, pitch } = accelToAngles(last[0], last[1], last[2]);

	euler.set(pitch, 0, roll, 'XYZ');
	targetQuat.setFromEuler(euler);
}

/* =========================
   UPDATE (FULL SMOOTH)
========================= */

function update(object3D) {
	// 🔥 suavizado continuo SIEMPRE
	currentQuat.slerp(targetQuat, SMOOTHING);

	object3D.quaternion.copy(currentQuat);
}

/* =========================
   INIT
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

function animate() {
	requestAnimationFrame(animate);

	update(mesh);

	controls.update();
	renderer.render(scene, camera);
}

/* =========================
   START
========================= */

init();
animate();
