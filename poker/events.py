# poker/events.py
from __future__ import annotations
import asyncio
import time
from typing import Any

from poker.server import sio, rooms
from poker.game.tournament import Room, Player, PlayerStatus, RoomState, BLIND_SCHEDULE
from poker.game.engine import Hand


async def _broadcast_room_state(room: Room) -> None:
    """Send private state (with hole cards) to each player individually."""
    for player in room.players:
        await sio.emit('room_state', room.private_state_for(player.sid), to=player.sid)


async def _start_new_hand(room: Room) -> None:
    """Deal a new hand and notify players."""
    eligible = [p for p in room.players if p.status != PlayerStatus.ELIMINATED]
    if len(eligible) < 2:
        return

    sb, bb = room.current_blinds()
    hand = Hand(
        players=eligible,
        dealer_pos=room.dealer_pos % len(eligible),
        small_blind=sb,
        big_blind=bb,
    )
    hand.deal()
    room.current_hand = hand
    room.hand_phase = hand.phase
    room.community_cards = hand.community_cards
    room.pot = sum(p.total_bet_in_hand for p in eligible)
    room.current_bet = hand.current_bet

    current = hand.current_player()
    room.action_sid = current.sid if current else None

    await _broadcast_room_state(room)

    if current:
        await sio.emit('action_required', {
            'player_sid': current.sid,
            'options': ['fold', 'call', 'raise', 'all_in'],
            'call_amount': max(0, hand.current_bet - current.street_bet),
            'min_raise': hand.current_bet + bb,
            'max_raise': current.chips + current.street_bet,
        }, room=room.id)


async def _blind_timer_loop(room_id: str) -> None:
    """Background task: advance blind level on schedule."""
    while True:
        room = rooms.get(room_id)
        if not room or room.state != RoomState.PLAYING:
            break
        wait = room.seconds_until_next_blind()
        await asyncio.sleep(max(1.0, wait))
        room = rooms.get(room_id)
        if not room or room.state != RoomState.PLAYING:
            break
        if room.seconds_until_next_blind() <= 1:
            room.blind_level += 1
            room.blind_timer_start = time.time()
            if room.blind_level >= len(BLIND_SCHEDULE) - 1:
                # Already at max level, no more increases needed
                sb, bb = room.current_blinds()
                await sio.emit('blind_up', {'level': room.blind_level, 'sb': sb, 'bb': bb},
                               room=room_id)
                await _broadcast_room_state(room)
                break
            sb, bb = room.current_blinds()
            await sio.emit('blind_up', {'level': room.blind_level, 'sb': sb, 'bb': bb},
                           room=room_id)
            await _broadcast_room_state(room)


async def _auto_fold_disconnected(sid: str, room_id: str) -> None:
    """Auto-fold a disconnected player after DISCONNECT_FOLD_SECONDS."""
    from poker.game.tournament import DISCONNECT_FOLD_SECONDS
    await asyncio.sleep(DISCONNECT_FOLD_SECONDS)
    room = rooms.get(room_id)
    if not room or room.state != RoomState.PLAYING:
        return
    player = room.get_player(sid)
    if not player or player.disconnected_at is None:
        return  # reconnected or already eliminated
    # Only act if it's their turn
    if room.action_sid == sid and room.current_hand:
        result = room.current_hand.apply_action(sid, 'fold')
        room.hand_phase = room.current_hand.phase
        room.community_cards = room.current_hand.community_cards
        room.current_bet = room.current_hand.current_bet
        if result:
            for winner in result['winners']:
                await sio.emit('hand_result', {
                    'winner_sid': winner['sid'],
                    'winner_name': winner['name'],
                    'amount': winner['amount'],
                    'hand_name': winner['hand_name'],
                    'community_cards': result['community_cards'],
                }, room=room_id)
            alive = [p for p in room.players if p.status != PlayerStatus.ELIMINATED]
            if len(alive) <= 1:
                if alive:
                    room.state = RoomState.FINISHED
                    await sio.emit('winner', {'player_name': alive[0].name,
                                              'player_sid': alive[0].sid}, room=room_id)
                await _broadcast_room_state(room)
                return
            room.dealer_pos = (room.dealer_pos + 1) % len(alive)
            room.current_hand = None
            await _broadcast_room_state(room)
            await asyncio.sleep(3)
            await _start_new_hand(room)
        else:
            current = room.current_hand.current_player()
            room.action_sid = current.sid if current else None
            await _broadcast_room_state(room)


