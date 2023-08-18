import copy
import random
from collections import namedtuple
import numpy as np
import sys
import time

sys.setrecursionlimit(2000)

StochasticGameState = namedtuple('StochasticGameState', 'to_move, utility, board, moves, chance')

GameState = namedtuple('GameState', 'to_move, utility, board, moves, player1, player2, depth')

# Things from nMensMorrisGame.py that is used globally

GameSteps = ['Setup', 'Move']
PlayerType = ["Human", "Random", "MinMax", "AlphaBeta", "AlphaBetaCutoff", "ExpectimaxCutoff"]


def gen_state(to_move='X', x_positions=[], o_positions=[], h=3, v=3):
    """Given whose turn it is to move, the positions of X's on the board, the
    positions of O's on the board, and, (optionally) number of rows, columns
    and how many consecutive X's or O's required to win, return the corresponding
    game state"""

    moves = set([(x, y) for x in range(1, h + 1) for y in range(1, v + 1)]) - set(x_positions) - set(o_positions)
    moves = list(moves)
    board = {}
    for pos in x_positions:
        board[pos] = 'X'
    for pos in o_positions:
        board[pos] = 'O'
    return GameState(to_move=to_move, utility=0, board=board, moves=moves)


# ______________________________________________________________________________
# MinMax Search


def minmax_decision(state, game):
    """Given a state in a game, calculate the best move by searching
    forward all the way to the terminal states."""

    player = game.to_move(state)

    def max_value(state2, end):
        v = 0
        if time.time() > end:
            return v

        if game.terminal_test(state2):
            return game.utility(state2, player)

        v = -np.inf
        saved_state = copy.deepcopy(state2)
        for a in game.actions(state2):
            if time.time() > end:
                return v
            time.sleep(0.001)
            state2 = copy.deepcopy(saved_state)
            v = max(v, min_value(game.result(state2, a, end), end))
            if time.time() > end:
                return v

        return v

    def min_value(state3, end):
        v = 0
        if time.time() > end:
            return v

        if game.terminal_test(state3):
            return game.utility(state3, player)

        v = np.inf
        saved_state = copy.deepcopy(state3)
        for a in game.actions(state3):
            if time.time() > end:
                return v
            time.sleep(0.001)
            state3 = copy.deepcopy(saved_state)
            v = min(v, max_value(game.result(state3, a, end), end))
            if time.time() > end:
                return v

        return v

    start = time.time()
    end = start + 5

    # Body of minmax_decision:
    return max(game.actions(state), key=lambda a: min_value(game.result(state, a, end), end))


# ______________________________________________________________________________

def expect_minmax(state, game, d=4):
    """
    Return the best move for a player after dice are thrown. The game tree
	includes chance nodes along with min and max nodes.
	"""

    player = game.to_move(state)

    def max_value(state5, depth, end8):
        v = 0
        if time.time() > end8 or depth >= d:
            return v

        v = -np.inf
        saved_state6 = copy.deepcopy(state5)
        for a in game.actions(state):

            state5 = copy.deepcopy(saved_state6)
            v = max(v, chance_node(state5, a,  depth + 1, end8))
        return v



    def min_value(state14, depth, end8):
        v = 0
        if time.time() > end8 or depth >= d:
            return v

        v = -np.inf
        saved_state6 = copy.deepcopy(state14)
        for a in game.actions(state14):

            state14 = copy.deepcopy(saved_state6)
            v = min(v, chance_node(state14, a,  depth + 1, end8))
        return v


    def chance_node(state9, action, depth, end8):
        v = 0
        if time.time() > end8 or depth >= d:
            return v

        res_state = game.result(state9, action, end8)
        if game.terminal_test(res_state):
            return game.utility(res_state, player)

        sum_chances = 0
        num_chances = len(game.actions(res_state))

        for chance in game.actions(res_state):
            if time.time() > end8 or depth == d:
                return sum_chances / num_chances

            res_state = game.result(res_state, chance, end8)

            util = 0
            if res_state.to_move == player:
                util = max_value(res_state, depth+1, end8)
            else:
                util = min_value(res_state, depth+1, end8)
            sum_chances += util
        return sum_chances / num_chances

    start = time.time()
    end8 = start + 5

    if d == -1:
        d = 4

    # Body of expect_minmax:
    return max(game.actions(state), key=lambda a: chance_node(state, a, 1, end8), default=None)


