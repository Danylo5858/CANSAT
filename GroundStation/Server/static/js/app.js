const WINDOW_SIZE = 60 * 1000;
const MAX_POINTS = 70;

const buffer = new Array(MAX_POINTS);
let index = 0;
let filled = false;

const options = {
	chart: {
		type: 'line',
		animations: {
			enabled: true,
			easing: 'linear',
			dynamicAnimation: {
				speed: 700 // SINCRONIZAR CON LOS DATOS
			},
			animateGradually: {
				enabled: false
			}
		},
		toolbar: {
			show: false
		},
		zoom: {
			enabled: false
		}
	},
	title: {
		text: 'Altitud del CanSat en tiempo real',
		align: 'center'
	},
	tooltip: {
		enabled: false,
		theme: 'dark',
		followCursor: true,
		intersect: false,
		shared: true,
		fixed: {
			enabled: true,
			position: 'topRight',
			offsetX: 0,
			offsetY: 0
		}
	},
	series: [{
		name: 'Altitud',
		data: []
	}],
	xaxis: {
		type: 'datetime',
		range: WINDOW_SIZE,
		tickAmount: 6,
		labels: {
			datetimeUTC: false,
			formatter: function (value, timestamp) {
				const d = new Date(timestamp);
				return d.toLocaleTimeString([], {
					hour: '2-digit',
					minute: '2-digit',
					second: '2-digit'
				});
			}
		}
	},
	yaxis: {
		title: {
			text: 'Altitud (m)'
		}
	},
	stroke: {
		curve: 'smooth',
		width: 2
	}
};

function addPoint(point) {
	buffer[index] = point;
	index = (index + 1) % MAX_POINTS;
	if (index === 0) filled = true;
}

function getNewPoint() {
	return {
		x: new Date().getTime(),
		y: Math.floor(Math.random() * 1000) + 100
	};
}

const chart = new ApexCharts(document.querySelector("#chart"), options);
chart.render();

setInterval(() => {
	const point = getNewPoint();
	addPoint(point);
	//chart.appendData([{
	//	data: [point]
	//}]);
	chart.updateSeries([{
		data: buffer
	}]);
}, 1000);


const socket = io('http://localhost:5000');
let firstData = true
const loadingTime = 4 * 1000;

setTimeout(() => {
	document.querySelector('.loader-container').classList.add('hide');
}, loadingTime);

socket.on('connect', () => {
	console.log('Conectado al servidor');
});

socket.on('BMP390_data', (data) => {
	console.log('Datos recibidos:', data);
	if (firstData) {
		setTimeout(() => {
			document.querySelector('.loader-container').classList.add('hide');
		}, loadingTime);
		firstData = false;
	}
});
