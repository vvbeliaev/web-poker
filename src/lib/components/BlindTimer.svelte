<!-- src/lib/components/BlindTimer.svelte -->
<script lang="ts">
	let {
		blindLevel,
		sb,
		bb,
		secondsUntilNext,
		totalDuration
	}: {
		blindLevel: number;
		sb: number;
		bb: number;
		secondsUntilNext: number;
		totalDuration: number;
	} = $props();

	const progress = $derived(totalDuration > 0 ? (1 - secondsUntilNext / totalDuration) * 100 : 100);
	const mins = $derived(Math.floor(secondsUntilNext / 60));
	const secs = $derived(Math.floor(secondsUntilNext % 60).toString().padStart(2, '0'));
	const levelLabel = $derived(`L${blindLevel + 1}`);
</script>

<div class="blind-timer">
	<span class="level">{levelLabel}</span>
	<div class="divider"></div>
	<div class="blinds">
		<span class="blinds-value">{sb.toLocaleString()} <span class="sep">/</span> {bb.toLocaleString()}</span>
	</div>
	<div class="track">
		<div class="bar" style="width: {progress}%"></div>
	</div>
	<span class="countdown">{mins}:{secs}</span>
</div>

<style>
	.blind-timer {
		display: flex;
		align-items: center;
		gap: 8px;
		padding: 0 12px;
		height: 100%;
	}

	.level {
		font-family: var(--font-mono, monospace);
		font-size: 9px;
		font-weight: 700;
		letter-spacing: 0.1em;
		color: var(--text-dim, rgba(232, 223, 200, 0.45));
		text-transform: uppercase;
	}

	.divider {
		width: 1px;
		height: 14px;
		background: rgba(201, 168, 76, 0.12);
	}

	.blinds-value {
		font-family: var(--font-mono, monospace);
		font-size: 12px;
		font-weight: 600;
		color: var(--gold, #c9a84c);
		letter-spacing: 0.04em;
		white-space: nowrap;
	}

	.sep {
		opacity: 0.4;
		font-weight: 300;
	}

	.track {
		width: 60px;
		height: 2px;
		background: rgba(201, 168, 76, 0.1);
		border-radius: 1px;
		overflow: hidden;
	}

	.bar {
		height: 100%;
		background: linear-gradient(90deg, rgba(201, 168, 76, 0.4), var(--gold, #c9a84c));
		border-radius: 1px;
		transition: width 1s linear;
	}

	.countdown {
		font-family: var(--font-mono, monospace);
		font-size: 10px;
		color: var(--text-dim, rgba(232, 223, 200, 0.45));
		letter-spacing: 0.05em;
		min-width: 28px;
		text-align: right;
	}
</style>