def alpha_beta_search(state, game):
    """Search game to determine best action; use alpha-beta pruning, this version searches all the way to the leaves."""

    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value(state2, alpha, beta, end2):
        v = 0
        if time.time() > end2:
            return v

        if game.terminal_test(state2):
            return game.utility(state2, player)
        v = -np.inf

        saved_state2 = copy.deepcopy(state2)
        for a in game.actions(state):
            if time.time() > end2:
                return v
            state2 = copy.deepcopy(saved_state2)
            v = max(v, min_value(game.result(state2, a, end2), alpha, beta, end2))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state3, alpha, beta, end2):
        v = 0
        if time.time() > end2:
            return v

        if game.terminal_test(state3):
            return game.utility(state3, player)

        v = np.inf
        saved_state1 = copy.deepcopy(state3)
        for a in game.actions(state3):
            if time.time() > end2:
                return v

            time.sleep(0.001)

            state3 = copy.deepcopy(saved_state1)
            v = min(v, max_value(game.result(state3, a, end2), alpha, beta, end2))

            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_search:

    start = time.time()
    end2 = start + 5

    best_score = -np.inf
    beta = np.inf
    best_action = None
    saved_state = copy.deepcopy(state)
    for a in game.actions(state):
        if time.time() > end2:
            return best_action
        state = copy.deepcopy(saved_state)
        v = min_value(game.result(state, a, end2), best_score, beta, end2)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


def alpha_beta_cutoff_search(state, game, d=4, cutoff_test=None, eval_fn=None):
    """Search game to determine best action; use alpha-beta pruning.
    This version cuts off search and uses an evaluation function."""

    player = game.to_move(state)

    # Functions used by alpha_beta
    def max_value(state2, alpha, beta, depth, end3):
        v = 0
        if time.time() > end3:
            return v
        if cutoff_test(state2, depth):
            return eval_fn(state2)
        v = -np.inf
        saved_state4 = copy.deepcopy(state2)
        for a in game.actions(state2):
            if time.time() > end3:
                return v
            state2 = copy.deepcopy(saved_state4)
            v = max(v, min_value(game.result(state2, a, end3), alpha, beta, depth + 1, end3))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(state3, alpha, beta, depth, end3):
        v = 0
        if time.time() > end3:
            return v
        if cutoff_test(state3, depth):
            return eval_fn(state3)
        v = np.inf

        saved_state5 = copy.deepcopy(state3)
        for a in game.actions(state3):
            if time.time() > end3:
                return v
            time.sleep(0.001)
            state3 = copy.deepcopy(saved_state5)
            v = min(v, max_value(game.result(state3, a, end3), alpha, beta, depth + 1, end3))

            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    # Body of alpha_beta_cutoff_search starts here:
    # The default test cuts off at depth d or at a terminal state

    start = time.time()
    end3 = start + 5

    if d == -1:
        d = 4

    cutoff_test = (cutoff_test or (lambda state, depth: depth > d or game.terminal_test(state)))
    eval_fn = eval_fn or (lambda state: game.utility(state, player))
    best_score = -np.inf
    beta = np.inf
    best_action = None
    saved_state = copy.deepcopy(state)
    for a in game.actions(state):
        if time.time() > end3:
            return best_action
        state = copy.deepcopy(saved_state)
        v = min_value(game.result(state, a, end3), best_score, beta, 1, end3)
        if v > best_score:
            best_score = v
            best_action = a
    return best_action


# ______________________________________________________________________________
# Players for Games

def query_player(game, state):
    """Make a move by querying standard input."""
    print("current state:")
    game.display(state)
    print("available moves: {}".format(game.actions(state)))
    print("")
    move = None
    if game.actions(state):
        move_string = input('Your move? ')
        try:
            move = eval(move_string)
        except NameError:
            move = move_string
    else:
        print('no legal moves: passing turn to next player')
    return move


