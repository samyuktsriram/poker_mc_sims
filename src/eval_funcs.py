#takes in a hand, and the open cards on the table
#returns the rank of the hand
#from classes import Card, Deck, Player, Game, Table

#have to figure out tiebreaks #FIXME 
class Evaluation:
    def __init__(self, eval, primary_cards, kickers=None):
        self.eval = eval  # Hand rank (9=straight flush, 8=four of a kind, etc.)
        self.primary_cards = sorted(primary_cards, reverse=True)  # Main cards that make the hand
        self.kickers = sorted(kickers, reverse=True) if kickers else []  # Remaining cards for tiebreaks
    
    def __lt__(self, other):
        if self.eval != other.eval:
            return self.eval < other.eval
            
        # Compare primary cards
        for self_card, other_card in zip(self.primary_cards, other.primary_cards):
            if self_card != other_card:
                return self_card < other_card
                
        # Compare kickers
        for self_kick, other_kick in zip(self.kickers, other.kickers):
            if self_kick != other_kick:
                return self_kick < other_kick
                
        return False  # Completely equal hands

    def __eq__(self, other):
        if not isinstance(other, Evaluation):
            return NotImplemented
        return (self.eval == other.eval and 
                self.primary_cards == other.primary_cards and 
                self.kickers == other.kickers)

def evaluate_hand(player, open_cards):
    all_cards = player.show_hand() + open_cards
    ranks = [card.rank for card in all_cards]
    suits = [card.suit for card in all_cards]

    rank_count = {rank: ranks.count(rank) for rank in set(ranks)}
    suit_count = {suit: suits.count(suit) for suit in set(suits)}

    # Find flush suit if it exists
    flush_suit = next((suit for suit, count in suit_count.items() if count >= 5), None)
    is_flush = flush_suit is not None

    # Get sorted ranks and handle flush
    sorted_ranks = sorted(ranks, reverse=True)

    # Check for straight flush first
    if is_flush:
        flush_cards = sorted([card.rank for card in all_cards 
                            if card.suit == flush_suit], reverse=True)
        straight_flush_high = check_straight(flush_cards)
        if straight_flush_high:
            return Evaluation(9, [straight_flush_high])  # Straight Flush

    # Check for four of a kind
    if 4 in rank_count.values():
        quads = [r for r, count in rank_count.items() if count == 4][0]
        kickers = [r for r in sorted_ranks if r != quads][:1]
        return Evaluation(8, [quads], kickers)

    # Check for full house
    if sorted(rank_count.values()) == [2, 3]:
        trips = [r for r, count in rank_count.items() if count == 3][0]
        pair = [r for r, count in rank_count.items() if count == 2][0]
        return Evaluation(7, [trips, pair])

    # Check for flush
    if is_flush:
        flush_cards = sorted([card.rank for card in all_cards 
                            if card.suit == flush_suit], reverse=True)[:5]
        return Evaluation(6, flush_cards)

    # Check for straight
    straight_high = check_straight(sorted_ranks)
    if straight_high:
        return Evaluation(5, [straight_high])

    # Check for three of a kind
    if 3 in rank_count.values():
        trips = [r for r, count in rank_count.items() if count == 3][0]
        kickers = sorted([r for r in sorted_ranks if r != trips], reverse=True)[:2]
        return Evaluation(4, [trips], kickers)

    # Check for two pair
    pairs = [r for r, count in rank_count.items() if count == 2]
    if len(pairs) >= 2:
        pairs.sort(reverse=True)
        pairs = pairs[:2]  # Take highest two pairs
        kickers = [r for r in sorted_ranks if r not in pairs][:1]
        return Evaluation(3, pairs, kickers)

    # Check for one pair
    if pairs:
        pair = pairs[0]
        kickers = [r for r in sorted_ranks if r != pair][:3]
        return Evaluation(2, [pair], kickers)

    # High card
    return Evaluation(1, [], sorted_ranks[:5])

def check_straight(ranks):
    """Helper function to check for straights."""
    # Remove duplicates and sort
    unique_ranks = sorted(set(ranks), reverse=True)
    
    # Regular straight check
    for i in range(len(unique_ranks) - 4):
        if unique_ranks[i] - unique_ranks[i + 4] == 4:
            return unique_ranks[i]
    
    # Ace-low straight check (A,2,3,4,5)
    if 14 in unique_ranks and {2,3,4,5}.issubset(set(unique_ranks)):
        return 5
    
    return None


###Tests

# ranks = list(range(2, 15))  # 2-14 where 11-14 are J, Q, K, A
# #suits = [1,2,3,4]
# suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
# cards = [Card(rank, suit) for rank in ranks for suit in suits]

# game = Game(num_players=2, cards=cards)
# game.start()
# game.flop()
# game.turn()
# game.river()

# for player in game.players:
#     hand_rank = evaluate_hand(player, game.open_cards)
#     print(f"Player {player.name} has a {hand_rank}")
