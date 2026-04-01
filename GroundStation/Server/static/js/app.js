const window_size = 60 * 1000;
const ticks = 6;

function createChart(element, title, xaxis, yaxis, color, type='line') {
	return new ApexCharts(element, {
		chart: {
			type: type,
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
		xaxis: xaxis,
		yaxis: yaxis,
		stroke: {
			curve: 'smooth',
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
		document.querySelector("#chart_a"),
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
		document.querySelector("#chart_t"),
		'Temperatura del CanSat en tiempo real',
		timeXaxis,
		{
			title: {
				text: 'Temperatura (Celsius)'
			}
		},
		'#00e5ff'
	),
	createChart(document.querySelector("#chart_p"),
		'Presión del CanSat en tiempo real',
		timeXaxis,
		{
			title: {
				text: 'Presión (hPa)'
			}
		},
		'#00ff88'
	),
	createChart(document.querySelector("#chart_pa"),
		'Presión - Altitud',
		{
			title: {
				text: 'Presión (hPa)'
			},
			forceNiceScale: true,
			range: undefined
		},
		{
			type: 'numeric',
  			title: {
    			text: 'Altitud (m)'
  			},
			forceNiceScale: true,
			range: undefined
  			//labels: {
    		//	formatter: (val) => `${Math.round(val)} m`
  			//}
  		},
		'#ff3b3b',
		'bar'
	)
];

for (const chart of charts) {
	chart.render();
}


const socket = io('http://localhost:5000');
const loadingTime = 7 * 1000;
let firstData = true
let no_realtime_data = [
	{
		chart_index: 3,
		data: []
	}
];

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
	no_realtime_data[0]['data'].push({
		x: pressure,
		y: altitude
	});
	//if (no_realtime_data[0]['data'].length > 30) {
  	//	no_realtime_data[0]['data'].shift();
	//}
});

setInterval(() => {
	no_realtime_data.forEach((data) => {
		data['data'].sort((a, b) => a.y - b.y);
		charts[data['chart_index']].updateSeries([{
			data: data['data']
		}]);
	});
}, 3 * 1000);
