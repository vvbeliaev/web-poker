<!-- src/lib/components/LobbyWaiting.svelte -->
<script lang="ts">
	import type { PlayerData } from '$lib/types';

	let {
		players,
		mySid,
		roomId,
		onReady
	}: {
		players: PlayerData[];
		mySid: string | null;
		roomId: string;
		onReady: (ready: boolean) => void;
	} = $props();

	const me = $derived(players.find((p) => p.sid === mySid));
	const shareUrl = $derived(typeof window !== 'undefined' ? window.location.href : '');
	const readyCount = $derived(players.filter((p) => p.ready).length);

	let copied = $state(false);

	async function copyLink() {
		await navigator.clipboard.writeText(shareUrl);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}
</script>

<div class="lobby">
	<div class="header">
		<div class="suit-mark">♠</div>
		<h1>Web Poker</h1>
		<p class="room-id">{roomId.toUpperCase()}</p>
	</div>

	<!-- Share link -->
	<div class="share-card">
		<p class="share-label">Invite friends</p>
		<div class="share-row">
			<span class="share-url">{shareUrl}</span>
			<button onclick={copyLink} class="copy-btn" class:copied>
				{copied ? '✓ Copied' : 'Copy'}
			</button>
		</div>
	</div>

	<!-- Player list -->
	<ul class="player-list">
		{#each players as player (player.sid)}
			<li class:ready={player.ready} class:me={player.sid === mySid}>
				<span class="seat-num">{player.seat + 1}</span>
				<span class="name">{player.name}{player.sid === mySid ? ' (you)' : ''}</span>
				<span class="status-dot" class:is-ready={player.ready}>
					{player.ready ? '●' : '○'}
				</span>
			</li>
		{/each}

		<!-- Empty seats -->
		{#each { length: Math.max(0, 2 - players.length) } as _}
			<li class="empty">
				<span class="seat-num">—</span>
				<span class="name empty-name">Waiting for player…</span>
			</li>
		{/each}
	</ul>

	<!-- Status + action -->
	<div class="footer">
		{#if players.length < 2}
			<p class="notice">Need at least 2 players</p>
		{:else}
			<p class="ready-status">
				<span class="ready-count">{readyCount}</span> / {players.length} ready
			</p>
		{/if}

		{#if me}
			<button
				onclick={() => onReady(!me.ready)}
				class="ready-btn"
				class:is-ready={me.ready}
			>
				{me.ready ? 'Cancel' : 'Ready'}
			</button>
		{/if}
	</div>
</div>

<style>
	.lobby {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1.5rem;
		padding: 2.5rem 1.5rem;
		width: 100%;
		max-width: 400px;
		animation: rise 0.5s ease-out both;
	}

	.header {
		text-align: center;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.4rem;
	}

	.suit-mark {
		font-family: var(--font-display, serif);
		font-size: 1.5rem;
		color: var(--gold, #c9a84c);
		opacity: 0.5;
		line-height: 1;
	}

	h1 {
		font-family: var(--font-display, serif);
		font-size: 2rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		text-transform: uppercase;
		color: var(--text, #e8dfc8);
		line-height: 1;
	}

	.room-id {
		font-family: var(--font-mono, monospace);
		font-size: 0.7rem;
		letter-spacing: 0.3em;
		color: var(--gold, #c9a84c);
		opacity: 0.6;
	}

	.share-card {
		width: 100%;
		background: rgba(10, 10, 20, 0.6);
		border: 1px solid var(--border, rgba(201, 168, 76, 0.08));
		border-radius: 6px;
		padding: 10px 14px;
	}

	.share-label {
		font-size: 9px;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		color: var(--text-muted, rgba(232, 223, 200, 0.2));
		margin-bottom: 6px;
	}

	.share-row {
		display: flex;
		gap: 8px;
		align-items: center;
	}

	.share-url {
		flex: 1;
		font-size: 11px;
		color: var(--text-dim, rgba(232, 223, 200, 0.45));
		overflow: hidden;
		text-overflow: ellipsis;
		white-space: nowrap;
		font-family: var(--font-mono, monospace);
	}

	.copy-btn {
		padding: 4px 12px;
		background: transparent;
		border: 1px solid rgba(201, 168, 76, 0.2);
		border-radius: 3px;
		color: var(--gold, #c9a84c);
		font-size: 10px;
		font-weight: 500;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		cursor: pointer;
		transition: background 0.15s, border-color 0.15s;
		white-space: nowrap;
	}

	.copy-btn:hover { background: rgba(201, 168, 76, 0.06); border-color: rgba(201, 168, 76, 0.4); }
	.copy-btn.copied { color: #4ade80; border-color: rgba(74, 222, 128, 0.35); }

	.player-list {
		list-style: none;
		width: 100%;
		display: flex;
		flex-direction: column;
		gap: 6px;
	}

	li {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 9px 14px;
		background: rgba(8, 8, 16, 0.7);
		border: 1px solid var(--border, rgba(201, 168, 76, 0.08));
		border-radius: 5px;
		transition: border-color 0.2s;
	}

	li.ready { border-color: rgba(201, 168, 76, 0.22); }
	li.me    { border-color: rgba(201, 168, 76, 0.3); }
	li.empty { opacity: 0.3; }

	.seat-num {
		font-family: var(--font-mono, monospace);
		font-size: 10px;
		color: var(--text-muted, rgba(232, 223, 200, 0.2));
		min-width: 12px;
	}

	.name {
		flex: 1;
		font-size: 13px;
		font-weight: 500;
		color: var(--text, #e8dfc8);
	}

	.empty-name {
		font-size: 11px;
		font-style: italic;
		color: var(--text-muted, rgba(232, 223, 200, 0.2));
	}

	li.me .name { color: var(--gold, #c9a84c); }

	.status-dot {
		font-size: 10px;
		color: var(--text-muted, rgba(232, 223, 200, 0.2));
		transition: color 0.2s;
	}

	.status-dot.is-ready { color: var(--gold, #c9a84c); }

	.footer {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 12px;
		width: 100%;
	}

	.notice {
		font-size: 11px;
		letter-spacing: 0.08em;
		color: var(--text-muted, rgba(232, 223, 200, 0.2));
	}

	.ready-status {
		font-size: 12px;
		color: var(--text-dim, rgba(232, 223, 200, 0.45));
		letter-spacing: 0.06em;
	}

	.ready-count {
		font-family: var(--font-mono, monospace);
		font-weight: 700;
		color: var(--gold, #c9a84c);
	}

	.ready-btn {
		width: 100%;
		padding: 0.85rem;
		background: transparent;
		border: 1px solid rgba(201, 168, 76, 0.25);
		border-radius: 4px;
		color: var(--text-dim, rgba(232, 223, 200, 0.45));
		font-size: 0.8rem;
		font-weight: 500;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		cursor: pointer;
		transition: background 0.2s, border-color 0.2s, color 0.2s, box-shadow 0.2s;
	}

	.ready-btn:hover {
		background: rgba(201, 168, 76, 0.04);
		border-color: rgba(201, 168, 76, 0.45);
		color: var(--gold, #c9a84c);
	}

	.ready-btn.is-ready {
		background: rgba(201, 168, 76, 0.08);
		border-color: rgba(201, 168, 76, 0.5);
		color: var(--gold, #c9a84c);
		box-shadow: 0 0 20px rgba(201, 168, 76, 0.1);
	}

	@keyframes rise {
		from { opacity: 0; transform: translateY(12px); }
		to   { opacity: 1; transform: translateY(0); }
	}
</style>
