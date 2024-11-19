import random
import connect4
import copy

unitTemplate = {
    "info": {"id": 0, "fitness": 0, "birthGeneration": 0, "startState": 0, "stateCount": 0, "col0": 1, "col1": 1, "col2": 1, "col3": 1, "col4": 1,
             "col5": 1, "col6": 1}, "stateMachine": [], "currentGame": {"currentState": 0}}

stateTemplate = [0, [0, 0, 0]]
# state template:
# index 0 is the state output, from 0-6
# index 1 contains the transitions of the state:
# each transition is marked by its index to the next state
populationCount = 100
mutationCount = 2
stateCountMax = 300
currentID = 1
startStateCount = 14

def initializePopulation():
    global currentID
    global startStateCount
    population = []
    for count in range(populationCount):

        newUnit = copy.deepcopy(unitTemplate)
        newUnit["info"]["generation"] = 0
        newUnit["info"]["id"] = currentID
        currentID += 1
        for i in range(startStateCount):
            newUnit["stateMachine"].append(copy.deepcopy(stateTemplate))
            newUnit["stateMachine"][i][0] = random.randint(0, 6)
            newUnit["stateMachine"][i][1][0] = random.randint(0, startStateCount - 1)
            newUnit["stateMachine"][i][1][1] = random.randint(0, startStateCount - 1)
            newUnit["stateMachine"][i][1][2] = random.randint(0, startStateCount - 1)
        newUnit["info"]["stateCount"] = startStateCount
        population.append(newUnit)
    return population


def getFitnesses(units):
    opponents = 5
    weightOfStateCount = 0.7
    for u in units:
        u["info"]["fitness"] = 0
        choices = []
        for o in range(opponents):
            chosen = False
            while not chosen:
                randOpponent = random.choice(units)
                if not choices.__contains__(randOpponent):
                    choices.append(randOpponent)
                    chosen = True
        for o in choices:
            win = playGame(u, o, connect4.createBoard())
            if win == 1:
                u["info"]["fitness"] += 1

        u["info"]["fitness"] += (u["info"]["stateCount"] / stateCountMax) * weightOfStateCount


def tournament(units):
    choices = list(range(populationCount))
    winners = []
    player1Wins = 0
    player2Wins = 0
    for i in range(int(populationCount / 2)):
        choice1 = random.choice(choices)
        choices.remove(choice1)
        choice2 = random.choice(choices)
        choices.remove(choice2)
        board = connect4.createBoard()
        # apparently only player 2 wins after the first generation
        winner, turns = playGame(units[choice1], units[choice2], board)
        if winner == 1:
            units[choice1]["info"]["fitness"] = turns / (7*6)
            units[choice2]["info"]["fitness"] = (7 * 6) / -turns
            player1Wins += 1
        elif winner == 2:
            units[choice2]["info"]["fitness"] = turns / (7 * 6)
            units[choice1]["info"]["fitness"] = (7 * 6) / -turns
            player2Wins += 1
        else:
            units[choice1]["info"]["fitness"] = 0
            units[choice2]["info"]["fitness"] = 0


def playGame(player1, player2, board):
    player1Number = 1
    player2Number = 2
    gameLoop = True
    tie = False
    turns = 0
    while gameLoop:
        valid = connect4.place(board, player1Number, decideMove(player1, board))
        if not valid:
            gameLoop = False
            tie = True
            break
        turns += 1
        win = connect4.checkWin(board)
        if win:
            return player1Number
        valid = connect4.place(board, player2Number, decideMove(player2, board))
        if not valid:
            gameLoop = False
            tie = True
            break
        turns += 1
        win = connect4.checkWin(board)
        if win:
            return player2Number
    if tie:
        return 0


def decideMove(player, board, player2=False):
    stateMachine = player["stateMachine"]
    currentPosition = player["info"]["startState"]
    boardString = connect4.getBoardString(board)
    if player2:
        boardString = boardString.replace("1", "a")
        boardString = boardString.replace("2", "1")
        boardString = boardString.replace("a", "2")
    for char in boardString:
        currentPosition = stateMachine[currentPosition][1][int(char)]
    return stateMachine[currentPosition][0]


