const WINDOW_SIZE = 60 * 1000;
const TICKS = 6;

function createChart(element, title, yLabel, color, window_size, ticks) {
	return new ApexCharts(element, {
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
			text: title,
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
		grid: {
			borderColor: '#1f2a37'
		},
		series: [{
			data: [],
			color: color
		}],
		xaxis: {
			type: 'datetime',
			range: window_size,
			tickAmount: ticks,
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
				text: yLabel
			}
		},
		stroke: {
			curve: 'smooth',
			width: 2
		}
	});
}

const charts = [
	createChart(document.querySelector("#chart_a"), 'Altitud del CanSat en tiempo real', 'Altitud (m)', '#7c4dff', WINDOW_SIZE, TICKS),
	createChart(document.querySelector("#chart_t"), 'Temperatura del CanSat en tiempo real', 'Temperatura (Celsius)', '#00e5ff', WINDOW_SIZE, TICKS),
	createChart(document.querySelector("#chart_p"), 'Presión del CanSat en tiempo real', 'Presión (hPa)', '#00ff88', WINDOW_SIZE, TICKS)
]; // #ff3b3b

for (const chart of charts) {
	chart.render();
}


const socket = io('http://localhost:5000');
const loadingTime = 4 * 1000;
let firstData = true

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

	const time = new Date().getTime();
	const altitude = data['altitude'];
	const temperature = data['temperature'];
	const pressure = data['pressure'];

	charts[0].appendData([{
		data: [{
			x: time,
			y: altitude
		}]
	}]);
	charts[1].appendData([{
		data: [{
			x: time,
			y: temperature
		}]
	}]);
	charts[2].appendData([{
		data: [{
			x: time,
			y: pressure
		}]
	}]);
});
