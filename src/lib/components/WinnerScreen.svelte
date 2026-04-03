<!-- src/lib/components/WinnerScreen.svelte -->
<script lang="ts">
	let {
		winnerName,
		onNewGame
	}: {
		winnerName: string;
		onNewGame: () => void;
	} = $props();
</script>

<div class="winner-screen">
	<div class="glow-ring"></div>
	<div class="suit">♠</div>
	<p class="over">Tournament Over</p>
	<h1 class="winner-name">{winnerName}</h1>
	<p class="subtitle">takes the pot</p>
	<button onclick={onNewGame} class="new-game-btn">New Table</button>
</div>

<style>
	.winner-screen {
		height: 100dvh;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
		text-align: center;
		position: relative;
		overflow: hidden;
		animation: fadeIn 0.8s ease-out both;
	}

	.glow-ring {
		position: absolute;
		width: 400px;
		height: 400px;
		border-radius: 50%;
		background: radial-gradient(ellipse, rgba(201, 168, 76, 0.08) 0%, transparent 70%);
		pointer-events: none;
	}

	.suit {
		font-family: var(--font-display, serif);
		font-size: 3.5rem;
		color: var(--gold, #c9a84c);
		opacity: 0.5;
		line-height: 1;
		animation: pulse 2s ease-in-out infinite;
	}

	.over {
		font-family: var(--font-ui, sans-serif);
		font-size: 0.7rem;
		font-weight: 300;
		letter-spacing: 0.35em;
		text-transform: uppercase;
		color: var(--text-dim, rgba(232, 223, 200, 0.4));
		margin-top: 0.5rem;
	}

	.winner-name {
		font-family: var(--font-display, serif);
		font-size: clamp(2rem, 6vw, 4rem);
		font-weight: 700;
		color: var(--gold, #c9a84c);
		letter-spacing: 0.04em;
		line-height: 1.1;
	}

	.subtitle {
		font-size: 0.7rem;
		font-weight: 300;
		letter-spacing: 0.25em;
		text-transform: uppercase;
		color: var(--text-dim, rgba(232, 223, 200, 0.35));
	}

	.new-game-btn {
		margin-top: 2rem;
		padding: 0.8rem 2.5rem;
		background: transparent;
		border: 1px solid rgba(201, 168, 76, 0.35);
		border-radius: 3px;
		color: var(--gold, #c9a84c);
		font-size: 0.75rem;
		font-weight: 500;
		letter-spacing: 0.2em;
		text-transform: uppercase;
		cursor: pointer;
		transition: background 0.2s, box-shadow 0.2s;
	}

	.new-game-btn:hover {
		background: rgba(201, 168, 76, 0.08);
		box-shadow: 0 0 20px rgba(201, 168, 76, 0.2);
	}

	@keyframes fadeIn {
		from { opacity: 0; transform: scale(0.97); }
		to   { opacity: 1; transform: scale(1); }
	}

	@keyframes pulse {
		0%, 100% { opacity: 0.5; transform: scale(1); }
		50%       { opacity: 0.7; transform: scale(1.05); }
	}
</style>
