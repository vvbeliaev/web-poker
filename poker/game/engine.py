from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from poker.game.deck import Card, Deck
from poker.game.evaluator import best_hand_score, hand_name


@dataclass
class Pot:
    amount: int
    eligible_sids: list[str]


def calculate_pots(contribs: list[dict]) -> list[Pot]:
    """
    contribs: list of {'sid': str, 'total_bet': int, 'folded': bool}
    Returns main pot + side pots.
    """
    sorted_c = sorted(contribs, key=lambda c: c['total_bet'])
    pots: list[Pot] = []
    processed = 0

    for i, entry in enumerate(sorted_c):
        level = entry['total_bet']
        if level <= processed:
            continue

        contribution_per_player = level - processed
        pot_amount = 0
        eligible: list[str] = []

        for c in contribs:
            if c['total_bet'] > processed:
                pot_amount += min(c['total_bet'] - processed, contribution_per_player)
                if not c['folded'] and c['total_bet'] >= level:
                    eligible.append(c['sid'])

        if pot_amount > 0 and eligible:
            pots.append(Pot(amount=pot_amount, eligible_sids=eligible))

        processed = level

    return pots


@dataclass
class Hand:
    """Manages one complete hand from deal to pot award."""
    players: list          # list[Player] — only non-eliminated players
    dealer_pos: int        # index into players list
    small_blind: int
    big_blind: int

    community_cards: list[Card] = field(default_factory=list)
    phase: str = 'preflop'   # preflop|flop|turn|river|showdown
    current_bet: int = 0
    _deck: Deck = field(default_factory=Deck)
    _action_idx: int = 0
    _num_to_act: int = 0

    def deal(self) -> None:
        """Post blinds and deal hole cards."""
        from poker.game.tournament import PlayerStatus
        n = len(self.players)
        # Reset per-hand state
        for p in self.players:
            p.hole_cards = []
            p.total_bet_in_hand = 0
            p.street_bet = 0
            if p.status != PlayerStatus.ELIMINATED:
                p.status = PlayerStatus.ACTIVE

        # Heads-up special rule: dealer = SB
        if n == 2:
            sb_idx = self.dealer_pos % n
            bb_idx = (self.dealer_pos + 1) % n
        else:
            sb_idx = (self.dealer_pos + 1) % n
            bb_idx = (self.dealer_pos + 2) % n

        self._post_blind(self.players[sb_idx], self.small_blind)
        self._post_blind(self.players[bb_idx], self.big_blind)
        self.current_bet = self.big_blind

        # Deal 2 cards to each active player
        for p in self.players:
            p.hole_cards = self._deck.deal(2)

        # Preflop: action starts left of BB
        self._action_idx = (bb_idx + 1) % n
        self._num_to_act = len(self._active_players())

    def _post_blind(self, player, amount: int) -> None:
        from poker.game.tournament import PlayerStatus
        actual = min(amount, player.chips)
        player.chips -= actual
        player.total_bet_in_hand += actual
        player.street_bet += actual
        if player.chips == 0:
            player.status = PlayerStatus.ALL_IN

    def _active_players(self) -> list:
        from poker.game.tournament import PlayerStatus
        return [p for p in self.players if p.status == PlayerStatus.ACTIVE]

    def current_player(self):
        active = self._active_players()
        if not active:
            return None
        n = len(self.players)
        for i in range(n):
            idx = (self._action_idx + i) % n
            if self.players[idx] in active:
                return self.players[idx]
        return None

    def apply_action(self, sid: str, action: str, amount: int = 0) -> Optional[dict]:
        """
        Apply a player action. Returns hand result dict if hand is over, else None.
        action: 'fold' | 'call' | 'raise' | 'all_in'
        amount: target total bet for this street (for raise)
        """
        from poker.game.tournament import PlayerStatus
        player = next(p for p in self.players if p.sid == sid)

        if action == 'fold':
            player.status = PlayerStatus.FOLDED
            self._num_to_act -= 1

        elif action == 'call':
            to_call = min(self.current_bet - player.street_bet, player.chips)
            player.chips -= to_call
            player.street_bet += to_call
            player.total_bet_in_hand += to_call
            if player.chips == 0:
                player.status = PlayerStatus.ALL_IN
            self._num_to_act -= 1

        elif action == 'raise':
            # amount = new total bet for this street; must exceed current bet
            min_amount = self.current_bet + 1
            amount = max(amount, min_amount)
            delta = min(amount - player.street_bet, player.chips)
            delta = max(delta, 0)
            player.chips -= delta
            player.street_bet += delta
            player.total_bet_in_hand += delta
            self.current_bet = player.street_bet
            if player.chips == 0:
                player.status = PlayerStatus.ALL_IN
            # Everyone else needs to act again
            self._num_to_act = len(self._active_players()) - 1

        elif action == 'all_in':
            delta = player.chips
            player.street_bet += delta
            player.total_bet_in_hand += delta
            if player.street_bet > self.current_bet:
                self.current_bet = player.street_bet
                self._num_to_act = len(self._active_players())
            player.chips = 0
            player.status = PlayerStatus.ALL_IN
            self._num_to_act -= 1

        # Advance action index
        n = len(self.players)
        self._action_idx = (self._action_idx + 1) % n

        # Check if hand is over (all but one folded)
        non_folded = [p for p in self.players
                      if p.status != PlayerStatus.FOLDED
                      and p.status != PlayerStatus.ELIMINATED]
        if len(non_folded) == 1:
            return self._award_pots()

        # Check if betting round is complete
        if self._num_to_act <= 0 or not self._active_players():
            return self._advance_phase()

        return None

    def _advance_phase(self) -> Optional[dict]:
        """Move to next phase, deal community cards. Returns result if hand over."""
        from poker.game.tournament import PlayerStatus
        for p in self.players:
            p.street_bet = 0
        self.current_bet = 0
        self._num_to_act = len(self._active_players())

        # First active position after dealer
        n = len(self.players)
        for i in range(1, n + 1):
            idx = (self.dealer_pos + i) % n
            if self.players[idx].status == PlayerStatus.ACTIVE:
                self._action_idx = idx
                break

        if self.phase == 'preflop':
            self.community_cards = self._deck.deal(3)
            self.phase = 'flop'
        elif self.phase == 'flop':
            self.community_cards += self._deck.deal(1)
            self.phase = 'turn'
        elif self.phase == 'turn':
            self.community_cards += self._deck.deal(1)
            self.phase = 'river'
        elif self.phase == 'river':
            self.phase = 'showdown'
            return self._award_pots()

        # If no active players (all all-in), run out the board
        if not self._active_players():
            if self.phase == 'flop':
                self.community_cards += self._deck.deal(1)
                self.community_cards += self._deck.deal(1)
            elif self.phase == 'turn':
                self.community_cards += self._deck.deal(1)
            self.phase = 'showdown'
            return self._award_pots()

        return None

    def _award_pots(self) -> dict:
        """Calculate winners and award chips."""
        from poker.game.tournament import PlayerStatus
        contribs = [
            {'sid': p.sid, 'total_bet': p.total_bet_in_hand,
             'folded': p.status == PlayerStatus.FOLDED}
            for p in self.players
        ]
        pots = calculate_pots(contribs)
        winners_summary = []

        for pot in pots:
            eligible = [p for p in self.players if p.sid in pot.eligible_sids]
            if len(eligible) == 1:
                eligible[0].chips += pot.amount
                winners_summary.append({
                    'sid': eligible[0].sid,
                    'name': eligible[0].name,
                    'amount': pot.amount,
                    'hand_name': 'Uncontested',
                })
            else:
                scores = {}
                for p in eligible:
                    all_cards = p.hole_cards + list(self.community_cards)
                    scores[p.sid] = best_hand_score(all_cards)
                best_score = max(scores.values())
                pot_winners = [p for p in eligible if scores[p.sid] == best_score]
                split = pot.amount // len(pot_winners)
                for w in pot_winners:
                    w.chips += split
                    winners_summary.append({
                        'sid': w.sid,
                        'name': w.name,
                        'amount': split,
                        'hand_name': hand_name(scores[w.sid]),
                    })

        # Merge winnings for the same player across multiple pots
        merged: dict[str, dict] = {}
        for entry in winners_summary:
            sid = entry['sid']
            if sid in merged:
                merged[sid]['amount'] += entry['amount']
            else:
                merged[sid] = dict(entry)
        merged_summary = list(merged.values())

        # Only reveal cards for players who reached a contested showdown
        showdown_sids: set[str] = set()
        for pot in pots:
            eligible = [p for p in self.players if p.sid in pot.eligible_sids]
            if len(eligible) > 1:
                showdown_sids.update(pot.eligible_sids)

        return {
            'winners': merged_summary,
            'community_cards': [c.to_dict() for c in self.community_cards],
            'hole_cards': {
                p.sid: [c.to_dict() for c in p.hole_cards]
                for p in self.players
                if p.sid in showdown_sids
            },
            'phase': self.phase,
        }
