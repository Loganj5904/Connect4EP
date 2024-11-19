import connect4
import population

def main():
    board = connect4.createBoard()
    units = population.initializePopulation()
    runEP(units, board)


def playGameTest(board):
    while True:
        placement = int(input("team 1: "))
        full = not connect4.place(board, 1, placement)
        print(connect4.printBoard(board))
        if full:
            print("full board")
            break
        if connect4.checkWin(board) == 1:
            print("player 1 wins")
            break
        placement = int(input("team 2: "))
        full = not connect4.place(board, 2, placement)
        print(connect4.printBoard(board))
        if full:
            print("full board")
            break
        if connect4.checkWin(board) == 2:
            print("player 2 wins")
            break
    print(connect4.checkThrees(board, 1))
    print(connect4.checkThrees(board, 2))


def runEP(units, board):
    unitPopulation = units
    generations = 48999
    for g in range(generations):
        population.getFitnesses(unitPopulation)
        population.repopulate(unitPopulation, g + 1)
        print(g)
    file = open("savedUnits.txt", "a")
    for u in unitPopulation:
        file.write(population.saveUnit(u) + "\n")
    file.close()



if __name__ == '__main__':
    main()