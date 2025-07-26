"This file contains all functions that apply selection criteria"
import random


def doNothing(world, mortalityRate):
    "do nothing"
    pass

def killRightHalf(world, mortalityRate):
    "kill every pixie that is on the right half of the grid"

    for pixie in list(world.getInhabitants()):
        if random.random() < mortalityRate:
            if pixie.yxPos[1] >= (world.size/2):
                world.inhabitants.remove(pixie)

def killLeftHalf(world, mortalityRate):
    "kill left half of the world"
    
    # alternative using a list comprehension --> thanks ChatGPT (DOESNT WORK; THANKS CHATGPT)
    # world.inhabitants = [pixie for pixie in world.getInhabitants if pixie.yxPos[1] < world.size/2]
    for pixie in list(world.getInhabitants()):
        if random.random() < mortalityRate:
            if pixie.yxPos[1] <= (world.size/2):
                world.inhabitants.remove(pixie)

def killRandomHalf(world, mortalityRate):
    "kill either the top, bottom, left or right half"
    half = random.choice(["l", "r", "t", "b"])

    if half == "l":
        for pixie in list(world.getInhabitants()):
            if random.random() < mortalityRate:
                if pixie.yxPos[1] <= (world.size/2):
                    world.inhabitants.remove(pixie)
    elif half == "r":
        for pixie in list(world.getInhabitants()):
            if random.random() < mortalityRate:
                if pixie.yxPos[1] >= (world.size/2):
                    world.inhabitants.remove(pixie)
    elif half == "t":
        for pixie in list(world.getInhabitants()):
            if random.random() < mortalityRate:
                if pixie.yxPos[0] <= (world.size/2):
                    world.inhabitants.remove(pixie)
    elif half == "b":
        for pixie in list(world.getInhabitants()):
            if random.random() < mortalityRate:
                if pixie.yxPos[0] >= (world.size/2):
                    world.inhabitants.remove(pixie)

def killSwitchingSides(world, mortalityRate, gen):
    "kill the left side if generation number is even, else the right side"
    if gen%  2 == 0:
        for pixie in list(world.getInhabitants()):
            if random.random() < mortalityRate:
                if pixie.yxPos[1] <= (world.size/2):
                    world.inhabitants.remove(pixie)
    else:
        for pixie in list(world.getInhabitants()):
            if random.random() < mortalityRate:
                if pixie.yxPos[1] >= (world.size/2):
                    world.inhabitants.remove(pixie)

def killMiddle(world, mortalityRate):
    "kill every pixie that isn't on one edge (E/W) of the grid"

    for pixie in list(world.getInhabitants()):
        if random.random() < mortalityRate:
            if pixie.yxPos[1] >= world.size*(1/8) and pixie.yxPos[1] <= world.size*(7/8):
                world.inhabitants.remove(pixie)

def killEdges(world, mortalityRate):
    "kill every pixie that is on the edge (E/W)"

    for pixie in list(world.getInhabitants()):
        if random.random() < mortalityRate:
            if pixie.yxPos[1] <= world.size*(1/3) or pixie.yxPos[1] >= world.size*(2/3):
                world.inhabitants.remove(pixie)

def killLowEnergy(world, mortalityRate):
    "kill every pixie that hasn't eaten"

    for pixie in list(world.getInhabitants()):
        if random.random() < mortalityRate:
            if pixie.energy < 6:
                world.inhabitants.remove(pixie)

def killMiddle_LowEnergy(world, mortalityRate):
    "combination of killLowEnergy and killMiddle" 
    killLowEnergy(world, mortalityRate)
    killMiddle(world, mortalityRate)

def killEdges_LowEnergy(world, mortalityRate):
    ""
    killLowEnergy(world, mortalityRate)
    killEdges(world, mortalityRate)