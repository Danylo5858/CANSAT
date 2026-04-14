import { socket } from './app.js';

let request_data = {};

export function analysisRequest(bmp, mpu, gps, start=0, end=0) {
	request_data = {
		bmp: bmp,
		mpu: mpu,
		gps: gps,
		start: start,
		end: end
	};
	socket.emit('backup_request', request_data);
	window.waitingForBackupDataChart = true;
	console.log('Enviando peticion de copia de seguridad del CanSat');
}
