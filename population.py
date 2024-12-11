import math
import random
import time
import connect4
import copy

unitTemplate = {
    "info": {"id": 0, "fitness": 0, "birthGeneration": 0, "startState": 0, "stateCount": 0}, "stateMachine": [], "currentGame": {"currentState": 0}}

stateTemplate = [0, [0, 0, 0]]
# state template:
# index 0 is the state output, from 0-6
# index 1 contains the transitions of the state:
# each transition is marked by its index to the next state
populationCount = 100
mutationCountStart = 150
mutationCountEnd = 40
stateCountMax = 3000
currentID = 1
startStateCount = 2000

# fitness parameters
winWeight = 1.6
loseWeight = 2.2
opponents = 5
weightOfStateCount = 1.01
weightOfStateUse = 1.1
weightOfOverflow = 0.05
weightOfEnemy3s = 0.1

generations = 10
runTime = 60 #864000
useTime = True

# repopulate parameters
unitCreate = 70

#mutation paramters
mutationOdds = [0.97, .0045, .0045, 0.001, 0.02]

stateCountHold1 = set()
stateCountHold2 = set()

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
    #start = time.time()
    #print("Start: " + str(time.time() * 1000))
    global stateCountHold1, stateCountHold2
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
        wins = [False] * len(choices)
        usedStates = set()
        # pool = multiprocessing.Pool(processes=len(choices))
        # inputs = []
        fitnesses = [0] * len(choices)
        for o in range(len(choices)):
            # inputs.append([u, choices[o], fitnesses, wins, o, len(choices)])
            unitPlay(u, choices[o], fitnesses, wins, o, len(choices), usedStates)
        # pool.map(unitPlayProcess, inputs)
        winCount = sum(wins)
        u["info"]["fitness"] += len(usedStates) / len(u["stateMachine"]) * weightOfStateUse
        u["info"]["fitness"] += math.pow(winCount, winWeight)
        u["info"]["fitness"] -= math.pow(len(choices) - winCount, loseWeight)
        u["info"]["fitness"] += (u["info"]["stateCount"] / stateCountMax) * weightOfStateCount
        test = True
        stateCountHold1 = set()
        stateCountHold2 = set()
    #print("Fitness Time: " + str((time.time()) - start))


def unitPlay(u, o, fitnessStore, winCondition, indexStore, count, usedStates):
    fitness = 0
    firstTurn = random.randint(1, 2)
    board = connect4.createBoard()
    if firstTurn == 1:
        gameStats = playGame(u, o, board)
    else:
        gameStats = playGame(o, u, board)
    if gameStats[0] == firstTurn:
        winCondition[indexStore] = True
    fitness += -(gameStats[1][firstTurn - 1] * weightOfOverflow) + weightOfEnemy3s * connect4.checkThrees(board, firstTurn)
    #usedStates.extend(gameStats[1][firstTurn - 1])
    if firstTurn == 1:
        usedStates = stateCountHold1
    else:
        usedStates = stateCountHold2

    #fitness += (weightOfStateUse * (math.log((gameStats[1][0] + 0.1) / 7)) + 3) / count
    #fitness += weightOfEnemy3s

    fitnessStore[indexStore] = fitness

def unitPlayProcess(inputs):
    fitness = 0
    firstTurn = random.randint(1, 2)
    board = connect4.createBoard()
    if firstTurn == 1:
        gameStats = playGame(inputs[0], inputs[1], board)
    else:
        gameStats = playGame(inputs[1], inputs[0], board)
    if gameStats[0] == firstTurn:
        inputs[3][inputs[4]] = True
    fitness -= gameStats[1][firstTurn - 1] * weightOfOverflow
    fitness += weightOfEnemy3s * connect4.checkThrees(board, firstTurn)

    #fitness += (weightOfStateUse * (math.log((gameStats[1][0] + 0.1) / 7)) + 3) / inputs[5]
    fitness += weightOfEnemy3s

    inputs[2][inputs[4]] = fitness


# def tournament(units):
#     choices = list(range(populationCount))
#     winners = []
#     player1Wins = 0
#     player2Wins = 0
#     for i in range(int(populationCount / 2)):
#         choice1 = random.choice(choices)
#         choices.remove(choice1)
#         choice2 = random.choice(choices)
#         choices.remove(choice2)
#         board = connect4.createBoard()
#         # apparently only player 2 wins after the first generation
#         winner, turn, overflow = playGame(units[choice1], units[choice2], board)
#         if winner == 1:
#             units[choice1]["info"]["fitness"] = turns / (7*6)
#             units[choice2]["info"]["fitness"] = (7 * 6) / -turns
#             player1Wins += 1
#         elif winner == 2:
#             units[choice2]["info"]["fitness"] = turns / (7 * 6)
#             units[choice1]["info"]["fitness"] = (7 * 6) / -turns
#             player2Wins += 1
#         else:
#             units[choice1]["info"]["fitness"] = 0
#             units[choice2]["info"]["fitness"] = 0
#     #print("End: " + str(time.time() * 1000))

