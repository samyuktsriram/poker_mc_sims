# Poker Monte Carlo Simulations
A basic Python implementation for simulating and analyzing poker games, with support for both Texas Hold'em and Omaha variants.

Using Streamlit to easily input and compute probabilities interactively.


### Features
1. Texas Hold'em and Omaha poker variants
2. Monte Carlo simulations for equity analysis at each stage.
3. Supports up to 6 players (for now)


### Installation

```
# Install with Poetry
git clone https://github.com/yourusername/poker_mc_sims.git
cd poker_mc_sims
poetry install
```

### Run the app
```
# Run with Streamlit
poetry run streamlit run src/simulator.py
```

### Install and run with Docker
```
docker pull samyukt14/poker_mc:latest
docker run -p 8501:8501 samyukt14/poker_mc:latest
```
Go to localhost:8501 in your browser


In case your port 8501 is used, change the first number in the command to another number

### Tests

```
poetry run pytest
```

### Code formatting - Black
```
poetry run black src tests --check
```