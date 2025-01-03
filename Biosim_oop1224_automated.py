import random
import math
import numpy as np
import Biosim_oop1224_render as render
import os


class world():
    """class containing the grid. Multiple grids are possible, but most of the times the
    simulation takes place in only one world ("grid0"). For continuity reasons the world
    always has to be referenced when calling a method for any pixie."""

    def __init__(self, size=10):
        self.size = size
        self.grid = np.empty((size,size), dtype=object)
        self.inhabitants = []
        self.environment = []
    
    def __str__(self):
        return str(self.grid)
    
    def getInhabitants(self):

        return self.inhabitants
    
    def getEnvironment(self):

        return self.environment

    def printInhabitants(self):
        "print the __str__ of every object in this world"

        for myPixies in self.getInhabitants():
            print(myPixies)
    
    def updateWorld(self):
        "place all pixies in their corresponding cell"
        "reload the grid to displace any pixies which have changed their x- and y-positional values"
        
        self.grid[:,:] = None       # all cells are set back to None
        
        for object in self.getEnvironment():

            self.grid[object.yxPos] = object # building environment

        for inhabitant in self.getInhabitants():

            self.grid[inhabitant.yxPos] = inhabitant # only inhabited cells get a value

class object():
    """class containing real world objects on the grid. this class can be inherited by pixies,
    immovable objects and food"""

    def __init__(self, worldToInhabit, name, yxPos):
        ""
        self.worldToInhabit = worldToInhabit
        self.yxPos = yxPos # Tupel, (y, x)
        self.name = name
    
    def __str__(self):
        
        return f"\"{self.name}\" at {self.yxPos}"
    
    def getPosition(otherObject):
        "returns the absolute coordinates of the referenced object"

        return otherObject.yxPos

class pixie(object):
    """class containing the pixies which roam the world.
    A pixie can scan its surroundings and sense nearby other objects (pixies or other),
    move to the left of the grid and thats pretty much it by now"""

    listOfFunctions = []

    def __init__(self, worldToInhabit, name, yxPos, color="FF0000", genome=None):
        ""
        super().__init__(worldToInhabit, name, yxPos)
        self.searchRadius = defaultSearchRadius
        self.energy = defaultEnergy
        self.color = color
        self.genome = genome
        self.shape = "round"