def random_player(game, state):
    """A player that chooses a legal move at random."""
    return random.choice(game.actions(state)) if game.actions(state) else None


def alpha_beta_player(game, state):
    return alpha_beta_search(state, game)


def minmax_player(game,state):
    return minmax_decision(state,game)


def expect_minmax_player(game, state):
    return expect_minmax(state, game)


# ______________________________________________________________________________
# Some Sample Games


class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move, end):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    def play_game(self, *players):
        """Play an n-person, move-alternating game."""
        state = self.initial
        while True:
            for player in players:
                move = player(self, state)
                state = self.result(state, move)
                if self.terminal_test(state):
                    self.display(state)
                    return self.utility(state, self.to_move(self.initial))


class NMMPlayer:
    def __init__(self, id, type, sym):
        self.id = id
        self.sym = sym
        self.type = type
        self.step = GameSteps[0]
        self.utility = 0
        self.livePieces = 9   # total number of pieces which can be set / used on the board. Initially set to 9. If a piece get eaten by the opponent, then livePieces number is decremented.
        self.poses = []  # array of position pair (row, col) for all the pieces of this player on board.
                        # max size of pos is 9
        self.numWin = 0    # number of 3-lineup wins during this game for this player so far
        self.picked = None  # picked position for the moving step

    def reset(self):
        self.step = GameSteps[0]
        self.utility = 0
        self.livePieces = 9
        self.poses.clear()
        self.picked = None


