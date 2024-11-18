# MiniGo_Agent

**MiniGo_Agent** is an AI-powered Go player designed to compete on a compact 5x5 board. This project encompasses both the Go AI agent and a parameter optimization framework leveraging [Optuna](https://optuna.org/) to enhance the agent's performance against a variety of opponents.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
- [Usage](#usage)
  - [Running the GoAI Agent](#running-the-goai-agent)
  - [Parameter Optimization](#parameter-optimization)
- [Configuration](#configuration)
  - [Opponent Configuration](#opponent-configuration)
  - [Input and Output Files](#input-and-output-files)
- [Results](#results)
- [License](#license)

## Features

- **AI Go Player for 5x5 Board:** A specialized AI agent capable of playing Go on a 5x5 mini board.
- **Parameter Optimization:** Utilizes Optuna for tuning the agent's evaluation parameters to maximize performance.
- **Multiple Opponents Support:** Compete against a variety of opponent scripts to ensure the AI's robustness.
- **Automated Game Management:** Handles game state transitions, move validations, and game termination seamlessly.
- **Detailed Logging:** Logs optimization runs and game outcomes for comprehensive analysis.

## Installation

Follow these steps to set up the MiniGo_Agent on your local machine.

### Prerequisites

Ensure you have the following installed:

- **Python 3.7 or higher**
- **pip** (Python package installer)

## Usage

### Running the GoAI Agent

The GoAI agent (player.py) interacts with game state files (input.txt and output.txt). To manually run a game:
- **Prepare input.txt**  <br>
The input.txt file should contain the following:
```
<player_color>
<previous_board_state>
<current_board_state>
```
<player_color>: 1 for Black, 2 for White.  <br>
<previous_board_state> / <current_board_state>: 5 lines each representing the board, where each line has 5 digits (0 for empty, 1 for Black, 2 for White).  <br>

- **Run the Agent**  <br>
```
python3 player.py
```
- **Retrieve the Move**  <br>
The agent writes its move to output.txt. The move is either PASS or in the format x,y.  <br>

### Parameter Optimization

The optimization.py script performs parameter optimization using Optuna to enhance the GoAI agent’s performance.
- **Configure Opponents** <br>
Ensure test_opponents.txt is populated with the commands to run each opponent.
- **Run Optimization** <br>
```
python3 optimization.py
```
Parameters:  <br>
	•	BOARD_SIZE: Size of the Go board (default is 5 for a 5x5 board  <br>
	•	MAX_MOVES: Maximum number of moves per game (default is 24).  <br>
	•	TIME_LIMIT: Time limit per move in seconds (default is 50).  <br>
	•	KOMI: Compensation points for White (default is 2.5).  <br>
	•	TOP_N: Number of top parameter sets to retain (default is 10).  <br>
	•	GAMES_PER_COMBINATION: Number of games per parameter set against each opponent (default is 15).  <br>

- **Review Results** <br>
After optimization, the results are saved in:  <br>
	•	top_10_parameters.txt: Details of the top 10 parameter sets and their performance.  <br>
	•	optimization_results.txt: Comprehensive results of all parameter evaluations.  <br>
	•	mid_result.txt: Intermediate results to prevent data loss during long optimization runs.  <br>

## Configuration

### Opponent Configuration

•	File: test_opponents.txt  <br>
•	Purpose: Lists all opponent commands or script names that the GoAI agent will compete against.  <br>
•	Format: Each line contains a command to run an opponent script.  <br>
Example:
```
python3 opponents/random_player.py
python3 opponents/greedy_player.py
python3 opponents/aggressive_player.py
```

### Input and Output Files

•	input.txt: Used by the GoAI agent to read the current game state. <br>
Format:
```
<player_color>
<previous_board_state>
<current_board_state>
```
•	output.txt: Used by the GoAI agent to write its chosen move. <br>
Format: Either PASS or x,y.  <br>

## Results

•	top_10_parameters.txt: Contains the top 10 parameter sets with the highest overall win rates, along with their performance against each opponent. <br>
•	optimization_results.txt: Logs all evaluated parameter sets and their corresponding win rates.  <br>
•	mid_result.txt: Continuously updated with intermediate results during the optimization process to safeguard against unexpected interruptions.  <br>

## License

This project is licensed under the MIT License.
