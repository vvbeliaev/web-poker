// src/lib/store.svelte.ts
import type { RoomState, ActionRequired, HandResult } from '$lib/types';

class GameStore {
	roomState = $state<RoomState | null>(null);
	actionRequired = $state<ActionRequired | null>(null);
	lastHandResult = $state<HandResult | null>(null);
	winnerName = $state<string | null>(null);
	eliminatedName = $state<string | null>(null);
	mySid = $state<string | null>(null);
	error = $state<string | null>(null);

	get isMyTurn(): boolean {
		return this.roomState?.action_sid === this.mySid;
	}

	get myPlayer() {
		return this.roomState?.players.find((p) => p.sid === this.mySid) ?? null;
	}

	reset() {
		this.roomState = null;
		this.actionRequired = null;
		this.lastHandResult = null;
		this.winnerName = null;
		this.eliminatedName = null;
		this.error = null;
	}
}

export const gameStore = new GameStore();
