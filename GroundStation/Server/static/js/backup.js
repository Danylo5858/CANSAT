import { socket } from './app.js';

export function backupRequest(bmp, mpu, gps, from_file, file, start=0, finish=0) {
	if (from_file) {

	}
	else {
		socket.emit('backup_request', {
			request_type: 'backup_request'
			bmp: bmp,
			mpu: mpu,
			gps: gps,
			start: start,
			finish: finish
		});
	}
}
