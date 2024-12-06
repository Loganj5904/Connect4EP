import network
import connect4 as c4
import copy
import random
import math
import pickle
import pandas as pd

def printPrettyBoard(board):
    # ANSI escape codes for colors
    RED = "\033[91m●\033[0m"
    YELLOW = "\033[93m●\033[0m"
    EMPTY = " "  # For empty cells
    BLUE = "\033[94m"  # For board lines
    RESET = "\033[0m"  # Reset color

    # Build the string representation of the board
    printString = "\n" + " " + " ".join(f"{i + 1:2} " for i in range(len(board))) + "\n"  # Column numbers
    printString += (
        BLUE + "╔" + "═══╦" * (len(board) - 1) + "═══╗\n" + RESET
    )  # Top border

    for row in range(len(board[0]) - 1, -1, -1):  # Print rows from top to bottom
        printString += BLUE + "║" + RESET
        for col in range(len(board)):
            cell = board[col][row]
            if cell == 1:  # Player 1
                printString += f" {RED} {BLUE}║{RESET}"
            elif cell == -1 or cell == 2:  # Player 2
                printString += f" {YELLOW} {BLUE}║{RESET}"
            else:  # Empty
                printString += f" {EMPTY} {BLUE}║{RESET}"
        printString += "\n"
        if row > 0:  # Add horizontal separators between rows
            printString += (
                BLUE + "╠" + "═══╬" * (len(board) - 1) + "═══╣\n" + RESET
            )

    printString += (
        BLUE + "╚" + "═══╩" * (len(board) - 1) + "═══╝\n" + RESET
    )  # Bottom border
    return printString


def getPossibleMoves(board):
    moves = []
    for col in range(len(board)):  # Iterate over all columns
        height = c4.columnHeight(board, col)  # Check the height of the column
        if height < len(board[col]):  # If there's space in the column
            moves.append(col)
    return moves



class Blondie(network.Network):

    def minimax(self, board, team=1, depth=7):
        if depth == 0:
            return self.evaluate(board), None
        
        if team == 1:
            bestScore = -math.inf
        else:
            bestScore = math.inf

        bestMove = None
        for move in getPossibleMoves(board):
            boardCopy = copy.deepcopy(board)
            if not c4.placeBlondie(boardCopy, team, move):
                continue
            score, _ = self.minimax(boardCopy, -team, depth-1)

            if team == 1:
                if score > bestScore:
                    bestScore = score
                    bestMove = move
            else:
                if score < bestScore:
                    bestScore = score
                    bestMove = move
        
        return bestScore, bestMove


    def alphabeta(self, board, team=1, depth=7, alpha=-math.inf, beta=math.inf):
        if c4.boardFull(board):
            return self.evaluate(board), None
        if depth == 0:
            return self.evaluate(board), random.choice(getPossibleMoves(board))
        
        bestMove = None
        
        if team == 1:  # Maximizing player
            bestScore = -math.inf
            for move in getPossibleMoves(board):
                boardCopy = copy.deepcopy(board)
                if not c4.placeBlondie(boardCopy, team, move):
                    continue
                score, _ = self.alphabeta(boardCopy, -team, depth - 1, alpha, beta)
                if score > bestScore:
                    bestScore = score
                    bestMove = move
                alpha = max(alpha, bestScore)
                if beta <= alpha:
                    break  # Beta cutoff
        else:  # Minimizing player
            bestScore = math.inf
            for move in getPossibleMoves(board):
                boardCopy = copy.deepcopy(board)
                if not c4.placeBlondie(boardCopy, team, move):
                    continue
                score, _ = self.alphabeta(boardCopy, -team, depth - 1, alpha, beta)
                if score < bestScore:
                    bestScore = score
                    bestMove = move
                beta = min(beta, bestScore)
                if beta <= alpha:
                    break  # Alpha cutoff
        
        if bestMove == None:
            print("TEAM: ", team)
            print(printPrettyBoard(board))
            print("POSSIBLE MOVES: ", getPossibleMoves(board))
        return bestScore, bestMove



def playGame(player1, player2, depth, alphabeta=True):
    board = c4.createBoard()
    
    # Randomly choose which player starts
    current_player = random.choice([1, -1])
    
    while not c4.boardFull(board):
        if current_player == 1:
            if not alphabeta: 
                _, player1Move = player1.minimax(board, 1, depth)
            else:
                _, player1Move = player1.alphabeta(board, 1, depth)
            c4.placeBlondie(board, 1, player1Move)
            if c4.checkWin(board) == 1: return 1
            if c4.boardFull(board): return 0
            current_player = -1
        else:
            if not alphabeta:
                _, player2Move = player2.minimax(board, -1, depth)
            else:
                _, player2Move = player2.alphabeta(board, -1, depth)
            c4.placeBlondie(board, -1, player2Move)
            if c4.checkWin(board) == -1: return -1
            current_player = 1

    return 0


def runES(generations = 840, depth = 7, alphabeta=True):
    networks = [Blondie() for _ in range(15)]
    offspring = [network.createOffspring() for network in networks]
    networks.extend(offspring)

    averages = []

    for i in range(generations):
        print(f"Generation: {i+1}/{generations}; Depth = {depth+1}")

        j = 1
        totalNetFitness = 0
        for currentNetwork in networks:
            
            possibleOpponents = [n for n in networks if n is not currentNetwork]
            selctedOpponents = random.choices(possibleOpponents, k=5)

            for opponent in selctedOpponents: # play each of 5 selected opponents to determine current network's fitness
                
                outcome = playGame(currentNetwork, opponent, depth, True)
                if outcome == 1: currentNetwork.fitness += 1
                elif outcome == -1: currentNetwork.fitness -= 2

            print(f"net {j} fitness: {currentNetwork.fitness}")
            j += 1
            totalNetFitness += currentNetwork.fitness
        averageFitness = totalNetFitness/30
        averages.append(averageFitness)
        print("AVERAGE FITNESS FOR GENERATION: ", averageFitness)
        print("===========================")
            
        networks.sort(key=lambda g: g.fitness, reverse=True)
        networks = networks[:15] # select survivors
        for network in networks: network.fitness = 0 # reset fitness for new round
        offspring = [network.createOffspring() for network in networks] # create offspring from selected individuals
        networks.extend(offspring)

    # dataframe to plot fitness over time
    fitnessDf = pd.DataFrame({'averageFitness': averages})
    fitnessDf.to_csv(f'{generations}g{depth+1}dfitnessOverTime.csv')
    
    networks.sort(key=lambda g: g.fitness)
    return networks # save top 15 networks

if __name__ == "__main__":
    bestNetworks = runES(840, 3)
    with open('840g4dbest15Networks.pkl', 'wb') as f:
        pickle.dump(bestNetworks, f) 


