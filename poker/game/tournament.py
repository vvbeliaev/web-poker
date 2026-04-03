from __future__ import annotations
import time
import secrets
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from poker.game.deck import Card

STARTING_CHIPS = 10_000
DISCONNECT_FOLD_SECONDS = 30

# (small_blind, big_blind, duration_seconds)
BLIND_SCHEDULE: list[tuple[int, int, int]] = [
    (25,   50,   180),
    (50,   100,  180),
    (100,  200,  120),
    (200,  400,  120),
    (300,  600,  120),
    (500,  1000, 120),
    (750,  1500, 120),
    (1000, 2000, 120),
]


class PlayerStatus(Enum):
    ACTIVE = 'active'
    FOLDED = 'folded'
    ALL_IN = 'all_in'
    ELIMINATED = 'eliminated'


class RoomState(Enum):
    WAITING = 'waiting'
    PLAYING = 'playing'
    FINISHED = 'finished'


ALLOWED_AVATARS = frozenset([
    '🦊', '🐼', '🦁', '🐯', '🐻', '🐨', '🐸', '🦝', '🦄', '🐺', '🦅', '🐙',
    '👁️', '👅', '👃', '👂', '🦷', '🦴', '💀', '👾', '🤡', '👺', '👹', '💩',
    '🫠', '🥴', '🤪', '😵', '🫣', '🧠', '👁️‍🗨️', '🫀', '🫁', '🦶', '👻', '🙈',
])
DEFAULT_AVATAR = '🦊'


@dataclass
class Player:
    sid: str
    name: str
    seat: int
    avatar: str = DEFAULT_AVATAR
    chips: int = STARTING_CHIPS
    hole_cards: list[Card] = field(default_factory=list)
    ready: bool = False
    status: PlayerStatus = PlayerStatus.ACTIVE
    total_bet_in_hand: int = 0
    street_bet: int = 0
    disconnected_at: Optional[float] = None
    player_id: str = ''  # Stable client UUID for reconnection

    def to_dict(self, include_cards: bool = False) -> dict:
        return {
            'sid': self.sid,
            'name': self.name,
            'seat': self.seat,
            'avatar': self.avatar,
            'chips': self.chips,
            'ready': self.ready,
            'status': self.status.value,
            'street_bet': self.street_bet,
            'hole_cards': [c.to_dict() for c in self.hole_cards] if include_cards else None,
        }


@dataclass
class Room:
    id: str = field(default_factory=lambda: secrets.token_hex(4))
    state: RoomState = RoomState.WAITING
    players: list[Player] = field(default_factory=list)
    community_cards: list[Card] = field(default_factory=list)
    pot: int = 0
    hand_phase: str = 'between_hands'
    dealer_pos: int = 0
    action_sid: Optional[str] = None
    current_bet: int = 0
    blind_level: int = 0
    blind_timer_start: float = field(default_factory=time.time)
    current_hand: Optional[object] = None  # Hand instance

    def add_player(self, sid: str, name: str, avatar: str = DEFAULT_AVATAR, player_id: str = '') -> Player:
        seat = len(self.players)
        validated_avatar = avatar if avatar in ALLOWED_AVATARS else DEFAULT_AVATAR
        player = Player(sid=sid, name=name, seat=seat, avatar=validated_avatar, player_id=player_id)
        self.players.append(player)
        return player

    def remove_player(self, sid: str) -> None:
        self.players = [p for p in self.players if p.sid != sid]
        for i, p in enumerate(self.players):
            p.seat = i

    def get_player(self, sid: str) -> Optional[Player]:
        return next((p for p in self.players if p.sid == sid), None)

    def should_start(self) -> bool:
        active = [p for p in self.players if p.status != PlayerStatus.ELIMINATED]
        return len(active) >= 2 and all(p.ready for p in active)

    def current_blinds(self) -> tuple[int, int]:
        level = min(self.blind_level, len(BLIND_SCHEDULE) - 1)
        sb, bb, _ = BLIND_SCHEDULE[level]
        return sb, bb

    def blind_level_duration(self) -> int:
        level = min(self.blind_level, len(BLIND_SCHEDULE) - 1)
        return BLIND_SCHEDULE[level][2]

    def seconds_until_next_blind(self) -> float:
        elapsed = time.time() - self.blind_timer_start
        return max(0.0, self.blind_level_duration() - elapsed)

    def active_players(self) -> list[Player]:
        return [p for p in self.players
                if p.status not in (PlayerStatus.ELIMINATED, PlayerStatus.FOLDED)]

    def public_state(self) -> dict:
        return {
            'room_id': self.id,
            'state': self.state.value,
            'players': [p.to_dict(include_cards=False) for p in self.players],
            'community_cards': [c.to_dict() for c in self.community_cards],
            'pot': self.pot,
            'hand_phase': self.hand_phase,
            'action_sid': self.action_sid,
            'current_bet': self.current_bet,
            'blind_level': self.blind_level,
            'blinds': {'sb': self.current_blinds()[0], 'bb': self.current_blinds()[1]},
            'seconds_until_next_blind': self.seconds_until_next_blind(),
        }

    def private_state_for(self, sid: str) -> dict:
        player = self.get_player(sid)
        return {
            **self.public_state(),
            'my_cards': [c.to_dict() for c in player.hole_cards] if player else [],
        }
