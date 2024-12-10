import connect4 as c4
from blondie24 import *
import numpy as np
import pickle
import os

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


print("opening network...")
with open('100g4dbest15Networks.pkl', 'rb') as f:
    blondies = pickle.load(f)
blondie = blondies[-1]
print("network opened.")


board = c4.createBoard()
while not c4.boardFull(board):
    _, blondieMove = blondie.alphabeta(board, 1, 5)
    c4.place(board, 1, blondieMove)
    os.system('clear')
    print(printPrettyBoard(board))
    if c4.checkWin(board) == 1:
        print("BLONDIE WINS!!")
        break

    playerMove = int(input("\n\nInput Column (1-7): ")) - 1
    c4.place(board, -1, playerMove)
    os.system('clear')
    print(printPrettyBoard(board))
    if c4.checkWin(board) == -1:
        print("YOU WIN!!")
        break
