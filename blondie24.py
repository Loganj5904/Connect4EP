import network
import connect4 as c4
import copy
import random
import math
import pickle

def getPossibleMoves(board):
    moves = []
    for i in range(7):
        boardCopy = copy.deepcopy(board)
        if c4.place(boardCopy, 1, i):
            moves.append(i)
    return moves


class Blondie(network.Network):

    def minimax(self, board, team=1, depth=8):
        if depth == 0:
            return self.evaluate(board), None
        
        if team == 1:
            bestScore = -math.inf
        else:
            bestScore = math.inf

        bestMove = None
        for move in getPossibleMoves(board):
            boardCopy = copy.deepcopy(board)
            if not c4.place(boardCopy, team, move):
                continue
            score, _ = self.minimax(boardCopy, -team, depth-1)
            
            if team ==1:
                if score > bestScore:
                    bestScore = score
                    bestMove = move
            else:
                if score < bestScore:
                    bestScore = score
                    bestMove = move
        
        return bestScore, bestMove

def playGame(player1, player2):
    board = c4.createBoard()
    
    while not c4.boardFull(board):
        _, player1Move = player1.minimax(board)
        c4.place(board, 1, player1Move)
        if c4.checkWin(board) == 1: return 1

        _, player2Move = player2.minimax(board)
        c4.place(board, -1, player2Move)
        if c4.checkWin(board) == -1: return -1

    return 0


def runES(generations = 840):
    networks = [Blondie() for _ in range(15)]
    offspring = [network.createOffspring() for network in networks]
    networks.append(offspring)

    for _ in range(generations):

        for currentNetwork in networks:
            possibleOpponents = [n for n in networks if n is not currentNetwork]
            selctedOpponents = random.choices(possibleOpponents, k=5)

            for opponent in selctedOpponents:
                if playGame(currentNetwork, opponent) == 1: currentNetwork.fitness += 1
                if playGame(currentNetwork, opponent) == 0: currentNetwork.fitness += 0
                if playGame(currentNetwork, opponent) == -1: currentNetwork.fitness += -2
            
        networks.sort(key=lambda g: g.fitness)
        networks = networks[:15] # select survivors
        offspring = [network.createOffspring() for network in networks]
        networks.append(offspring)
    
    networks.sort(key=lambda g: g.fitness)
    return networks[-1]

bestNetwork = runES()
with open('bestNetwork.pkl', 'wb') as f:
    pickle.dump(bestNetwork, f)


