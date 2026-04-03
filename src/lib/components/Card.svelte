<!-- src/lib/components/Card.svelte -->
<script lang="ts">
	import type { CardData } from '$lib/types';

	let {
		card,
		faceDown = false,
		small = false
	}: {
		card: CardData | null;
		faceDown?: boolean;
		small?: boolean;
	} = $props();

	const isRed = $derived(card && (card.suit === 'h' || card.suit === 'd'));
</script>

<div class="card" class:small class:face-down={faceDown || !card} class:red={isRed}>
	{#if !faceDown && card}
		<span class="rank">{card.rank_symbol}</span>
		<span class="suit">{card.suit_symbol}</span>
	{:else}
		<span class="back-symbol">♠</span>
	{/if}
</div>

<style>
	.card {
		width: 44px;
		height: 62px;
		background: var(--card-bg, #f8f2e8);
		border-radius: 5px;
		box-shadow:
			0 4px 12px rgba(0, 0, 0, 0.8),
			0 1px 3px rgba(0, 0, 0, 0.6),
			inset 0 1px 0 rgba(255, 255, 255, 0.9);
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		justify-content: flex-start;
		padding: 4px 5px;
		flex-shrink: 0;
		position: relative;
		animation: flip-in 0.3s ease-out both;
	}

	.card.small {
		width: 32px;
		height: 46px;
		padding: 3px 4px;
		border-radius: 4px;
	}

	.card.face-down {
		background: linear-gradient(145deg, #1a1a3e 0%, #0d0d26 50%, #0a0a1f 100%);
		border: 1px solid rgba(201, 168, 76, 0.12);
		box-shadow:
			0 4px 12px rgba(0, 0, 0, 0.8),
			inset 0 1px 0 rgba(201, 168, 76, 0.08);
	}

	.back-symbol {
		position: absolute;
		inset: 0;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 18px;
		color: rgba(201, 168, 76, 0.15);
		pointer-events: none;
	}

	.card.small .back-symbol {
		font-size: 13px;
	}

	.rank {
		font-size: 14px;
		font-weight: 700;
		line-height: 1;
		color: #1a1610;
		font-family: var(--font-mono, monospace);
	}

	.suit {
		font-size: 14px;
		line-height: 1;
		color: #1a1610;
		margin-top: 1px;
	}

	.red .rank,
	.red .suit {
		color: #b91c1c;
	}

	.small .rank,
	.small .suit {
		font-size: 11px;
	}

	@keyframes flip-in {
		from { transform: rotateY(90deg); opacity: 0; }
		to   { transform: rotateY(0deg);  opacity: 1; }
	}
</style>