#   List of all functions for idividual genes to choose from
        pixie.listOfFunctions = [
            self.walkTowards, self.move
        ]

        self.createGenome()
        worldToInhabit.inhabitants.append(self)
    
    def getGenome(self):
        ""
        return self.genome

    def createGenome(self):
        ""
        self.genome=genome()

    def executeGenome(self):
        ""
        self.genome.executeGenes()

    ## moving around

    def walkTowards(self, world, otherObject):
        "walk towards the referenced object"

        targetVector = self.getRelativeVector(world, otherObject)
        targetDirection = self.getDirection(targetVector)

        self.move(world, targetDirection)

    
    def move(self, world, vector):
        """, but only if the new value is in bounds and the
        neighbouring cell is empty"""

        if self.yxPos[1]+vector[1] < 0 or self.yxPos[1]+vector[1] > np.size(world.grid, 0)-1:
            return
        if self.yxPos[0]+vector[0] < 0 or self.yxPos[0]+vector[0] > np.size(world.grid, 0)-1:
            return
        else:
            if world.grid[self.yxPos[0]+vector[0]][self.yxPos[1]+vector[1]]:
                return
            else:
                self.yxPos = (self.yxPos[0]+vector[0], self.yxPos[1]+vector[1])
                world.updateWorld()
                self.energy -= energyDeficitPerMove
                print(f"{self.name} moved by {vector}")

    ## scanning neighbourhood

    def getDirection(self, object=None, vector=None):
        """return the direction of a referenced object OR vector as a vector tuple by checking 
        if the calculated angle is within 22.5° of any cardinal direction"""

        if not vector and not object:
            raise ValueError("neither an object or vector was provided")
        
        if vector:
            angle = self.getRelativeAngle(relVector=vector)
        elif object:
            angle = self.getRelativeAngle(world, otherObject=object)

        if abs(0 - angle) < (1/8) * math.pi or abs(2*math.pi - angle) < (1/8) * math.pi: # 0° and 360°
            direction = (0,1)
        elif abs(0.25*math.pi - angle) < (1/8) * math.pi: # 45°
            direction = (1,1)
        elif abs(0.5*math.pi - angle) < (1/8) * math.pi: # 90°
            direction = (1,0)
        elif abs(0.75*math.pi - angle) < (1/8) * math.pi: # 120°
            direction = (1,-1)
        elif abs(math.pi - angle) < (1/8) * math.pi: # 180°
            direction = (0,-1)
        elif abs(1.25*math.pi - angle) < (1/8) * math.pi: # 225°
            direction = (-1,-1)
        elif abs(1.5*math.pi - angle) < (1/8) * math.pi: # 270°
            direction = (-1,0)
        elif abs(1.75*math.pi - angle) < (1/8) * math.pi: # 315°
            direction = (-1,1)

        return direction


    def searchNeighbourhood(self, world):
        "scans the surrounding grid and returns a list of all objects within the search radius"

        foundObjects = []
        gridSize = np.size(world.grid, 0) # edge length of the grid (only works for square grids)

        for x in range(max(0, self.yxPos[1] - self.searchRadius), min(gridSize, self.yxPos[1] + self.searchRadius)):
            for y in range(max(0, self.yxPos[0] - self.searchRadius), min(gridSize, self.yxPos[0] + self.searchRadius)):
                if math.sqrt((x-self.yxPos[1])**2 + (y - self.yxPos[0])**2) <= self.searchRadius:
                    if world.grid[y,x] and world.grid[y,x] != self:
                        foundObjects.append(world.grid[y,x])
        return foundObjects
    
    def getAllEuclidianDistances(self, world):
        """scans the surrounding grid and returns a list of tuples containing all objects
        and their corresponding distances"""

        outlist = []

        for neighbour in self.searchNeighbourhood(world):

            dx = neighbour.yxPos[1] - self.yxPos[1]
            dy = neighbour.yxPos[0] - self.yxPos[0]

            distance = math.sqrt(dx**2 + dy**2)
            outlist.append((neighbour, distance))
        return outlist
    
    def getNearest(self, world):
        "scans the surrounding grid and returns the nearest object"

        neighbourhood = self.getAllEuclidianDistances(world, searchRadius)
        #print(neighbourhood)
        
        if neighbourhood:
            nearest = min(neighbourhood, key=lambda x: x[1])
            return nearest[0]
        else:
            pass
    
    def getNearestPixie(self, world):
        "scans the surrounding grid and returns the nearest pixie"

        neighbourhood = self.getAllEuclidianDistances(world)
        #print(neighbourhood)
        neighbouring_pixies = []
        
        for i in neighbourhood:
            if i[0] in world.inhabitants:
                neighbouring_pixies.append(i)

        if neighbouring_pixies:
            nearest = min(neighbouring_pixies, key=lambda x: x[1])
            return nearest[0]
        else:
            print("mäp")
            pass

    ## scanning neighbourhood for a specific, referenced object

    def getEuclidianDistance(self, world, otherObject):
        "returns the absolute distance between the referenced object and self"

        dx = otherObject.yxPos[1] - self.yxPos[1]
        dy = otherObject.yxPos[0] - self.yxPos[0]

        distance = math.sqrt(dx**2 + dy**2)
        return distance

    def getRelativeVector(self, world, otherObject):
        """returns a twodimensional tuple containing the y- and x-position of the 
        referenced object relative to self"""

        dx = otherObject.yxPos[1] - self.yxPos[1]
        dy = otherObject.yxPos[0] - self.yxPos[0]

        return dy, dx
    
    def getRelativeAngle(self, world, otherObject):
        """returns the angle of the referenced object in relation to self, angles
        are expressed as radiant with range (-pi/pi), going clockwise from the right"""

        relVector = self.getRelativeVector(world, otherObject)
        relAngle = math.atan2(relVector[0],relVector[1])
        if relAngle < 0 : 
            relAngle += 2*math.pi # angle now runs counterclockwise starting east

        return relAngle

    ##combined function

    def moveToNearestPixie(self, world):
        ""
        nearestPixie = self.getNearestPixie(world)
        self.walkTowards(world, nearestPixie)    

