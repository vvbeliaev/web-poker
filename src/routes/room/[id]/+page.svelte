<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { connectSocket, disconnectSocket } from '$lib/socket';
	import { gameStore } from '$lib/store.svelte';
	import { playCardDeal, playChips, playFold, playWin, playHandEnd, playEliminated } from '$lib/sounds';
	import LobbyWaiting from '$lib/components/LobbyWaiting.svelte';
	import Table from '$lib/components/Table.svelte';
	import ActionBar from '$lib/components/ActionBar.svelte';
	import BlindTimer from '$lib/components/BlindTimer.svelte';
	import WinnerScreen from '$lib/components/WinnerScreen.svelte';
	import type { RoomState, ActionRequired, HandResult } from '$lib/types';

	const roomId = $derived(page.params.id ?? '');

	const AVATARS = [
		'🦊', '🐼', '🦁', '🐯', '🐻', '🐨', '🐸', '🦝', '🦄', '🐺', '🦅', '🐙',
		'👁️', '👅', '👃', '👂', '🦷', '🦴', '💀', '👾', '🤡', '👺', '👹', '💩',
		'🫠', '🥴', '🤪', '😵', '🫣', '🧠', '👁️‍🗨️', '🫀', '🫁', '🦶', '👻', '🙈',
	];

	let name = $state('');
	let avatar = $state('🦊');
	let nameSubmitted = $state(false);
	let lastHandResult = $state<HandResult | null>(null);
	let showHandResult = $state(false);
	let revealedCards = $state<Record<string, import('$lib/types').CardData[]>>({});

	const BLIND_DURATIONS = [180, 180, 120, 120, 120, 120, 120, 120];

	function getPlayerId(): string {
		let id = localStorage.getItem('poker_pid');
		if (!id) {
			id = crypto.randomUUID();
			localStorage.setItem('poker_pid', id);
		}
		return id;
	}

	function joinRoom(joinName: string, joinAvatar: string) {
		const socket = connectSocket();
		socket.emit('join_room', {
			room_id: roomId,
			name: joinName,
			avatar: joinAvatar,
			player_id: getPlayerId(),
		});
	}

	onMount(() => {
		const socket = connectSocket();
		gameStore.mySid = socket.id ?? null;

		// Pre-fill name/avatar from any previous session in any room
		const anyPrev = localStorage.getItem('poker_last_profile');
		if (anyPrev) {
			try {
				const { name: n, avatar: a } = JSON.parse(anyPrev);
				if (!name) name = n;
				if (avatar === '🦊') avatar = a;
			} catch { /* ignore */ }
		}

		// Auto-reconnect if we've been in this room before
		const saved = localStorage.getItem(`poker_room_${roomId}`);
		if (saved) {
			try {
				const { name: savedName, avatar: savedAvatar } = JSON.parse(saved);
				name = savedName;
				avatar = savedAvatar;
				nameSubmitted = true;
				socket.on('connect', () => {
					gameStore.mySid = socket.id ?? null;
					joinRoom(savedName, savedAvatar);
				});
				if (socket.connected) joinRoom(savedName, savedAvatar);
			} catch {
				localStorage.removeItem(`poker_room_${roomId}`);
			}
		} else {
			socket.on('connect', () => {
				gameStore.mySid = socket.id ?? null;
			});
		}

		socket.on('room_state', (state: RoomState) => {
			const prev = gameStore.roomState;
			gameStore.roomState = state;

			// New hole cards dealt (hand start)
			if (state.my_cards.length === 2 && (prev?.my_cards.length ?? 0) === 0) {
				playCardDeal();
				setTimeout(playCardDeal, 110);
			}
			// New community cards revealed
			const prevCount = prev?.community_cards.length ?? 0;
			const newCount = state.community_cards.length;
			if (newCount > prevCount) {
				for (let i = 0; i < newCount - prevCount; i++) {
					setTimeout(playCardDeal, i * 110);
				}
			}
		});

		socket.on('action_required', (data: ActionRequired) => {
			gameStore.actionRequired = data;
		});

		socket.on('hand_result', (data: HandResult) => {
			lastHandResult = data;
			showHandResult = true;
			gameStore.actionRequired = null;
			if (data.hole_cards) revealedCards = data.hole_cards;
			if (data.winner_sid === gameStore.mySid) {
				playWin();
			} else {
				playHandEnd();
			}
			setTimeout(() => {
				showHandResult = false;
				revealedCards = {};
			}, 3500);
		});

		socket.on('eliminated', ({ player_name }: { player_name: string }) => {
			gameStore.eliminatedName = player_name;
			playEliminated();
			setTimeout(() => {
				gameStore.eliminatedName = null;
			}, 3000);
		});

		socket.on('winner', ({ player_name }: { player_name: string }) => {
			gameStore.winnerName = player_name;
		});

		socket.on('blind_up', () => {});

		socket.on('error', ({ message }: { message: string }) => {
			gameStore.error = message;
		});
	});

	onDestroy(() => {
		disconnectSocket();
		gameStore.reset();
	});

	function submitName() {
		if (!name.trim()) return;
		nameSubmitted = true;
		const profile = { name: name.trim(), avatar };
		localStorage.setItem(`poker_room_${roomId}`, JSON.stringify(profile));
		localStorage.setItem('poker_last_profile', JSON.stringify(profile));
		joinRoom(name.trim(), avatar);
	}

	function handleReady(ready: boolean) {
		const socket = connectSocket();
		socket.emit('set_ready', { ready });
	}

	function handleAction(type: string, amount?: number) {
		if (type === 'fold') playFold();
		else playChips();
		const socket = connectSocket();
		socket.emit('action', { type, amount: amount ?? 0 });
		gameStore.actionRequired = null;
	}

	async function handleNewGame() {
		const res = await fetch('/api/rooms', { method: 'POST' });
		const { room_id } = await res.json();
		await goto(`/room/${room_id}`);
	}

	const roomState = $derived(gameStore.roomState);
	const blindDuration = $derived(
		BLIND_DURATIONS[Math.min(roomState?.blind_level ?? 0, BLIND_DURATIONS.length - 1)]
	);
