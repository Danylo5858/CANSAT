import { socket } from './app.js';

let request_data = {};

socket.on('backup_response', (res) => {
	if (res['success'] === true) {
		console.log('Copia de seguridad del CanSat recibida correctamente');
		console.log(res['data'])
	}
	else {
		console.log('Fallo recibiendo la copia de seguridad del CanSat');
	}
});

export function backupRequest(bmp, mpu, gps, start=0, end=0) {
	request_data = {
		bmp: bmp,
		mpu: mpu,
		gps: gps,
		start: start,
		end: end
	};
	socket.emit('backup_request', request_data);
	console.log('Enviando peticion de copia de seguridad del CanSat');
}
