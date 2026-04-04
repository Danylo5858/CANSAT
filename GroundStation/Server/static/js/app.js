import { onReceiveQuats } from './3D_visualization.js';
import { backupRequest } from './backup.js';

const WINDOW_SIZE = 60 * 1000;
const TICKS = 6;

function createChart(element, title, xaxis, yaxis, color, animations=true, type='line', curve='smooth') {
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
		xaxis: xaxis,
		yaxis: yaxis,
		stroke: {
			curve: curve,
			width: 2
		}
	});
}

function generateTimeXaxis(range, ticks, timeConfig) {
	return {
		type: 'datetime',
		range: range,
		tickAmount: ticks,
		labels: {
			datetimeUTC: false,
			formatter: function (value, timestamp) {
				const d = new Date(timestamp);
				return d.toLocaleTimeString([], timeConfig);
			}
		}
	};
}

const charts = [
	createChart(
		document.querySelector('#chart_a'),
		'Altitud del CanSat en tiempo real',
		generateTimeXaxis(WINDOW_SIZE, TICKS, {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
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
		generateTimeXaxis(WINDOW_SIZE, TICKS, {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff'
	),
	createChart(document.querySelector('#chart_p'),
		'Presión del CanSat en tiempo real',
		generateTimeXaxis(WINDOW_SIZE, TICKS, {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
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
		true,
		'line',
		'straight'
	),
	createChart(
		document.querySelector('#chart_aq'),
		'Calidad del aire desde estación de tierra',
		generateTimeXaxis(WINDOW_SIZE, TICKS, {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
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
		generateTimeXaxis(WINDOW_SIZE, TICKS, {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff'
	),
	createChart(document.querySelector('#chart_h'),
		'Humedad desde estación de tierra',
		generateTimeXaxis(WINDOW_SIZE, TICKS, {
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
		{
			title: {
				text: 'Humedad'
			}
		},
		'#00ff88'
	),
	createChart(
		document.querySelector('#chart_a_b'),
		'Altitud del CanSat (Copia de seguridad)',
		generateTimeXaxis(undefined, undefined, {
			year: '2-digit',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
		{
			title: {
				text: 'Altitud (m)'
			}
		},
		'#7c4dff',
		false
	),
	createChart(
		document.querySelector('#chart_t_b'),
		'Temperatura del CanSat (Copia de seguridad)',
		generateTimeXaxis(undefined, undefined, {
			year: '2-digit',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff',
		false
	),
	createChart(document.querySelector('#chart_p_b'),
		'Presión del CanSat (Copia de seguridad)',
		generateTimeXaxis(undefined, undefined, {
			year: '2-digit',
			month: '2-digit',
			day: '2-digit',
			hour: '2-digit',
			minute: '2-digit',
			second: '2-digit'
		}),
		{
			title: {
				text: 'Presión (hPa)'
			}
		},
		'#00ff88',
		false
	),
	createChart(document.querySelector('#chart_pa_b'),
		'Altitud - Presión (Copia de seguridad)',
		{
			title: {
				text: 'Presión (hPa)'
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
		false,
		'line',
		'straight'
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
	onReceiveQuats(data);
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
		charts[7].updateSeries([{ data: altitudeData, color: '#7c4dff' }]);
		charts[8].updateSeries([{ data: temperatureData, color: '#00e5ff' }]);
		charts[9].updateSeries([{ data: pressureData, color: '#00ff88' }]);
		charts[10].updateSeries([{ data: pressureAltitudeData, color: '#ff3b3b' }]);
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
}
window.handleSidebarAction = handleSidebarAction;

function generateInterval() {
    showBackupLoader();
    const startDate = document.getElementById('start-date').value;
    const startTime = document.getElementById('start-time').value;
    const endDate = document.getElementById('end-date').value;
    const endTime = document.getElementById('end-time').value;
    if (!startDate || !startTime || !endDate || !endTime) {

    }
    else {
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