class stone(object):
    ""

    def __init__(self, worldToInhabit, name, yxPos, shape="square"):
        super().__init__(worldToInhabit, name, yxPos)
        self.shape = shape
        self.color = "5d5555" # gray
        worldToInhabit.environment.append(self)


class food(object):
    ""
    def __init__(self, worldToInhabit, name, yxPos, shape="food"):
        super().__init__(worldToInhabit, name, yxPos)
        self.shape = shape
        self.color = "FFFF00" # yellow
        worldToInhabit.environment.append(self)

class genome():
    """class containing all existing genomes. 
    Each genome has a corresponding Object it belongs to (currently only Pixies can have genomes)
    and a number of genes"""

    def __init__(self):
        ""
        self.length = numberOfGenes
        self.genes = []
        for i in range(0, self.length):
            self.genes.append(gene())
    
    def getGenes(self):
        ""
        return self.genes
    
    def executeGenes(self):
        ""
        for gene in self.genes:
            gene.executeFunctionality()


class gene():
    """class containing all existing genes. Each gene has a 
    functionality (one of the methods of Pixies) and a floating point probability of being expressed. 
    0 by default, can mutate."""
    
    def __init__(self):
        ""
        self.functionality = random.choice(pixie.listOfFunctions)
        self.expressionProbability = 1.0    

    def executeFunctionality(self):
        "executing the function encoded in the gene with the specific expressionProbaility"
        if random.random() <= self.expressionProbability:
            self.functionality()
        else:
            return

def spawnPixies(numberOfPixies, worldToSpawnIn):
    """spawn new pixies onto the grid by randomly generating a name, coordinates, color and genome.
    The coordinates are checked for already existing objects before spawning and if the desired cell
    is not available, the pixie gets discarded and a new one gets generated"""

    p=0
    while p < numberOfPixies:
    #for i in range(numberOfPixies):
        newPixieName = "Pixie_" + str(random.randint(0,1000))
        #wir lassen das checkexist erstmal weg, vielleicht braucht es das gar nicht mehr
        #Doppelungen können aber gefährlich werden: Check oder nicht random Namen?
        newYXPos = (random.randint(0, np.size(worldToSpawnIn.grid, 0)-1), random.randint(0, np.size(worldToSpawnIn.grid, 0)-1))
        if worldToSpawnIn.grid[newYXPos]: # check if cell is already inhabited
            continue
        newHexColor = "%06x" % random.randint(0,0xFFFFFF)
        newPixieName = pixie(worldToSpawnIn, newPixieName, newYXPos, newHexColor)
        worldToSpawnIn.updateWorld()
        p += 1

##################
#Parameters
size = 10
numberOfGenerations = 1
simulatorSteps = 3
numberOfGenes = 3
defaultEnergy = 10
energyDeficitPerMove = 1
defaultSearchRadius = 5

#initiate world
grid0 = world(size)
# manual instancing
myPixie1 = pixie(worldToInhabit=grid0, name="Pixie 1", yxPos=(3,1))
myPixie2 = pixie(worldToInhabit=grid0, name="Pixie 2", yxPos=(5,1))
#myStone1 = stone(grid0, "Stone_1", (2,2))
#myFlower1 = food(grid0, "Flower_1", (3,3))
grid0.updateWorld()
render.render(grid0)
myPixie1.moveToNearestPixie(grid0)
#myPixie1.move(grid0, (1,1))
#print(myPixie1.energy)

#automatic instancing
#spawnPixies(3, grid0)

## running the simulation
#print(grid0.inhabitants[0].yxPos)
render.render(grid0)
#print(grid0.inhabitants[0].energy)

#for i in range(0, numberOfGenerations):
#for a in range (0, simulatorSteps):
    #grid0.inhabitants[0].move(grid0, (1,0))
    #print(grid0.inhabitants[0].energy)
    #render.render(grid0)
    #print(grid0.inhabitants[0].yxPos)
    #for instance in grid0.inhabitants:
    #    instance.executeGenome()
    #render.render(grid0)

render.create_gif()
#print("cwd: ", os.getcwd())
render.clear_gif()