def playGame(player1, player2, board):
    player1Number = 1
    player2Number = 2
    # totalStateUse1 = []
    # totalStateUse2 = []
    overFlowMoves = [0, 0]
    gameLoop = True
    tie = False
    turns = 0
    while gameLoop:
        moveDecide = decideMove(player1, board)
        stateCountHold1.update(moveDecide[1])
        if connect4.columnHeight(board, moveDecide[0]) == len(board):
            overFlowMoves[0] += 1
        valid = connect4.place(board, player1Number, moveDecide[0])
        if not valid:
            gameLoop = False
            tie = True
            break
        turns += 1
        win = connect4.checkWin(board)
        if win:
            return player1Number, overFlowMoves
            #return player1Number, (totalStateUse1, totalStateUse2), overFlowMoves
        moveDecide = decideMove(player2, board)
        stateCountHold2.update(moveDecide[1])
        if connect4.columnHeight(board, moveDecide[0]) == len(board):
            overFlowMoves[1] += 1
        valid = connect4.place(board, player2Number, moveDecide[0])
        if not valid:
            gameLoop = False
            tie = True
            break
        turns += 1
        win = connect4.checkWin(board)
        if win:
            return player2Number, overFlowMoves
            #return player2Number, (totalStateUse1, totalStateUse2), overFlowMoves
    if tie:
        return 0, overFlowMoves
        #return 0, (totalStateUse1, totalStateUse2), overFlowMoves


def decideMove(player, board, player2=False):
    stateMachine = player["stateMachine"]
    currentPosition = player["info"]["startState"]
    boardString = connect4.getBoardStringCol(board)
    statesVisited = [currentPosition]
    boardString = boardString.replace("-1", "2")
    if player2:
        boardString = boardString.replace("1", "a")
        boardString = boardString.replace("2", "1")
        boardString = boardString.replace("a", "2")
    for char in boardString:
        if char == "-1": char = 2
        currentPosition = stateMachine[currentPosition][1][int(char)]
        if not statesVisited.__contains__(currentPosition):
            statesVisited.append(currentPosition)
    return stateMachine[currentPosition][0], statesVisited


def repopulate(units, generation):
    global currentID
    unitCheck = 20
    unitReplace = 10
    unitStage = []
    for i in range(unitCheck):
        repeat = False
        choice = None
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


    #mutation
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


def MuLambdaRepopulate(units, generation):
    global currentID
    newUnits = []
    testUnits = []
    for i in range(unitCreate):
        randomUnit = copy.deepcopy(random.choice(units))
        mutationCount = ((mutationCountEnd - mutationCountStart) / generations) * generation + 100
        mutate(randomUnit, round(mutationCount))
        testUnits.append(randomUnit)
    getFitnesses(testUnits)
    testUnits.sort(key=getFit)
    for i in range(len(units)):
        newUnits.append(testUnits[i])
    for unit in newUnits:
        unit["info"]["id"] = currentID
        unit["info"]["birthGeneration"] = generation
        currentID += 1
    return newUnits


def mutate(unit, mutationCount):
    for m in range(mutationCount):
        mutation = 0
        randomChoice = random.random()
        odds = 0
        for i in range(len(mutationOdds)):
            odds += mutationOdds[i]
            if randomChoice <= odds:
                mutation = i + 1
                break
        if mutation == 0:
            mutation = 1
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
        if mutation == 5: # change a state's output column
            stateChoice = random.randint(0, unit["info"]["stateCount"] - 1)
            columnChoice = random.randint(0, 6)
            unit["stateMachine"][stateChoice][0] = columnChoice


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


def loadUnit(unitString:str):
    unit = copy.copy(unitTemplate)
    unitInfo = unitString.split("|")
    unit["info"]["birthGeneration"] = int(unitInfo[0])
    unit["info"]["startState"] = int(unitInfo[1])
    unit["info"]["stateCount"] = int(unitInfo[2])
    for i in range(3, len(unitInfo)):
        stateParts = unitInfo[i].replace("[", ",").replace("]", "").split(",")
        newState = copy.deepcopy(stateTemplate)
        newState[0] = int(stateParts[1])
        newState[1][0] = int(stateParts[2])
        newState[1][1] = int(stateParts[3])
        newState[1][2] = int(stateParts[4])
        unit["stateMachine"].append(newState)
    return unit


def pickUnits(count, units):
    picked = []
    pickList = copy.deepcopy(units)
    for i in range(count):
        pickedUnit = random.choice(pickList)
        while picked.__contains__(pickedUnit):
            pickedUnit = random.choice(pickList)
        picked.append(pickedUnit)
        pickList.remove(pickedUnit)
    return picked


def unitCompare(unit1, unit2):
    if unit1["stateMachine"] == unit2["stateMachine"] and unit1["info"]["startState"] == unit2["info"]["startState"]:
        return True
    return False
