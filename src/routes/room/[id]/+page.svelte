<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { connectSocket, disconnectSocket } from '$lib/socket';
  import { gameStore } from '$lib/store.svelte';
  import LobbyWaiting from '$lib/components/LobbyWaiting.svelte';
  import Table from '$lib/components/Table.svelte';
  import ActionBar from '$lib/components/ActionBar.svelte';
  import BlindTimer from '$lib/components/BlindTimer.svelte';
  import WinnerScreen from '$lib/components/WinnerScreen.svelte';
  import type { RoomState, ActionRequired, HandResult } from '$lib/types';

  const roomId = $derived($page.params.id ?? '');

  let name = $state('');
  let nameSubmitted = $state(false);
  let lastHandResult = $state<HandResult | null>(null);
  let showHandResult = $state(false);

  // Blind schedule durations (must match BLIND_SCHEDULE in tournament.py)
  const BLIND_DURATIONS = [180, 180, 120, 120, 120, 120, 120, 120];

  onMount(() => {
    const socket = connectSocket();
    gameStore.mySid = socket.id ?? null;

    socket.on('connect', () => {
      gameStore.mySid = socket.id ?? null;
    });

    socket.on('room_state', (state: RoomState) => {
      gameStore.roomState = state;
    });

    socket.on('action_required', (data: ActionRequired) => {
      gameStore.actionRequired = data;
    });

    socket.on('hand_result', (data: HandResult) => {
      lastHandResult = data;
      showHandResult = true;
      gameStore.actionRequired = null;
      setTimeout(() => { showHandResult = false; }, 3000);
    });

    socket.on('eliminated', ({ player_name }: { player_name: string }) => {
      gameStore.eliminatedName = player_name;
      setTimeout(() => { gameStore.eliminatedName = null; }, 3000);
    });

    socket.on('winner', ({ player_name }: { player_name: string }) => {
      gameStore.winnerName = player_name;
    });

    socket.on('blind_up', () => {
      // room_state broadcast follows immediately
    });

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
    const socket = connectSocket();
    socket.emit('join_room', { room_id: roomId, name: name.trim() });
  }

  function handleReady(ready: boolean) {
    const socket = connectSocket();
    socket.emit('set_ready', { ready });
  }

  function handleAction(type: string, amount?: number) {
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

<main>
  {#if !nameSubmitted}
    <!-- Name entry screen -->
    <div class="name-entry">
      <h1>Join Table</h1>
      <p class="room-code">Room · <span>{roomId.toUpperCase()}</span></p>
      <form onsubmit={(e) => { e.preventDefault(); submitName(); }}>
        <input
          bind:value={name}
          placeholder="Your name"
          maxlength="20"
          autofocus
          class="name-input"
        />
        <button type="submit" class="join-btn" disabled={!name.trim()}>Join</button>
      </form>
    </div>

  {:else if gameStore.error}
    <div class="error-screen">
      <p>{gameStore.error}</p>
      <button onclick={() => gameStore.error = null}>Back</button>
    </div>

  {:else if !roomState}
    <div class="loading">Connecting…</div>

  {:else if roomState.state === 'waiting'}
    <div class="page">
      <LobbyWaiting
        players={roomState.players}
        mySid={gameStore.mySid}
        {roomId}
        onReady={handleReady}
      />
    </div>

  {:else if roomState.state === 'playing'}
    <div class="game-page">
      <!-- Top bar -->
      <div class="top-bar">
        <span class="room-code-sm">{roomId.toUpperCase()}</span>
        <BlindTimer
          blindLevel={roomState.blind_level}
          sb={roomState.blinds.sb}
          bb={roomState.blinds.bb}
          secondsUntilNext={roomState.seconds_until_next_blind}
          totalDuration={blindDuration}
        />
      </div>

      <!-- Table -->
      <div class="table-wrap">
        <Table
          players={roomState.players}
          communityCards={roomState.community_cards}
          pot={roomState.pot}
          actionSid={roomState.action_sid}
          mySid={gameStore.mySid}
          myCards={roomState.my_cards}
        />
      </div>

      <!-- Action bar -->
      <div class="action-wrap">
        <ActionBar
          actionRequired={gameStore.actionRequired}
          isMyTurn={gameStore.isMyTurn}
          onAction={handleAction}
        />
      </div>

      <!-- Toasts -->
      {#if showHandResult && lastHandResult}
        <div class="toast">
          <strong>{lastHandResult.winner_name}</strong> wins {lastHandResult.amount.toLocaleString()}
          {#if lastHandResult.hand_name !== 'Uncontested'}
            with <em>{lastHandResult.hand_name}</em>
          {/if}
        </div>
      {/if}

      {#if gameStore.eliminatedName}
        <div class="toast eliminated">{gameStore.eliminatedName} is eliminated</div>
      {/if}
    </div>

  {:else if roomState.state === 'finished'}
    <WinnerScreen
      winnerName={gameStore.winnerName ?? 'Winner'}
      onNewGame={handleNewGame}
    />
  {/if}
</main>

<style>
  main {
    min-height: 100vh;
    background: #080810;
    color: #fff;
    font-family: system-ui, sans-serif;
  }

  .name-entry {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    gap: 1.25rem;
  }

  h1 {
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
  }

  .room-code span { color: #e8c96a; }
  .room-code { color: #555; font-size: 0.8rem; letter-spacing: 0.2em; text-transform: uppercase; }

  form { display: flex; gap: 0.5rem; }

  .name-input {
    padding: 0.65rem 1rem;
    background: #0d0d1a;
    border: 1px solid #ffffff20;
    border-radius: 7px;
    color: #fff;
    font-size: 1rem;
    outline: none;
    width: 220px;
  }

  .name-input:focus { border-color: #ffffff40; }

  .join-btn {
    padding: 0.65rem 1.5rem;
    background: #1a3a1a;
    border: 1px solid rgba(74, 222, 128, 0.3);
    border-radius: 7px;
    color: #4ade80;
    font-weight: 600;
    cursor: pointer;
  }

  .join-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .loading, .error-screen {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    color: #555;
  }

  .page {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
  }

  .game-page {
    display: flex;
    flex-direction: column;
    gap: 12px;
    padding: 12px;
    max-width: 900px;
    margin: 0 auto;
  }

  .top-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .room-code-sm {
    font-size: 10px;
    letter-spacing: 0.2em;
    color: #ffffff30;
  }

  .table-wrap { width: 100%; }

  .action-wrap { width: 100%; }

  .toast {
    position: fixed;
    bottom: 80px;
    left: 50%;
    transform: translateX(-50%);
    background: #1a1a2e;
    border: 1px solid #ffffff20;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 0.9rem;
    color: #e8c96a;
    white-space: nowrap;
    pointer-events: none;
    animation: fadein 0.3s ease-out;
  }

  .toast.eliminated { color: #f87171; }

  @keyframes fadein {
    from { opacity: 0; transform: translateX(-50%) translateY(10px); }
    to   { opacity: 1; transform: translateX(-50%) translateY(0); }
  }
</style>
