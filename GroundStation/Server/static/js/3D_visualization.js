import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, can;
let frames = [];
let index = 0;
let currentQuat = new THREE.Quaternion();

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

function decodeMPU6050(bin) {
	const buffer = new Uint8Array(bin).slice().buffer;
	const view = new DataView(buffer);
	const quats = [];
	const stride = 8;
	const max = view.byteLength - (view.byteLength % stride);
	for (let i = 0; i < max; i += stride) {
		const w = view.getInt16(i, true) / 32767;
		const x = view.getInt16(i+2, true) / 32767;
		const y = view.getInt16(i+4, true) / 32767;
		const z = view.getInt16(i+6, true) / 32767;
		quats.push(new THREE.Quaternion(x*100, y*100, z*100, w*100));
	}
	return quats;
}

export function onReceivePacket(bin) {
	frames = decodeMPU6050(bin);
	console.log(frames);
	index = 0;
}

function animate() {
	requestAnimationFrame(animate);
	if (frames.length > 0) {
		const target = frames[index];
		currentQuat.slerp(target, 0.2);
		can.quaternion.copy(currentQuat);
		index++;
		if (index >= frames.length) index = 0;
	}
  	controls.update();
  	renderer.render(scene, camera);
}

const q = new THREE.Quaternion(0, 0, 0.7071068, 0.7071068);
can.quaternion.copy(q);
