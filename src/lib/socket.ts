// src/lib/socket.ts
import { browser } from '$app/environment';
import { io, type Socket } from 'socket.io-client';

let _socket: Socket | null = null;

export function getSocket(): Socket {
	if (!browser) throw new Error('Socket only available in browser');
	if (!_socket) {
		_socket = io({ autoConnect: false, transports: ['websocket'] });
	}
	return _socket;
}

export function connectSocket(): Socket {
	const s = getSocket();
	if (!s.connected) s.connect();
	return s;
}

export function disconnectSocket(): void {
	_socket?.disconnect();
	_socket = null;
}
