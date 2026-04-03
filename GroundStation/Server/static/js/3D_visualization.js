import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, mesh;

let queue = [];

let qA = new THREE.Quaternion();
let qB = new THREE.Quaternion();
let qOut = new THREE.Quaternion();

let hasInit = false;

let alpha = 0;
const speed = 0.08; // suavidad (más bajo = más suave)

// =======================
// INIT
// =======================
init();
animate();

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
	controls.enableDamping = true;
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
}

export function onReceiveQuats(quats) {
	if (!quats || quats.length === 0) return;

	for (const q of quats) {
		const quat = new THREE.Quaternion(q[0], q[1], q[2], q[3]);
		quat.normalize(); // IMPORTANTÍSIMO

		queue.push(quat);
	}
}

function animate() {
	requestAnimationFrame(animate);

	if (!hasInit) {
		if (queue.length === 0) {
			renderer.render(scene, camera);
			return;
		}

		qA.copy(queue.shift());
		qB.copy(qA);
		hasInit = true;
	}

	// si hay nuevos datos, avanzamos target
	if (queue.length > 0) {
		const next = queue[0];

		// evitar flip (shortest path)
		if (qB.dot(next) < 0) {
			next.set(-next.x, -next.y, -next.z, -next.w);
		}

		qB.copy(next);
		queue.shift();
	}

	// interpolación suave continua
	qA.slerp(qB, speed);

	mesh.quaternion.copy(qA);

	controls.update();
	renderer.render(scene, camera);
}
