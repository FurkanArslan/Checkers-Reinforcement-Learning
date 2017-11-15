from Player import Player
from Board import Board
import numpy as np
import IPython.core.debugger
dbg = IPython.core.debugger.Pdb()


class Value_Iteration_AI(Player):
    LOSING_STATES = -100
    WINNING_STATES = 100

    def __init__(self, opponent, player_id=1, discount_factor=0.5, board=None):
        self.player_id = player_id
        self.discount_factor = discount_factor
        self.states = []
        self.value_function = []
        self.policy = []
        self.opponent = opponent
        self.board = board

        if self.board is None:
            self.board = Board()

        self.value_iteration()

    def reward_function(self, state_info1, state_info2):
        if self.board.is_game_over():
            if state_info2[1] == 0 and state_info2[3] == 0:    # winning state
                return 100
            elif state_info2[0] == 0 and state_info2[2] == 0:  # losing state
                return -100
            else:
                return 0                                       # draw state
        else:
            # if my player eats a opponent's piece, gain 5. if my player eats a opponent's king, gain 10
            gained_reward = 5*(state_info2[0] - state_info1[0]) + 10 * (state_info2[2] - state_info1[2])
            # if opponent eats my piece, punish -5. if opponent eats my king, punish -10
            lost_reward = 5*(state_info2[1] - state_info1[1]) + 10 * (state_info2[3] - state_info1[3])

            return gained_reward - lost_reward

    def get_reward(self, current_spots, next_spots):
        current_status = self.board.get_states_from_boards_spots([current_spots])
        next_status = self.board.get_states_from_boards_spots([next_spots])

        return self.reward_function(current_status[0], next_status[0])

    def get_transition_probabilities(self, actions, opponent_action):
        # the probability of taking the action is calculated by 1 / (number of actions x number of opponent actions)
        return 1 / (len(actions) * len(opponent_action))

    def get_value(self, state):
        try:    # if the state has already observed, find state's index and state's value and return them
            index = self.states.index(state)

            return self.value_function[index], index
        except ValueError:      # if the state has not been observed yet, create a new state and add it to states array
            self.states.append(state)
            self.value_function.append(0)
            index = len(self.value_function) - 1

            return 0, index

    def calculate_value_of_action(self, state, possible_moves, opponent_moves):
        next_state = self.board.spots                     # determine next state
        next_state_value = self.get_value(next_state)[0]  # obtain value of next state. If the state is not in the states array, this function creates the state and adds to the array
        reward = self.get_reward(state, next_state)
        prob = self.get_transition_probabilities(possible_moves, opponent_moves)

        return prob * (reward + self.discount_factor * next_state_value)

    def calculate_expected_value(self, state):
        if self.board.is_game_over():
            return [self.LOSING_STATES]

        possible_moves = self.board.get_possible_next_moves()
        expected_value = np.zeros(len(possible_moves))

        for i in range(len(possible_moves)):
            move = possible_moves[i]
            self.board.set_spots(state)                             # recover board to state condition

            self.board.make_move(move)                              # make my move
            opponent_moves = [self.opponent.get_next_move()]  # determine possible opponent's moves

            if self.board.is_game_over():
                expected_value[i] = self.calculate_value_of_action(state, possible_moves, opponent_moves)
                self.board.switch_turn()

                continue

            for opp_move in opponent_moves:                         # maybe there can be more than one opponent moves
                self.board.make_move(opp_move)                      # make opponent move to obtain next state
                expected_value[i] += self.calculate_value_of_action(state, possible_moves, opponent_moves)

        return expected_value

    def value_iteration(self, theta=0.0001):
        self.states.append(self.board.spots)
        self.value_function.append(0)

        while True:
            delta = 0

            for state in self.states:
                self.board.set_spots(state)  # make the board look like same as the state

                v, index = self.get_value(state)

                expected_value = self.calculate_expected_value(state)

                self.value_function[index] = np.max(expected_value)

                delta = max(delta, np.abs(v - self.value_function[index]))

            if delta < theta:
                break

        self.board.reset_board()
        self.calculate_policy()

    def calculate_policy(self):
        for state in self.states:
            expected_value = self.calculate_expected_value(state)       # get values of actions
            self.policy[state] = [0 for i in expected_value]            # init policy's values for this state

            best_action = np.argmax(expected_value)                     # find best action in this state
            self.policy[state, best_action] = 1.0                       # assign best action to 1

    def game_completed(self):
        pass

    def get_next_move(self):
        """
        Gets the desired next move from the AI.
        """
        current_state = self.board.spots                            # determine current state
        determine_policies = np.array(self.policy[current_state])   # obtain policy array for current state
        possible_actions = self.board.get_possible_next_moves()     # obtain available actions

        return possible_actions[determine_policies == 1]            # return selected action whose value is 1

