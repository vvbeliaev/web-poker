from __future__ import annotations
from collections import Counter
from enum import IntEnum
from itertools import combinations

from poker.game.deck import Card


class HandRank(IntEnum):
    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8


_HAND_NAMES = {
    HandRank.HIGH_CARD: "High Card",
    HandRank.ONE_PAIR: "One Pair",
    HandRank.TWO_PAIR: "Two Pair",
    HandRank.THREE_OF_A_KIND: "Three of a Kind",
    HandRank.STRAIGHT: "Straight",
    HandRank.FLUSH: "Flush",
    HandRank.FULL_HOUSE: "Full House",
    HandRank.FOUR_OF_A_KIND: "Four of a Kind",
    HandRank.STRAIGHT_FLUSH: "Straight Flush",
}


def evaluate_5(cards: list[Card]) -> tuple:
    """Return a comparable score tuple for exactly 5 cards."""
    if len(cards) != 5:
        raise ValueError(f"evaluate_5 requires exactly 5 cards, got {len(cards)}")
    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]
    is_flush = len(set(suits)) == 1

    rank_counts = Counter(ranks)
    # Sort by (count desc, rank desc) so primary group is first
    groups = sorted(rank_counts, key=lambda r: (rank_counts[r], r), reverse=True)
    counts = [rank_counts[r] for r in groups]
    sorted_ranks = sorted(ranks, reverse=True)

    # Straight detection — needs exactly 5 unique ranks
    is_straight = False
    straight_high = 0
    unique = sorted(set(ranks), reverse=True)
    if len(unique) == 5:
        if unique[0] - unique[4] == 4:
            is_straight, straight_high = True, unique[0]
        elif unique == [14, 5, 4, 3, 2]:   # Wheel: A-2-3-4-5
            is_straight, straight_high = True, 5

    if is_straight and is_flush:
        return (HandRank.STRAIGHT_FLUSH, straight_high)
    if counts[0] == 4:
        return (HandRank.FOUR_OF_A_KIND, groups[0], groups[1])
    if counts[0] == 3 and len(counts) > 1 and counts[1] == 2:
        return (HandRank.FULL_HOUSE, groups[0], groups[1])
    if is_flush:
        return (HandRank.FLUSH, *sorted_ranks)
    if is_straight:
        return (HandRank.STRAIGHT, straight_high)
    if counts[0] == 3:
        return (HandRank.THREE_OF_A_KIND, groups[0], groups[1], groups[2])
    if counts[0] == 2 and len(counts) > 1 and counts[1] == 2:
        return (HandRank.TWO_PAIR, groups[0], groups[1], groups[2])
    if counts[0] == 2:
        return (HandRank.ONE_PAIR, groups[0], groups[1], groups[2], groups[3])
    return (HandRank.HIGH_CARD, *sorted_ranks)


def best_hand_score(cards: list[Card]) -> tuple:
    """Best 5-card score from 5–7 cards."""
    return max(evaluate_5(list(combo)) for combo in combinations(cards, 5))


def hand_name(score: tuple) -> str:
    return _HAND_NAMES[score[0]]
