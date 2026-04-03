import { onReceiveQuats } from './3D_visualization.js';
import { backupRequest } from './backup.js';

const window_size = 60 * 1000;
const ticks = 6;

function createChart(element, title, xaxis, yaxis, color, type='line', curve='smooth') {
	return new ApexCharts(element, {
		chart: {
			type: type,
			animations: {
				enabled: true,
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

const timeXaxis = {
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
};

const charts = [
	createChart(
		document.querySelector('#chart_a'),
		'Altitud del CanSat en tiempo real',
		timeXaxis,
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
		timeXaxis,
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff'
	),
	createChart(document.querySelector('#chart_p'),
		'Presión del CanSat en tiempo real',
		timeXaxis,
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
		'line',
		'straight'
	),
	createChart(
		document.querySelector('#chart_aq'),
		'Calidad del aire desde estación de tierra',
		timeXaxis,
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
		timeXaxis,
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff'
	),
	createChart(document.querySelector('#chart_h'),
		'Humedad desde estación de tierra',
		timeXaxis,
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

socket.on('backup_response', (res) => {
	if (res['success'] === true) {
		console.log('Copia de seguridad del CanSat recibida correctamente');
		console.log(res['data'])
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
		backupRequest(true, true, false, '2026-04-03 23:15:00', '2026-04-03 23:17:35');
	}
}
window.handleSidebarAction = handleSidebarAction;


function disableInputs() {
    document.querySelectorAll('#backup-config input').forEach(el => {
        el.disabled = true;
    });
}

function showLoader() {
    document.getElementById('backup-loader').classList.remove('hide');
}

function generateInterval() {
    disableInputs();
    showLoader();

    // aquí iría tu lógica real
}
window.generateInterval = generateInterval

function generateFull() {
    disableInputs();
    showLoader();

    // aquí iría tu lógica real
}
window.generateFull = generateFull
