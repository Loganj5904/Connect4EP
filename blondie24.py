import connect4
import numpy as np
import random
import copy
from math import exp

tau = 0.0839


def tanh(x):
    return (exp(x)-exp(-x))/(exp(x)+exp(-x))


def getSubsquares(board, rows, cols, startSize=3):
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
                            subsquare.append(board[index])

                    subsquareList.append(subsquare)
            allSubsquares.append(subsquareList)

    def flattenOutput(subsquares):
        return [item for sublist in subsquares for subsublist in sublist for item in subsublist]
    
    return flattenOutput(allSubsquares)


class Network():
    def __init__(self, inputSize = 2600):
        self.kingValue = 2
        self.sigma = 0.05

        self.weightsInputHidden1 = np.random.randn(inputSize, 91) * 0.2 
        self.biasHidden1 = np.random.randn((1, 91)) * 0.2

        self.weightsHidden1Hidden2 = np.random.randn(91, 40) * 0.2
        self.biasHidden2 = np.randn((1, 40)) * 0.2

        self.weightsHidden2Output = np.random.randn(91, 10) * 0.2
        self.biasOutput = np.randn((1, 10)) * 0.2
    
    def forward(self, X):
        self.hidden1Input = np.dot(X, self.weightsInputHidden1) + self.biasHidden1
        self.hidden1Output = tanh(self.hidden1Input)

        self.hidden2Input = np.dot(self.hidden1Input, self.weightsHidden1Hidden2) + self.biasHidden2
        self.hidden2Output = tanh(self.hidden2Input)

        self.outputInput = np.dot(self.hidden2Output, self.weightsHidden2Output) + self.biasOutput
        self.outputInput += sum(X[-42:]) # sum of original board inputs
        return tanh(self.outputInput)


    def evaluate(self, board):
        subsquares = getSubsquares(connect4.getBoardString(board), 6, 7)
        return self.forward(subsquares)
    

    def createOffspring(self):
        offspring = copy.deepcopy(self)
        offspring.sigma = offspring.sigma * exp(tau*random.gauss(0,1))

        def mutate(l):
            l = [wj + offspring.sigma * random.gauss(0,1) for wj in l]
        
        mutate(offspring.weightsInputHidden1)
        mutate(offspring.biasHidden1)
        mutate(offspring.weightsHidden1Hidden2)
        mutate(offspring.biasHidden2)
        mutate(offspring.weightsHidden2Output)
        mutate(offspring.biasOutput)

        return offspring

