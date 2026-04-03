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
    myCards,
  }: {
    players: PlayerData[];
    communityCards: CardData[];
    pot: number;
    actionSid: string | null;
    mySid: string | null;
    myCards: CardData[];
  } = $props();

  // Positions around the ellipse (% from top-left of container)
  // Arranged for up to 9 seats: bottom-center is always "my seat"
  const SEAT_POSITIONS = [
    { top: '80%', left: '50%' },  // 0 — bottom center (me if seat 0)
    { top: '65%', left: '18%' },  // 1 — bottom left
    { top: '35%', left: '5%'  },  // 2 — middle left
    { top: '8%',  left: '20%' },  // 3 — top left
    { top: '5%',  left: '50%' },  // 4 — top center
    { top: '8%',  left: '78%' },  // 5 — top right
    { top: '35%', left: '92%' },  // 6 — middle right
    { top: '65%', left: '80%' },  // 7 — bottom right
    { top: '50%', left: '50%' },  // 8 — emergency 9th (center, rare)
  ];

  // Rotate seats so current player appears at bottom
  const myIndex = $derived(players.findIndex(p => p.sid === mySid));

  const rotatedPlayers = $derived(
    players.map((p, i) => {
      const rotatedSeat = myIndex >= 0
        ? (p.seat - myIndex + players.length) % players.length
        : p.seat;
      return { ...p, displaySeat: rotatedSeat };
    })
  );
</script>

<div class="table-container">
  <!-- Felt -->
  <div class="felt">
    <!-- Community cards + pot -->
    <div class="center">
      <div class="pot-label">POT</div>
      <div class="pot-amount">{pot.toLocaleString()}</div>
      <div class="community">
        {#each communityCards as card, i (i)}
          <Card {card} />
        {/each}
        {#each { length: 5 - communityCards.length } as _, i}
          <Card card={null} faceDown />
        {/each}
      </div>
    </div>

    <!-- Player seats -->
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

<style>
  .table-container {
    width: 100%;
    position: relative;
    padding-bottom: 48%;
  }

  .felt {
    position: absolute;
    inset: 0;
    background: radial-gradient(ellipse at center, #0f1f0f 0%, #070f07 100%);
    border-radius: 50%;
    border: 3px solid #1a2e1a;
    box-shadow:
      0 0 0 6px #0a0a12,
      0 0 60px rgba(0, 0, 0, 0.9),
      inset 0 2px 30px rgba(0, 0, 0, 0.5);
  }

  .center {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .pot-label {
    font-size: 9px;
    letter-spacing: 0.2em;
    color: #ffffff35;
    text-transform: uppercase;
  }

  .pot-amount {
    font-size: 16px;
    font-weight: 700;
    color: #e8c96a;
    letter-spacing: 0.05em;
  }

  .community {
    display: flex;
    gap: 5px;
    margin-top: 4px;
  }

  .seat-anchor {
    position: absolute;
  }
</style>
