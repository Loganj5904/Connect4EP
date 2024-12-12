from blondie24 import *
import population
import connect4
import pickle
import time

def compete(EPMachine, BLNetwork, turnStart=0):
    board = connect4.createBoard()
    gameLoop = True
    currentTurn = turnStart
    while gameLoop:
        if currentTurn == 0:
            start = time.time()
            col, _ = population.decideMove(EPMachine, board, turnStart == 0)
            full = not connect4.place(board, 1, col)
            if full:
                print("full board")
                return 0
            if connect4.checkWin(board):
                print("EP Win")
                return 1
            currentTurn = 1
            print("EP turn time:", time.time() - start)
        elif currentTurn == 1:
            start = time.time()
            col = BLNetwork.alphabeta(board, team=1, depth=4)[1]
            full = not connect4.place(board, -1, col)
            if full:
                print("full board")
                return 0
            if connect4.checkWin(board):
                print("BL Win")
                return 2
            currentTurn = 0
            print("BL turn time:", time.time() - start)


def runGames():
    results = []
    EPUnits = []
    with open('840g4dbest15Networks.pkl', 'rb') as f:
        BLUnits = pickle.load(f)

    with open('runNetworks.txt', 'rb') as f:
        for line in f:
            unitString = str(line).replace("b\'", "").replace("\'", "")
            if unitString != '':
                EPUnits.append(population.loadUnit(unitString))

    for epUnit in EPUnits:
        for blUnit in BLUnits:
            for turn in range(2):
                results = compete(epUnit, blUnit, turn)
                print(results, turn)