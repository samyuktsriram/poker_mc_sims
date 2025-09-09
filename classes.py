#card 
#hand
#deck
import random
#random.seed(3)


# #state_dict_schema
# test_state_dict = {
#     "players": [
#         {
#             "name": "Sam",
#             "hand": [(14, 'Hearts'), (13, 'Hearts')]
#         },
#         {
#             "name": "Arch",
#             #"hand": None
#             "hand": [(10, 'Hearts'), (2, 'Hearts')]
#         }
#     ],
#     "table": {
#     #     "flop": [(10, 'Hearts'), (11, 'Hearts'), (12, 'Hearts')],
#             "flop": None,
#     #     "turn": (3, 'Spades'), 
#     #     "river": (4, 'Hearts')
#     }
# }

from eval_funcs import evaluate_hand

class Deck:
    def __init__(self, cards):
        self.cards = cards

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self):
        if len(self.cards) == 0:
            return None
        return self.cards.pop()
    def find_and_pop_card(self, rank, suit):
        for card in self.cards:
            if card.rank == rank and card.suit == suit:
                return self.cards.pop(self.cards.index(card))
        return None
    
class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{self.rank} of {self.suit}"
    
class Player:
    def __init__(self, deck, name=None, known_cards=None):
        self.cards = []
        self.deck = deck
        if name:
            self.name = name
        else:
            self.name = f"Player{random.randint(1,1000)}" #fix this
        self.known_cards = known_cards

    def draw_card(self):
        self.cards.append(self.deck.draw())

    def remove_card(self, card):
        self.cards.remove(card)

    def show_hand(self):
        return self.cards
    
