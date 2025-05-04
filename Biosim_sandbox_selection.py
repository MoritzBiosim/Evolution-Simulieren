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
        if pixie.yxPos[1] >= world.size*(1/8) and pixie.yxPos[1] <= world.size*(7/8):
            world.inhabitants.remove(pixie)

def killEdges(world):
    "kill every pixie that is on the edge (E/W)"

    for pixie in list(world.getInhabitants()):
        if pixie.yxPos[1] <= world.size*(1/3) or pixie.yxPos[1] >= world.size*(2/3):
            world.inhabitants.remove(pixie)

def killLowEnergy(world):
    "kill every pixie that hasn't eaten"

    for pixie in list(world.getInhabitants()):
        if pixie.energy < 1:
            world.inhabitants.remove(pixie)