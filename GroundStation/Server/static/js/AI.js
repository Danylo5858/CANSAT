import { socket } from './app.js';

export function analysisRequest(img='') {
	socket.emit('analysis_request', img);
	window.waitingForAIData = true;
	console.log('Enviando peticion de analisis de imagenes');
}