def repopulate(units, generation):
    global currentID
    unitCheck = 20
    unitReplace = 10
    unitStage = []
    for i in range(unitCheck):
        repeat = False
        while not repeat:
            repeat = True
            choice = random.choice(units)
            if choice in unitStage:
                repeat = False
        unitStage.append(choice)
    unitStage.sort(key=getFit)
    for unit in range(len(unitStage)):
        unitStage[unit] = [unitStage[unit], unit]
    alive = []

    for choice in range(unitReplace):
        choice = random.randint(0, sum(range(len(unitStage))))
        count = 0
        for unit in range(len(unitStage)):
            count += unitStage[unit][1]
            if count >= choice:
                alive.append(unitStage[unit])
                del unitStage[unit]
                break
    for unit in unitStage:
        units.remove(unit[0])
    for unit in alive:
        if len(alive) < 10:
            what = True
        newUnit = copy.deepcopy(unit[0])
        newUnit["info"]["id"] = currentID
        newUnit["info"]["birthGeneration"] = generation
        currentID += 1
        mutate(newUnit)
        units.append(newUnit)
    if len(units) < populationCount:
        what = True

    return 0


def mutate(unit):
    mutations = [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 3, 3, 4, 4, 4]
    for m in range(mutationCount):
        mutation = random.choice(mutations)
        if mutation == 1: # change transition of state
            stateChoice = random.randint(0, unit["info"]["stateCount"] - 1)
            destChoice = random.randint(0, unit["info"]["stateCount"] - 1)
            inputChoice = random.randint(0, 2)
            unit["stateMachine"][stateChoice][1][inputChoice] = destChoice
        if mutation == 2: # add state
            if unit["info"]["stateCount"] == stateCountMax:
                pass
            else:
                unit["stateMachine"].append(copy.deepcopy(stateTemplate))
                unit["stateMachine"][unit["info"]["stateCount"]][0] = random.randint(0, 6)
                unit["stateMachine"][unit["info"]["stateCount"]][1][0] = random.randint(0, unit["info"]["stateCount"])
                unit["stateMachine"][unit["info"]["stateCount"]][1][1] = random.randint(0, unit["info"]["stateCount"])
                unit["stateMachine"][unit["info"]["stateCount"]][1][2] = random.randint(0, unit["info"]["stateCount"])
                unit["info"]["stateCount"] += 1
        if mutation == 3: # remove state
            if unit["info"]["stateCount"] == 1:
                pass
            else:

                choices = list(range(len(unit["stateMachine"])))
                deleteState = random.choice(choices)

                dests = [unit["stateMachine"][deleteState][1][0], unit["stateMachine"][deleteState][1][1], unit["stateMachine"][deleteState][1][2]]

                for state in range(len(unit["stateMachine"])):
                    for i in range(0, 3):
                        if unit["stateMachine"][state][1][i] == deleteState:
                            if dests[i] == deleteState:
                                unit["stateMachine"][state][1][i] = state
                            else:
                                unit["stateMachine"][state][1][i] = dests[i]
                    for i in range(0, 3):
                        if unit["stateMachine"][state][1][i] > deleteState:
                            unit["stateMachine"][state][1][i] -= 1

                del unit["stateMachine"][deleteState]
                unit["info"]["stateCount"] -= 1

                if unit["info"]["startState"] > deleteState:
                    unit["info"]["startState"] -= 1
                elif unit["info"]["startState"] == deleteState:
                    unit["info"]["startState"] = random.choice(list(range(len(unit["stateMachine"]))))

        if mutation == 4: # change start state
            choices = list(range(len(unit["stateMachine"])))
            unit["info"]["startState"] = random.choice(choices)


def getFit(e):
    return e["info"]["fitness"]

def saveUnit(unit):
    StringData = ""
    StringData += str(unit["info"]["birthGeneration"]) + "|"
    StringData += str(unit["info"]["startState"]) + "|"
    StringData += str(unit["info"]["stateCount"]) + "|"
    for trans in unit["stateMachine"]:
        StringData += "[" + str(trans[0]) + "["
        StringData += str(trans[1][0]) + "," + str(trans[1][1]) + "," + str(trans[1][2]) + "]]|"
    StringData = StringData[:-1]
    return StringData