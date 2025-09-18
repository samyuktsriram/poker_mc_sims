import pytest
from src.classes import Game, Card
from copy import deepcopy


@pytest.fixture
def base_state_omaha():
    """Base state dictionary for testing Omaha poker"""
    return {
        "players": [
            {
                "name": "Sam",
                "hand": [
                    (14, "Hearts"),  # A♥
                    (13, "Hearts"),  # K♥
                    (12, "Hearts"),  # Q♥
                    (11, "Hearts"),  # J♥
                ],
            },
            {
                "name": "Arch",
                "hand": [
                    (10, "Diamonds"),  # 10♦
                    (10, "Clubs"),  # 10♣
                    (9, "Diamonds"),  # 9♦
                    (9, "Clubs"),  # 9♣
                ],
            },
        ],
        "table": {"flop": None, "turn": None, "river": None},
        "game_type": "omaha",  # Specify Omaha variant
    }


@pytest.mark.parametrize(
    "scenario",
    [
        {
            "name": "Nut Flush vs Full House",
            "player1_hand": [
                (14, "Hearts"),
                (13, "Hearts"),  # A♥ K♥
                (12, "Clubs"),
                (11, "Diamonds"),  # Q♣ J♦
            ],
            "player2_hand": [
                (10, "Spades"),
                (10, "Clubs"),  # 10♠ 10♣
                (9, "Hearts"),
                (9, "Diamonds"),  # 9♥ 9♦
            ],
            "community_cards": {
                "flop": [(2, "Hearts"), (3, "Hearts"), (10, "Hearts")],  # 2♥ 3♥ 10♥
                "turn": [(9, "Clubs")],  # 9♣
                "river": [(10, "Diamonds")],  # 10♦
            },
            "expected_winner": "Arch",
            "winning_hand": "Full House",
        },
        {
            "name": "Two Pair Limited by Must-Use-Two Rule",
            "player1_hand": [
                (7, "Hearts"),
                (7, "Diamonds"),  # 7♥ 7♦
                (6, "Hearts"),
                (6, "Diamonds"),  # 6♥ 6♦
            ],
            "player2_hand": [
                (8, "Clubs"),
                (8, "Spades"),  # 8♣ 8♠
                (5, "Clubs"),
                (5, "Spades"),  # 5♣ 5♠
            ],
            "community_cards": {
                "flop": [(7, "Clubs"), (8, "Hearts"), (9, "Hearts")],  # 7♣ 8♥ 9♥
                "turn": [(10, "Diamonds")],  # 10♦
                "river": [(11, "Clubs")],  # J♣
            },
            "expected_winner": "Arch",
            "winning_hand": "Higher Two Pair",
        },
    ],
)
def test_omaha_hand_rankings(base_state_omaha, scenario):
    """
    Test Omaha poker hand rankings and winner determination.

    Key differences from Texas Hold'em:
    - Players must use exactly 2 cards from their 4-card hand
    - Must use exactly 3 cards from the community cards
    """
    # Setup the game state
    state = deepcopy(base_state_omaha)
    state["players"][0]["hand"] = scenario["player1_hand"]
    state["players"][1]["hand"] = scenario["player2_hand"]
    state["table"]["flop"] = scenario["community_cards"]["flop"]
    state["table"]["turn"] = scenario["community_cards"]["turn"]
    state["table"]["river"] = scenario["community_cards"]["river"]

    # Initialize and run the Omaha game
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


def test_omaha_must_use_two_rule():
    """Test that players must use exactly 2 cards from their hand"""
    state = {
        "players": [
            {
                "name": "Sam",
                "hand": [
                    (14, "Hearts"),
                    (13, "Hearts"),  # A♥ K♥
                    (12, "Hearts"),
                    (11, "Diamonds"),  # Q♥ J♦
                ],
            }
        ],
        "table": {
            "flop": [(2, "Hearts"), (3, "Hearts"), (4, "Hearts")],  # 2♥ 3♥ 4♥
            "turn": [(5, "Hearts")],  # 5♥
            "river": [(6, "Hearts")],  # 6♥
        },
        "game_type": "omaha",
    }

    game = Game(1, state_dict=state)
    game.start()
    game.flop()
    game.turn()
    game.river()
    game.compute_winner()

    # Player should not have a straight flush despite all hearts
    # They must use exactly 2 from their hand and 3 from the board
    evaluation = game.players[0].evaluation
    assert (
        evaluation.eval != 9
    ), "Should not have straight flush - must use exactly 2 cards from hand"


def test_omaha_four_card_deal(base_state_omaha):
    """Test that players are dealt exactly 4 cards in Omaha"""
    state = deepcopy(base_state_omaha)
    state["players"][0]["hand"] = None  # Let the game deal the cards
    state["players"][1]["hand"] = None  # Let the game deal the cards
    game = Game(2, state_dict=state)
    game.start()

    for player in game.players:
        assert (
            len(player.cards) == 4
        ), f"Player {player.name} should have exactly 4 cards in Omaha"
