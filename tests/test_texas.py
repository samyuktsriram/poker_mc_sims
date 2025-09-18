import pytest
import random
from src.classes import Game, Card, Player, Deck
from copy import deepcopy

random.seed(44)  # For reproducibility in tests


@pytest.fixture
def base_state():
    """Base state dictionary for testing"""
    return {
        "players": [
            {"name": "Sam", "hand": [(14, "Hearts"), (13, "Hearts")]},  # A♥ K♥
            {"name": "Arch", "hand": [(7, "Diamonds"), (3, "Hearts")]},  # 7♦ 3♥
        ],
        "table": {"flop": None, "turn": None, "river": None},
        "game_type": "texas",  # or "omaha"
    }


@pytest.fixture
def game(base_state):
    """Creates a basic game instance"""
    return Game(2, state_dict=base_state)


def test_game_initialization(game):
    """Test basic game setup"""
    assert len(game.players) == 2
    assert {game.players[0].name, game.players[1].name} == {"Sam", "Arch"}
    game.start()
    assert len(game.deck.cards) == 52 - 4  # 52 - 4 dealt cards


def test_twice_pop_card():
    """Test that popping the same card twice raises an error"""
    ranks = list(range(2, 15))  # 2-14 where 11-14 are J, Q, K, A
    # suits = [1,2,3,4]
    suits = ["Hearts", "Diamonds", "Clubs", "Spades"]
    cards = [Card(rank, suit) for rank in ranks for suit in suits]
    deck = Deck(cards)
    card = deck.find_and_pop_card(14, "Hearts")  # A♥
    assert card.rank == 14 and card.suit == "Hearts"
    with pytest.raises(ValueError):
        deck.find_and_pop_card(14, "Hearts")  # Should raise error


def test_known_hands(game):
    """Test that known hands are dealt correctly"""
    game.start()
    sam_cards = game.players[0].show_hand()

    assert len(sam_cards) == 2
    assert sam_cards[0].rank == 14 and sam_cards[0].suit == "Hearts"
    assert sam_cards[1].rank == 13 and sam_cards[1].suit == "Hearts"


def test_royal_flush_scenario(base_state):
    """Test royal flush winning scenario"""
    state = deepcopy(base_state)
    state["table"]["flop"] = [(10, "Hearts"), (11, "Hearts"), (12, "Hearts")]
    state["table"]["turn"] = [(9, "Diamonds")]
    state["table"]["river"] = [(8, "Clubs")]

    game = Game(2, state_dict=state)
    game.start()
    game.flop()
    game.turn()
    game.river()

    winner = game.compute_winner()
    assert winner == "Sam"


def test_card_conflict_resolution(base_state):
    """Test handling of duplicate cards between players and community cards"""
    state = deepcopy(base_state)
    # Give player a card that will appear in the flop
    state["players"][0]["hand"] = [(10, "Hearts"), (13, "Hearts")]
    state["table"]["flop"] = [(10, "Hearts"), (11, "Hearts"), (12, "Hearts")]

    game = Game(2, state_dict=state)
    game.start()
    original_cards = [card for card in game.players[0].show_hand()]
    game.flop()

    new_cards = game.players[0].show_hand()
    assert (
        new_cards != original_cards
    ), "Hand should change when card conflicts with flop"


def test_tie_scenario(base_state):
    """Test tie detection"""
    state = deepcopy(base_state)
    # Both players have the same straight
    state["players"][0]["hand"] = [(14, "Hearts"), (13, "Diamonds")]
    state["players"][1]["hand"] = [(14, "Clubs"), (13, "Spades")]
    state["table"]["flop"] = [(12, "Hearts"), (11, "Diamonds"), (10, "Clubs")]

    game = Game(2, state_dict=state)
    game.start()
    game.flop()
    game.turn()
    game.river()

    assert game.compute_winner() == "Tie"


def test_flush_vs_straight(base_state):
    """Test flush beating straight"""
    state = deepcopy(base_state)
    state["players"][0]["hand"] = [(2, "Hearts"), (4, "Hearts")]  # Flush draw
    state["players"][1]["hand"] = [(9, "Diamonds"), (8, "Clubs")]  # Straight draw
    state["table"]["flop"] = [(5, "Hearts"), (6, "Hearts"), (7, "Hearts")]

    game = Game(2, state_dict=state)
    game.start()
    game.flop()
    game.turn()
    game.river()

    assert game.compute_winner() == "Sam"


@pytest.mark.parametrize(
    "scenario",
    [
        {
            "name": "Royal Flush beats Two Pair",
            "player1_hand": [(14, "Hearts"), (13, "Hearts")],  # A♥ K♥
            "player2_hand": [(2, "Diamonds"), (2, "Clubs")],  # 2♦ 2♣
            "community_cards": {
                "flop": [(12, "Hearts"), (11, "Hearts"), (10, "Hearts")],  # Q♥ J♥ 10♥
                "turn": [(5, "Diamonds")],  # 5♦
                "river": [(2, "Spades")],  # 2♠
            },
            "expected_winner": "Sam",
            "winning_hand": "Royal Flush",
        },
        {
            "name": "Higher Pair beats Lower Pair",
            "player1_hand": [(7, "Clubs"), (7, "Diamonds")],  # 7♣ 7♦
            "player2_hand": [(8, "Hearts"), (8, "Spades")],  # 8♥ 8♠
            "community_cards": {
                "flop": [(2, "Hearts"), (3, "Diamonds"), (4, "Clubs")],  # 2♥ 3♦ 4♣
                "turn": [(5, "Diamonds")],  # 5♦
                "river": [(14, "Hearts")],  # A♥
            },
            "expected_winner": "Arch",
            "winning_hand": "Pair of Eights",
        },
        {
            "name": "Flush beats Straight",
            "player1_hand": [(2, "Hearts"), (4, "Hearts")],  # 2♥ 4♥
            "player2_hand": [(9, "Diamonds"), (8, "Clubs")],  # 9♦ 8♣
            "community_cards": {
                "flop": [(5, "Hearts"), (6, "Hearts"), (7, "Hearts")],  # 5♥ 6♥ 7♥
                "turn": [(10, "Diamonds")],  # 10♦
                "river": [(11, "Clubs")],  # J♣
            },
            "expected_winner": "Sam",
            "winning_hand": "Flush",
        },
    ],
)
def test_poker_hand_rankings(base_state, scenario):
    """
    Test various poker hand rankings and winner determination.

    Parameters:
        base_state (dict): Base game state fixture
        scenario (dict): Test scenario containing:
            - name: Description of the test case
            - player1_hand: Sam's hole cards
            - player2_hand: Arch's hole cards
            - community_cards: Flop, turn, and river cards
            - expected_winner: Expected winning player
            - winning_hand: Description of the winning hand
    """
    # Setup the game state
    state = deepcopy(base_state)
    state["players"][0]["hand"] = scenario["player1_hand"]
    state["players"][1]["hand"] = scenario["player2_hand"]
    state["table"]["flop"] = scenario["community_cards"]["flop"]
    state["table"]["turn"] = scenario["community_cards"]["turn"]
    state["table"]["river"] = scenario["community_cards"]["river"]

    # Initialize and run the game
    game = Game(2, state_dict=state)
    game.start()
    game.flop()
    game.turn()
    game.river()

    # Assert the winner
    winner = game.compute_winner()
    assert (
        winner == scenario["expected_winner"]
    ), f"Failed {scenario['name']}: Expected {scenario['expected_winner']} to win with {scenario['winning_hand']}"
