import streamlit as st
from classes import Card, Deck, Player, Game, Table


st.title("Texas Hold 'Em Simulator")

if 'state_dict' not in st.session_state:
    st.session_state.state_dict = None

custom_state_dict = {
    "players": [
        {
            "name": "Sam",
            "hand": [(14, 'Spades'), (13, 'Hearts') ]
        },
        {
            "name": "Arch",
            "hand": None
        },
        # {
        #     "name": "Bob",
        #     "hand": None
        # }
    ],
    "table": { #these cannot repeat cards on the table
        #"flop": [(4, 'Spades'), (14, 'Clubs'), (12, 'Hearts')],
        "flop": None,
        #"turn": [(9, 'Diamonds')], 
        "turn": None,
        #"river": (12, 'Clubs')
        "river": None
    }
}
outcomes = {
    'Sam': 0,
    'Arch': 0,
    #'Bob': 0,
    'Tie': 0
}

card1 = st.selectbox("Sam Card 1", 
                     options=[(rank, suit) for rank in range(2, 15) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']],
                     index=0)  # Default to Ace of Spades
card2 = st.selectbox("Sam Card 2", 
                     options=[(rank, suit) for rank in range(2, 15) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']],
                     index=1)  # Default to King of Spades

custom_state_dict['players'][0]['hand'] = [card1, card2]

if st.checkbox("Add Flop Cards?"):
    card3 = st.selectbox("Flop 1", 
                        options=[(rank, suit) for rank in range(2, 15) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']],
                        index=2)  # Default to Ace of Spades
    card4 = st.selectbox("Flop 2", 
                        options=[(rank, suit) for rank in range(2, 15) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']],
                        index=3)  # Default to King of Spades
    card5 = st.selectbox("Flop 3", 
                        options=[(rank, suit) for rank in range(2, 15) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']],
                        index=4)  # Default to Queen of Spades
    custom_state_dict['table']['flop'] = [card3, card4, card5]
if st.checkbox("Add Turn Card?"):
    card6 = st.selectbox("Turn", 
                         options=[(rank, suit) for rank in range(2, 15) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']],
                         index=5)  # Default to Jack of Spades
    custom_state_dict['table']['turn'] = [card6]
if st.checkbox("Add River Card?"):
    card7 = st.selectbox("River", 
                         options=[(rank, suit) for rank in range(2, 15) for suit in ['Hearts', 'Diamonds', 'Clubs', 'Spades']],
                         index=6)  # Default to 10 of Spades
    custom_state_dict['table']['river'] = [card7]


#FIXME: add validation to ensure no duplicate cards

st.session_state.state_dict = custom_state_dict


sims = 10_000
for _ in range(sims):
    game = Game(num_players=3, state_dict=st.session_state.state_dict, verbose=False)
    game.start()
    game.flop()
    game.turn()
    game.river()
    winner = game.compute_winner()
    #print(f"Winner: {winner}")
    outcomes[winner] += 1

# print(f"Final outcomes after {sims} games:")
# for player, wins in outcomes.items():
#     print(f"{player}: {wins} wins")

win_prob = {player: wins / sims for player, wins in outcomes.items()}
print("Win probabilities:")
print(win_prob)
st.write("Win probabilities after {} simulations:".format(sims))
st.write(win_prob)