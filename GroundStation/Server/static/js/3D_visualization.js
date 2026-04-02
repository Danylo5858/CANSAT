import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, can;
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

init();

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
  	const material = new THREE.MeshBasicMaterial({ color: 0x4FD1C5, wireframe: true });
  	can = new THREE.Mesh(geometry, material);
  	scene.add(can);
  	scene.add(new THREE.AxesHelper(2));
  	window.addEventListener('resize', onResize);
}

function onResize() {
	const container = document.getElementById('viewer');
	camera.aspect = container.clientWidth / container.clientHeight;
	camera.updateProjectionMatrix();
	renderer.setSize(container.clientWidth, container.clientHeight);
}

let queue = [];
let qCurrent = new THREE.Quaternion();
let qNext = new THREE.Quaternion();
let qInterpolated = new THREE.Quaternion();
let segmentStartTime = performance.now();
const segmentDuration = 250; // ms (4 por segundo)

function randomQuaternion() {
	const u1 = Math.random();
	const u2 = Math.random();
	const u3 = Math.random();
	const sqrt1MinusU1 = Math.sqrt(1 - u1);
	const sqrtU1 = Math.sqrt(u1);
  	return new THREE.Quaternion(
    	sqrt1MinusU1 * Math.sin(2 * Math.PI * u2),
    	sqrt1MinusU1 * Math.cos(2 * Math.PI * u2),
    	sqrtU1 * Math.sin(2 * Math.PI * u3),
    	sqrtU1 * Math.cos(2 * Math.PI * u3)
  	);
}

export async function onReceiveQuats(quats) {
	for (const q of quats) {
		queue.push(new THREE.Quaternion(q[0], q[1], q[2], q[3]));
		await sleep(250);
	}
}

qCurrent.copy(can.quaternion);

function animate(time) {
  	requestAnimationFrame(animate);

  	if (queue.length > 0 && qNext.lengthSq() === 0) {
    	qNext.copy(queue.shift());
    	qCurrent.copy(qNext);
    	segmentStartTime = time;
  	}

  	if (queue.length > 0 && time - segmentStartTime >= segmentDuration) {
    	qCurrent.copy(qNext);
    	qNext.copy(queue.shift());
    	segmentStartTime = time;

    	if (qCurrent.dot(qNext) < 0) {
      		qNext.set(-qNext.x, -qNext.y, -qNext.z, -qNext.w);
    	}
  	}

  	let alpha = (time - segmentStartTime) / segmentDuration;
  	alpha = Math.min(alpha, 1);

  	qInterpolated.copy(qCurrent).slerp(qNext, alpha);
  	can.quaternion.copy(qInterpolated);

  	controls.update();
  	renderer.render(scene, camera);
}

animate(performance.now());
