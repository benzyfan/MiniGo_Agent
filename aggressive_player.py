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

def simulate_move(board, move, player):
    new_board = copy_board(board)
    new_board[move[0]][move[1]] = player
    opponent = 3 - player
    remove_dead_stones(new_board, opponent)
    return new_board

def evaluate_board(board, player):
    opponent = 3 - player
    player_stones = np.sum(board == player)
    opponent_stones = np.sum(board == opponent)
    return player_stones - opponent_stones

def main():
    player, prev_board, curr_board = read_input()
    opponent = 3 - player
    valid_moves = get_valid_moves(curr_board)
    max_captured = -float('inf')
    best_move = None

    for move in valid_moves:
        first_board = simulate_move(curr_board, move, player)
        if not has_liberty(first_board, move[0], move[1]):
            continue  # Suicide move
        if not is_move_valid(curr_board, first_board, player, move):
            continue  # Invalid move

        # Opponent's best response (assume opponent plays greedily)
        opponent_moves = get_valid_moves(first_board)
        max_opponent_captured = -1
        for opp_move in opponent_moves:
            second_board = simulate_move(first_board, opp_move, opponent)
            if not has_liberty(second_board, opp_move[0], opp_move[1]):
                continue
            captured = remove_dead_stones(second_board, player)
            if captured > max_opponent_captured:
                max_opponent_captured = captured

        # Our next move after opponent's response
        next_valid_moves = get_valid_moves(first_board)
        max_total_captured = -1
        for next_move in next_valid_moves:
            third_board = simulate_move(first_board, next_move, player)
            captured = remove_dead_stones(third_board, opponent)
            total_captured = captured - max_opponent_captured
            if total_captured > max_total_captured:
                max_total_captured = total_captured

        if max_total_captured > max_captured:
            max_captured = max_total_captured
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

class AggressivePlayer():
    def __init__(self):
        self.type = 'aggressive'

    def get_input(self, go, piece_type):
        '''
        Get one input based on an aggressive strategy.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input or "PASS".
        '''
        max_aggression = -float('inf')
        best_moves = []

        opponent_type = 3 - piece_type

        for i in range(go.size):
            for j in range(go.size):
                if go.valid_place_check(i, j, piece_type, test_check=True):
                    # Copy the board for simulation
                    test_go = go.copy_board()
                    test_go.place_chess(i, j, piece_type)
                    # Remove dead opponent stones
                    dead_stones = test_go.remove_died_pieces(opponent_type)
                    num_captured = len(dead_stones)

                    # Calculate aggression score
                    aggression_score = num_captured * 10  # Prioritize capturing stones

                    # Reduce opponent liberties
                    opponent_liberties = self.count_opponent_liberties(test_go, opponent_type)
                    aggression_score += (self.count_opponent_liberties(go, opponent_type) - opponent_liberties)

                    # Threaten opponent groups
                    threatened_groups = self.count_threatened_groups(test_go, opponent_type)
                    aggression_score += threatened_groups * 5

                    # Prefer moves closer to the center
                    distance_to_center = abs(i - go.size // 2) + abs(j - go.size // 2)
                    aggression_score -= distance_to_center * 0.1  # Slightly prefer center positions

                    if aggression_score > max_aggression:
                        max_aggression = aggression_score
                        best_moves = [(i, j)]
                    elif aggression_score == max_aggression:
                        best_moves.append((i, j))

        if best_moves:
            return random.choice(best_moves)
        else:
            # If no aggressive moves are possible, return "PASS"
            return "PASS"

    def count_opponent_liberties(self, go, opponent_type):
        total_liberties = 0
        visited = set()
        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == opponent_type and (i, j) not in visited:
                    group = go.ally_dfs(i, j)
                    visited.update(group)
                    liberties = self.count_group_liberties(go, group)
                    total_liberties += liberties
        return total_liberties

    def count_group_liberties(self, go, group):
        '''
        Count the number of liberties for a group of stones.

        :param go: Go instance.
        :param group: List of positions in the group.
        :return: Number of liberties for the group.
        '''
        liberties = set()
        for (i, j) in group:
            neighbors = go.detect_neighbor(i, j)
            for (x, y) in neighbors:
                if go.board[x][y] == 0:
                    liberties.add((x, y))
        return len(liberties)

    def count_threatened_groups(self, go, opponent_type):
        '''
        Count the number of opponent groups that have only one liberty (in atari).

        :param go: Go instance.
        :param opponent_type: 1('X') or 2('O').
        :return: Number of opponent groups in atari.
        '''
        threatened_groups = 0
        visited = set()
        for i in range(go.size):
            for j in range(go.size):
                if go.board[i][j] == opponent_type and (i, j) not in visited:
                    group = go.ally_dfs(i, j)
                    visited.update(group)
                    liberties = self.count_group_liberties(go, group)
                    if liberties == 1:
                        threatened_groups += 1
        return threatened_groups

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = readInput(N)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    player = AggressivePlayer()
    action = player.get_input(go, piece_type)
    writeOutput(action)