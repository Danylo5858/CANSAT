import { onReceiveAccel } from './3D_visualization.js';
import { backupRequest } from './backup.js';
import { updateMap } from './map.js';

const WINDOW_SIZE = 60 * 1000;
const TICKS = 6;

function getDynamicTimeFormat(min, max) {
  	const diff = max - min;

  	const oneMinute = 60 * 1000;
  	const oneHour = 60 * oneMinute;
  	const oneDay = 24 * oneHour;
  	const oneMonth = 30 * oneDay;

  	if (diff <= oneHour) {
    	return { hour: '2-digit', minute: '2-digit', second: '2-digit' };
  	}
  	else if (diff <= oneDay) {
    	return { hour: '2-digit', minute: '2-digit' };
  	}
  	else if (diff <= oneMonth) {
    	return { day: '2-digit', month: 'short' };
  	}
  	else {
    	return { month: 'short', year: 'numeric' };
  	}
}

function createChart(element, title, xaxis, yaxis, color, type='line', curve='smooth', animations=true, tooltip=false) {
	return new ApexCharts(element, {
		chart: {
			type: type,
			animations: {
				enabled: animations,
				easing: 'linear',
				dynamicAnimation: {
					speed: 700
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
			enabled: tooltip,
			theme: 'dark',
			//intersect: false,
			//shared: true
		},
		grid: {
			borderColor: '#1f2a37'
		},
		series: [{
			data: [],
			color: color
		}],
		xaxis: xaxis,
		yaxis: yaxis,
		stroke: {
			curve: curve,
			width: 2
		}
	});
}

function createBackupChart(element, title, yaxis, color, dataset, type='line', curve='smooth') {
	const timestamps = dataset.map(d =>
    	new Date(`${d.date}T${d.time.replace(/-/g, ":")}`).getTime()
  	);

  	let currentMin = Math.min(...timestamps);
  	let currentMax = Math.max(...timestamps);

	return new ApexCharts(element, {
		chart: {
			type: type,
			toolbar: {
				show: false
			},
			zoom: {
				type: 'x',
				enabled: false,
				autoScaleYaxis: true
			}
		},
		title: {
			text: title,
			align: 'center'
		},
		tooltip: {
			enabled: true,
			theme: 'dark',
			//intersect: false,
			//shared: true
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
	      	min: currentMin,
	      	max: currentMax,
	      	labels: {
	        	datetimeUTC: false,
	        	formatter: function (value, timestamp) {
	          		const format = getDynamicTimeFormat(currentMin, currentMax);
	          		return new Date(timestamp).toLocaleString('es-ES', format);
	        	}
	      	}
	    },
		yaxis: yaxis,
		stroke: {
			curve: curve,
			width: 2
		}
	});
}

function generateTimeXaxis(range, ticks) {
	return {
		type: 'datetime',
		range: range,
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
	};
}

const charts = [
	createChart(
		document.querySelector('#chart_a'),
		'Altitud del CanSat en tiempo real',
		generateTimeXaxis(WINDOW_SIZE, TICKS),
		{
			title: {
				text: 'Altitud (m)'
			}
		},
		'#7c4dff'
	),
	createChart(
		document.querySelector('#chart_t'),
		'Temperatura del CanSat en tiempo real',
		generateTimeXaxis(WINDOW_SIZE, TICKS),
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff'
	),
	createChart(document.querySelector('#chart_p'),
		'Presión del CanSat en tiempo real',
		generateTimeXaxis(WINDOW_SIZE, TICKS),
		{
			title: {
				text: 'Presión (hPa)'
			}
		},
		'#00ff88'
	),
	createChart(document.querySelector('#chart_pa'),
		'Altitud - Presión',
		{
			title: {
				text: 'Presión (hPa)'
			},
			labels: {
				formatter: (val) => `${Math.round(val)} hPa`
			}
		},
		{
			type: 'numeric',
			title: {
				text: 'Altitud (m)'
			},
			labels: {
				formatter: (val) => `${Math.round(val)} m`
			}
		},
		'#ff3b3b',
		'line',
		'straight'
	),
	createChart(
		document.querySelector('#chart_aq'),
		'Calidad del aire desde estación de tierra',
		generateTimeXaxis(WINDOW_SIZE, TICKS),
		{
			title: {
				text: 'Calidad del aire'
			}
		},
		'#7c4dff'
	),
	createChart(
		document.querySelector('#chart_t_g'),
		'Temperatura desde estación de tierra',
		generateTimeXaxis(WINDOW_SIZE, TICKS),
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff'
	),
	createChart(document.querySelector('#chart_h'),
		'Humedad desde estación de tierra',
		generateTimeXaxis(WINDOW_SIZE, TICKS),
		{
			title: {
				text: 'Humedad'
			}
		},
		'#00ff88'
	)
];

for (const chart of charts) {
	chart.render();
}


export const socket = io('http://localhost:5000', {
	reconnection: true,
	reconnectionAttempts: Infinity,
	reconnectionDelay: 1000,
	reconnectionDelayMax: 5000,
	timeout: 20000,
});
const loadingTime = 7 * 1000;
const backupLoadingTime = 3 * 1000;
let firstData = true

setTimeout(() => {
	document.querySelector('.loader-container').classList.add('hide');
}, loadingTime); // ESTE TIMEOUT ESTÁ DUPLICADO

socket.on('connect', () => {
	console.log('Conectado al servidor');
});

socket.on('disconnect', (reason) => {
  console.log('Desconectado:', reason);
});

socket.on('reconnect_attempt', (attempt) => {
  console.log('Intento de reconexión:', attempt);
});

socket.on('reconnect', () => {
  console.log('Reconectado');
});

socket.on('BMP390_data', (data) => {
	//console.log('Datos recibidos (BMP390_data):', data);

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
	charts[3].appendData([{
		data: [{
			x: pressure,
			y: altitude
		}]
	}]);
});

socket.on('ground_data', (data) => {
	//console.log('Datos recibidos (ground_data):', data);

	const time = new Date().getTime();
	const air_quality = data['air_quality'];
	const temperature = data['temperature'];
	const humidity = data['humidity'];

	charts[4].appendData([{
		data: [{
			x: time,
			y: air_quality
		}]
	}]);
	charts[5].appendData([{
		data: [{
			x: time,
			y: temperature
		}]
	}]);
	charts[6].appendData([{
		data: [{
			x: time,
			y: humidity
		}]
	}]);
});

socket.on('MPU6050_data', (data) => {
	//console.log('Datos recibidos (MPU6050_data)');
	onReceiveAccel(data);
});

function showBackupLoader() {
    document.getElementById('backup-loader').classList.remove('hide');
}

function hideBackupLoader() {
    document.getElementById('backup-loader').classList.add('hide');
}

socket.on('backup_response', (res) => {
	if (res['success'] === true) {
		console.log('Copia de seguridad del CanSat recibida correctamente');
		console.log(res['data'])
		const dataset = res['data']['BMP390'];
		const charts_b = [
			createBackupChart(
				document.querySelector('#chart_a_b'),
				'Altitud del CanSat (Copia de seguridad)',
				{
					title: {
						text: 'Altitud (m)'
					}
				},
				'#7c4dff',
				dataset
			),
			createBackupChart(
				document.querySelector('#chart_t_b'),
				'Temperatura del CanSat (Copia de seguridad)',
				{
					title: {
						text: 'Temperatura (Celsius)'
					}
				},
				'#00e5ff',
				dataset
			),
			createBackupChart(document.querySelector('#chart_p_b'),
				'Presión del CanSat (Copia de seguridad)',
				{
					title: {
						text: 'Presión (hPa)'
					}
				},
				'#00ff88',
				dataset
			),
			createChart(document.querySelector('#chart_pa_b'),
				'Altitud - Presión (Copia de seguridad)',
				{
					title: {
						text: 'Presión (hPa)'
					},
					labels: {
						formatter: (val) => `${Math.round(val)} hPa`
					}
				},
				{
					type: 'numeric',
					title: {
						text: 'Altitud (m)'
					},
					labels: {
						formatter: (val) => `${Math.round(val)} m`
					}
				},
				'#ff3b3b',
				'line',
				'straight',
				false,
				true
			)
		];
		const altitudeData = dataset.map(d => {
			const timestamp = new Date(`${d.date}T${d.time.replace(/-/g, ":")}`).getTime();
			return {
				x: timestamp,
				y: d.altitude
			};
		});
		const temperatureData = dataset.map(d => {
			const timestamp = new Date(`${d.date}T${d.time.replace(/-/g, ":")}`).getTime();
			return {
				x: timestamp,
				y: d.temperature
			};
		});
		const pressureData = dataset.map(d => {
			const timestamp = new Date(`${d.date}T${d.time.replace(/-/g, ":")}`).getTime();
			return {
				x: timestamp,
				y: d.pressure
			};
		});
		const pressureAltitudeData = dataset.map(d => {
			return {
				x: d.pressure,
				y: d.altitude
			};
		});
		for (const chart of charts_b) {
			chart.render();
		}
		charts_b[0].updateSeries([{ name: 'Altitud (m)', data: altitudeData, color: '#7c4dff' }]);
		charts_b[1].updateSeries([{ name: 'Temperatura (Celsius)', data: temperatureData, color: '#00e5ff' }]);
		charts_b[2].updateSeries([{ name: 'Presión (hPa)', data: pressureData, color: '#00ff88' }]);
		charts_b[3].updateSeries([{ name: 'Altitud (m)', data: pressureAltitudeData, color: '#ff3b3b' }]);
		setTimeout(() => {
			hideBackupLoader();
			document.querySelectorAll('.main-content').forEach(el => {
				el.classList.add('hide');
			});
			document.querySelector('#backup-charts').classList.remove('hide');
		}, backupLoadingTime);
	}
	else {
		console.log('Fallo recibiendo la copia de seguridad del CanSat');
	}
});

socket.on('GPS_data', (data) => {
	if (data['latitude'] === 0 && data['longitude'] === 0) {
		return;
	}
	else {
		//console.log('Datos recibidos (GPS_data)');
		updateMap(data['latitude'], data['longitude']);
	}
});


function handleSidebarAction(button) {
	document.querySelectorAll('.sidebar-btn').forEach(btn => {
		btn.classList.remove('active');
	});
	button.classList.add('active');
	document.querySelectorAll('.main-content').forEach(el => {
		el.classList.add('hide');
	});
	if (button.getAttribute('id') === 'ground-charts-btn') {
		document.querySelector('#ground-charts').classList.remove('hide');
	}
	else if (button.getAttribute('id') === 'cansat-charts-btn') {
		document.querySelector('#cansat-charts').classList.remove('hide');
	}
	else if (button.getAttribute('id') === 'backup-btn') {
		document.querySelector('#backup-config').classList.remove('hide');
	}
	else if (button.getAttribute('id') === 'map-btn') {
		document.querySelector('#map-view').classList.remove('hide');
	}
}
window.handleSidebarAction = handleSidebarAction;

function generateInterval() {
    const startDate = document.getElementById('start-date').value;
    const startTime = document.getElementById('start-time').value;
    const endDate = document.getElementById('end-date').value;
    const endTime = document.getElementById('end-time').value;
    if (!startDate || !startTime || !endDate || !endTime) {
    	console.log('Faltan campos por rellenar para generar un análisis en intervalo');
    }
    else {
    	showBackupLoader();
    	const formattedStartTime = startTime.replace(':', '-') + '-00';
    	const formattedEndTime = endTime.replace(':', '-') + '-00';
    	const start = `${startDate} ${formattedStartTime}`;
    	const end = `${endDate} ${formattedEndTime}`;
		backupRequest(true, false, false, start, end);
    }
}
window.generateInterval = generateInterval

function generateFull() {
    showBackupLoader();
	backupRequest(true, false, false);
}
window.generateFull = generateFull