@sio.event
async def connect(sid: str, environ: dict, auth: Any = None) -> None:
    pass  # Connection accepted; player must join_room


@sio.event
async def disconnect(sid: str) -> None:
    for room in rooms.values():
        player = room.get_player(sid)
        if player:
            if room.state == RoomState.WAITING:
                room.remove_player(sid)
                await _broadcast_room_state(room)
            else:
                player.disconnected_at = time.time()
                asyncio.create_task(_auto_fold_disconnected(sid, room.id))
            break


@sio.event
async def join_room(sid: str, data: dict) -> None:
    room_id: str = data.get('room_id', '')
    name: str = (data.get('name', 'Player') or 'Player')[:20].strip() or 'Player'

    room = rooms.get(room_id)
    if not room:
        await sio.emit('error', {'message': 'Room not found'}, to=sid)
        return

    if room.state == RoomState.FINISHED:
        await sio.emit('error', {'message': 'Game has ended'}, to=sid)
        return

    if room.state == RoomState.PLAYING:
        existing = room.get_player(sid)
        if not existing:
            await sio.emit('error', {'message': 'Game in progress'}, to=sid)
            return
    elif len(room.players) >= 9:
        await sio.emit('error', {'message': 'Table is full'}, to=sid)
        return

    if not room.get_player(sid):
        room.add_player(sid=sid, name=name)

    await sio.enter_room(sid, room_id)
    await _broadcast_room_state(room)


@sio.event
async def set_ready(sid: str, data: dict) -> None:
    ready: bool = bool(data.get('ready', True))

    for room in rooms.values():
        player = room.get_player(sid)
        if player and room.state == RoomState.WAITING:
            player.ready = ready
            await _broadcast_room_state(room)

            if room.should_start():
                room.state = RoomState.PLAYING
                room.blind_timer_start = time.time()
                for p in room.players:
                    p.status = PlayerStatus.ACTIVE
                asyncio.create_task(_blind_timer_loop(room.id))
                await _start_new_hand(room)
            return


@sio.event
async def action(sid: str, data: dict) -> None:
    action_type: str = data.get('type', '')
    try:
        amount: int = int(data.get('amount') or 0)
    except (ValueError, TypeError):
        amount = 0

    room = next((r for r in rooms.values() if r.get_player(sid)), None)
    if not room or room.state != RoomState.PLAYING or not room.current_hand:
        return

    hand: Hand = room.current_hand
    if room.action_sid != sid:
        return  # Not your turn

    result = hand.apply_action(sid, action_type, amount)

    # Sync room state from hand
    room.community_cards = hand.community_cards
    room.current_bet = hand.current_bet
    room.hand_phase = hand.phase
    room.pot = sum(p.total_bet_in_hand for p in hand.players)

    if result:
        # Hand is over — announce results
        for winner in result['winners']:
            await sio.emit('hand_result', {
                'winner_sid': winner['sid'],
                'winner_name': winner['name'],
                'amount': winner['amount'],
                'hand_name': winner['hand_name'],
                'community_cards': result['community_cards'],
            }, room=room.id)

        # Eliminate players with 0 chips
        for p in room.players:
            if p.chips == 0 and p.status != PlayerStatus.ELIMINATED:
                p.status = PlayerStatus.ELIMINATED
                await sio.emit('eliminated', {'player_name': p.name}, room=room.id)

        # Check tournament winner
        alive = [p for p in room.players if p.status != PlayerStatus.ELIMINATED]
        if len(alive) == 1:
            room.state = RoomState.FINISHED
            await sio.emit('winner', {
                'player_name': alive[0].name,
                'player_sid': alive[0].sid,
            }, room=room.id)
            await _broadcast_room_state(room)
            return

        # Rotate dealer and start next hand after a pause
        alive_count = len(alive)
        room.dealer_pos = (room.dealer_pos + 1) % alive_count
        room.current_hand = None
        await _broadcast_room_state(room)
        await asyncio.sleep(3)
        await _start_new_hand(room)
    else:
        # Hand continues — update whose turn it is
        current = hand.current_player()
        room.action_sid = current.sid if current else None
        sb, bb = room.current_blinds()
        await _broadcast_room_state(room)
        if current:
            await sio.emit('action_required', {
                'player_sid': current.sid,
                'options': ['fold', 'call', 'raise', 'all_in'],
                'call_amount': max(0, hand.current_bet - current.street_bet),
                'min_raise': hand.current_bet + bb,
                'max_raise': current.chips + current.street_bet,
            }, room=room.id)
