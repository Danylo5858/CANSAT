import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

/* =========================
   THREE
========================= */

let scene, camera, renderer, controls, mesh;

/* =========================
   BUFFER
========================= */

const buffer = [];
const MIN_BUFFER = 2;

/* =========================
   GLOBAL STATE (FLAT STREAM)
========================= */

let packetIndex = 0;   // qué packet
let pointIndex = 0;    // qué punto dentro del packet (0..3)
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
   INPUT
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

	if (buffer.length > 10) buffer.shift();

	if (packetIndex > buffer.length - 2) {
		packetIndex = Math.max(0, buffer.length - 2);
	}
}

/* =========================
   HELPERS
========================= */

function canPlay() {
	return buffer.length >= MIN_BUFFER;
}

function getPoint(pIdx, iIdx) {
	const p = buffer[pIdx];
	if (!p) return null;
	return p.angles[iIdx];
}

/* =========================
   APPLY
========================= */

function applyInterp(a0, a1, t, object3D) {
	if (!a0 || !a1) return;

	const roll = lerp(a0.roll, a1.roll, t);
	const pitch = lerp(a0.pitch, a1.pitch, t);

	object3D.rotation.x = pitch * Math.PI / 180;
	object3D.rotation.z = roll * Math.PI / 180;

	// yaw locked
	object3D.rotation.y = 0;
}

/* =========================
   UPDATE (CONTINUOUS STREAM)
========================= */

function update(dt, object3D) {
	if (!canPlay()) return;

	const currentPacket = buffer[packetIndex];
	const nextPacket = buffer[packetIndex + 1];

	if (!currentPacket || !nextPacket) return;

	const a0 = currentPacket.angles[pointIndex];
	let a1;

	// 👉 clave: continuidad entre packets
	if (pointIndex < 3) {
		a1 = currentPacket.angles[pointIndex + 1];
	} else {
		// 🔥 transición REAL entre packets
		a1 = nextPacket.angles[0];
	}

	const segDuration = currentPacket.time / 3;
	t += dt;

	const u = Math.min(t / segDuration, 1);

	applyInterp(a0, a1, u, object3D);

	if (t >= segDuration) {
		t = 0;
		pointIndex++;

		if (pointIndex >= 4) {
			pointIndex = 0;
			packetIndex++;
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