#pass some kind of state dict here - that can be checked at each round.
class Game:
    def __init__(self, num_players, state_dict=None, verbose=True, omaha=False):
        self.verbose = verbose
        self.state_dict = state_dict
        #self.omaha = omaha
        
        ranks = list(range(2, 15))  # 2-14 where 11-14 are J, Q, K, A
        #suits = [1,2,3,4]
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        cards = [Card(rank, suit) for rank in ranks for suit in suits]
        self.deck = Deck(cards)


        self.players = [Player(self.deck, player['name'], player['hand']) for player in state_dict['players']]
        
        self.table = Table(self.deck)

        self.open_cards = []
        self.deck.shuffle()
        self.burnt_cards = []

    def start(self):
        for player in self.players:
        #for player in state_dict['players']:
            if player.known_cards is None:
                player.draw_card()
                player.draw_card()
                # if self.omaha:
                #     player.draw_card()
                #     player.draw_card()
            else:
                for card in player.known_cards:
                    #print(card)
                    setup_card = self.deck.find_and_pop_card(card[0], card[1]) #rank and suit
                    if setup_card:
                        player.cards.append(setup_card)

            if self.verbose:
                print("Player:", player.name, player.show_hand())
    
    def flop(self):
        known_flop = self.state_dict['table']['flop']

        if known_flop is None:
            burn_card = self.deck.draw()  # Burn a card
            self.burnt_cards.append(burn_card)
            for _ in range(3):
                self.table.draw_card(self.deck)
        else:
            for card in known_flop:
                setup_card = None
                #interesting edge case to deal with: if we know the flop, we may have to remove those cards from the other players and give them new ones.
                for player in self.players:
                        card_to_remove = next((c for c in player.cards if c.rank == card[0] and c.suit == card[1]), None)
                        if card_to_remove is None:
                            #setup_card = self.deck.find_and_pop_card(card[0], card[1])
                            continue
                        else:
                            if self.verbose:
                                print(f"Removing {card_to_remove} from {player.name}'s hand to set up the flop.")
                            player.remove_card(card_to_remove) #take out this card from the player's hands
                            player.draw_card() #give them a new card from the deck
                            setup_card = Card(card[0], card[1]) #create this setup_card, to be added to table
                
                if setup_card is None:
                    self.table.cards.append(self.deck.find_and_pop_card(card[0], card[1]))
                else:  
                    self.table.cards.append(setup_card)

            #burn at the end because we know the flop
            burn_card = self.deck.draw()
            self.burnt_cards.append(burn_card)

        if self.verbose:
            print("Flop:", self.table.show_table())
        self.open_cards = self.table.show_table()

    def turn(self):
        known_turn = self.state_dict['table']['turn']
        if known_turn is None:
            burn_card = self.deck.draw()
            self.burnt_cards.append(burn_card)
            self.table.draw_card(self.deck)
        else:
            for card in known_turn:
                setup_card = None
                #interesting edge case to deal with: if we know the turn, we may have to remove those cards from the other players and give them new ones. They may also be in the burnt cards! FIXME
                for player in self.players:
                        card_to_remove = next((c for c in player.cards if c.rank == card[0] and c.suit == card[1]), None)
                        if card_to_remove is None:
                            #setup_card = self.deck.find_and_pop_card(card[0], card[1])
                            continue
                        else:
                            if self.verbose:
                                print(f"Removing {card_to_remove} from {player.name}'s hand to set up the flop.")
                            player.remove_card(card_to_remove) #take out this card from the player's hands
                            player.draw_card() #give them a new card from the deck
                            setup_card = Card(card[0], card[1]) #create this setup_card, to be added to table
                

                burnt_card_to_replace = next((c for c in self.burnt_cards if c.rank == card[0] and c.suit == card[1]), None)
                if burnt_card_to_replace:
                    if self.verbose:
                        print(f"Removing {burnt_card_to_replace} from burnt cards to set up the turn.")
                    self.burnt_cards.remove(burnt_card_to_replace)
                    setup_card = Card(card[0], card[1])
                    #self.burnt_cards.append(self.deck.draw()) #replace the burnt card with a new one from the deck

                if setup_card is None: #not in player's hands, not in burnt cards
                    self.table.cards.append(self.deck.find_and_pop_card(card[0], card[1]))
                else:  
                    self.table.cards.append(setup_card)
                
                burn_card = self.deck.draw()
                self.burnt_cards.append(burn_card)
        if self.verbose:
            print("Turn:", self.table.show_table())
    
        self.open_cards = self.table.show_table()

    def river(self):
        burn_card = self.deck.draw()
        self.burnt_cards.append(burn_card)
        self.table.draw_card(self.deck)
        if self.verbose:
            print("River:", self.table.show_table())
        self.open_cards = self.table.show_table()
    
    def compute_winner(self):
        if self.verbose:
            print(len(self.burnt_cards), "burnt cards:", self.burnt_cards)
        
        # Evaluate all hands
        for player in self.players:
            player.evaluation = evaluate_hand(player, self.open_cards)
            if self.verbose:
                print(f"{player.name} has evaluation {player.evaluation.eval} "
                    f"with cards {player.evaluation.primary_cards}")

        # Find highest hand rank
        max_eval = max(player.evaluation.eval for player in self.players)
        potential_winners = [p for p in self.players if p.evaluation.eval == max_eval]
        
        if len(potential_winners) == 1:
            winner = potential_winners[0]
            if self.verbose:
                print(f"The winner is {winner.name} with {(winner.evaluation.eval)} "
                    f"({winner.evaluation.primary_cards})")
            return winner.name
            
        # Compare primary cards and kickers
        best_hand = None
        winners = []
        
        for player in potential_winners:
            if not best_hand:
                best_hand = player.evaluation
                winners = [player]
            elif player.evaluation < best_hand:
                continue
            elif best_hand < player.evaluation:
                best_hand = player.evaluation
                winners = [player]
            else:
                winners.append(player)
        
        if len(winners) == 1:
            if self.verbose:
                print(f"The winner is {winners[0].name} with {(winners[0].evaluation.eval)} "
                    f"({winners[0].evaluation.primary_cards})")
            return winners[0].name
        else:
            names = ', '.join(w.name for w in winners)
            if self.verbose:
                print(f"It's a tie between: {names} with {(winners[0].evaluation.eval)} "
                    f"({winners[0].evaluation.primary_cards})")
            return 'Tie'

    # def compute_winner(self):
    #     if self.verbose:
    #         print(len(self.burnt_cards), "burnt cards:", self.burnt_cards)
    #     for player in self.players:
    #         player.evaluation = evaluate_hand(player, self.open_cards)
    #         if self.verbose:
    #             print(f"{player.name} has evaluation {player.evaluation.eval} and high card {player.evaluation.high_card}")

    #     max_eval = max(player.evaluation.eval for player in self.players)
    #     potential_winners = [player for player in self.players if player.evaluation.eval == max_eval]
    #     if len(potential_winners) == 1:
    #         winner = potential_winners[0]
    #         if self.verbose:
    #             print(f"The winner is {winner.name} with evaluation {winner.evaluation.eval} and high card {winner.evaluation.high_card}")
    #         return winner.name
    #     else:
    #         max_high_card = max(player.evaluation.high_card for player in potential_winners)
    #         final_winners = [player for player in potential_winners if player.evaluation.high_card == max_high_card]
    #         if len(final_winners) == 1:
    #             winner = final_winners[0]
    #             if self.verbose:
    #                 print(f"The winner is {winner.name} with evaluation {winner.evaluation.eval} and high card {winner.evaluation.high_card}")
    #             return winner.name
    #         else:
    #             winners_names = ', '.join(winner.name for winner in final_winners)
    #             if self.verbose:
    #                 print(f"It's a tie between: {winners_names} with evaluation {final_winners[0].evaluation.eval} and high card {final_winners[0].evaluation.high_card}")
    #             return 'Tie'


class Table:
    def __init__(self, deck):
        self.cards = []
        self.deck = deck

    def draw_card(self, deck):
        self.cards.append(deck.draw())

    def show_table(self):
        return self.cards

##Tests


#setup:
ranks = list(range(2, 15))  # 2-14 where 11-14 are J, Q, K, A
#suits = [1,2,3,4]
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
cards = [Card(rank, suit) for rank in ranks for suit in suits]

# deck = Deck(cards)
# deck.shuffle()

# hand1 = Player(deck)
# hand1.draw_card()
# hand1.draw_card()

# hand2 = Player(deck)
# hand2.draw_card()
# hand2.draw_card()

# print("Hand 1:", hand1.show_hand())
# print("Hand 2:", hand2.show_hand())

# game = Game(2, state_dict=test_state_dict, verbose=True)
# game.start()
# game.flop()
# game.turn()
# game.river()
# game.compute_winner()
