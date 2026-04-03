import pytest
from poker.game.deck import Card
from poker.game.evaluator import evaluate_5, best_hand_score, hand_name, HandRank


def cards(*specs: str) -> list[Card]:
    """Helper: 'Ah' -> Card(14,'h'), '2c' -> Card(2,'c')"""
    rank_map = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
                '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
    result = []
    for s in specs:
        result.append(Card(rank=rank_map[s[0]], suit=s[1]))
    return result


def test_high_card():
    score = evaluate_5(cards('2h', '4d', '6c', '8s', 'Th'))
    assert score[0] == HandRank.HIGH_CARD
    assert score[1] == 10  # highest card


def test_one_pair():
    score = evaluate_5(cards('Ah', 'Ad', '2c', '4s', '6h'))
    assert score[0] == HandRank.ONE_PAIR
    assert score[1] == 14  # pair of aces


def test_two_pair():
    score = evaluate_5(cards('Kh', 'Kd', 'Qc', 'Qs', '2h'))
    assert score[0] == HandRank.TWO_PAIR
    assert score[1] == 13  # higher pair
    assert score[2] == 12


def test_three_of_a_kind():
    score = evaluate_5(cards('Ah', 'Ad', 'Ac', '2s', '4h'))
    assert score[0] == HandRank.THREE_OF_A_KIND
    assert score[1] == 14


def test_straight():
    score = evaluate_5(cards('5h', '6d', '7c', '8s', '9h'))
    assert score[0] == HandRank.STRAIGHT
    assert score[1] == 9  # high card of straight


def test_wheel_straight():
    """A-2-3-4-5 is a straight with high card 5."""
    score = evaluate_5(cards('Ah', '2d', '3c', '4s', '5h'))
    assert score[0] == HandRank.STRAIGHT
    assert score[1] == 5


def test_flush():
    score = evaluate_5(cards('2h', '5h', '7h', 'Jh', 'Kh'))
    assert score[0] == HandRank.FLUSH


def test_full_house():
    score = evaluate_5(cards('Ah', 'Ad', 'Ac', 'Kh', 'Kd'))
    assert score[0] == HandRank.FULL_HOUSE
    assert score[1] == 14  # trips
    assert score[2] == 13  # pair


def test_four_of_a_kind():
    score = evaluate_5(cards('Ah', 'Ad', 'Ac', 'As', '2h'))
    assert score[0] == HandRank.FOUR_OF_A_KIND
    assert score[1] == 14


def test_straight_flush():
    score = evaluate_5(cards('5h', '6h', '7h', '8h', '9h'))
    assert score[0] == HandRank.STRAIGHT_FLUSH
    assert score[1] == 9


def test_hand_ordering():
    sf = evaluate_5(cards('9h', 'Th', 'Jh', 'Qh', 'Kh'))
    foak = evaluate_5(cards('Ah', 'Ad', 'Ac', 'As', '2h'))
    flush = evaluate_5(cards('2h', '5h', '7h', 'Jh', 'Kh'))
    straight = evaluate_5(cards('5h', '6d', '7c', '8s', '9h'))
    assert sf > foak > flush > straight


def test_best_hand_from_7_cards():
    # Hole: Ah Kh | Board: Qh Jh Th 2d 3c → Royal Flush in hearts
    seven = cards('Ah', 'Kh', 'Qh', 'Jh', 'Th', '2d', '3c')
    score = best_hand_score(seven)
    assert score[0] == HandRank.STRAIGHT_FLUSH
    assert score[1] == 14  # A-high straight flush


def test_hand_name():
    score = evaluate_5(cards('Ah', 'Ad', 'Ac', 'As', '2h'))
    assert hand_name(score) == "Four of a Kind"


def test_evaluate_5_rejects_wrong_count():
    with pytest.raises(ValueError, match="exactly 5 cards"):
        evaluate_5(cards('Ah', 'Kh', 'Qh'))
