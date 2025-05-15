"this file contains all environment building functions"
import random
import numpy as np

class object():
    """class containing real world objects on the grid. this class can be inherited by pixies,
    immovable objects and food"""

    def __init__(self, worldToInhabit, name, yxPos):
        ""
        self.worldToInhabit = worldToInhabit
        self.yxPos = yxPos # Tupel, (y, x)
        self.name = name
    
    def __str__(self):
        
        return f"\"{self.name}\" at ({self.yxPos[0]};{self.yxPos[1]})"
    
    def getPosition(otherObject):
        "returns the absolute coordinates of the referenced object"

        return otherObject.yxPos

class stone(object):
    "class for stone (barrier) objects"

    def __init__(self, worldToInhabit, name, yxPos, shape="square"):
        super().__init__(worldToInhabit, name, yxPos)
        self.shape = shape
        self.color = "5d5555" # gray
        worldToInhabit.environment.append(self)

class food(object):
    "class for food objects"

    def __init__(self, worldToInhabit, name, yxPos, nutritionValue=5, shape="food"):
        super().__init__(worldToInhabit, name, yxPos)
        self.shape = shape
        self.color = "FFFF00" # yellow
        self.energy = nutritionValue

        worldToInhabit.environment.append(self)


def noEnvironment(world):
    "no environment"
    return

def barrierMiddleVertical(world):
    "generate a barrier out of immovable stone objects in the middle of the world"

    xPos = int(world.size / 2)
    yPos = [i for i in range(world.size) if i < world.size*0.75 and i > world.size*0.25] # the top and bottom quarter stay unblocked

    for idx in yPos:
        myStone = stone(world, "mystone", (idx, xPos))

def sparseFood(world):
    "place food randomly in the world, 1 in every 40 gridspaces"

    num_food = int(world.size**2 / 40)

    for i in range(num_food):
        p = 0
        while p < 1:
            newYXPos = (random.randint(0, np.size(world.grid, 0)-1), random.randint(0, np.size(world.grid, 0)-1))
            if world.grid[newYXPos]: # check if cell is already inhabited
                continue
            else:
                newFood = food(world, "myFood", newYXPos, nutritionValue=5)
                p += 1

def denseFood(world):
    "place food randomly in the world, approx. 1 in every 20 gridspaces"

    num_food = int(world.size**2 / 20)

    for i in range(num_food):
        p = 0
        while p < 1:
            newYXPos = (random.randint(0, np.size(world.grid, 0)-1), random.randint(0, np.size(world.grid, 0)-1))
            if world.grid[newYXPos]: # check if cell is already inhabited
                continue
            else:
                newFood = food(world, "myFood", newYXPos)
                p += 1

def sparseRocks(world):
    "randomly placed stones in 1 in every 30 gridspaces"

    num_stones = int(world.size**2/30)

    for i in range(num_stones):
        p = 0
        while p < 1:
            newYXPos = (random.randint(0, np.size(world.grid, 0)-1), random.randint(0, np.size(world.grid, 0)-1))
            if world.grid[newYXPos]: # check if cell is already inhabited
                continue
            else:
                newStone = stone(world, "myStone", newYXPos)
                p += 1


def foodAndStones(world):
    "combination of denseFood and sparseRocks"

    denseFood(world)
    sparseRocks(world)