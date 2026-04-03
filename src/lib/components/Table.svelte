<!-- src/lib/components/Table.svelte -->
<script lang="ts">
	import PlayerSeat from './PlayerSeat.svelte';
	import Card from './Card.svelte';
	import type { PlayerData, CardData } from '$lib/types';

	let {
		players,
		communityCards,
		pot,
		actionSid,
		mySid,
		myCards
	}: {
		players: PlayerData[];
		communityCards: CardData[];
		pot: number;
		actionSid: string | null;
		mySid: string | null;
		myCards: CardData[];
	} = $props();

	// Positions around the ellipse (% from top-left of .felt)
	// Seat 0 = bottom center (the current player after rotation)
	const SEAT_POSITIONS = [
		{ top: '83%', left: '50%' }, // 0 — bottom center
		{ top: '68%', left: '16%' }, // 1 — bottom left
		{ top: '38%', left: '4%' },  // 2 — middle left
		{ top: '10%', left: '18%' }, // 3 — top left
		{ top: '6%',  left: '50%' }, // 4 — top center
		{ top: '10%', left: '80%' }, // 5 — top right
		{ top: '38%', left: '94%' }, // 6 — middle right
		{ top: '68%', left: '82%' }, // 7 — bottom right
		{ top: '50%', left: '50%' }, // 8 — overflow (9th player)
	];

	const myIndex = $derived(players.findIndex((p) => p.sid === mySid));

	const rotatedPlayers = $derived(
		players.map((p) => {
			const rotatedSeat =
				myIndex >= 0 ? (p.seat - myIndex + players.length) % players.length : p.seat;
			return { ...p, displaySeat: rotatedSeat };
		})
	);
</script>

<!--
  .table-wrap constrains the table to maintain ~2.4:1 aspect ratio
  while filling all available height. Parent should be a flex container.
-->
<div class="table-wrap">
	<div class="felt">
		<!-- Rail overlay for depth -->
		<div class="felt-inner">
			<!-- Community cards + pot -->
			<div class="center">
				{#if pot > 0}
					<div class="pot">
						<span class="pot-label">pot</span>
						<span class="pot-amount">{pot.toLocaleString()}</span>
					</div>
				{/if}
				<div class="community">
					{#each communityCards as card, i (i)}
						<Card {card} />
					{/each}
					{#each { length: 5 - communityCards.length } as _, i (i + 5)}
						<div class="card-ghost"></div>
					{/each}
				</div>
			</div>

			<!-- Player seats positioned around the ellipse -->
			{#each rotatedPlayers as player (player.sid)}
				{@const pos = SEAT_POSITIONS[player.displaySeat] ?? SEAT_POSITIONS[0]}
				<div
					class="seat-anchor"
					style="top: {pos.top}; left: {pos.left}; transform: translate(-50%, -50%);"
				>
					<PlayerSeat
						{player}
						isActive={player.sid === actionSid}
						isMe={player.sid === mySid}
						myCards={player.sid === mySid ? myCards : null}
					/>
				</div>
			{/each}
		</div>
	</div>
</div>

<style>
	.table-wrap {
		/* Fill available height; constrain width to maintain aspect ratio */
		width: 100%;
		aspect-ratio: 2.4 / 1;
		max-height: 100%;
		/* When height is the constraint: cap width so aspect ratio holds */
		max-width: calc(100vh * 2.4 - 136px * 2.4);
		position: relative;
		margin: auto;
	}

	.felt {
		position: absolute;
		inset: 0;
		border-radius: 50%;
		/* Layered shadows for depth and the dark mahogany rail */
		background: var(--rail, #1c0e04);
		box-shadow:
			0 0 0 10px var(--rail, #1c0e04),
			0 0 0 13px rgba(58, 31, 8, 0.5),
			0 8px 60px rgba(0, 0, 0, 0.95),
			0 0 120px rgba(0, 0, 0, 0.6);
	}

	.felt-inner {
		position: absolute;
		inset: 8px;
		border-radius: 50%;
		background: radial-gradient(
			ellipse at 50% 40%,
			var(--felt-center, #132213) 0%,
			var(--felt, #0d1d0c) 45%,
			#070f07 100%
		);
		border: 1px solid rgba(58, 31, 8, 0.6);
		box-shadow: inset 0 0 80px rgba(0, 0, 0, 0.5);
		overflow: hidden;
	}

	/* Subtle felt grain */
	.felt-inner::after {
		content: '';
		position: absolute;
		inset: 0;
		border-radius: 50%;
		background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
		background-size: 200px 200px;
		opacity: 0.5;
		pointer-events: none;
	}

	.center {
		position: absolute;
		top: 50%;
		left: 50%;
		transform: translate(-50%, -50%);
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 6px;
	}

	.pot {
		display: flex;
		align-items: baseline;
		gap: 6px;
	}

	.pot-label {
		font-size: 9px;
		letter-spacing: 0.25em;
		color: rgba(201, 168, 76, 0.35);
		text-transform: uppercase;
		font-family: var(--font-ui, sans-serif);
		font-weight: 300;
	}

	.pot-amount {
		font-family: var(--font-mono, monospace);
		font-size: 15px;
		font-weight: 700;
		color: var(--gold, #c9a84c);
		letter-spacing: 0.06em;
	}

	.community {
		display: flex;
		gap: 6px;
		align-items: center;
	}

	.card-ghost {
		width: 44px;
		height: 62px;
		border-radius: 5px;
		border: 1px dashed rgba(201, 168, 76, 0.08);
		background: rgba(201, 168, 76, 0.02);
		flex-shrink: 0;
	}

	.seat-anchor {
		position: absolute;
		z-index: 2;
	}
</style>
