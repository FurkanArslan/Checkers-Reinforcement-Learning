"""
@author: Sam Ragusa
NOTES:
-Should store moves as array of locations e.g.: [[x1,y1],[x2,y2],[x3,y3]]
which is showing the piece at [x1,x2] goes to [x2,y2] then [x3,y3] as one move
-0 is empty spot, 1 is p1, 2 is p2, 3 is p1 king, 4 is p2 king
-if self.player_turn == True then it is player 1's turn
"""

import math
import copy
from functools import reduce


class Board:
    """
    A class to represent and play an 8x8 game of checkers.
    """
    EMPTY_SPOT = 0
    P1 = 1
    P2 = 2
    P1_K = 3
    P2_K = 4
    BACKWARDS_PLAYER = P2

    def __init__(self, height=8, width=4, old_spots=None, the_player_turn=True):
        """
        Initializes a new instance of the Board class.  Unless specified otherwise, 
        the board will be created with a start board configuration.
        
        NOTE:
        Maybe have default parameter so board is 8x8 by default but nxn if wanted.
        :type height: int
        :type width: int
        """
        self.player_turn = the_player_turn
        self.HEIGHT = 8
        self.WIDTH = 4

        if old_spots is None:
            self.spots = [[j, j, j, j] for j in
                          [self.P1, self.P1, self.P1, self.EMPTY_SPOT, self.EMPTY_SPOT, self.P2, self.P2, self.P2]]
            # self.spots = [[j, j, j] for j in
            #               [self.P1, self.P1, self.EMPTY_SPOT, self.EMPTY_SPOT, self.P2, self.P2]]
        else:
            self.spots = old_spots

    def reset_board(self):
        """
        Resets the current configuration of the game board to the original 
        starting position.
        """
        self.spots = Board().spots

    def empty_board(self):
        """
        Removes any pieces currently on the board and leaves the board with nothing but empty spots.
        """
        self.spots = [[j, j, j, j] for j in [self.EMPTY_SPOT] * self.HEIGHT]

    def is_game_over(self):
        """
        Finds out and returns weather the game currently being played is over or
        not.
        """
        if not self.get_possible_next_moves():
            return True
        return False

    def not_spot(self, loc):
        """
        Finds out of the spot at the given location is an actual spot on the game board.
        """
        if len(loc) == 0 or loc[0] < 0 or loc[0] > self.HEIGHT - 1 or loc[1] < 0 or loc[1] > self.WIDTH - 1:
            return True
        return False

    def get_spot_info(self, loc):
        """
        Gets the information about the spot at the given location.
        
        NOTE:
        Might want to not use this for the sake of computational time.
        """
        return self.spots[loc[0]][loc[1]]

    def forward_n_locations(self, start_loc, n, backwards=False):
        """
        Gets the locations possible for moving a piece from a given location diagonally
        forward (or backwards if wanted) a given number of times(without directional change midway).  
        """
        if n % 2 == 0:
            temp1 = 0
            temp2 = 0
        elif start_loc[0] % 2 == 0:
            temp1 = 0
            temp2 = 1
        else:
            temp1 = 1
            temp2 = 0

        answer = [[start_loc[0], start_loc[1] + math.floor(n / 2) + temp1],
                  [start_loc[0], start_loc[1] - math.floor(n / 2) - temp2]]

        if backwards:
            answer[0][0] = answer[0][0] - n
            answer[1][0] = answer[1][0] - n
        else:
            answer[0][0] = answer[0][0] + n
            answer[1][0] = answer[1][0] + n

        if self.not_spot(answer[0]):
            answer[0] = []
        if self.not_spot(answer[1]):
            answer[1] = []

        return answer

    def get_simple_moves(self, start_loc):
        """    
        Gets the possible moves a piece can make given that it does not capture any opponents pieces.
        
        PRE-CONDITION:
        -start_loc is a location with a players piece
        """
        if self.spots[start_loc[0]][start_loc[1]] > 2:
            next_locations = self.forward_n_locations(start_loc, 1)
            next_locations.extend(self.forward_n_locations(start_loc, 1, True))
        elif self.spots[start_loc[0]][start_loc[1]] == self.BACKWARDS_PLAYER:
            next_locations = self.forward_n_locations(start_loc, 1, True)  # Switched the true from the statement below
        else:
            next_locations = self.forward_n_locations(start_loc, 1)

        possible_next_locations = []

        for location in next_locations:
            if len(location) != 0:
                if self.spots[location[0]][location[1]] == self.EMPTY_SPOT:
                    possible_next_locations.append(location)

        return [[start_loc, end_spot] for end_spot in possible_next_locations]

    def get_capture_moves(self, start_loc, move_beginnings=None):
        """
        Recursively get all of the possible moves for a piece which involve capturing an opponent's piece.
        """
        if move_beginnings is None:
            move_beginnings = [start_loc]

        answer = []
        if self.spots[start_loc[0]][start_loc[1]] > 2:
            next1 = self.forward_n_locations(start_loc, 1)
            next2 = self.forward_n_locations(start_loc, 2)
            next1.extend(self.forward_n_locations(start_loc, 1, True))
            next2.extend(self.forward_n_locations(start_loc, 2, True))
        elif self.spots[start_loc[0]][start_loc[1]] == self.BACKWARDS_PLAYER:
            next1 = self.forward_n_locations(start_loc, 1, True)
            next2 = self.forward_n_locations(start_loc, 2, True)
        else:
            next1 = self.forward_n_locations(start_loc, 1)
            next2 = self.forward_n_locations(start_loc, 2)

        for j in range(len(next1)):
            if (not self.not_spot(next2[j])) and (not self.not_spot(next1[j])):  # if both spots exist
                if self.get_spot_info(next1[j]) != self.EMPTY_SPOT and self.get_spot_info(
                        next1[j]) % 2 != self.get_spot_info(start_loc) % 2:  # if next spot is opponent
                    if self.get_spot_info(next2[j]) == self.EMPTY_SPOT:  # if next next spot is empty
                        temp_move1 = copy.deepcopy(move_beginnings)
                        temp_move1.append(next2[j])

                        answer_length = len(answer)

                        if self.get_spot_info(start_loc) != self.P1 or next2[j][0] != self.HEIGHT - 1:
                            if self.get_spot_info(start_loc) != self.P2 or next2[j][0] != 0:
                                temp_move2 = [start_loc, next2[j]]

                                temp_board = Board(copy.deepcopy(self.spots), self.player_turn)
                                temp_board.make_move(temp_move2, False)

                                answer.extend(temp_board.get_capture_moves(temp_move2[1], temp_move1))

                        if len(answer) == answer_length:
                            answer.append(temp_move1)

        return answer

    def get_piece_locations(self):
        piece_locations = []

        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                if (self.player_turn is True and (self.spots[j][i] == self.P1 or self.spots[j][i] == self.P1_K)) or \
                        (self.player_turn is False and (self.spots[j][i] == self.P2 or self.spots[j][i] == self.P2_K)):
                    piece_locations.append([j, i])

        return piece_locations

    def get_possible_next_moves_for_a_piece(self, piece_location):
        capture_moves = self.get_capture_moves(piece_location)

        if len(capture_moves) != 0:
            return capture_moves

        return self.get_simple_moves(piece_location)

    def get_possible_next_moves(self, spots=None):
        """
        Gets the possible moves that can be made from the current board configuration.
        """
        if spots is None:
            spots = self.spots

        piece_locations = []
        for j in range(self.HEIGHT):
            for i in range(self.WIDTH):
                if (self.player_turn is True and (spots[j][i] == self.P1 or spots[j][i] == self.P1_K)) or (self.player_turn is False and (spots[j][i] == self.P2 or spots[j][i] == self.P2_K)):
                    piece_locations.append([j, i])

        try:  # Should check to make sure if this try statement is still necessary
            capture_moves = list(reduce(lambda a, b: a + b, list(map(self.get_capture_moves, piece_locations))))

            if len(capture_moves) != 0:
                return capture_moves

            return list(reduce(lambda a, b: a + b, list(map(self.get_simple_moves, piece_locations))))
        except TypeError:
            return []

    def make_move(self, move, switch_player_turn=True):
        """
        Makes a given move on the board, and (as long as is wanted) switches the indicator for
        which players turn it is.
        """
        if abs(move[0][0] - move[1][0]) == 2:
            for j in range(len(move) - 1):
                if move[j][0] % 2 == 1:
                    if move[j + 1][1] < move[j][1]:
                        middle_y = move[j][1]
                    else:
                        middle_y = move[j + 1][1]
                else:
                    if move[j + 1][1] < move[j][1]:
                        middle_y = move[j + 1][1]
                    else:
                        middle_y = move[j][1]

                self.spots[int((move[j][0] + move[j + 1][0]) / 2)][middle_y] = self.EMPTY_SPOT

        self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.spots[move[0][0]][move[0][1]]
        if move[len(move) - 1][0] == self.HEIGHT - 1 and self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == self.P1:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.P1_K
        elif move[len(move) - 1][0] == 0 and self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] == self.P2:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.P2_K
        else:
            self.spots[move[len(move) - 1][0]][move[len(move) - 1][1]] = self.spots[move[0][0]][move[0][1]]
        self.spots[move[0][0]][move[0][1]] = self.EMPTY_SPOT

        if switch_player_turn:
            self.player_turn = not self.player_turn

    def get_potential_spots_from_moves(self, moves):
        """
        Get's the potential spots for the board if it makes any of the given moves.
        If moves is None then returns it's own current spots.
        """
        if moves is None:
            return self.spots
        answer = []
        for move in moves:
            original_spots = copy.deepcopy(self.spots)
            self.make_move(move, switch_player_turn=False)
            answer.append(self.spots)
            self.spots = original_spots
        return answer

    def get_states_from_boards_spots(self, boards_spots, player_id=None):
        """
        Gets an array of tuples from the given set of board spots,
        each tuple representing the characteristics which define the
        state the board is in.

        Format of returned data:
        [(own_pieces, opp_pieces, own_kings, opp_kings, own_edges, own_vert_center_mass, opp_vert_center_mass), ...]
        """
        piece_counters = [[0, 0, 0, 0, 0, 0, 0] for j in range(len(boards_spots))]
        for k in range(len(boards_spots)):
            for j in range(len(boards_spots[k])):
                for i in range(len(boards_spots[k][j])):
                    if boards_spots[k][j][i] != 0:
                        piece_counters[k][boards_spots[k][j][i] - 1] = piece_counters[k][boards_spots[k][j][i] - 1] + 1
                        if (player_id and (boards_spots[k][j][i] == 1 or boards_spots[k][j][i] == 3)) or \
                                (not player_id and (boards_spots[k][j][i] == 2 or boards_spots[k][j][i] == 4)):
                            if i == 0 and j % 2 == 0:
                                piece_counters[k][4] = piece_counters[k][4] + 1
                            elif i == 3 and j % 2 == 1:
                                piece_counters[k][4] = piece_counters[k][4] + 1

                            piece_counters[k][5] = piece_counters[k][5] + j
                        else:
                            piece_counters[k][6] = piece_counters[k][6] + j

            if piece_counters[k][0] + piece_counters[k][2] != 0:
                piece_counters[k][5] = int(piece_counters[k][5] / (piece_counters[k][0] + piece_counters[k][2]))
            else:
                piece_counters[k][5] = 0
            if piece_counters[k][1] + piece_counters[k][3] != 0:
                piece_counters[k][6] = int(piece_counters[k][6] / (piece_counters[k][1] + piece_counters[k][3]))
            else:
                piece_counters[k][6] = 0

        return [tuple(counter) for counter in piece_counters]

    def insert_pieces(self, pieces_info):
        """
        Inserts a set of pieces onto a board.

        pieces_info is in the form: [[vert1, horz1, piece1], [vert2, horz2, piece2], ..., [vertn, horzn, piecen]]
        """
        for piece_info in pieces_info:
            self.spots[piece_info[0]][piece_info[1]] = piece_info[2]

    def get_symbol(self, location):
        """
        Gets the symbol for what should be at a board location.
        """
        if self.spots[location[0]][location[1]] == self.EMPTY_SPOT:
            return " "
        elif self.spots[location[0]][location[1]] == self.P1:
            return "o"
        elif self.spots[location[0]][location[1]] == self.P2:
            return "x"
        elif self.spots[location[0]][location[1]] == self.P1_K:
            return "O"
        else:
            return "X"

    def print_board(self):
        """
        Prints a string representation of the current game board.
        """
        norm_line = "|---|---|---|---|---|---|---|---|"
        print(norm_line)
        for j in range(self.HEIGHT):
            if j % 2 == 1:
                temp_line = "|///|"
            else:
                temp_line = "|"
            for i in range(self.WIDTH):
                temp_line = temp_line + " " + self.get_symbol([j, i]) + " |"
                if i != 3 or j % 2 != 1:  # should figure out if this 3 should be changed to self.WIDTH-1
                    temp_line = temp_line + "///|"
            print(temp_line)
            print(norm_line)

    def get_number_of_pieces_and_kings(self, spots, player_id=None):
        """
        Gets the number of pieces and the number of kings that each player has on the current
        board configuration represented in the given spots. The format of the function with defaults is:
        [P1_pieces, P2_pieces, P1_kings, P2_kings]
        and if given a player_id:
        [player_pieces, player_kings]
        """
        piece_counter = [0, 0, 0, 0]
        for row in spots:
            for element in row:
                if element != 0:
                    piece_counter[element - 1] = piece_counter[element - 1] + 1

        if player_id == True:
            return [piece_counter[0], piece_counter[2]]
        elif player_id == False:
            return [piece_counter[1], piece_counter[3]]
        else:
            return piece_counter

    def set_spots(self, spots):
        if spots is not None:
            self.spots = copy.deepcopy(spots)

    def switch_turn(self):
        self.player_turn = not self.player_turn
