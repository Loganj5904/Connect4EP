

def createBoard():
    cols = 7
    rows = 6
    board = []
    for x in range(cols):
        board.append([])
        for y in range(rows):
            board[x].append(0)

    return board

# team is a number, usually 1 or 2
def place(board, team, col):
    if boardFull(board):
        return False
    column = board[col]
    height = columnHeight(board, col)
    if height < len(column):
        board[col][height] = team
    else:
        newSpot = col + 1
        if newSpot > len(board) - 1:
            newSpot = 0
        return place(board, team, newSpot)
    return True

def placeBlondie(board, team, col):
    if boardFull(board):
        return False
    height = columnHeight(board, col)
    if height < len(board[col]):  # If the column is not full
        board[col][height] = team
        return True
    return False


def columnHeight(board, col):
    column = board[col]
    height = 0
    for i in range(len(column)):
        if column[i] != 0:
            height += 1
    return height


def boardFull(board):
    full = True
    for col in range(len(board)):
        if columnHeight(board, col) != len(board[col]):
            full = False
            break
    return full


def checkWin(board):
    checkDirections = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    width = len(board)
    height = len(board[width - 1])
    for col in range(width):
        for row in range(height):
            for direction in checkDirections:
                teamCheck = board[col][row]
                if teamCheck == 0:
                    break
                distance = 0
                probeX = col
                probeY = row
                while distance != 4 and 0 <= probeX < width and 0 <= probeY < height:
                    if board[probeX][probeY] == teamCheck:
                        distance += 1
                    else:
                        break
                    probeX += direction[0]
                    probeY += direction[1]
                if distance == 4:
                    return teamCheck
    return 0


def checkThrees(board, team):
    threeCount = 0
    checkDirections = [[1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]]
    width = len(board)
    height = len(board[width - 1])
    for col in range(width):
        for row in range(height):
            for direction in checkDirections:
                teamCheck = board[col][row]
                if teamCheck == 0:
                    break
                distance = 0
                probeX = col
                probeY = row
                while distance != 4 and 0 <= probeX < width and 0 <= probeY < height:
                    if board[probeX][probeY] == teamCheck:
                        distance += 1
                    else:
                        break
                    probeX += direction[0]
                    probeY += direction[1]
                if distance == 4:
                    threeCount += 1
    return threeCount


def printBoard(board):
    printString = "\n"
    for row in range(len(board[0])):
        for col in range(len(board)):
            printString += " [" + str(board[col][len(board[0]) - row - 1]) + "] "
        printString += "\n"
    return printString


def getBoardString(board):
    boardString = ""
    for row in range(len(board[0])):
        for col in range(len(board)):
            boardString += str(board[col][len(board[0]) - row - 1])
    return boardString
