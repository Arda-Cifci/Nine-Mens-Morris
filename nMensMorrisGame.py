import random
import time
from tkinter import *
import tkinter.font as font
from games import NMensMorris
import games
from collections import namedtuple
import sys
import copy
sys.setrecursionlimit(2000)

"""
Playertype Options are Human: # means this is human player. Then the player has to manually click on spots on gameboard to make a move
Random: # For AI player. Chooses randomly among all possible move options
MinMax: # For AI player. Uses MinMax adversarial algorithm all the way to the leaf nodes 
AlphaBeta(MinMax with Alpha-Beta Pruning): # For AI player. Uses AlphaBeta algorithm all the way to the leaf
AlphaBetaCutoff (AlphaBeta with cutoff depth): # For AI player. Similar to AlphaBeta case, except now the computation is cutoff at a depth d and an evaluation function is used at that level for Utility value
ExpectimaxCutoff: Use chance nodes instead of the min nodes. This means at min level, use average of all successors' utility value. Similar to abov case, computation is cutoff at depth d
"""
PlayerType = ["Human", "Random", "MinMax", "AlphaBeta", "AlphaBetaCutoff", "ExpectimaxCutoff"]
GameState = namedtuple('GameState', 'to_move, utility, board, moves, player1, player2, depth')

class Cell:
    pos = (0, 0)
    button = None
    def __init__(self, pos, btn):
        self.pos = pos
        self.button = btn


"""# game has 2 steps for each player: setting up step in which player is setting up his 9 pieces,
and next step is 'Move' step where she is moving her pieces around the board. """

GameSteps = ['Setup', 'Move']


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


