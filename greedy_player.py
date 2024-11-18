import numpy as np

BOARD_SIZE = 5

def read_input():
    with open('input.txt', 'r') as f:
        lines = f.readlines()
        player = int(lines[0].strip())
        prev_board = np.array([list(map(int, list(line.strip()))) for line in lines[1: BOARD_SIZE+1]])
        curr_board = np.array([list(map(int, list(line.strip()))) for line in lines[BOARD_SIZE+1: 2*BOARD_SIZE+1]])
    return player, prev_board, curr_board

def write_output(move):
    with open('output.txt', 'w') as f:
        if move == 'PASS':
            f.write('PASS')
        else:
            f.write(f"{move[0]},{move[1]}")

def get_valid_moves(board):
    moves = []
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == 0:
                moves.append((i, j))
    return moves

def copy_board(board):
    return np.copy(board)

def has_liberty(board, x, y, visited=None):
    if visited is None:
        visited = set()
    if (x, y) in visited:
        return False
    visited.add((x, y))
    player = board[x][y]
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if board[nx][ny] == 0:
                return True
            elif board[nx][ny] == player:
                if has_liberty(board, nx, ny, visited):
                    return True
    return False

def remove_dead_stones(board, player):
    removed = 0
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if board[i][j] == player and not has_liberty(board, i, j):
                board[i][j] = 0
                removed += 1
    return removed

def is_move_valid(curr_board, new_board, player, move):
    # Simple legality check
    if np.array_equal(curr_board, new_board):
        return False
    return True

def main():
    player, prev_board, curr_board = read_input()
    opponent = 3 - player
    valid_moves = get_valid_moves(curr_board)
    max_captured = -1
    best_move = None

    for move in valid_moves:
        test_board = copy_board(curr_board)
        test_board[move[0]][move[1]] = player
        captured = remove_dead_stones(test_board, opponent)
        if not has_liberty(test_board, move[0], move[1]):
            continue  # Suicide move
        if not is_move_valid(curr_board, test_board, player, move):
            continue  # Invalid move
        if captured > max_captured:
            max_captured = captured
            best_move = move

    if best_move:
        write_output(best_move)
    else:
        write_output('PASS')

if __name__ == "__main__":
    main()

import random
import sys
from read import readInput
from write import writeOutput

from host import GO

class GreedyPlayer():
    def __init__(self):
        self.type = 'greedy'

    def get_input(self, go, piece_type):
        '''
        Get one input based on a greedy strategy.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input or "PASS".
        '''        
        possible_placements = []
        max_captured = -1
        best_moves = []

        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    # Copy the board for simulation
                    test_go = go.copy_board()
                    test_go.place_chess(i, j, piece_type)
                    # Remove dead opponent stones
                    dead_stones = test_go.remove_died_pieces(3 - piece_type)
                    num_captured = len(dead_stones)

                    if num_captured > max_captured:
                        max_captured = num_captured
                        best_moves = [(i, j)]
                    elif num_captured == max_captured:
                        best_moves.append((i, j))

        if best_moves:
            return random.choice(best_moves)
        else:
            # If no captures are possible, return "PASS" or a random valid move
            return "PASS"

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = GreedyPlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)