// CHART.JS
const WINDOW = 60 * 1000;

function createChart(ctx, label, color, yLabel) {
	return new Chart(ctx, {
		type: 'line',
		data: {
			datasets: [{
				label: label,
				data: [],
				borderColor: color,
				tension: 0.4,
		   		//cubicInterpolationMode: 'monotone',
		  		//borderWidth: 2
			}]
		},
		options: {
			responsive: true,
			//animation: {
	    	//	duration: 1000,
	  		//},
			scales: {
				x: {
					type: 'time',
					//time: {
					//	unit: 'second',
					//	displayFormats: {
					//		second: 'HH:mm:ss',
					//		minute: 'HH:mm',
					//		hour: 'HH:mm'
					//	}
					//},
					//ticks: {
					//	callback: function(value) {
					//		return new Date(value).toLocaleTimeString('es-ES', {
					//			hour: '2-digit',
					//			minute: '2-digit',
					//			second: '2-digit',
					//			hour12: false
					//		});
					//	}
					//},
					title: {
						display: true,
						text: 'Tiempo'
					},
					offset: true
				},
				y: {
					title: {
						display: true,
						text: yLabel
					}
				}
			},
			layout: {
	    		padding: {
	      			left: 10,
	      			right: 10
	    		}
	  		},
	  		plugins: {
				tooltip: {
					callbacks: {
						title: (items) => {
							const date = new Date(items[0].parsed.x);
							return date.toLocaleTimeString('es-ES', {
								year: 'numeric',
								month: '2-digit',
								day: '2-digit',
								hour: '2-digit',
								minute: '2-digit',
								second: '2-digit',
								hour12: false
							});
						}
					}
				}
			}
		}
	});
}

const charts = [
	//createChart(document.getElementById('chart_a'), 'Altitud del CanSat', 'rgb(75, 192, 192)', 'Altitud (m)'),
	//createChart(document.getElementById('chart_t'), 'Temperatura del CanSat', 'rgb(75, 192, 75)', 'Temperatura (Celsius)'),
	//createChart(document.getElementById('chart_p'), 'Presión del CanSat', 'rgb(75, 75, 192)', 'Presión (hPa)')
];

let lastDate = 0;
let data = [];
let TICKINTERVAL = 1000;
let XAXISRANGE = 60 * 1000;

function getNewSeries(baseval, yrange) {
	let newDate = baseval + TICKINTERVAL;
	lastDate = newDate;
	for (let i = 0; i < data.length - 10; i++) {
		data[i].x = newDate - XAXISRANGE - TICKINTERVAL;
		data[i].y = 0;
	}
	data.push({
		x: newDate,
		y: Math.floor(Math.random() * (yrange.max - yrange.min + 1)) + yrange.min
	});
}

const options = {
	chart: {
		type: 'line',
		animations: {
			enabled: true,
			dynamicAnimation: {
				speed: 1000
			}
		},
		toolbar: {
			show: false
		}
	},
	xaxis: {
		type: 'datetime',
		range: XAXISRANGE
	},
	yaxis: {
		max: 100
	}
};

const test = new ApexCharts(document.querySelector('#chart'), options);
test.render();

setInterval(function () {
	getNewSeries(lastDate, { min: 10, max: 90 });
	test.updateSeries([{ data: data }]);
}, 1000);

// SOCKETIO
const socket = io("http://localhost:5000");

socket.on("connect", () => {
	console.log("Conectado al servidor");
});

socket.on("BMP390_data", (data) => {
	console.log("Datos recibidos:", data);

	const now = new Date();
	const altitude = data['altitude'];
	const temperature = data['temperature'];
	const pressure = data['pressure'];

	//series[0].data.push({
	//	x: now,
	//	y: data.altitude
	//});

	//test.updateSeries(series);

	//charts[0].data.datasets[0].data.push({
	//	x: now,
	//	y: altitude
	//});
	//charts[1].data.datasets[0].data.push({
	//	x: now,
	//	y: temperature
	//});
	//charts[2].data.datasets[0].data.push({
	//	x: now,
	//	y: pressure
	//});

	//for (const chart of charts) {
	//	chart.update('none');
	//}
});
