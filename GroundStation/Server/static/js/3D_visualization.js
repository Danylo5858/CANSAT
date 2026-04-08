import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

/* =========================
   UTILS
========================= */

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

const samples = [];

let index = 0;
let t = 0;

const INTERP_SPEED = 12; // cuánto tarda en cruzar entre samples

/* =========================
   INPUT
========================= */

export function onReceiveAccel(packet) {
	const converted = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});

	for (const s of converted) {
		samples.push(s);
	}

	// limit buffer
	if (samples.length > 200) {
		const remove = samples.length - 200;
		samples.splice(0, remove);
		index = Math.max(0, index - remove);
	}
}

/* =========================
   UPDATE (ROBUST STREAM)
========================= */

function update(dt, object3D) {
	if (samples.length < 2) return;

	const a = samples[index];
	const b = samples[index + 1];

	if (!a || !b) return;

	t += dt * INTERP_SPEED;

	if (t > 1) {
		t = 0;
		index++;

		// si no hay más data, quedarnos quietos en último estado
		if (index >= samples.length - 1) {
			index = samples.length - 2;
		}
	}

	const roll = lerp(a.roll, b.roll, t);
	const pitch = lerp(a.pitch, b.pitch, t);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;
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

function onResize() {
	const container = document.getElementById('viewer');

	camera.aspect = container.clientWidth / container.clientHeight;
	camera.updateProjectionMatrix();

	renderer.setSize(container.clientWidth, container.clientHeight);
	controls.update();
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
