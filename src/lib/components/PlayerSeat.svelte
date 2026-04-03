<!-- src/lib/components/PlayerSeat.svelte -->
<script lang="ts">
  import Card from './Card.svelte';
  import type { PlayerData, CardData } from '$lib/types';

  let {
    player,
    isActive,
    myCards = null,
    isMe = false,
  }: {
    player: PlayerData;
    isActive: boolean;
    myCards?: CardData[] | null;
    isMe?: boolean;
  } = $props();

  const statusColor: Record<string, string> = {
    active: '#aaa',
    folded: '#f87171',
    all_in: '#fb923c',
    eliminated: '#444',
  };

  const displayCards = $derived(isMe && myCards ? myCards : null);
</script>

<div
  class="seat"
  class:active={isActive}
  class:eliminated={player.status === 'eliminated'}
  class:me={isMe}
>
  <div class="cards-row">
    {#if displayCards}
      {#each displayCards as card}
        <Card {card} small />
      {/each}
    {:else if player.status !== 'eliminated' && player.status !== 'folded'}
      <Card card={null} faceDown small />
      <Card card={null} faceDown small />
    {/if}
  </div>

  <div class="info">
    <span class="name">{player.name}{isMe ? ' ★' : ''}</span>
    <span class="chips">{player.chips.toLocaleString()}</span>
  </div>

  {#if player.street_bet > 0}
    <div class="bet">Bet {player.street_bet}</div>
  {/if}

  <div class="status-dot" style="color: {statusColor[player.status] ?? '#aaa'}">
    {player.status === 'all_in' ? 'ALL IN' : player.status === 'folded' ? 'FOLD' : ''}
  </div>
</div>

<style>
  .seat {
    background: #0d0d1a;
    border: 1px solid #ffffff15;
    border-radius: 10px;
    padding: 6px 10px;
    min-width: 80px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 3px;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .seat.active {
    border-color: rgba(74, 222, 128, 0.5);
    box-shadow: 0 0 12px rgba(74, 222, 128, 0.15);
  }

  .seat.me { border-color: rgba(232, 201, 106, 0.25); }
  .seat.eliminated { opacity: 0.35; }

  .cards-row {
    display: flex;
    gap: 3px;
  }

  .info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1px;
  }

  .name {
    font-size: 11px;
    color: #ccc;
    white-space: nowrap;
    max-width: 80px;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .chips {
    font-size: 11px;
    color: #e8c96a;
    font-weight: 600;
  }

  .bet {
    font-size: 9px;
    color: #fb923c;
    letter-spacing: 0.05em;
  }

  .status-dot {
    font-size: 8px;
    font-weight: 700;
    letter-spacing: 0.08em;
    min-height: 10px;
  }
</style>