class NMensMorris(Game):
    '''
           A simple Gameboard for 9MensMorris game class. This class contains all game specifics logic like
           what next move to take, if a point (completing a row or diagonal or column) been achieved, if
           game is terminated, and so on. For deciding on next move, there are 3 phases to the game:
            •	Placing pieces on vacant points (9 turns each)
            •	Moving placed pieces to adjacent points.
            •	Moving pieces to any vacant point (when the player has been reduced to 3 men)

            This class governs all the logic of the game. This means it has to check validity of each player's
            move, as well as deciding on next move for the AI player. This class receives the game state,
            in form of the list of rows of cells on the board.

        '''

    def __init__(self, h=3, v=3, k=3):
        self.h = h
        self.v = v
        self.k = k
        self.player1 = NMMPlayer(0, PlayerType[1], "X")
        self.player2 = NMMPlayer(1, PlayerType[1], "O")

        self.cells = []
        self.neighborDict = {}
        self.setupNeighborhood()
        board = []  # an array of 7 rows, each row an array of element from set {'X', 'O', '-'}.
                    #. 'X' means occupied by Human player, 'O' is occupied by AI, '-' means still vacant
        self.initial = GameState(to_move='X', utility=0, board={}, moves={}, player1=None, player2=None, depth=0)

    def setupNeighborhood(self):
        """fills up the dictionary of neighborhood, to be used to find out what cells are neighbors (means player can move to them) to a cell"""
        # row 0
        self.neighborDict[(0, 0)] = [(0, 3), (1, 1), (3, 0)]
        self.neighborDict[(0, 3)] = [(0, 0), (0, 6), (1, 3)]
        self.neighborDict[(0, 6)] = [(0, 3), (1, 5), (3, 6)]

        # row 1
        self.neighborDict[(1, 1)] = [(0, 0), (1, 3), (3, 1), (2, 2)]
        self.neighborDict[(1, 3)] = [(0, 3), (1, 1), (1, 5), (2, 3)]
        self.neighborDict[(1, 5)] = [(0, 6), (1, 3), (2, 4), (3, 5)]

        # row 2
        self.neighborDict[(2, 2)] = [(2, 3), (3, 2), (1, 1)]
        self.neighborDict[(2, 3)] = [(2, 2), (1, 3), (2, 4)]
        self.neighborDict[(2, 4)] = [(2, 3), (3, 4), (1, 5)]

        # row 3
        self.neighborDict[(3, 0)] = [(0, 0), (6, 0), (3, 1)]
        self.neighborDict[(3, 1)] = [(3, 0), (3, 2), (1, 1), (5, 1)]
        self.neighborDict[(3, 2)] = [(3, 1), (2, 2), (4, 2)]
        self.neighborDict[(3, 4)] = [(3, 5), (2, 4), (4, 4)]
        self.neighborDict[(3, 5)] = [(3, 4), (3, 6), (1, 5), (5, 5)]
        self.neighborDict[(3, 6)] = [(3, 5), (0, 6), (6, 6)]

        # row 4
        self.neighborDict[(4, 2)] = [(4, 3), (3, 2), (5, 1)]
        self.neighborDict[(4, 3)] = [(4, 2), (4, 4), (5, 3)]
        self.neighborDict[(4, 4)] = [(4, 3), (3, 4), (5, 5)]

        # row 5
        self.neighborDict[(5, 1)] = [(6, 0), (5, 3), (3, 1), (4, 2)]
        self.neighborDict[(5, 3)] = [(6, 3), (5, 1), (5, 5), (4, 3)]
        self.neighborDict[(5, 5)] = [(6, 6), (5, 3), (4, 4), (3, 5)]

        # row 6
        self.neighborDict[(6, 0)] = [(6, 3), (5, 1), (3, 0)]
        self.neighborDict[(6, 3)] = [(6, 0), (6, 6), (5, 3)]
        self.neighborDict[(6, 6)] = [(6, 3), (5, 5), (3, 6)]



    def getButton(self, pos):
        lpos = list(pos)
        for cellrow in self.cells:
            for cell in cellrow:
                if cell.pos == lpos:
                    return cell.button

        print("getButton(): button at pos ", pos, " is not found")
        raise "getButton: wrong position passed!"
        return None

    def findPossibleMoves(self, player, state):
        """For player find all the pieces which can potentially move"""
        moves = []   # a dictionary of start:[possible ends] which represent a start position as key, all possible end positions as value
        if player.sym == "X":
            opponent = state.player2
        else:
            opponent = state.player1

        for pos in player.poses:
            possibleEnds = self.findPossibleEnds(player, pos)
            if len(possibleEnds) > 0:
                for x in range(len(possibleEnds)):
                    if (possibleEnds[x] not in opponent.poses) and (possibleEnds[x] not in player.poses):
                        moves.append((pos, possibleEnds[x]))

        return moves


    def findPossibleEnds(self, player, pos):
        """Find all possible end position as legal move from pos position for player"""
        validEnds = []
        possibleEnds = self.neighborDict[pos]
        for end in possibleEnds:
            button = self.getButton(end)
            if button["text"] == "":
                validEnds.append(end)

        return validEnds


    def actions(self, state):
        """Legal moves are any square not yet taken."""
        player = state.to_move
        moves = state.moves
        game_step = GameSteps[0]
        p = state.player1

        if player == 'X':
            game_step = state.player1.step
        else:
            game_step = state.player2.step
            p = state.player2

        if game_step == GameSteps[0]:
            return moves
        else:
            moves = self.findPossibleMoves(p, state)

        set(moves)
        list(moves)

        return moves


    def isMoveLegal(self, start, end, sym, state):
        """ check to see if cells with pos start and end are neighbors or not"""

        theNeigbors = self.neighborDict[start]

        player = state.to_move

        if player == 'X':
            player = state.player1
            opponent = state.player2
        else:
            player = state.player2
            opponent = state.player1


        if (end in theNeigbors) and (start in player.poses) and (end not in opponent.poses) and (end not in player.poses):
            return True

        return False



    def checkMillForPlayer(self, player, pos, state):
        """check if a mill has happened for player as result of the latest move to pos, if so apply the result which is remove
        a piece from the opponent."""

        theNeigbors = self.neighborDict[pos]
        mills = []
        board = state.board.copy()
        mil_flag = 0
        next_to_piece_flag = 0
        free_space_2mil_flag = 0
        opponent_next = 0

        opponent = state.player1
        playerr = state.player2
        if opponent.sym == player.sym:
            opponent = state.player2
            playerr = state.player1

        for next in theNeigbors:
            #check if next, pos, are part of a mill:

            if next in opponent.poses:
                opponent_next = 1

            if next in player.poses:
                next_to_piece_flag = 1
                x1,y1 = pos
                x2,y2 = next
                dx, dy = x1-x2, y1-y2
                x3,y3 = x2-dx, y2-dy
                x4, y4 = x1+dx, y1+dy
                if ((x3, y3) not in state.player1.poses) or ((x3, y3) not in state.player2.poses):
                    free_space_2mil_flag = 1

                if (x3,y3) in player.poses:
                    newmill = {pos, next, (x3, y3)}
                    if newmill not in mills:
                        mills.append(newmill)
                elif (x4, y4) in player.poses:
                    newmill = {pos, next, (x4, y4)}
                    if newmill not in mills:
                        mills.append(newmill)


        for i in range(len(mills)):

            # change random to something else
            mil_flag = 1
            pos2cull = random.choice(opponent.poses)

            board[pos2cull] = ""
            opponent.poses.remove(pos2cull)
            opponent.livePieces -= 1
            state.moves.append(pos2cull)

        return playerr, opponent, board, state, mil_flag, next_to_piece_flag, free_space_2mil_flag, opponent_next


    def free_cells(self, state):
        freecells = []

        spots = [(0, 0), (0, 3), (0, 6), (1, 1), (1, 3), (1, 5), (2, 2), (2, 3), (2, 4),
                 (3, 0), (3, 1), (3, 2), (3, 4), (3, 5), (3, 6), (4, 2), (4, 3), (4, 4), (5, 1), (5, 3),
                 (5, 5), (6, 0), (6, 3), (6, 6)]

        boardt = {}

        for pos in spots:
            boardt[pos] = ""
        for pos in state.player1.poses:
            boardt[pos] = 'X'
        for pos in state.player2.poses:
            boardt[pos] = 'O'

        for pos in spots:
            if (boardt[pos] != "X" or boardt[pos] != "0"):
                freecells.append(pos)

        return freecells



    def result(self, state, move, end):

        if state.to_move == 'X' and state.player1.step == GameSteps[1] \
                and (state.player1.type == PlayerType[3] or state.player2.type == PlayerType[3]
                     or state.player1.type == PlayerType[2] or state.player1.type == PlayerType[5] or state.player2.type == PlayerType[5]):
            a, b = move
            if a == 0 or a == 1 or a == 2 or a == 3 or a == 4 or a == 5 or a == 6 or a == 7 or a == 8 or a == 9:
                moves = self.findPossibleMoves(state.player1, state)
                state = state._replace(moves=moves)
                if len(moves) > 0:
                    move = random.choice(moves)
                else:
                    return state

        elif state.to_move == 'O' and state.player2.step == GameSteps[1]\
                and (state.player1.type == PlayerType[3] or state.player2.type == PlayerType[3]
                     or state.player2.type == PlayerType[2] or state.player2.type == PlayerType[5] or state.player1.type == PlayerType[5]):
            a, b = move
            if a == 0 or a == 1 or a == 2 or a == 3 or a == 4 or a == 5 or a == 6 or a == 7 or a == 8 or a == 9:
                moves = self.findPossibleMoves(state.player2, state)
                state = state._replace(moves=moves)
                if len(moves) > 0:
                    move = random.choice(moves)
                else:
                    return state

        if state.to_move == 'X' and state.player1.step == GameSteps[0]:
            t1, t2 = move
            if t1 == 0 or t1 == 1 or t1 == 2 or t1 == 3 or t1 == 4 or t1 == 5 or t1 == 6 or t1 == 7 or t1 == 8 or t1 == 9:
                pass
            else:
                moves = self.free_cells(state)
                state = state._replace(moves=moves)

                if len(moves) > 0:
                    move = random.choice(moves)
                else:
                    return state
        elif state.to_move == 'O' and state.player2.step == GameSteps[0]:
            t1, t2 = move
            if t1 == 0 or t1 == 1 or t1 == 2 or t1 == 3 or t1 == 4 or t1 == 5 or t1 == 6 or t1 == 7 or t1 == 8 or t1 == 9:
                pass
            else:
                moves = self.free_cells(state)
                state = state._replace(moves=moves)

                if len(moves) > 0:
                    move = random.choice(moves)
                else:
                    return state


        if time.time() > end:
            return state

        start, end = move

        # CHECK IF MOVE IS ILLEGAL HERE
        if state.to_move == 'X' and state.player1.step == GameSteps[0]:
            if move not in state.moves:
                return state  # Illegal move has no effect

        elif state.to_move == 'O' and state.player2.step == GameSteps[0]:
            if move not in state.moves:
                return state  # Illegal move has no effect

        if state.to_move == 'X' and state.player1.step == GameSteps[1]:
            if self.isMoveLegal(start, end, 'X', state):
                pass
            else:
                return state
        elif state.to_move == 'O' and state.player2.step == GameSteps[1]:
            if self.isMoveLegal(start, end, 'O', state):
                pass
            else:
                return state


        if (state.to_move == 'X' and state.player1.step == GameSteps[0]) or (state.to_move == 'O' and state.player2.step == GameSteps[0]):

            board = state.board.copy()
            board[move] = state.to_move

            if state.to_move == 'X':

                state.player1.poses.append(move)

                p1, p2, b, st, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next = self.checkMillForPlayer(state.player1, move, state)

                state = st
                state = state._replace(player1=p1, player2=p2)
                board = b

                moves = list(state.moves)

                moves.remove(move)

                if len(state.player1.poses) == state.player1.livePieces:

                    state.player1.step = GameSteps[1]
                    if state.player2.step == GameSteps[1] and state.player1.step == GameSteps[1]:
                        moves = self.findPossibleMoves(state.player2, state)

                return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                                 utility=self.compute_utility(state.to_move, state, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next),
                                 board=board, moves=moves, player1=state.player1, player2=state.player2,depth=state.depth+1)
            else:
                state.player2.poses.append(move)

                p1, p2, b, st, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next = self.checkMillForPlayer(state.player2, move, state)

                state = st
                state = state._replace(player1=p2, player2=p1)
                board = b

                moves = list(state.moves)
                moves.remove(move)

                if len(state.player2.poses) == state.player2.livePieces:
                    state.player2.step = GameSteps[1]
                    if state.player1.step == GameSteps[1] and state.player1.step == GameSteps[1]:
                        moves = self.findPossibleMoves(state.player1, state)

                return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                                 utility=self.compute_utility(state.to_move, state, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next),
                                 board=board, moves=moves, player1=state.player1, player2=state.player2,depth=state.depth+1)


        elif (state.to_move == 'O' and state.player2.step == GameSteps[1]) or (state.to_move == 'X' and state.player1.step == GameSteps[1]):

            state = self.move(start, end, state)

            if state.to_move == 'X':

                p1, p2, b, st, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next = self.checkMillForPlayer(state.player1, end, state)

                state = st
                state = state._replace(player1=p1, player2=p2)
                board = b

                moves = self.findPossibleMoves(state.player2, state)

                return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                                 utility=self.compute_utility(state.to_move, state, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next),
                                 board=board, moves=moves, player1=state.player1, player2=state.player2,depth=state.depth+1)
            else:

                p1, p2, b, st, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next = self.checkMillForPlayer(state.player2, end, state)

                state = st
                state = state._replace(player1=p2, player2=p1)
                board = b

                moves = self.findPossibleMoves(state.player1, state)

                return GameState(to_move=('O' if state.to_move == 'X' else 'X'),
                                 utility=self.compute_utility(state.to_move, state, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next),
                                 board=board, moves=moves, player1=state.player1, player2=state.player2,depth=state.depth+1)

        return state



    def move(self, start, end, state):
        """try to move a piece from start to end position"""

        player = state.to_move

        state.board[end] = player
        state.board[start] = ""

        if state.to_move == "X":
            state.player1.poses.remove(start)
            state.player1.poses.append(end)
        else:
            state.player2.poses.remove(start)
            state.player2.poses.append(end)

        return state




    def utility(self, state, player):
        """Return the value to player; 1 for win, -1 for loss, 0 otherwise."""
        return state.utility if player == 'X' else -state.utility


    # DON"T THINK I NEED THIS
    def is_legal_move(self, board, start, end, player):
        """ can be used to check if a move from start to end positions by player. This function can
        be called for example by get_all_moves() for checking validity of on-board piece moves
        """

        # DID NOT USE THIS FUNCTION SPECIFICALLY, SIMILAR ONE ABOVE
        pass

    # DON'T THINK I NEED THIS?
    def get_all_moves(self, board, player):
        """All possible moves for a player. Depending of the state of the game, it can
        include all positions to put a new piece, or all position to move the current pieces."""

        # DID NOT USE THIS FUNCTION SPECIFICALLY, SIMILAR ONE ABOVE
        pass

    def terminal_test(self, state):
        """A state is terminal if it is won or there are no empty squares."""

        #or state.depth >= 10
        if state.to_move == 'X':
            return state.player2.livePieces <= 2 or len(state.moves) == 0 or state.depth >= 20 or state.utility >= 3 or state.utility <= -2
        elif state.to_move == 'O':
            return state.player1.livePieces <= 2 or len(state.moves) == 0 or state.depth >= 20 or state.utility >= 3 or state.utility <= -2

        return False

    def display(self, state):
        board = state.board.copy()
        for x in range(1, self.h + 1):
            for y in range(1, self.v + 1):
                print(board.get((x, y), '.'), end=' ')
            print()

    def compute_utility(self, player, state, mil_f, next_to_piece_f, free_space_2mil_f, opponent_next):
        """If 'X' wins with this move, return 1; if 'O' wins return -1; else return 0."""

        util_value = 0

        if player == "X":

            if state.player1.livePieces < 3 or len(self.findPossibleMoves(state.player1, state)) == 0:
                return state.utility+100 if player == 'X' else state.utility-100

            if mil_f == 1:
                util_value = util_value + 3
                return state.utility + util_value if player == 'X' else state.utility - util_value

            if next_to_piece_f == 1:
                util_value = util_value + 1
                return state.utility + util_value if player == 'X' else state.utility - util_value

            if free_space_2mil_f == 1:
                util_value = util_value + 2
                return state.utility + util_value if player == 'X' else state.utility - util_value

            if opponent_next == 1:
                util_value = util_value - 1
                return state.utility + util_value if player == 'X' else state.utility - util_value


        else:
            if state.player2.livePieces < 3 or len(self.findPossibleMoves(state.player2, state)) == 0:
                return state.utility+100 if player == 'X' else state.utility-100

            if mil_f == 1:
                util_value = util_value + 3
                return state.utility + util_value if player == 'X' else state.utility - util_value

            if next_to_piece_f == 1:
                util_value = util_value + 1
                return state.utility + util_value if player == 'X' else state.utility - util_value

            if free_space_2mil_f == 1:
                util_value = util_value + 2
                return state.utility + util_value if player == 'X' else state.utility - util_value

            if opponent_next == 1:
                util_value = util_value - 1
                return state.utility + util_value if player == 'X' else state.utility - util_value

        return 0

    # DID NOT USE THIS FUNCTION, MADE MY OWN.
    def k_in_row(self, board, move, player, delta_x_y):
        """Return true if there is a line through move on board for player."""
        (delta_x, delta_y) = delta_x_y
        x, y = move
        n = 0  # n is number of moves in row
        while board.get((x, y)) == player:
            n += 1
            x, y = x + delta_x, y + delta_y
        x, y = move
        while board.get((x, y)) == player:
            n += 1
            x, y = x - delta_x, y - delta_y
        n -= 1  # Because we counted move itself twice
        return n >= self.k

