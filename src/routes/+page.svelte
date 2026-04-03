<script lang="ts">
  import { goto } from '$app/navigation';

  let loading = $state(false);
  let error = $state('');

  async function createTable() {
    loading = true;
    error = '';
    try {
      const res = await fetch('/api/rooms', { method: 'POST' });
      if (!res.ok) throw new Error('Server error');
      const { room_id } = await res.json();
      await goto(`/room/${room_id}`);
    } catch (e) {
      error = 'Could not create table. Is the server running?';
      loading = false;
    }
  }
</script>

<main>
  <div class="bg-mesh"></div>

  <div class="hero">
    <div class="logo-mark">♠</div>
    <h1>Web Poker</h1>
    <p class="subtitle">Texas Hold'em · Tournament · No registration</p>

    <button onclick={createTable} disabled={loading} class="create-btn">
      {#if loading}
        <span class="spinner"></span> Creating…
      {:else}
        Create Table
      {/if}
    </button>

    {#if error}
      <p class="error">{error}</p>
    {/if}

    <p class="hint">Create a table → share the link → play with friends</p>
  </div>
</main>

<style>
  main {
    height: 100dvh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
  }

  .bg-mesh {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(ellipse 80% 60% at 50% 50%, rgba(13, 29, 12, 0.8) 0%, transparent 70%),
      radial-gradient(ellipse 40% 40% at 20% 80%, rgba(28, 14, 4, 0.4) 0%, transparent 60%),
      radial-gradient(ellipse 40% 40% at 80% 20%, rgba(28, 14, 4, 0.3) 0%, transparent 60%);
    pointer-events: none;
  }

  .hero {
    position: relative;
    text-align: center;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
    animation: rise 0.6s ease-out both;
  }

  .logo-mark {
    font-size: 3rem;
    color: var(--gold);
    opacity: 0.6;
    line-height: 1;
    font-family: var(--font-display);
  }

  h1 {
    font-family: var(--font-display);
    font-size: clamp(2.5rem, 6vw, 4.5rem);
    font-weight: 700;
    letter-spacing: 0.12em;
    color: var(--text);
    text-transform: uppercase;
    line-height: 1;
  }

  .subtitle {
    color: var(--text-dim);
    font-size: 0.75rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    font-weight: 300;
  }

  .create-btn {
    margin-top: 1.5rem;
    padding: 0.9rem 3rem;
    background: transparent;
    border: 1px solid var(--gold);
    border-radius: 3px;
    color: var(--gold);
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    cursor: pointer;
    transition: background 0.2s, box-shadow 0.2s, color 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .create-btn:hover:not(:disabled) {
    background: var(--gold-faint);
    box-shadow: 0 0 24px var(--gold-glow);
    color: #e8c96a;
  }

  .create-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .spinner {
    width: 12px;
    height: 12px;
    border: 1.5px solid rgba(201, 168, 76, 0.3);
    border-top-color: var(--gold);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    display: inline-block;
  }

  .hint {
    color: var(--text-muted);
    font-size: 0.75rem;
    letter-spacing: 0.05em;
  }

  .error {
    color: #f87171;
    font-size: 0.8rem;
    letter-spacing: 0.03em;
  }

  @keyframes rise {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  @keyframes spin {
    to { transform: rotate(360deg); }
  }
</style>
