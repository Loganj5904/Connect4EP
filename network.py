import connect4
import numpy as np
import random
import copy
from math import exp

tau = 0.0839

""" 
def tanh(X):
    return [(exp(x)-exp(-x))/(exp(x)+exp(-x)) for x in X] """


def getSubsquares(boardString, rows, cols, startSize=3):
    allSubsquares = []  

    for height in range(startSize, rows + 1):  
        for width in range(startSize, cols + 1): 
            subsquareList = []  

            for row in range(rows - height + 1):
                for col in range(cols - width + 1):
                    subsquare = []

                    for h in range(height):  
                        for w in range(width): 
                            index = (row + h) * cols + (col + w)
                            char = boardString[index]
                            subsquare.append(char)

                    subsquareList.append(subsquare)
            allSubsquares.extend(subsquareList)

    def flattenOutput(subsquares):
        return [item for sublist in subsquares for subsublist in sublist for item in subsublist]
    
    return flattenOutput(allSubsquares)


class Network():
    def __init__(self, inputSize = 2600):
        print("initializing network...")
        self.kingValue = 2
        self.sigma = 0.05
        self.fitness = 0

        self.weightsInputHidden1 = np.random.randn(inputSize, 91) * 0.2 # normalizing values to range [-0.2, 0.2]
        self.biasHidden1 = np.random.randn(1, 91) * 0.2

        self.weightsHidden1Hidden2 = np.random.randn(91, 40) * 0.2
        self.biasHidden2 = np.random.randn(1, 40) * 0.2

        self.weightsHidden2Hidden3 = np.random.randn(40, 10) * 0.2
        self.biasHidden3 = np.random.randn(1, 10) * 0.2

        self.weightsHidden3Output = np.random.randn(10, 1) * 0.2
        self.biasOutput = np.random.randn(1, 1) * 0.2
    
    def forward(self, X):
        self.hidden1Input = np.dot(X, self.weightsInputHidden1) + self.biasHidden1
        self.hidden1Output = np.tanh(self.hidden1Input)

        self.hidden2Input = np.dot(self.hidden1Output, self.weightsHidden1Hidden2) + self.biasHidden2
        self.hidden2Output = np.tanh(self.hidden2Input)

        self.hidden3Input = np.dot(self.hidden2Output, self.weightsHidden2Hidden3) + self.biasHidden3
        self.hidden3Output = np.tanh(self.hidden3Input)

        self.outputInput = np.dot(self.hidden3Output, self.weightsHidden3Output) + self.biasOutput
        self.outputInput += sum(X[-42:]) # sum of original board inputs
        finalOutput = np.tanh(self.outputInput)
        return finalOutput


    def evaluate(self, board):
        subsquares = getSubsquares(connect4.getBoardString(board), 6, 7)
        #print(subsquares)
        subsquares = [-1.0 if item == '-' else float(item) for item in subsquares]
        subsquares = np.array(subsquares, dtype=np.float32)  # Ensure NumPy array
        return self.forward(subsquares)
    

    def createOffspring(self):
        offspring = copy.deepcopy(self)
        offspring.sigma = offspring.sigma * exp(tau*random.gauss(0,1))

        kingDelta = random.choice([-0.1, 0.0, 0.1])
        if offspring.kingValue + kingDelta < 3.0 and offspring.kingValue + kingDelta > 1.0:
            offspring.kingValue += kingDelta

        def mutate(l):
            l = [wj + offspring.sigma * random.gauss(0,1) for wj in l]
        
        mutate(offspring.weightsInputHidden1)
        mutate(offspring.biasHidden1)
        mutate(offspring.weightsHidden1Hidden2)
        mutate(offspring.biasHidden2)
        mutate(offspring.weightsHidden2Hidden3)
        mutate(offspring.biasHidden3)
        mutate(offspring.weightsHidden3Output)
        mutate(offspring.biasOutput)

        return offspring

