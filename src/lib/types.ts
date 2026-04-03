// src/lib/types.ts

export interface CardData {
	rank: number;
	suit: 'h' | 'd' | 'c' | 's';
	rank_symbol: string;
	suit_symbol: string;
}

export interface PlayerData {
	sid: string;
	name: string;
	seat: number;
	chips: number;
	ready: boolean;
	status: 'active' | 'folded' | 'all_in' | 'eliminated';
	street_bet: number;
	hole_cards: CardData[] | null;
}

export interface RoomState {
	room_id: string;
	state: 'waiting' | 'playing' | 'finished';
	players: PlayerData[];
	community_cards: CardData[];
	pot: number;
	hand_phase: string;
	action_sid: string | null;
	current_bet: number;
	blind_level: number;
	blinds: { sb: number; bb: number };
	seconds_until_next_blind: number;
	my_cards: CardData[];
}

export interface ActionRequired {
	player_sid: string;
	options: string[];
	call_amount: number;
	min_raise: number;
	max_raise: number;
}

export interface HandResult {
	winner_sid: string;
	winner_name: string;
	amount: number;
	hand_name: string;
	community_cards: CardData[];
}
