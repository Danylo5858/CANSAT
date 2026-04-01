import * as THREE from 'three';
console.log('3D');

let scene, camera, renderer, controls, can;

init();
animate();

function init() {
	scene = new THREE.Scene();
	camera = new THREE.PerspectiveCamera(
		75,
		window.innerWidth / window.innerHeight,
		0.1,
		1000
	);
	camera.position.z = 3;
	renderer = new THREE.WebGLRenderer({ antialias: true });
  	renderer.setSize(window.innerWidth, window.innerHeight);
  	document.body.appendChild(renderer.domElement);
  	controls = new THREE.OrbitControls(camera, renderer.domElement);
  	controls.enableDamping = true;
  	const geometry = new THREE.CylinderGeometry(0.5, 0.5, 1.2, 32);
  	const material = new THREE.MeshBasicMaterial({ color: 0x00aaff, wireframe: true });
  	can = new THREE.Mesh(geometry, material);
  	scene.add(can);
}

function animate() {
	requestAnimationFrame(animate);
  	controls.update();
  	renderer.render(scene, camera);
}
