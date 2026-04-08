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

const queue = [];
const state = {
	points: [],
	duration: 0,
	segment: 0,
	segmentTime: 0,
	segmentDuration: 0,
	playing: false
};

export function onReceiveAccel(packet) {
	const angles = packet.accel.map(p => {
		const { roll, pitch } = accelToAngles(p[0], p[1], p[2]);
		return { roll, pitch };
	});
	queue.push({
		angles,
		time: packet.time
	});
}

function loadNext() {
	if (queue.length === 0) return;
	const packet = queue.shift();
	state.points = packet.angles;
	state.duration = packet.time;
	state.segment = 0;
	state.segmentTime = 0;
	state.segmentDuration = state.duration / 3;
	state.playing = true;
}

function update(dt, object3D) {
	if (!state.playing) {
		if (queue.length > 0) loadNext();
		return;
	}
	state.segmentTime += dt;
	const tRaw = state.segmentTime / state.segmentDuration;
	const t = Math.min(tRaw, 1);
	const i = state.segment;
	const a0 = state.points[i];
	const a1 = state.points[i + 1];
	if (!a0 || !a1) return;
	const roll = lerp(a0.roll, a1.roll, t);
	const pitch = lerp(a0.pitch, a1.pitch, t);
	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;
	if (state.segmentTime >= state.segmentDuration) {
		state.segment++;
		state.segmentTime = 0;
		if (state.segment >= state.points.length - 1) {
			state.playing = false;
		}
	}
}

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
