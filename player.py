import numpy as np
import copy
import time
import sys

# Define possible directions for movement (up, right, down, left)
DIRECTIONS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


class GoAI:
    def __init__(self):
        # Board configuration
        self.board_size = 5
        self.komi = 2.5  # Compensation points for white
        self.time_limit = 9.5  # Time limit for making a move
        self.max_depth = 2  # Maximum depth for alpha-beta search
        self.max_branching = 25  # Maximum number of moves to consider at each step

        # Game state information
        self.player_color = None
        self.opponent_color = None
        self.previous_board = None
        self.current_board = None
        self.step = 0

        # Evaluation weights
        self.weight_c = None
        self.weight_d = None
        self.weight_e = None
        self.weight_g = None
        self.weight_h = None

    def set_weight(self):
        """
        Initialize evaluation weights based on player color.
        Currently, weights are the same regardless of color.
        """
        self.weight_c = 3.57
        self.weight_d = 0.76
        self.weight_e = 3.61
        self.weight_g = -9.45
        self.weight_h = 4.64

    def read_input(self):
        """
        Read the game state from 'input.txt'.
        The first line indicates the player's color.
        The next five lines represent the previous board state.
        The following five lines represent the current board state.
        """
        with open('input.txt', 'r') as file:
            data = file.readlines()
        self.player_color = int(data[0].strip())
        self.opponent_color = 3 - self.player_color
        self.previous_board = np.array([list(map(int, line.strip())) for line in data[1:6]], dtype=int)
        self.current_board = np.array([list(map(int, line.strip())) for line in data[6:11]], dtype=int)

    def write_output(self, move):
        """
        Write the chosen move to 'output.txt'.
        If the move is a pass, write 'PASS'; otherwise, write the coordinates.
        """
        with open('output.txt', 'w') as file:
            if move == "PASS":
                file.write('PASS')
            else:
                file.write(f'{move[0]},{move[1]}')

    def update_step(self):
        """
        Update the current step of the game.
        Reads the previous step from 'step.txt' and increments it.
        Initializes step based on the initial board states.
        """
        if np.all(self.previous_board == 0) and np.all(self.current_board == 0):
            self.step = 0
        elif np.all(self.previous_board == 0) and not np.all(self.current_board == 0):
            self.step = 1
        else:
            try:
                with open("step.txt", "r") as step_file:
                    self.step = int(step_file.readline()) + 2
            except FileNotFoundError:
                self.step = 2
        with open("step.txt", 'w') as step_file:
            step_file.write(f'{self.step}')

    def get_position_weights(self):
        """
        Return a matrix of positional weights for the board.
        Higher weights are given to central positions.
        """
        return np.array([
            [1, 2, 3, 2, 1],
            [2, 4, 6, 4, 2],
            [3, 6, 9, 6, 3],
            [2, 4, 6, 4, 2],
            [1, 2, 3, 2, 1]
        ])

    def evaluate(self, board, color):
        """
        Evaluate the board state from the perspective of the given color.
        Considers factors like stone count, liberties, atari, positional advantage, cut potential, etc.
        """
        opponent_color = 3 - color
        position_weights = self.get_position_weights()

        # Count stones
        own_stones = np.sum(board == color)
        opponent_stones = np.sum(board == opponent_color)

        # Count liberties
        own_liberties = self.count_total_liberties(board, color)
        opponent_liberties = self.count_total_liberties(board, opponent_color)

        # Count atari stones
        own_atari = self.count_atari_stones(board, color)
        opponent_atari = self.count_atari_stones(board, opponent_color)

        # Positional advantage
        own_position = np.sum(position_weights * (board == color))
        opponent_position = np.sum(position_weights * (board == opponent_color))

        # Potential cuts and opponent's low liberties
        own_cut_potential = self.evaluate_cut_potential(board, color)
        opponent_low_liberty = self.count_low_liberty_stones(board, opponent_color, max_liberties=1)

        # Calculate total score based on weighted factors
        score = 0
        score += 10 * (own_stones - opponent_stones)
        score += self.weight_c * (own_liberties - opponent_liberties)
        score += self.weight_d * (own_atari - opponent_atari)
        score += (own_position - opponent_position) * self.weight_e
        score += self.komi if color == 2 else 0
        score += own_cut_potential * self.weight_g
        score += opponent_low_liberty * self.weight_h

        return score

    def count_total_liberties(self, board, color):
        """
        Count the total number of unique liberties for all groups of the specified color.
        """
        liberties = set()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == color:
                    group_liberties = self.get_group_liberties(board, i, j, color)
                    liberties.update(group_liberties)
        return len(liberties)

    def get_group_liberties(self, board, x, y, color):
        """
        Get all unique liberties for the group of stones connected to (x, y).
        """
        visited = set()
        stack = [(x, y)]
        liberties = set()

        while stack:
            i, j = stack.pop()
            if (i, j) in visited:
                continue
            visited.add((i, j))
            for dx, dy in DIRECTIONS:
                adj_x, adj_y = i + dx, j + dy
                if 0 <= adj_x < self.board_size and 0 <= adj_y < self.board_size:
                    if board[adj_x][adj_y] == 0:
                        liberties.add((adj_x, adj_y))
                    elif board[adj_x][adj_y] == color and (adj_x, adj_y) not in visited:
                        stack.append((adj_x, adj_y))
        return liberties

    def count_atari_stones(self, board, color):
        """
        Count the number of stones that are in atari (only one liberty left).
        """
        count = 0
        visited = set()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == color and (i, j) not in visited:
                    liberties = self.get_group_liberties(board, i, j, color)
                    if len(liberties) == 1:
                        group = self.get_group(board, i, j, color)
                        count += len(group)
                        visited.update(group)
        return count

    def count_low_liberty_stones(self, board, color, max_liberties):
        """
        Count the number of stones in groups with liberties less than or equal to max_liberties.
        """
        count = 0
        visited = set()
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == color and (i, j) not in visited:
                    liberties = self.get_group_liberties(board, i, j, color)
                    if len(liberties) <= max_liberties:
                        group = self.get_group(board, i, j, color)
                        count += len(group)
                        visited.update(group)
        return count

    def get_group(self, board, x, y, color):
        """
        Get all stones connected to (x, y) of the specified color.
        """
        visited = set()
        stack = [(x, y)]
        group = set()

        while stack:
            i, j = stack.pop()
            if (i, j) in visited:
                continue
            visited.add((i, j))
            group.add((i, j))
            for dx, dy in DIRECTIONS:
                adj_x, adj_y = i + dx, j + dy
                if 0 <= adj_x < self.board_size and 0 <= adj_y < self.board_size:
                    if board[adj_x][adj_y] == color and (adj_x, adj_y) not in visited:
                        stack.append((adj_x, adj_y))
        return group

    def evaluate_cut_potential(self, board, color):
        """
        Evaluate the potential for making cuts against the opponent.
        A cut is possible if placing a stone results in splitting opponent's groups.
        """
        opponent_color = 3 - color
        cutting_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if board[i][j] == 0:
                    adjacent_groups = self.get_adjacent_opponent_groups(board, i, j, opponent_color)
                    if len(adjacent_groups) >= 2:
                        cutting_moves.append((i, j))
        return len(cutting_moves)

    def get_adjacent_opponent_groups(self, board, x, y, opponent_color):
        """
        Get all unique opponent groups adjacent to the position (x, y).
        """
        adjacent_groups = set()
        for dx, dy in DIRECTIONS:
            adj_x, adj_y = x + dx, y + dy
            if 0 <= adj_x < self.board_size and 0 <= adj_y < self.board_size:
                if board[adj_x][adj_y] == opponent_color:
                    group = self.get_group(board, adj_x, adj_y, opponent_color)
                    adjacent_groups.add(frozenset(group))
        return adjacent_groups

    def is_valid_move(self, board, move, color):
        """
        Check if a move is valid:
        - The position must be empty.
        - The move must not be suicidal.
        - The move must not violate the Ko rule.
        """
        x, y = move
        if board[x][y] != 0:
            return False  # Position is already occupied
        test_board = self.simulate_move(board, move, color)
        if test_board is None:
            return False  # Move is suicidal
        if self.is_ko(self.previous_board, test_board):
            return False  # Move violates Ko rule
        return True

    def simulate_move(self, board, move, color):
        """
        Simulate placing a stone on the board and return the new board state.
        Capture any opponent groups with no liberties after the move.
        If the move results in no liberties for the placed stone, it's suicidal and returns None.
        """
        new_board = copy.deepcopy(board)
        x, y = move
        new_board[x][y] = color
        opponent_color = 3 - color
        to_check = []

        # Collect adjacent opponent positions to check for captures
        for dx, dy in DIRECTIONS:
            adj_x, adj_y = x + dx, y + dy
            if 0 <= adj_x < self.board_size and 0 <= adj_y < self.board_size:
                if new_board[adj_x][adj_y] == opponent_color:
                    to_check.append((adj_x, adj_y))

        # Remove opponent groups with no liberties
        for i, j in to_check:
            if not self.has_liberty(new_board, i, j, opponent_color):
                self.remove_group(new_board, i, j, opponent_color)

        # Check if the placed stone has at least one liberty
        if not self.has_liberty(new_board, x, y, color):
            return None  # Suicidal move

        return new_board

    def has_liberty(self, board, x, y, color):
        """
        Check if the stone at (x, y) has at least one liberty.
        """
        visited = set()
        stack = [(x, y)]

        while stack:
            i, j = stack.pop()
            if (i, j) in visited:
                continue
            visited.add((i, j))
            for dx, dy in DIRECTIONS:
                adj_x, adj_y = i + dx, j + dy
                if 0 <= adj_x < self.board_size and 0 <= adj_y < self.board_size:
                    if board[adj_x][adj_y] == 0:
                        return True  # Found a liberty
                    elif board[adj_x][adj_y] == color:
                        stack.append((adj_x, adj_y))
        return False  # No liberties found

    def remove_group(self, board, x, y, color):
        """
        Remove all stones in the group connected to (x, y) of the specified color.
        """
        stack = [(x, y)]
        while stack:
            i, j = stack.pop()
            if board[i][j] == color:
                board[i][j] = 0  # Remove the stone
                for dx, dy in DIRECTIONS:
                    adj_x, adj_y = i + dx, j + dy
                    if 0 <= adj_x < self.board_size and 0 <= adj_y < self.board_size:
                        if board[adj_x][adj_y] == color:
                            stack.append((adj_x, adj_y))

    def is_ko(self, previous_board, current_board):
        """
        Check for Ko rule violation by comparing the current board with the previous board.
        """
        return np.array_equal(previous_board, current_board)

    def get_valid_moves(self, board, color):
        """
        Generate a list of all valid moves for the given color.
        """
        valid_moves = []
        for i in range(self.board_size):
            for j in range(self.board_size):
                if self.is_valid_move(board, (i, j), color):
                    valid_moves.append((i, j))
        return valid_moves

    def alpha_beta_search(self, board, color, depth, alpha, beta, passed):
        """
        Perform alpha-beta pruning search to evaluate board positions.
        """
        if depth == self.max_depth or self.step + depth >= 24:
            return self.evaluate(board, self.player_color)

        valid_moves = self.get_valid_moves(board, color)
        if not valid_moves:
            if passed:
                return self.evaluate(board, self.player_color)
            else:
                # If no moves available, pass the turn to the opponent
                return self.alpha_beta_search(board, 3 - color, depth + 1, alpha, beta, True)

        if color == self.player_color:
            value = -np.inf
            for move in valid_moves[:self.max_branching]:
                new_board = self.simulate_move(board, move, color)
                if new_board is None:
                    continue
                value = max(value, self.alpha_beta_search(new_board, 3 - color, depth + 1, alpha, beta, False))
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # Beta cutoff
            return value
        else:
            value = np.inf
            for move in valid_moves[:self.max_branching]:
                new_board = self.simulate_move(board, move, color)
                if new_board is None:
                    continue
                value = min(value, self.alpha_beta_search(new_board, 3 - color, depth + 1, alpha, beta, False))
                beta = min(beta, value)
                if alpha >= beta:
                    break  # Alpha cutoff
            return value

    def choose_move(self):
        """
        Choose the best move based on the current board state using alpha-beta search.
        Includes opening moves heuristics.
        """
        # Opening move heuristics
        if self.player_color == 1 and self.step == 0:
            return (2, 2)  # Play center on the first move
        if self.player_color == 2 and self.step == 1:
            if self.current_board[2][2] == 0:
                return (2, 2)  # Play center if it's free

        # Get all valid moves
        valid_moves = self.get_valid_moves(self.current_board, self.player_color)
        if not valid_moves:
            return "PASS"  # No valid moves, must pass

        best_move = None
        best_value = -np.inf

        # Evaluate each valid move
        for move in valid_moves[:self.max_branching]:
            new_board = self.simulate_move(self.current_board, move, self.player_color)
            if new_board is None:
                continue
            value = self.alpha_beta_search(new_board, self.opponent_color, 0, -np.inf, np.inf, False)
            if value > best_value:
                best_value = value
                best_move = move

        return best_move if best_move else "PASS"


if __name__ == '__main__':
    start_time = time.time()
    player = GoAI()
    player.read_input()
    player.set_weight()
    player.update_step()

    # If you want to find a better parameter,you can use the testvalue.py to run optuna for better one
    # if len(sys.argv) != 6:
    #     print("Usage: python3 player.py C D E G H I")
    #     sys.exit(1)
    #
    # try:
    #     player.weight_c = float(sys.argv[1])
    #     player.weight_d = float(sys.argv[2])
    #     player.weight_e = float(sys.argv[3])
    #     player.weight_g = float(sys.argv[4])
    #     player.weight_h = float(sys.argv[5])
    # except ValueError:
    #     print("Parameters must be numbers.")
    #     sys.exit(1)

    best_move = player.choose_move()
    player.write_output(best_move)

    # Uncomment the following line to print the elapsed time for debugging
    # print(time.time() - start_time)
