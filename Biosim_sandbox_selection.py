"This file contains all functions that apply selection criteria"


def doNothing(world):
    "do nothing"
    pass

def killRightHalf(world):
    "kill every pixie that is on the right half of the grid"

    for pixie in list(world.getInhabitants()):
        
        if pixie.yxPos[1] >= (world.size/2):
            world.inhabitants.remove(pixie)

def killLeftHalf(world):
    "kill left half of the world"
    
    # alternative using a list comprehension --> thanks ChatGPT
    world.inhabitants = [pixie for pixie in world.getInhabitants if pixie.yxPos[1] < world.size/2]

def killMiddle(world):
    "kill every pixie that isn't on one edge (E/W) of the grid"

    for pixie in list(world.getInhabitants()):
        if pixie.yxPos[1] >= world.size*(1/6) and pixie.yxPos[1] <= world.size*(5/6):
            world.inhabitants.remove(pixie)
