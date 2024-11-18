import os
import sys
import time
import subprocess
import numpy as np

# Game configuration (You can manually modify these settings)
BOARD_SIZE = 5
MAX_MOVES = 24
TIME_LIMIT = 10  # seconds per move
KOMI = 2.5
TOTAL_GAMES = 10  # Total games against each opponent

# Define the player's command or script name
PLAYER1_COMMAND = 'python3 player11.py'  # Replace with your player1's command or script

# Read opponents from opponents.txt
with open('test_opponents.txt', 'r') as f:
    OPPONENTS_COMMANDS = [line.strip() for line in f if line.strip()]

def initialize_board():
    return np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)

def read_output():
    try:
        with open('output.txt', 'r') as f:
            content = f.read().strip()
            if content == 'PASS':
                return 'PASS'
            else:
                x_str, y_str = content.split(',')
                return int(x_str), int(y_str)
    except Exception as e:
        # Commented out the print statement
        # print(f"Error reading output.txt: {e}")
        return None

def write_input(player, prev_board, curr_board):
    with open('input.txt', 'w') as f:
        f.write(f"{player}\n")
        for row in prev_board:
            f.write(''.join(map(str, row.tolist())) + '\n')
        for row in curr_board:
            f.write(''.join(map(str, row.tolist())) + '\n')

def is_move_valid(prev_board, curr_board, player, move):
    # Implement the legality check including suicide and KO
    # For simplicity, we'll assume the agents handle this correctly
    return True  # Placeholder

def remove_dead_stones(board, player):
    removed = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player and not has_liberty(board, i, j):
                board[i][j] = 0
                removed += 1
    return removed

def has_liberty(board, x, y):
    player = board[x][y]
    visited = set()
    stack = [(x, y)]
    while stack:
        i, j = stack.pop()
        visited.add((i, j))
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = i + dx, j + dy
            if 0 <= ni < BOARD_SIZE and 0 <= nj < BOARD_SIZE:
                if board[ni][nj] == 0:
                    return True
                elif board[ni][nj] == player and (ni, nj) not in visited:
                    stack.append((ni, nj))
    return False

def calculate_winner(final_board):

    black_stones = np.sum(final_board == 1)
    white_stones = np.sum(final_board == 2)

    # Total scores
    black_score = black_stones
    white_score = white_stones +  KOMI

    if black_score > white_score:
        return 1  # Black wins
    else:
        return 2  # White wins

def play_game(black_command, white_command, black_first=True):
    prev_board = initialize_board()
    curr_board = initialize_board()
    move_number = 0
    consecutive_passes = 0
    player_turn = 1 if black_first else 2
    winner = None

    black_captured = 0
    white_captured = 0

    # Before starting, reset any persistent files if necessary
    if os.path.exists('step_num.txt'):
        os.remove('step_num.txt')

    if os.path.exists('step.txt'):
        os.remove('step.txt')


    # Also, remove any existing 'output.txt'
    if os.path.exists('output.txt'):
        os.remove('output.txt')

    while move_number < MAX_MOVES:
        move_number += 1
        opponent = 3 - player_turn
        player_command = black_command if player_turn == 1 else white_command

        # Write input for the player
        write_input(player_turn, prev_board, curr_board)

        # Run the player's code with time limit
        start_time = time.time()
        try:
            subprocess.run(player_command, timeout=TIME_LIMIT, shell=True)
        except subprocess.TimeoutExpired:
            winner = opponent
            # Commented out the print statement
            print(f"Player {player_turn} exceeded time limit.")
            break
        except Exception as e:
            winner = opponent
            # Commented out the print statement
            print(f"Error running player {player_turn}'s code: {e}")
            break

        # Read the player's move
        move = read_output()
        if move is None:
            winner = opponent
            # Commented out the print statement
            # print(f"Player {player_turn} made an invalid move.")
            break

        # Check move validity
        if move != 'PASS':
            if not (0 <= move[0] < BOARD_SIZE and 0 <= move[1] < BOARD_SIZE):
                winner = opponent
                # Commented out the print statement
                # print(f"Player {player_turn} made an invalid move.")
                break
            if curr_board[move[0]][move[1]] != 0:
                winner = opponent
                # Commented out the print statement
                # print(f"Player {player_turn} placed on an occupied position.")
                break
            # Update the board
            new_board = np.copy(curr_board)
            new_board[move[0]][move[1]] = player_turn

            # Remove opponent's stones that have no liberties
            opponent = 2 if player_turn == 1 else 1
            captured = remove_dead_stones(new_board, opponent)
            if player_turn == 1:
                black_captured += captured
            else:
                white_captured += captured

            if not is_move_valid(prev_board, new_board, player_turn, move):
                winner = opponent
                # Commented out the print statement
                # print(f"Player {player_turn} made an illegal move.")
                break

            prev_board = np.copy(curr_board)
            curr_board = new_board
            consecutive_passes = 0
        else:
            consecutive_passes += 1
            if consecutive_passes >= 2:
                # Game ends with both players passing
                break
            prev_board = np.copy(curr_board)

        # After each move, remove 'output.txt' to prevent confusion
        if os.path.exists('output.txt'):
            os.remove('output.txt')

        # Swap player
        player_turn = opponent

        # Commented out the print statement
        # print(curr_board)

    if winner is None:
        winner = calculate_winner(curr_board)
        # Commented out the print statement
        # print(curr_board)
    return winner

def main():
    for opponent_command in OPPONENTS_COMMANDS:
        total_games = TOTAL_GAMES
        round_games = total_games // 2
        black_player1_wins = 0
        white_player1_wins = 0
        # Commented out the print statements
        print(f"Playing against opponent: {opponent_command}")
        # print("Game round 1: Player 1 as Black, Opponent as White")
        for i in range(round_games):
            # Commented out the print statement
            # print(f"Round {i+1}")
            winner = play_game(PLAYER1_COMMAND, opponent_command, black_first=True)
            if winner == 1:
                black_player1_wins += 1
            elif winner == 2:
                pass  # Opponent wins
            else:
                pass  # Draw
        # print("Game round 2: Opponent as Black, Player 1 as White")
        for i in range(round_games):
            # Commented out the print statement
            # print(f"Round {i+1+round_games}")
            winner = play_game(opponent_command, PLAYER1_COMMAND, black_first=True)
            if winner == 2:
                white_player1_wins += 1
            elif winner == 1:
                pass  # Opponent wins
            else:
                pass  # Draw

        total_player1_wins = black_player1_wins + white_player1_wins
        total_opponent_wins = total_games - total_player1_wins
        win_rate = total_player1_wins / total_games if total_games > 0 else 0

        print(f"Against opponent '{opponent_command}':")
        print(f"Total games: {total_games}")
        print(f"  - As Black: {black_player1_wins} wins out of {round_games}, win rate: {black_player1_wins/round_games:.2f}")
        print(f"  - As White: {white_player1_wins} wins out of {round_games}, win rate: {white_player1_wins/round_games:.2f}")
        print(f"Player wins: {total_player1_wins}, win rate: {win_rate:.2f}")
        print("-" * 50)

if __name__ == "__main__":
    print("Start Checking......")
    start_time = time.time()
    main()
    print(f"Execution time: {time.time() - start_time:.2f} seconds")