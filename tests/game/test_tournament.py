import pytest
import time
from poker.game.tournament import Room, Player, PlayerStatus, RoomState


def make_room() -> Room:
    return Room()


def add_player(room: Room, sid: str, name: str) -> Player:
    return room.add_player(sid=sid, name=name)


def test_room_starts_in_waiting_state():
    room = make_room()
    assert room.state == RoomState.WAITING


def test_add_player_assigns_seat():
    room = make_room()
    p = add_player(room, 'sid1', 'Alice')
    assert p.seat == 0
    p2 = add_player(room, 'sid2', 'Bob')
    assert p2.seat == 1


def test_cannot_start_with_one_player():
    room = make_room()
    add_player(room, 'sid1', 'Alice')
    room.players[0].ready = True
    assert not room.should_start()


def test_starts_when_all_ready():
    room = make_room()
    add_player(room, 'sid1', 'Alice')
    add_player(room, 'sid2', 'Bob')
    room.players[0].ready = True
    assert not room.should_start()
    room.players[1].ready = True
    assert room.should_start()


def test_remove_player_in_lobby():
    room = make_room()
    add_player(room, 'sid1', 'Alice')
    add_player(room, 'sid2', 'Bob')
    room.remove_player('sid1')
    assert len(room.players) == 1
    assert room.players[0].sid == 'sid2'


def test_blind_schedule_returns_correct_level():
    room = make_room()
    sb, bb = room.current_blinds()
    assert sb == 25
    assert bb == 50


def test_blind_level_advances():
    room = make_room()
    room.blind_level = 1
    sb, bb = room.current_blinds()
    assert sb == 50
    assert bb == 100


def test_room_public_state_hides_hole_cards():
    room = make_room()
    p = add_player(room, 'sid1', 'Alice')
    from poker.game.deck import Card
    p.hole_cards = [Card(14, 'h'), Card(13, 's')]
    state = room.public_state()
    player_data = next(pd for pd in state['players'] if pd['sid'] == 'sid1')
    assert player_data['hole_cards'] is None  # hidden from public state


def test_room_private_state_shows_hole_cards():
    room = make_room()
    p = add_player(room, 'sid1', 'Alice')
    from poker.game.deck import Card
    p.hole_cards = [Card(14, 'h'), Card(13, 's')]
    state = room.private_state_for('sid1')
    assert len(state['my_cards']) == 2
