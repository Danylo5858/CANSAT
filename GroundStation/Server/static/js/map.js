let lineCoords = [];

const map = new google.maps.Map(document.getElementById('map-canvas'), {
	center: { 28.0469041, -16.6598639 },
	zoom: 18,
	mapTypeId: 'satellite'
});
const mark = new google.maps.Marker({
	position: { 28.0469041, -16.6598639 },
	map
});

export function updateMap(lat, lon) {
	map.setCenter({ lat, lon });
	mark.setPosition({ lat, lon });
	lineCoords.push(new google.maps.LatLng(lat, lon));
	const line = new google.maps.Polyline({
		path: lineCoords,
		geodesic: true,
		strokeColor: "#2E10FF"
	});
	line.setMap(map);
}