class BoardGui(Frame):
    cells = []  # all the cells of the board
    to_move = "X"  # It can have 2 values: X for human player  or O for AI player
    dims = 7  # game board dimension : 7 x 7
    neighborDict = {}   # a dictionary of assigning neighbor cells to each cell.
    stop_flag = 0

    def __init__(self, parent, board):

        self.depth = -1  # -1 means search up to leaf level. So no restriction
        self.player1 = NMMPlayer(0, PlayerType[0], "X")
        self.player2 = NMMPlayer(1, PlayerType[1], "O")
        game.player1 = self.player1
        game.player2 = self.player2
        game.cells = self.cells

        self.game = board
        self.parent = parent

        # setup the game board:
        for i in range(self.dims):
            parent.columnconfigure(i, weight=1, minsize=75)
            parent.rowconfigure(i, weight=1, minsize=50)
            cellsInFrame = []
            for j in range(0, self.dims):
                frame = Frame( master=parent, relief=RAISED, borderwidth=1)
                frame.grid(row=i, column=j, padx=5, pady=5)
                if((i%6 == 0 and j%3 == 0) or
                    (i%4 == 1 and j%2 == 1 ) or
                    ((i == 2 or i == 4) and (j==2 or j==3 or j==4)) or
                    (i == 3 and j != 3)):
                        button = Button(master=frame, width=3, text="", bg="pink")
                        button['font'] = font.Font(family='Helvetica')
                        button.config(command=lambda btn=button: self.on_click(btn))
                        button.pack(padx=5, pady=5)
                        cellsInFrame.append(Cell([i, j], button))
                elif(i==3 and j==3):
                    frame.config(height= 30, width=30, bg='black')
                else:
                    frame.config(height=3, bg='black', width=30)

            self.cells.append(cellsInFrame)

        # setup the UI panel:
        parent.rowconfigure(self.dims, weight=1, minsize=75)

        newButton = Button(parent, text="New", fg="white", bg="blue", command=self.reset)
        newButton.grid(row=self.dims, column=0, padx=5, pady=5)

        quitButton = Button(parent, text="Quit", fg="white", bg="black", command=self.quit)
        quitButton.grid(row=self.dims, column=1, padx=5, pady=5)

        """Player1 can be either Human or AI player"""
        choiceStr = StringVar(parent)
        choiceStr.set(PlayerType[0])
        menu = OptionMenu(parent, choiceStr, *PlayerType, command=self.set_player1)
        menu.grid(row=self.dims, column=2, padx=1, pady=5)

        """Player2 can be only AI player"""
        choiceStr = StringVar(parent)
        choiceStr.set(PlayerType[1])
        menu = OptionMenu(parent, choiceStr, *PlayerType[1:], command=self.set_player2)
        menu.grid(row=self.dims, column=3, padx=1, pady=5)

        """'nextbutton' is used to step through the game when 2 AI players are playing against each other.
         Each clicking on next plays one sequence of Player1-Player2"""
        nextButton = Button(master=parent, text="next", borderwidth=1, border=1, command=self.on_click_AI)
        nextButton.grid(row=self.dims, column=4, padx=1, pady=5)

        depthLabel = Label(master=parent, text="Depth:", width=10)
        depthLabel.grid(row=self.dims, column=5, padx=1, pady=5)
        depthStr = StringVar()
        depthStr.set(str(self.depth))
        self.depthEntry = Entry(parent, width =7, textvariable=depthStr)
        self.depthEntry.grid(row=self.dims, column=6, padx=1, pady=5)
        depthButton = Button(parent, text="Set Depth", command=self.set_depth)
        depthButton.grid(row=self.dims, column=8, padx=25, pady=5)

        # setting up UI panel for points and stats of each player
        parent.rowconfigure(self.dims+1, weight=1, minsize=75)
        self.player1Label = Label(master=parent, text="LivePieces_1:"+str(self.player1.livePieces), fg="white", bg="blue", width=15)
        self.player1Label.grid(row=self.dims+1, column=0, padx=1, pady=2)
        self.player2Label = Label(master=parent, text="LivePieces_2:"+str(self.player2.livePieces), fg="white", bg="red", width=15)
        self.player2Label.grid(row=self.dims+1, column=3, padx=1, pady=2)

        self.gameResultLabel = Label(master=parent, text="Player1 Turn:", fg="white", bg="black", width=13)
        self.gameResultLabel.grid(row=self.dims+1, column=5, padx=2, pady=2)

        self.setupNeighborhood()



    def reset(self):
        """reset the game's board"""
        print("Resetting the game.")

        for row in self.cells:
            for x in row:
                x.button.config(state='normal', text="")

        self.stop_flag = 0
        self.player1.reset()
        self.player2.reset()
        self.player1Label["text"] = "LivePieces_1:"+str(self.player1.livePieces)
        self.player2Label["text"] = "LivePieces_2:"+str(self.player2.livePieces)
        self.gameResultLabel["text"] = "Player1 Turn:"

    def setupNeighborhood(self):
        """fills up the dictionary of neighborhood, to be used to find out what cells are neighbors (means player can move to them) to a cell"""
        #row 0
        self.neighborDict[(0, 0)] = [(0, 3), (1, 1), (3, 0)]
        self.neighborDict[(0, 3)] = [(0, 0), (0, 6), (1, 3)]
        self.neighborDict[(0, 6)] = [(0, 3), (1, 5), (3, 6)]

        #row 1
        self.neighborDict[(1, 1)] = [(0, 0), (1, 3), (3, 1), (2, 2)]
        self.neighborDict[(1, 3)] = [(0, 3), (1, 1), (1, 5), (2, 3)]
        self.neighborDict[(1, 5)] = [(0, 6), (1, 3), (2, 4), (3, 5)]

        #row 2
        self.neighborDict[(2, 2)] = [(2, 3), (3, 2), (1, 1)]
        self.neighborDict[(2, 3)] = [(2, 2), (1, 3), (2, 4)]
        self.neighborDict[(2, 4)] = [(2, 3), (3, 4), (1, 5)]

        #row 3
        self.neighborDict[(3, 0)] = [(0, 0), (6, 0), (3, 1)]
        self.neighborDict[(3, 1)] = [(3, 0), (3, 2), (1, 1), (5, 1)]
        self.neighborDict[(3, 2)] = [(3, 1), (2, 2), (4, 2)]
        self.neighborDict[(3, 4)] = [(3, 5), (2, 4), (4, 4)]
        self.neighborDict[(3, 5)] = [(3, 4), (3, 6), (1, 5), (5, 5)]
        self.neighborDict[(3, 6)] = [(3, 5), (0, 6), (6, 6)]

        #row 4
        self.neighborDict[(4, 2)] = [(4, 3), (3, 2), (5, 1)]
        self.neighborDict[(4, 3)] = [(4, 2), (4, 4), (5, 3)]
        self.neighborDict[(4, 4)] = [(4, 3), (3, 4), (5, 5)]

        #row 5
        self.neighborDict[(5, 1)] = [(6, 0), (5, 3), (3, 1), (4, 2)]
        self.neighborDict[(5, 3)] = [(6, 3), (5, 1), (5, 5), (4, 3)]
        self.neighborDict[(5, 5)] = [(6, 6), (5, 3), (4, 4), (3, 5)]

        #row 6
        self.neighborDict[(6, 0)] = [(6, 3), (5, 1), (3, 0)]
        self.neighborDict[(6, 3)] = [(6, 0), (6, 6), (5, 3)]
        self.neighborDict[(6, 6)] = [(6, 3), (5, 5), (3, 6)]


    def set_player1(self, choice):
        """ Set the level of first player. If chosen Human, it is human player.
        """
        self.player1.type = choice
        print("set_player1: level set to ", self.player1.type)

    def set_player2(self, choice):
        """ Set the level of second player. Same as above.
        """
        self.player2.type = choice
        print("set_player2: level set to ", self.player2.type)

    def set_depth(self):
        """Sets the depth to be used for cut-off searches for corresponding search: alpha_beta_cutoff
        Note: This is used for any player with type which use depth value
        """
        x = self.depthEntry.get()
        self.depth = int(x)
        print("set_depth: depth set to ", int(x))

    def getCoordinates(self, btn):
        try:
            for i in range(self.dims):
                row = self.cells[i]
                for j in range(len(row)):
                    if row[j].button == btn:
                        return row[j].pos
        except IndexError:
            print("ERROR! getCoordinate(): could not find the button's indices\n")
            return

    def printBoard(self):
        try:
            for i in range(self.dims):
                for j in range(self.cells[i]):
                    cell = self.cells[i][j]
                    print("Cell: ",i, ", ",j, ", text:", cell.button["text"])
                print("\n")
        except IndexError:
            print("printboard: index error ")


    def quit(self):
        print("Quitting the game.")
        self.parent.destroy()

    def getButton(self, pos):
        lpos = list(pos)
        for cellrow in self.cells:
            for cell in cellrow:
                if cell.pos == lpos:
                    return cell.button

        print("getButton(): button at pos ", pos, " is not found")
        raise "getButton: wrong position passed!"
        return None

    def disable_game(self):
        """
        This function deactivates the game after a win, loss or draw or error.
        """
        self.stop_flag = 1
        for row in self.cells:
            for x in row:
                x.button.config(state='disable')


    def on_click_AI(self):

        if self.player1.type == PlayerType[0]:
            print("Human player detected, button disabled.")
        elif self.player1.type == PlayerType[1]:
            print("Random AI finding move for X.")
            self.randomPlayerMove("X")
        elif self.player1.type == PlayerType[2]:
            self.ai_move("X", "MinMax")
        elif self.player1.type == PlayerType[3]:
            self.ai_move("X", "AlphaBeta")
        elif self.player1.type == PlayerType[4]:
            self.ai_move("X", "AlphaBetaCutoff")
        elif self.player1.type == PlayerType[5]:
            self.ai_move("X", "ExpectimaxCutoff")


        if self.player1.type == PlayerType[0]:
            pass
        elif self.player2.type == PlayerType[1] and self.stop_flag != 1:
            print("Random AI finding move for O.")
            self.randomPlayerMove("O")
        elif self.player2.type == PlayerType[2] and self.stop_flag != 1:
            self.ai_move("O", "MinMax")
        elif self.player2.type == PlayerType[3] and self.stop_flag != 1:
            self.ai_move("O", "AlphaBeta")
        elif self.player2.type == PlayerType[4] and self.stop_flag != 1:
            self.ai_move("O", "AlphaBetaCutoff")
        elif self.player2.type == PlayerType[5] and self.stop_flag != 1:
            self.ai_move("O", "ExpectimaxCutoff")



    def ai_move(self, player, algo):
        """randomly select a move for player"""

        if player == "O":
            curPlayer = self.player2
        else:
            curPlayer = self.player1


        if curPlayer.step == GameSteps[0]:

            freeCells = []
            x_positions = []
            o_positions = []
            for cellrow in self.cells:
                for cell in cellrow:
                    if cell.button["text"] == "":
                        x, y = cell.pos
                        freeCells.append((x, y))
                    if cell.button["text"] == "X":
                        x, y = cell.pos
                        x_positions.append((x, y))
                    if cell.button["text"] == "O":
                        x, y = cell.pos
                        o_positions.append((x, y))
            board = {}

            for pos in x_positions:
                board[pos] = 'X'
            for pos in o_positions:
                board[pos] = 'O'

            state = GameState(to_move=player, utility=0, board=board, moves=freeCells, player1=self.player1, player2=self.player2, depth=0)

            savep1 = copy.deepcopy(self.player1)
            savep2 = copy.deepcopy(self.player2)


            if algo == "MinMax" :
                print("MinMax AI calculating, please wait 5 seconds...")
                x, y = games.minmax_decision(state, game)
            elif algo == "AlphaBeta":
                print("AlphaBeta AI calculating, please wait 5 seconds...")
                x, y = games.alpha_beta_search(state, game)
            elif algo == "AlphaBetaCutoff":
                print("AlphaBetaCutoff calculating, please wait 5 seconds...")
                x, y = games.alpha_beta_cutoff_search(state, game, d=self.depth)
            elif algo == "ExpectimaxCutoff":
                print("ExpectimaxCutoff calculating, please wait 5 seconds...")
                x, y = games.expect_minmax(state, game, d=self.depth)

            self.player1 = savep1
            self.player2 = savep2

            if player == "O":
                curPlayer = self.player2
            else:
                curPlayer = self.player1

            if len(curPlayer.poses) < curPlayer.livePieces:  # means we are in phase 1 of the game still putting down new pieces

                curPlayer.poses.append((x, y))
                button = self.getButton((x, y))
                if button is None:
                    print("!!ERROR! getButton returned null. Error")
                    return

                button.config(text=player, state='disabled', disabledforeground="green")

                print("AI Move: button.text=", button['text'], "pos: ", x, ", ", y)

                self.checkMillForPlayer(curPlayer, (x, y))
                if len(curPlayer.poses) == curPlayer.livePieces:
                    curPlayer.step = GameSteps[1]
                    self.enablePlayerCells(curPlayer.poses)

        else:  # means we are in phase 2 mode, meaning player need to move a piece.

            freeCells = []
            x_positions = []
            o_positions = []
            for cellrow in self.cells:
                for cell in cellrow:
                    if cell.button["text"] == "":
                        x, y = cell.pos
                        freeCells.append((x, y))
                    if cell.button["text"] == "X":
                        x, y = cell.pos
                        x_positions.append((x, y))
                    if cell.button["text"] == "O":
                        x, y = cell.pos
                        o_positions.append((x, y))
            board = {}

            for pos in x_positions:
                board[pos] = 'X'
            for pos in o_positions:
                board[pos] = 'O'

            potentialMoves = self.findPossibleMoves2(curPlayer)

            state = GameState(to_move=player, utility=0, board=board, moves=potentialMoves, player1=self.player1,
                             player2=self.player2, depth=0)

            savep1 = copy.deepcopy(self.player1)
            savep2 = copy.deepcopy(self.player2)

            if algo == "MinMax":
                print("MinMax AI calculating, please wait 5 seconds...")
                start, end = games.minmax_decision(state, game)
            elif algo == "AlphaBeta":
                print("AlphaBeta AI calculating, please wait 5 seconds...")
                start, end = games.alpha_beta_search(state, game)
            elif algo == "AlphaBetaCutoff":
                print("AlphaBetaCutoff calculating, please wait 5 seconds...")
                start, end = games.alpha_beta_cutoff_search(state, game, d=self.depth)
            elif algo == "ExpectimaxCutoff":
                print("ExpectimaxCutoff calculating, please wait 5 seconds...")
                start, end = games.expect_minmax(state, game, d=self.depth)

            self.player1 = copy.deepcopy(savep1)
            self.player2 = copy.deepcopy(savep2)

            if player == "O":
                curPlayer = self.player2
            else:
                curPlayer = self.player1

            #  # find all possible moves for this player
            if start == None or end == None:
                print("!No more move possible for player ", player)
                return

            time.sleep(0.1)

            # apply the move:
            if self.move(start, end, player) == True:

                time.sleep(0.1)
                curPlayer.poses.remove(start)
                curPlayer.poses.append(end)
                self.checkMillForPlayer(curPlayer, end)



    def on_click(self, button):
        """ is used to step through the game. If Player1 is Human, then on_click is called when Human
        player clicks on an available spot. In case of AI vs AI playing, on_click is called as result
        of pressing 'next' button. """
        x, y = self.getCoordinates(button)

        if self.player1.step == GameSteps[0]:
            if len(self.player1.poses) < self.player1.livePieces:  # means we are in phase 1 of the game still putting down new pieces
                self.player1.poses.append((x, y))
                button.config(text=self.to_move, state='disabled', disabledforeground="green")
                print("Human onClick: button.text=", button['text'], "pos: ", x, ", ", y)
                self.checkMillForPlayer(self.player1, (x, y))
                if len(self.player1.poses) == self.player1.livePieces:
                    self.player1.step = GameSteps[1]
                    self.enablePlayerCells(self.player1.poses)

        else:   # means we are in phase 2 mode, meaning player need to move a piece.
            if (x, y) in self.player1.poses:
                self.player1.picked = (x, y)
                print("item at cell index ", self.player1.picked , " picked")
                return
            elif self.player1.picked is not None:
                start = self.player1.picked
                print("attempt to move a piece from loc [", start[0], ", ",start[1], "] to location [", x, ",", y, "]")
                if self.move(start, (x,y), self.player1.sym) == True:
                    self.player1.poses.remove(start)
                    self.player1.poses.append((x,y))
                    self.checkMillForPlayer(self.player1, (x, y))

                self.player1.picked = None
            else:
                print("Warning: to move a piece, click on one of your existing pieces!")
                return

        time.sleep(0.5)

        if self.player2.type == PlayerType[1] and self.stop_flag != 1:
            print("Random AI finding move for X.")
            self.randomPlayerMove("O")
        elif self.player2.type == PlayerType[2] and self.stop_flag != 1:
            self.ai_move("O", "MinMax")
        elif self.player2.type == PlayerType[3] and self.stop_flag != 1:
            self.ai_move("O", "AlphaBeta")
        elif self.player2.type == PlayerType[4] and self.stop_flag != 1:
            self.ai_move("O", "AlphaBetaCutoff")
        elif self.player2.type == PlayerType[5] and self.stop_flag != 1:
            self.ai_move("O", "ExpectimaxCutoff")


    def randomPlayerMove(self, player):
        """randomly select a move for player"""

        curPlayer = self.player1
        if player == "O":
            curPlayer = self.player2


        if curPlayer.step == GameSteps[0]:
            x, y = self.randomFreePick()
            if len(curPlayer.poses) < curPlayer.livePieces:  # means we are in phase 1 of the game still putting down new pieces
                curPlayer.poses.append((x, y))
                button = self.getButton((x, y))
                if button is None:
                    print("!!ERROR! getButton returned null. Error")
                    return

                button.config(text=player, state='disabled', disabledforeground="green")
                print("randomPlayerMove: button.text=", button['text'], "pos: ", x, ", ", y)
                self.checkMillForPlayer(curPlayer, (x, y))
                if len(curPlayer.poses) == curPlayer.livePieces:
                    curPlayer.step = GameSteps[1]
                    self.enablePlayerCells(curPlayer.poses)

        else:   # means we are in phase 2 mode, meaning player need to move a piece.
            potentialMoves = self.findPossibleMoves(curPlayer)   # find all possible moves for this player

            if len(potentialMoves) == 0:
                print("!No more move possible for player ", player)
                return

            start, moves = random.choice(list(potentialMoves.items()))  # pick a piece to move randomly
            end = random.choice(moves) # pick a legal move for the selected piece randomly

            # apply the move:
            if self.move(start, end, player) == True:
                    curPlayer.poses.remove(start)
                    curPlayer.poses.append(end)
                    self.checkMillForPlayer(curPlayer, end)


    def checkMillForPlayer(self, player, pos):
        """check if a mill has happened for player as result of the latest move to pos, if so apply the result which is remove
        a piece from the opponent."""
        theNeigbors = self.neighborDict[pos]
        mills = []
        for next in theNeigbors:
            #check if next, pos, are part of a mill:
            if next in player.poses:
                x1,y1 = pos
                x2,y2 = next
                dx, dy = x1-x2, y1-y2
                x3,y3 = x2-dx, y2-dy
                x4, y4 = x1+dx, y1+dy
                if (x3,y3) in player.poses:
                    newmill = {pos, next, (x3, y3)}
                    if newmill not in mills:
                        mills.append(newmill)
                elif (x4, y4) in player.poses:
                    newmill = {pos, next, (x4, y4)}
                    if newmill not in mills:
                        mills.append(newmill)

        opponent = self.player1
        if opponent.sym == player.sym:
            opponent = self.player2

        for i in range(len(mills)):
            print("Mill for ", player.sym, ": ", str(mills[i]))
            pos2cull = self.remove_piece(opponent)
            print("culling ", str(pos2cull), " from player ", opponent.sym)

            thebutton = self.getButton(pos2cull)
            thebutton["text"] = ""
            thebutton.config(state='normal')
            opponent.poses.remove(pos2cull)

            opponent.livePieces -= 1
            self.checkStatus(opponent)
            self.player1Label["text"]="LivePieces_1:"+str(self.player1.livePieces)
            self.player2Label["text"]="LivePieces_2:"+str(self.player2.livePieces)
            time.sleep(0.5)

    def remove_piece(self, opponent):
        poses = opponent.poses

        for x in poses:
            theNeigbors = self.neighborDict[x]

            for next in theNeigbors:
                if next in opponent.poses:
                    x1,y1 = x
                    x2,y2 = next
                    dx, dy = x1-x2, y1-y2
                    x3,y3 = x2-dx, y2-dy
                    x4, y4 = x1+dx, y1+dy
                    if ((x3,y3) not in opponent.poses) and ((x4, y4) not in opponent.poses):
                        return x
                    else:
                        continue

        return random.choice(opponent.poses)

    def randomFreePick(self):
        """Randomly pick a free position on the board"""
        freeCells = []
        for cellrow in self.cells:
            for cell in cellrow:
                if cell.button["text"] == "":
                    freeCells.append(tuple(cell.pos))

        aFreePos = random.choice(freeCells)
        a, b = aFreePos
        return a, b

    def checkStatus(self, player):
        """ check if player is still in the game and not lost"""
        if player.livePieces < 3 or len(self.findPossibleMoves(player)) == 0:
            print("Not enough pieces or No possible move for player ", player.sym, " possible. Game OVER!")
            self.gameResultLabel["text"] = player.sym + " LOST!"
            self.disable_game()



    def findPossibleMoves2(self, player):
        """For player find all the pieces which can potentially move"""
        moves = []

        if player.sym == "X":
            opponent = self.player2
        else:
            opponent = self.player1

        for pos in player.poses:
            possibleEnds = self.findPossibleEnds(player, pos)
            if len(possibleEnds) > 0:
                for x in range(len(possibleEnds)):
                    if (possibleEnds[x] not in opponent.poses) and (possibleEnds[x] not in player.poses):
                        moves.append((pos, possibleEnds[x]))

        return moves

    def findPossibleMoves(self, player):
        """For player find all the pieces which can potentially move"""
        moves = {}   # a dictionary of start:[possible ends] which represent a start position as key, all possible end positions as value

        for pos in player.poses:
            possibleEnds = self.findPossibleEnds(player, pos)
            if len(possibleEnds) > 0:
                moves[pos] = possibleEnds

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


    def enablePlayerCells(self, poses):
        """go through all the cells occupied by positions in pos array and enable their buttons for clicking"""
        for pos in poses:
            for row in self.cells:
                for cell in row:
                    if cell.pos == list(pos):
                        cell.button.config(state='normal')

    def move(self, start, end, sym):
        """try to move a piece from start to end position"""
        print("move: ", sym, " from ", str(start), " to ", str(end))
        x, y = start
        a, b = end
        for sCell in self.cells[x]:
            if sCell.pos == list(start):
                assert sCell.button["text"] == sym, "move: Error: start cell has wrong symbol"
                for eCell in self.cells[a]:
                    if eCell.pos == list(end):
                        if eCell.button["text"] != "":
                            print("move: end cell is not empty! Ignoring move request")
                        elif self.isMoveLegal(start, end, sym):
                            eCell.button["text"] = sCell.button["text"]
                            sCell.button["text"] = ""
                            sCell.button.config(state='normal')
                            time.sleep(0.4)
                            return True
                        else:
                            print("move: The move from ", str(start), " to ", str(end), " is not legal. Ignore the move request.")
                            return False

        print("!Failed to move successfully")

        return False

    def isMoveLegal(self, start, end, sym):
        """ check to see if cells with pos start and end are neighbors or not"""
        theNeigbors = self.neighborDict[start]
        if end in theNeigbors:
            return True

        theplayer = self.player1
        if theplayer.sym != sym:
            theplayer = self.player2

        if theplayer.livePieces == 3:   # means theplayer is in jump mode.
            return True
        return False



def initialize(nmm):
    root = Tk()
    root.title("9 MensMorris Game")

    gui = BoardGui(root, nmm)

    root.resizable(1,1)
    root.mainloop()

if __name__ == "__main__":
    game = NMensMorris()
    initialize(game)
