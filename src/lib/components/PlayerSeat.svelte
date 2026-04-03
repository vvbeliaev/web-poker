<!-- src/lib/components/PlayerSeat.svelte -->
<script lang="ts">
	import Card from './Card.svelte';
	import type { PlayerData, CardData } from '$lib/types';

	let {
		player,
		isActive,
		myCards = null,
		isMe = false
	}: {
		player: PlayerData;
		isActive: boolean;
		myCards?: CardData[] | null;
		isMe?: boolean;
	} = $props();

	const displayCards = $derived(isMe && myCards ? myCards : null);
	const inHand = $derived(player.status !== 'eliminated' && player.status !== 'folded');
</script>

<div
	class="seat"
	class:active={isActive}
	class:me={isMe}
	class:folded={player.status === 'folded'}
	class:eliminated={player.status === 'eliminated'}
	class:all-in={player.status === 'all_in'}
>
	<!-- Hole cards -->
	<div class="cards-row">
		{#if displayCards}
			{#each displayCards as card}
				<Card {card} small />
			{/each}
		{:else if inHand}
			<Card card={null} faceDown small />
			<Card card={null} faceDown small />
		{:else}
			<div class="cards-placeholder"></div>
		{/if}
	</div>

	<!-- Name + chips -->
	<div class="info">
		<span class="name">{player.name}{isMe ? ' ◆' : ''}</span>
		<span class="chips">{player.chips.toLocaleString()}</span>
	</div>

	<!-- Bet badge -->
	{#if player.street_bet > 0}
		<div class="bet">{player.street_bet.toLocaleString()}</div>
	{/if}

	<!-- Status badge -->
	{#if player.status === 'all_in'}
		<div class="badge all-in-badge">ALL IN</div>
	{:else if player.status === 'folded'}
		<div class="badge folded-badge">FOLD</div>
	{/if}
</div>

<style>
	.seat {
		background: rgba(8, 8, 18, 0.92);
		border: 1px solid var(--border, rgba(201, 168, 76, 0.08));
		border-radius: 10px;
		padding: 6px 9px;
		min-width: 76px;
		max-width: 96px;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 3px;
		transition: border-color 0.25s, box-shadow 0.25s, opacity 0.25s;
		backdrop-filter: blur(4px);
	}

	.seat.active {
		border-color: var(--border-active, rgba(201, 168, 76, 0.55));
		box-shadow:
			0 0 0 1px rgba(201, 168, 76, 0.2),
			0 0 24px rgba(201, 168, 76, 0.25),
			0 0 60px rgba(201, 168, 76, 0.08);
	}

	.seat.me {
		border-color: rgba(201, 168, 76, 0.22);
	}

	.seat.folded {
		opacity: 0.45;
		filter: grayscale(0.5);
	}

	.seat.eliminated {
		opacity: 0.25;
		filter: grayscale(1);
	}

	.cards-row {
		display: flex;
		gap: 3px;
		height: 46px;
		align-items: center;
	}

	.cards-placeholder {
		width: 67px;
		height: 46px;
	}

	.info {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1px;
		min-width: 0;
		width: 100%;
	}

	.name {
		font-size: 10px;
		font-family: var(--font-ui, sans-serif);
		font-weight: 500;
		color: var(--text, #e8dfc8);
		white-space: nowrap;
		max-width: 78px;
		overflow: hidden;
		text-overflow: ellipsis;
		letter-spacing: 0.02em;
	}

	.seat.me .name {
		color: var(--gold, #c9a84c);
	}

	.chips {
		font-size: 11px;
		font-family: var(--font-mono, monospace);
		font-weight: 600;
		color: var(--gold, #c9a84c);
		letter-spacing: 0.04em;
	}

	.bet {
		font-size: 9px;
		font-family: var(--font-mono, monospace);
		color: rgba(234, 108, 20, 0.9);
		letter-spacing: 0.06em;
		background: rgba(234, 108, 20, 0.1);
		border: 1px solid rgba(234, 108, 20, 0.2);
		border-radius: 3px;
		padding: 1px 5px;
	}

	.badge {
		font-size: 7px;
		font-weight: 700;
		letter-spacing: 0.12em;
		border-radius: 2px;
		padding: 1px 5px;
		text-transform: uppercase;
	}

	.all-in-badge {
		background: rgba(234, 108, 20, 0.15);
		border: 1px solid rgba(234, 108, 20, 0.35);
		color: #ea6c14;
	}

	.folded-badge {
		background: rgba(100, 80, 60, 0.1);
		border: 1px solid rgba(100, 80, 60, 0.2);
		color: rgba(200, 180, 150, 0.4);
	}
</style>