</script>

<svelte:head>
	<title>Poker · {roomId.toUpperCase()}</title>
</svelte:head>

<div class="root">
	{#if !nameSubmitted}
		<!-- Name entry -->
		<div class="center-screen">
			<div class="join-card">
				<p class="join-room-code">{roomId.toUpperCase()}</p>
				<h1>Join Table</h1>
				<div class="avatar-preview">{avatar}</div>
				<div class="avatar-grid">
					{#each AVATARS as emoji}
						<button
							type="button"
							class="avatar-opt"
							class:selected={avatar === emoji}
							onclick={() => (avatar = emoji)}
						>{emoji}</button>
					{/each}
				</div>
				<form onsubmit={(e) => { e.preventDefault(); submitName(); }}>
					<input
						bind:value={name}
						placeholder="Your name"
						maxlength="20"
						autofocus
						class="name-input"
					/>
					<button type="submit" class="join-btn" disabled={!name.trim()}>
						Enter →
					</button>
				</form>
			</div>
		</div>

	{:else if gameStore.error}
		<div class="center-screen">
			<div class="join-card">
				<p class="error-msg">{gameStore.error}</p>
				<button class="join-btn" onclick={() => (gameStore.error = null)}>Back</button>
			</div>
		</div>

	{:else if !roomState}
		<div class="center-screen">
			<span class="connecting">Connecting…</span>
		</div>

	{:else if roomState.state === 'waiting'}
		<div class="center-screen">
			<LobbyWaiting
				players={roomState.players}
				mySid={gameStore.mySid}
				{roomId}
				onReady={handleReady}
			/>
		</div>

	{:else if roomState.state === 'playing'}
		<div class="game-layout">
			<!-- Top bar -->
			<header class="top-bar">
				<span class="room-badge">{roomId.toUpperCase()}</span>
				<BlindTimer
					blindLevel={roomState.blind_level}
					sb={roomState.blinds.sb}
					bb={roomState.blinds.bb}
					secondsUntilNext={roomState.seconds_until_next_blind}
					totalDuration={blindDuration}
				/>
			</header>

			<!-- Table (fills remaining space) -->
			<main class="table-area">
				<Table
					players={roomState.players}
					communityCards={roomState.community_cards}
					pot={roomState.pot}
					actionSid={roomState.action_sid}
					mySid={gameStore.mySid}
					myCards={roomState.my_cards}
					{revealedCards}
				/>
			</main>

			<!-- Action bar -->
			<footer class="action-area">
				<ActionBar
					actionRequired={gameStore.actionRequired}
					isMyTurn={gameStore.isMyTurn}
					onAction={handleAction}
				/>
			</footer>
		</div>

		<!-- Hand result toast -->
		{#if showHandResult && lastHandResult}
			<div class="toast">
				<span class="toast-winner">{lastHandResult.winner_name}</span>
				<span class="toast-amount">+{lastHandResult.amount.toLocaleString()}</span>
				{#if lastHandResult.hand_name !== 'Uncontested'}
					<span class="toast-hand">{lastHandResult.hand_name}</span>
				{/if}
			</div>
		{/if}

		{#if gameStore.eliminatedName}
			<div class="toast toast-eliminated">
				{gameStore.eliminatedName} eliminated
			</div>
		{/if}

	{:else if roomState.state === 'finished'}
		<WinnerScreen winnerName={gameStore.winnerName ?? 'Winner'} onNewGame={handleNewGame} />
	{/if}
</div>

<style>
	.root {
		height: 100dvh;
		overflow: hidden;
	}

	/* ─── Full-screen game layout ─── */
	.game-layout {
		height: 100dvh;
		display: grid;
		grid-template-rows: 44px 1fr 80px;
		background: var(--bg, #06060a);
	}

	.top-bar {
		display: flex;
		align-items: center;
		justify-content: space-between;
		padding: 0 16px;
		border-bottom: 1px solid rgba(201, 168, 76, 0.06);
		background: rgba(6, 6, 10, 0.95);
		z-index: 10;
	}

	.room-badge {
		font-family: var(--font-mono, monospace);
		font-size: 10px;
		letter-spacing: 0.25em;
		color: rgba(201, 168, 76, 0.3);
	}

	.table-area {
		display: flex;
		align-items: center;
		justify-content: center;
		overflow: hidden;
		padding: 12px 16px;
	}

	.action-area {
		border-top: 1px solid rgba(201, 168, 76, 0.06);
	}

	/* ─── Center screen (name entry / lobby) ─── */
	.center-screen {
		height: 100dvh;
		display: flex;
		align-items: center;
		justify-content: center;
		background: var(--bg, #06060a);
	}

	.join-card {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
		animation: rise 0.5s ease-out both;
	}

	.join-room-code {
		font-family: var(--font-mono, monospace);
		font-size: 0.7rem;
		letter-spacing: 0.35em;
		color: var(--gold, #c9a84c);
		opacity: 0.5;
	}

	h1 {
		font-family: var(--font-display, serif);
		font-size: 2rem;
		font-weight: 700;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--text, #e8dfc8);
	}

	.avatar-preview {
		font-size: 3rem;
		line-height: 1;
		margin-bottom: 0.25rem;
	}

	.avatar-grid {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 6px;
		margin-bottom: 0.5rem;
		max-height: 160px;
		overflow-y: auto;
		padding-right: 2px;
	}

	.avatar-opt {
		font-size: 1.4rem;
		background: rgba(10, 10, 20, 0.6);
		border: 1px solid rgba(201, 168, 76, 0.1);
		border-radius: 6px;
		padding: 4px;
		cursor: pointer;
		transition: border-color 0.15s, background 0.15s;
		line-height: 1;
	}

	.avatar-opt:hover {
		background: rgba(201, 168, 76, 0.06);
		border-color: rgba(201, 168, 76, 0.35);
	}

	.avatar-opt.selected {
		border-color: var(--gold, #c9a84c);
		background: rgba(201, 168, 76, 0.1);
		box-shadow: 0 0 10px rgba(201, 168, 76, 0.2);
	}

	form {
		display: flex;
		gap: 8px;
		margin-top: 0.5rem;
	}

	.name-input {
		padding: 0.65rem 1rem;
		width: 200px;
		background: rgba(10, 10, 20, 0.8);
		border: 1px solid rgba(201, 168, 76, 0.15);
		border-radius: 4px;
		color: var(--text, #e8dfc8);
		font-size: 0.95rem;
		outline: none;
		transition: border-color 0.2s;
	}

	.name-input::placeholder { color: rgba(232, 223, 200, 0.2); }
	.name-input:focus { border-color: rgba(201, 168, 76, 0.4); }

	.join-btn {
		padding: 0.65rem 1.4rem;
		background: transparent;
		border: 1px solid rgba(201, 168, 76, 0.3);
		border-radius: 4px;
		color: var(--gold, #c9a84c);
		font-size: 0.85rem;
		font-weight: 500;
		letter-spacing: 0.1em;
		cursor: pointer;
		transition: background 0.2s, box-shadow 0.2s;
	}

	.join-btn:hover:not(:disabled) {
		background: rgba(201, 168, 76, 0.06);
		box-shadow: 0 0 16px rgba(201, 168, 76, 0.15);
	}

	.join-btn:disabled { opacity: 0.3; cursor: not-allowed; }

	.connecting {
		font-size: 0.8rem;
		letter-spacing: 0.2em;
		color: var(--text-muted, rgba(232, 223, 200, 0.2));
		text-transform: uppercase;
	}

	.error-msg {
		color: #f87171;
		font-size: 0.85rem;
	}

	/* ─── Toasts ─── */
	.toast {
		position: fixed;
		bottom: 96px;
		left: 50%;
		transform: translateX(-50%);
		display: flex;
		align-items: center;
		gap: 10px;
		background: rgba(10, 10, 20, 0.95);
		border: 1px solid rgba(201, 168, 76, 0.2);
		border-radius: 6px;
		padding: 10px 20px;
		pointer-events: none;
		white-space: nowrap;
		animation: toast-in 0.3s ease-out both, toast-out 0.3s ease-in 3.2s both;
		z-index: 100;
	}

	.toast-winner {
		font-weight: 600;
		color: var(--text, #e8dfc8);
		font-size: 0.85rem;
	}

	.toast-amount {
		font-family: var(--font-mono, monospace);
		font-size: 0.85rem;
		color: var(--gold, #c9a84c);
		font-weight: 700;
	}

	.toast-hand {
		font-size: 0.75rem;
		color: var(--text-dim, rgba(232, 223, 200, 0.45));
		font-style: italic;
	}

	.toast-eliminated {
		border-color: rgba(220, 38, 38, 0.2);
		color: #f87171;
		font-size: 0.8rem;
		letter-spacing: 0.05em;
	}

	@keyframes rise {
		from { opacity: 0; transform: translateY(12px); }
		to   { opacity: 1; transform: translateY(0); }
	}

	@keyframes toast-in {
		from { opacity: 0; transform: translateX(-50%) translateY(8px); }
		to   { opacity: 1; transform: translateX(-50%) translateY(0); }
	}

	@keyframes toast-out {
		from { opacity: 1; }
		to   { opacity: 0; }
	}
</style>
