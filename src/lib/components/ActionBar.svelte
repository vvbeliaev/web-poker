<!-- src/lib/components/ActionBar.svelte -->
<script lang="ts">
	import type { ActionRequired } from '$lib/types';
	import { playTimerTick } from '$lib/sounds';

	let {
		actionRequired,
		isMyTurn,
		onAction
	}: {
		actionRequired: ActionRequired | null;
		isMyTurn: boolean;
		onAction: (type: string, amount?: number) => void;
	} = $props();

	let raiseAmount = $state(0);
	let timeLeft = $state(0);
	let timerInterval: ReturnType<typeof setInterval> | null = null;

	$effect(() => {
		if (actionRequired) {
			raiseAmount = actionRequired.min_raise;
			timeLeft = actionRequired.timeout_seconds;
			if (timerInterval) clearInterval(timerInterval);
			timerInterval = setInterval(() => {
				timeLeft = Math.max(0, timeLeft - 1);
				if (timeLeft <= 10 && timeLeft > 0) playTimerTick();
			}, 1000);
		} else {
			if (timerInterval) {
				clearInterval(timerInterval);
				timerInterval = null;
			}
		}
		return () => {
			if (timerInterval) clearInterval(timerInterval);
		};
	});

	const canRaise = $derived(actionRequired?.options.includes('raise') ?? false);
	const callAmount = $derived(actionRequired?.call_amount ?? 0);
	const timerPct = $derived(actionRequired ? (timeLeft / actionRequired.timeout_seconds) * 100 : 0);
	const urgent = $derived(timeLeft <= 10);
</script>

<div class="action-bar" class:my-turn={isMyTurn && actionRequired}>
	{#if isMyTurn && actionRequired}
		<!-- Turn timer -->
		<div class="timer-row">
			<div class="timer-track">
				<div class="timer-fill" class:urgent style="width: {timerPct}%"></div>
			</div>
			<span class="timer-num" class:urgent>{timeLeft}s</span>
		</div>

		<!-- Action buttons -->
		<div class="buttons">
			<button class="btn fold" onclick={() => onAction('fold')}>
				<span class="btn-label">Fold</span>
			</button>

			<button class="btn call" onclick={() => onAction('call')}>
				<span class="btn-label">{callAmount === 0 ? 'Check' : 'Call'}</span>
				{#if callAmount > 0}
					<span class="btn-amount">{callAmount.toLocaleString()}</span>
				{/if}
			</button>

			{#if canRaise}
				<div class="raise-group">
					<button class="btn raise" onclick={() => onAction('raise', raiseAmount)}>
						<span class="btn-label">Raise</span>
						<span class="btn-amount">{raiseAmount.toLocaleString()}</span>
					</button>
					<input
						type="number"
						bind:value={raiseAmount}
						min={actionRequired.min_raise}
						max={actionRequired.max_raise}
						step={actionRequired.min_raise}
						class="raise-input"
					/>
				</div>
			{/if}

			<button class="btn allin" onclick={() => onAction('all_in')}>
				<span class="btn-label">All In</span>
			</button>
		</div>
	{:else}
		<div class="waiting">
			<span class="waiting-dots">
				<span></span><span></span><span></span>
			</span>
			<span class="waiting-text">Waiting for other players</span>
		</div>
	{/if}
</div>

<style>
	.action-bar {
		height: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 0 16px;
		gap: 8px;
		border-top: 1px solid rgba(201, 168, 76, 0.06);
		background: rgba(6, 6, 10, 0.96);
	}

	.timer-row {
		display: flex;
		align-items: center;
		gap: 8px;
		width: 100%;
		max-width: 480px;
	}

	.timer-track {
		flex: 1;
		height: 2px;
		background: rgba(255, 255, 255, 0.06);
		border-radius: 1px;
		overflow: hidden;
	}

	.timer-fill {
		height: 100%;
		background: var(--gold, #c9a84c);
		border-radius: 1px;
		transition: width 1s linear, background 0.4s;
	}

	.timer-fill.urgent { background: #dc2626; }

	.timer-num {
		font-family: var(--font-mono, monospace);
		font-size: 10px;
		font-weight: 600;
		color: var(--gold, #c9a84c);
		min-width: 24px;
		text-align: right;
		transition: color 0.4s;
	}

	.timer-num.urgent { color: #dc2626; }

	.buttons {
		display: flex;
		gap: 6px;
		align-items: stretch;
	}

	.btn {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		padding: 8px 20px;
		border-radius: 4px;
		cursor: pointer;
		border: 1px solid transparent;
		transition: background 0.15s, border-color 0.15s, box-shadow 0.15s;
		background: transparent;
		gap: 1px;
		min-width: 72px;
	}

	.btn-label {
		font-size: 11px;
		font-weight: 600;
		letter-spacing: 0.1em;
		text-transform: uppercase;
	}

	.btn-amount {
		font-family: var(--font-mono, monospace);
		font-size: 10px;
		opacity: 0.75;
		letter-spacing: 0.04em;
	}

	.fold {
		border-color: rgba(220, 38, 38, 0.25);
		color: #f87171;
	}
	.fold:hover {
		border-color: rgba(220, 38, 38, 0.6);
		background: rgba(220, 38, 38, 0.06);
	}

	.call {
		border-color: rgba(255, 255, 255, 0.12);
		color: var(--text, #e8dfc8);
	}
	.call:hover {
		border-color: rgba(255, 255, 255, 0.28);
		background: rgba(255, 255, 255, 0.04);
	}

	.raise-group {
		display: flex;
		gap: 4px;
		align-items: stretch;
	}

	.raise {
		border-color: rgba(201, 168, 76, 0.3);
		color: var(--gold, #c9a84c);
	}
	.raise:hover {
		border-color: rgba(201, 168, 76, 0.65);
		background: rgba(201, 168, 76, 0.06);
		box-shadow: 0 0 16px rgba(201, 168, 76, 0.1);
	}

	.raise-input {
		width: 64px;
		background: rgba(201, 168, 76, 0.04);
		border: 1px solid rgba(201, 168, 76, 0.15);
		border-radius: 4px;
		padding: 6px;
		color: var(--gold, #c9a84c);
		font-family: var(--font-mono, monospace);
		font-size: 11px;
		text-align: center;
		outline: none;
	}

	.raise-input:focus {
		border-color: rgba(201, 168, 76, 0.4);
	}

	.allin {
		border-color: rgba(234, 108, 20, 0.25);
		color: #fb923c;
	}
	.allin:hover {
		border-color: rgba(234, 108, 20, 0.6);
		background: rgba(234, 108, 20, 0.06);
	}

	.waiting {
		display: flex;
		align-items: center;
		gap: 10px;
		color: var(--text-muted, rgba(232, 223, 200, 0.2));
		font-size: 0.75rem;
		letter-spacing: 0.12em;
		text-transform: uppercase;
	}

	.waiting-dots {
		display: flex;
		gap: 4px;
	}

	.waiting-dots span {
		width: 3px;
		height: 3px;
		border-radius: 50%;
		background: currentColor;
		animation: blink 1.4s ease-in-out infinite;
	}

	.waiting-dots span:nth-child(2) { animation-delay: 0.2s; }
	.waiting-dots span:nth-child(3) { animation-delay: 0.4s; }

	@keyframes blink {
		0%, 80%, 100% { opacity: 0.2; }
		40%            { opacity: 0.7; }
	}
</style>
