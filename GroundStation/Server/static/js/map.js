const baseLat = 28.0469041;
const baseLon = -16.6598639;
let lineCoords = [];

const map = new google.maps.Map(document.getElementById('map-canvas'), {
	center: { lat: baseLat, lng: baseLon },
	zoom: 18,
	mapTypeId: 'satellite',
	fullscreenControl: false
});
const mark = new google.maps.Marker({
	position: { lat: baseLat, lng: baseLon },
	map
});

const line = new google.maps.Polyline({
	path: lineCoords,
	geodesic: true,
	strokeColor: "#2E10FF"
});
line.setMap(map);

export function updateMap(lat, lon) {
	// map.setCenter({ lat: lat, lng: lon });
	mark.setPosition({ lat: lat, lng: lon });
	lineCoords.push(new google.maps.LatLng(lat, lon));
	line.setPath(lineCoords);
}

function getRandomNearBase() {
	const offset = 0.0002; // ~20 metros aprox

	const lat = baseLat + (Math.random() - 0.5) * offset;
	const lng = baseLon + (Math.random() - 0.5) * offset;

	return { lat, lng };
}

setInterval(() => {
	const { lat, lng } = getRandomNearBase();
	updateMap(lat, lng);
}, 1000);
