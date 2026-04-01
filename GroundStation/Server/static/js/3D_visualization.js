import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

let scene, camera, renderer, controls, can;

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
  	const geometry = new THREE.CylinderGeometry(0.5, 0.5, 1.2, 32);
  	const material = new THREE.MeshNormalMaterial();
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

function animate() {
	requestAnimationFrame(animate);
  	controls.update();
  	renderer.render(scene, camera);
}
