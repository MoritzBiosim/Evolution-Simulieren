import random
import numpy as np
import math 
import time
import Biosim_sandbox_render as render
import Biosim_sandbox_neurons as neurons
import Biosim_sandbox_selection as selection
import Biosim_sandbox_environment as environment


class world():
    """class containing the grid."""

    def __init__(self, size=10):
        self.size = size
        self.grid = np.empty((size,size), dtype=object)
        self.inhabitants = []
        self.environment = []

        self.queueForMove = set()
        self.queueForKill = set()
        self.sexualityCount = 0
    
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


################################################
# OBJECT CLASSES

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

class pixie(object):
    """class containing the pixies which roam the world.
    A pixie can scan its surroundings and sense nearby other objects (pixies or other),
    move to the left of the grid and thats pretty much it by now"""

    # listOfFunctions = []

    def __init__(self, worldToInhabit, name, yxPos, inheritedDNA=None, color="FF0000"):
        ""
        super().__init__(worldToInhabit, name, yxPos)
        #   List of all functions for idividual genes to choose from
        self.energy = defaultEnergy
        self.color = color
        self.genome = None
        self.inheritedDNA = inheritedDNA
        self.shape = "round"
        self.facing = 0 

        # variables to track the "movement urge" in each simstep. These get reset every new simstep
        self.moveX = 0
        self.moveY = 0


        self.createGenome()
        worldToInhabit.inhabitants.append(self)
    
    def getGenome(self):
        ""
        return self.genome

    def createGenome(self):
        ""
        self.genome=genome(attributedPixie=self, inheritedDNA=self.inheritedDNA)

    def executeGenome(self):
        ""
        #self.genome.executeGenes()
        self.genome.executeGenome()

    ## moving around

    def executeMove(self):
        Y_normed = lambda x : int(x > 0) - int(x < 0) # True = 1, False = 0
        X_normed = lambda x : int(x > 0) - int(x < 0)
        moveVector = (Y_normed(self.moveY), X_normed(self.moveX))
        
        # print(self.moveY, self.moveX)
        # print(moveVector)

        self.move(vector=moveVector)

        self.moveX = 0
        self.moveY = 0

    def walkTowards(self, otherObject):
        "walk towards the referenced object"
        world = self.worldToInhabit

        targetVector = self.getRelativeVector(otherObject)
        targetDirection = self.getNormalizedDirection(targetVector)

        self.move(world, targetDirection)
    
    def move(self, vector):
        "move along a provided vector, but only if the new box is in bounds and empty"
        
        world = self.worldToInhabit # this makes providing the argument "world" obsolete

        if self.yxPos[1]+vector[1] < 0 or self.yxPos[1]+vector[1] > np.size(world.grid, 0)-1:
            # out of bounds
            return
        if self.yxPos[0]+vector[0] < 0 or self.yxPos[0]+vector[0] > np.size(world.grid, 0)-1:
            # out of bounds
            return
        if world.grid[(int(self.yxPos[0]+vector[0]), int(self.yxPos[1]+vector[1]))]:
            # cell already inhabited
            return
        else:
            self.yxPos = (int(self.yxPos[0]+vector[0]), int(self.yxPos[1]+vector[1])) # moving
            self.facing = self.getRelativeAngle(relVector=vector) # update "facing"-direction

            world.updateWorld() # <<<<<<<<<<< this may be needed
            #self.energy -= energyDeficitPerMove  #DAS HIER IST AUSGESCHALTET
            if self.energy < 0:
                self.energy = 0
            # print(f"{self.name} moved by {vector}")

    def moveRandom(self):
        """move in a random direction but only if the new value is in bounds and the
        neighbouring cell is empty"""
        world = self.worldToInhabit # this makes providing the argument "world" obsolete
        randomVector = (random.randint(-1,1), random.randint(-1,1))

        self.move(randomVector)

    ## scanning neighbourhood

    def getNormalizedDirection(self, object=None, vector=None, angle=None):
        """return the direction of a referenced object OR vector OR angle as a vector tuple by checking 
        if the calculated angle is within 22.5° of any cardinal direction"""

        if vector is None and object is None and angle is None:
            raise ValueError("neither an object, vector or angle was provided")
        
        if vector:
            angle = self.getRelativeAngle(relVector=vector)
        elif object:
            angle = self.getRelativeAngle(otherObject=object)

        if angle < 0:
            angle = angle + 2*math.pi

        if angle > 2*math.pi:
            k = angle // (2*math.pi)
            angle = angle - k*2*math.pi

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


    def searchNeighbourhood(self):
        "scans the surrounding grid and returns a list of all objects within the search radius"
        "this includes pixies occupying the same gridspace as the searching pixie!"

        world = self.worldToInhabit # this makes providing the argument "world" obsolete
        searchRadius = int(self.genome.searchRadius) #consistency??

        foundObjects = []
        gridSize = np.size(world.grid, 0) # edge length of the grid (only works for square grids)

        for x in range(max(0, self.yxPos[1] - searchRadius), min(gridSize, self.yxPos[1] + searchRadius)):
            for y in range(max(0, self.yxPos[0] - searchRadius), min(gridSize, self.yxPos[0] + searchRadius)):
                if math.sqrt((x-self.yxPos[1])**2 + (y - self.yxPos[0])**2) <= searchRadius:
                    if world.grid[y,x] and world.grid[y,x] != self:
                        foundObjects.append(world.grid[y,x])
        return foundObjects
    
    def getAllEuclidianDistances(self):
        """scans the surrounding grid and returns a list of tuples containing all objects
        and their corresponding distances"""

        outlist = []

        for neighbour in self.searchNeighbourhood():

            dx = neighbour.yxPos[1] - self.yxPos[1]
            dy = neighbour.yxPos[0] - self.yxPos[0]

            distance = math.sqrt(dx**2 + dy**2)
            outlist.append((neighbour, distance))
        return outlist
    
    def getNearest(self):
        "scans the surrounding grid and returns the nearest object"

        neighbourhood = self.getAllEuclidianDistances()
        #print(neighbourhood)
        
        if neighbourhood:
            nearest = min(neighbourhood, key=lambda x: x[1])
            return nearest[0]
        else:
            pass
    
    def getNearestPixie(self):
        "scans the surrounding grid and returns the nearest pixie"

        neighbourhood = self.getAllEuclidianDistances()
        #print(neighbourhood)
        neighbouring_pixies = []
        
        for i in neighbourhood:
            if i[0] in self.worldToInhabit.inhabitants:
                neighbouring_pixies.append(i)

        if neighbouring_pixies:
            nearest = min(neighbouring_pixies, key=lambda x: x[1])
            return nearest[0]
        else:
            return None

    ## scanning neighbourhood for a specific, referenced object

    def getEuclidianDistance(self, otherObject):
        "returns the absolute distance between the referenced object and self"

        dx = otherObject.yxPos[1] - self.yxPos[1]
        dy = otherObject.yxPos[0] - self.yxPos[0]

        distance = math.sqrt(dx**2 + dy**2)
        return distance

    def getRelativeVector(self, otherObject):
        """returns a twodimensional tuple containing the y- and x-position of the 
        referenced object relative to self"""

        dx = otherObject.yxPos[1] - self.yxPos[1]
        dy = otherObject.yxPos[0] - self.yxPos[0]

        return dy, dx
    
    def getRelativeAngle(self, otherObject=None, relVector=None):
        """returns the angle of the referenced object in relation to self, angles
        are expressed as radiant with range (-pi/pi), going clockwise from the right"""

        if not otherObject and not relVector:
            raise ValueError("neither an object nor a vector was provided")

        if otherObject:
            relVector = self.getRelativeVector(otherObject)
        relAngle = math.atan2(relVector[0],relVector[1])
        if relAngle < 0 : 
            relAngle += 2*math.pi # angle now runs counterclockwise starting east

        return relAngle
    
    def searchProximateField(self):
        "returns any objects located in the next field in FACING DIRECTION"
        viewAxis = self.facing
        direction = self.getNormalizedDirection(angle=viewAxis)
        proximateField = (self.yxPos[0]+direction[0], self.yxPos[1]+direction[1])
        gridSize = self.worldToInhabit.size
       
        # boundary check
        if not (0 <= proximateField[0] < gridSize and 0 <= proximateField[1] < gridSize):
            return None  # Out of bounds, return None
        else:
            proximateObject = self.worldToInhabit.grid[proximateField]
        return proximateObject    

    def getFwdObjects(self):
        "returns a list of all objects in viewAxis within searchRadius"
        viewAxis = self.facing
        direction = self.getNormalizedDirection(angle=viewAxis)
        gridSize = self.worldToInhabit.size
        objects = []
        searchRadius = self.genome.searchRadius
        
        for r in range(1, int(searchRadius)+1):
            nextField = (self.yxPos[0]+r*direction[0], self.yxPos[1]+r*direction[1])
            #boundary check
            if not (0 <= nextField[0] < gridSize and 0 <= nextField[1] < gridSize):
                break  # Out of bounds, return list as of now
            
            nextObject = self.worldToInhabit.grid[nextField]
            if nextObject is not None:
                objects.append(nextObject)
        
        return objects
    
    def getFwdPixies(self):
        "returns a list of all pixies in viewAxis within searchRadius"
        viewAxis = self.facing
        direction = self.getNormalizedDirection(angle=viewAxis)
        gridSize = self.worldToInhabit.size
        fwdPixies = []
        searchRadius = self.genome.searchRadius
        
        for r in range(1, int(searchRadius+1)):
            nextField = (self.yxPos[0]+r*direction[0], self.yxPos[1]+r*direction[1])
            #boundary check
            if not (0 <= nextField[0] < gridSize and 0 <= nextField[1] < gridSize):
                break  # Out of bounds, return list as of now
            
            nextObject = self.worldToInhabit.grid[nextField]
            if isinstance(nextObject, pixie):
                fwdPixies.append(nextObject)
        
        return fwdPixies


################################################
# GENOME CLASS

"""the genome class assembles the neural network 'brain' of each pixie by asserting source- and sink-neurons.
The neurolinks generate their own 'DNA'=32bit integer when instantiated and choose their corresponding source- 
and sink-classes based on the generated DNA string, so completely random yet deterministic.
Each class that is represented by at least one neurolink is then sorted into a set (allNeuronClasses) and from 
this set new individual Neurons for the pixie is instantiated (allNeurons). The Neurons get additionally sorted
into sourceNeurons/sinkNeurons by querying the neurolinks.
(Most) non-functioning connections or genomes get discarded right at the start to save memory and if no functionality
arises, the genome never gets executed for this pixie.
The expression(=execution) of the genome gets controlled by executeGenome()"""

class genome():
    """class containing all existing genomes. 
    Each genome has a corresponding Object it belongs to (currently only Pixies can have genomes)
    and a number of genes=Neurolinks"""

    def __init__(self, attributedPixie, inheritedDNA=None):
        ""
        self.attributedPixie = attributedPixie
        self.length = numberOfGenes
        self.inheritedDNA = inheritedDNA
        self.genes = [] # actually contains neurolinks
        self.functioningGenome = True

        self.allNeuronClasses = set() # includes all neuron class objects

        self.allNeurons = set() # includes all neuron objects    
        self.sourceNeurons = [] # contains all source neurons
        self.sinkNeurons = [] # contains all sink neurons

        self.wantsToMate = set()
        self.hasAlreadyMated = False
        
        # self.sensorToInternal = [] # obsolete
        # self.internalToInternal = [] # obsolete
        # self.sensor_InternalToAction = [] # obsolete

        self.oscillatorPeriod = 8 # number of simsteps in one oscillator cycle
        self.searchRadius = 5 # searchradius used by functions like searchNeighbourhood
        self.killRadius = 2 #used by class kill()
        self.isOn = True # used by OnOff neuron: True = On (1), False = Off (0)

        # instantiate new Neurolink objects
        if self.inheritedDNA: # instantiate new neurolink objects from old dna
            for gene in self.inheritedDNA:
                self.genes.append(Neurolink(self.attributedPixie, gene))
        else: # generate new DNA from scratch
            for i in range(0, self.length):
                self.genes.append(Neurolink(self.attributedPixie))
        
        self.loadGenome()

    def __str__(self):
        for neurolink in self.genes:
            return neurolink 
    
    def getGenes(self):
        ""
        return self.genes
    
    def printNeurons(self):
        "return all attributes for each neuron"
        for n in self.allNeurons:
            print(n)


    def loadGenome(self):
        "sort the neuron objects into the sets and lists above."

        # append new neuron functions to the allNeuronClasses-set
        for neurolink in self.genes:
            self.allNeuronClasses.add(neurolink.source) 
            self.allNeuronClasses.add(neurolink.sink) 

        # for each element in allNeuronClasses, a new neuron object gets instantiated
        for neuronClass in self.allNeuronClasses:
            self.allNeurons.add(neuronClass(self.attributedPixie))
        
        # now sort them into the .sourceNeurons and .sinkNeurons sets using the neurolinks
        for neuron in self.allNeurons:
            if any(neuron.__class__ == neurolink.source for neurolink in self.genes):
                self.sourceNeurons.append(neuron)
            if any(neuron.__class__ == neurolink.sink for neurolink in self.genes):
                self.sinkNeurons.append(neuron)
        
        # update the numInputs, numOutputs, numSelfInputs
        self.calculateConnectivity()

        # remove all genes that don't resolve in a logical connection
        self.removeUselessGenes()

        # assert corresponding sinks to every source neuron
        self.assertOwnSinks()
        # for neuron in self.sourceNeurons:
        #     print(f"{neuron}: {neuron.ownSinks}")

        # last step: evaluate if the genome is functioning or not
        self.checkFunctioningGenome()

    def calculateConnectivity(self):
        "calculate the number of Inputs, Outputs and selfInputs for each neuron"
        
        #print("all neurons:", self.allNeurons)
        for neuron in self.allNeurons:
            #print(neuron, neuron.numOutputs)
            # reset the count
            neuron.numInputs = 0
            neuron.numOutputs = 0
            neuron.numSelfInputs = 0
            #print("reset", neuron)
            # recount the connections
            for neurolink in self.genes:
                if neurolink.source == neuron.__class__:
                    neuron.numOutputs += 1
                if neurolink.sink == neuron.__class__:
                    neuron.numInputs += 1
                if neurolink.source == neuron.__class__ and neurolink.sink == neuron.__class__:
                    neuron.numSelfInputs += 1
        
    def removeUselessGenes(self):
        "dangerous business"

        # need to be also removed from allNeurons
        
        for neuron in self.sinkNeurons:
            if neuron.__class__ in internal_dict.values():
                # remove all internal neurons which have numOutputs 0 and the neurolinks that lead to it
                if neuron.numOutputs == 0:
                    self.sinkNeurons.remove(neuron)
                    #print("removed", neuron)
                    try:
                        self.allNeurons.remove(neuron)
                    except KeyError:
                        pass
                    selfLinks_to_remove = [neurolink for neurolink in self.genes if neurolink.sink == neuron.__class__]
                    if selfLinks_to_remove:
                        for selfLink_to_remove in selfLinks_to_remove:
                            self.genes.remove(selfLink_to_remove)
                            #print("removed link", selfLink_to_remove)
                # remove all internal neurons which have numInputs 0 and the neurolinks that lead from it
                if neuron.numInputs == 0:
                    self.sinkNeurons.remove(neuron)
                    # print("removed", neuron)
                    try:
                        self.allNeurons.remove(neuron)
                    except KeyError:
                        pass
                    links_to_remove = [neurolink for neurolink in self.genes if neurolink.source == neuron.__class__]
                    if links_to_remove:
                        for selfLink_to_remove in links_to_remove:
                            self.genes.remove(selfLink_to_remove)
                            # print("removed link", selfLink_to_remove)
                # remove all internal neurons which have numSelfInputs = numOutputs or numInputs, + its neurolinks
                elif (neuron.numOutputs == neuron.numSelfInputs or neuron.numInputs == neuron.numSelfInputs) and neuron.numSelfInputs > 0:
                    self.sinkNeurons.remove(neuron)
                    # print("removed", neuron)
                    try:
                        self.sourceNeurons.remove(neuron)
                        self.allNeurons.remove(neuron)
                    except KeyError:
                        pass
                    selfLinks_to_remove = [neurolink for neurolink in self.genes if neurolink.source == neuron.__class__ or neurolink.sink == neuron.__class__]
                    if selfLinks_to_remove:
                        for selfLink_to_remove in selfLinks_to_remove:
                            self.genes.remove(selfLink_to_remove)
                            # print("removed link", selfLink_to_remove)
        # now check if there are any sources left with numOutputs 0 and if yes, remove them
        self.calculateConnectivity()
        for neuron in self.sourceNeurons:
            if neuron.numOutputs == 0:
                self.sourceNeurons.remove(neuron)
                # print("removed", neuron)
                try:
                    self.allNeurons.remove(neuron)
                except KeyError:
                    pass
        # also check if there are any sinks left with numInputs 0
        for neuron in self.sinkNeurons:
            if neuron.numInputs == 0:
                self.sinkNeurons.remove(neuron) 
                # print("removed", neuron)
                try:
                    self.allNeurons.remove(neuron)
                except KeyError:
                    pass
        self.calculateConnectivity()

        # NOTE: This could lead to problems if there are longer chains of internal neurons that link each other..
        # and don't resolve in an action neuron: The last internal neuron will get removed along with its neurolink,
        # the next internal neuron as well, but if there is another previous connection leading to that neuron it will
        # probably generate an error because it can't find its sink neuron. Should only pop up when multiple internal
        # neurons are enabled.

        # print(f"sources: {self.sourceNeurons}, sinks: {self.sinkNeurons}")

    def assertOwnSinks(self):
        "sort the corresponding sink objects into the ownSinks-list of the source neuron"

        for neurolink in self.genes:
            source_neuron = next(obj for obj in self.sourceNeurons if neurolink.source == obj.__class__)
            sink_neuron = next(obj for obj in self.sinkNeurons if neurolink.sink == obj.__class__)
            weight = neurolink.weight
            source_neuron.ownSinks.append((sink_neuron, weight))

    def checkFunctioningGenome(self):
        "check if there are any action neurons in the sink list or sensors in the source list"
        "this does'nt catch all non-functioning genomes, especially if there are many internal neurons,"
        "but in most cases this won't be a problem memorywise because the remaining connections will never be called"

        if any(neuron.__class__ in sensor_dict.values() for neuron in self.sourceNeurons) or any(neuron.__class__ in action_dict.values() for neuron in self.sinkNeurons):
            self.functioningGenome = True
        else: 
            self.functioningGenome = False

    
    def executeGenome(self):
        "execute all sensor neurons, the neural network will do the rest"
        if self.functioningGenome:
            for sensor_neuron in self.sourceNeurons:
                if sensor_neuron.__class__ in sensor_dict.values():
                    sensor_neuron.execute()



################################################
# NEURAL NETWORK

"""Neurolinks form connections between Neuron objects by telling the Genome-class which sources and sinks belong
to each other. They generate these connections randomly by birth or can inherit them from previous pixies."""

class Neurolink():
    ""

    def __init__(self, attributedPixie, inheritedDNA=None):
        self.attributedPixie = attributedPixie
        self.inheritedDNA = inheritedDNA
        if not inheritedDNA:
            self.DNA = self.generateDNA()
        else:
            self.DNA = inheritedDNA
            if len(self.DNA) != 32:
                raise ValueError("DNA is not 32 characters long!")
        self.source = None
        self.sink = None
        self.weight = None
        self.mapIDs2Links()

    def __str__(self):
        return f"DNA: {self.DNA}, source: {self.source}, sink: {self.sink}, weight: {self.weight}"

    def generateDNA(self):
        "generate a 32bit binary string which codes for a neuronal link"
        # example DNA: '00001100011110010101111111111111'
        #               ^^      ^^       ^
        #               ^src ID|^sink ID|weigth (16bit)
        #               srctype|sinktype     

        DNA_string = format(random.randint(0, (2**32)-1), "032b")

        return DNA_string
    
    def mapDNA2IDs(self):
        "convert the 32bit string into integers for source/sink IDs"
        DNA = self.DNA

        src_type = int(DNA[0], base=2)
        snk_type = int(DNA[8], base=2)

        src_ID = int(DNA[1:8], base=2) # int between 0 and 127
        snk_ID = int(DNA[9:16], base=2) # -"-

        weight_str = DNA[16:]
        # weight (16bit str) gets converted to a signed integer between +32767 and -32768
        if weight_str[0] == '1':  # negative
            weight = int(weight_str, 2) - (1 << len(weight_str))
        else:  # positive
            weight = int(weight_str, 2)

        # return a tuple with following example format: (1, 69, 0, 80, -11691)
        return [src_type, src_ID, snk_type, snk_ID, weight]
    
    def normIDs(self):
        "normalize the map IDs so that each number corresponds to a single function in the neuron list"
        map = self.mapDNA2IDs()

        if map[0] == 0: # source internal neuron
            normfactor_src = 2**7 / (len(internal_dict)-1)
            map[1] = round(map[1] / normfactor_src)
        elif map[0] == 1: # source sensor neuron
            normfactor_src = 2**7 / (len(sensor_dict)-1)
            map[1] = round(map[1] / normfactor_src)
        
        if map[2] == 0: # sink internal neuron
            normfactor_sink = 2**7 / (len(internal_dict)-1)
            map[3] = round(map[3] / normfactor_sink)
        elif map[2] == 1: # sink action neuron
            normfactor_sink = 2**7 / (len(action_dict)-1)
            map[3] = round(map[3] / normfactor_sink)

        map[4] = map[4] / 16384 # a float between -2 and 2 comes out

        return (map[0], map[1], map[2], map[3], map[4])
    
    def mapIDs2Links(self):
        "map the IDs to the corresponding neuron objects and save them in the source/sink variable"
        map = self.normIDs()

        if map[0] == 0: # internal neuron
            self.source = internal_dict[map[1]]
        elif map[0] == 1: # sensory neuron
            self.source = sensor_dict[map[1]]
        
        if map[2] == 0: # internal neuron
            self.sink = internal_dict[map[3]]
        elif map[2] == 1: # sensory neuron
            self.sink = action_dict[map[3]]
        
        self.weight = map[4]


#############################################
# NEURONS AND FUNCTIONS

"""There are three superclasses of neurons: sensor Neurons, internal Neurons and action Neurons.
In each superclass there are subclasses which represent the single neurons which in turn are responsible
for the functions that each pixie can express.
Neuron objects get instantiated individually for each pixie and store their own inputs, outputs and corresponding
sinks (if any) and weights.

Neurons act very autonomously and execute automatically when enough inputs have arrived (apart from sensor neurons),
and also automatically transfer these outputs to the next neuron (unless they are an action neuron).

Neuron classes are stored in neuron_dicts so they can be referenced by Neurolinks or other functions."""


# neuron_dicts are for storing object templates for the corresponding neuron
sensor_dict = {
    0: neurons.xPosition,
    1: neurons.yPosition,
    2: neurons.inverseXPosition,
    3: neurons.inverseYPosition,
    4: neurons.randomOutput, 
    5: neurons.oscillator,
    6: neurons.popDensityFwd,
    7: neurons.blockageFwd,
    8: neurons.barrierFwd,
    9: neurons.nextPixie,
    10: neurons.nextObject,
    11: neurons.OnOff,
    12: neurons.geneticSimilarity,
    13: neurons.xPosition
} # first and last index always has to code for the same neuron!

internal_dict = {
    0: neurons.InterNeuron1,
    1: neurons.InterNeuron2,
    2: neurons.InterNeuron3,
    3: neurons.InterNeuron1
} # first and last index always has to code for the same neuron!

action_dict = {
    0: neurons.moveN,
    1: neurons.moveS,
    2: neurons.moveE,
    3: neurons.moveW,
    4: neurons.moveB,
    5: neurons.moveF,
    6: neurons.moveL,
    7: neurons.moveR,
    8: neurons.moveRandom,
    9: neurons.setOscPeriod,
    10: neurons.setSearchRadius,
    11: neurons.turnLeft,
    12: neurons.turnRight,
    13: neurons.eatFood,
    14: neurons.initiateSex,
    15: neurons.moveN
} # first and last index always has to code for the same neuron!

################################################
# SELECTION CRITERIA

selection_criteria = {
    0: lambda x: selection.doNothing(x),
    1: lambda x: selection.killRightHalf(x),
    2: lambda x: selection.killLeftHalf(x), 
    3: lambda x: selection.killMiddle(x),
    4: lambda x: selection.killEdges(x),
    5: lambda x: selection.killLowEnergy(x)
}

################################################
# ENVIRONMENT

environment_dict = {
    0: lambda x: environment.noEnvironment(x),
    1: lambda x: environment.barrierMiddleVertical(x),
    2: lambda x: environment.sparseFood(x),
    3: lambda x: environment.denseFood(x)
}

################################################
# SIMULATOR FUNCTIONS

def eachSimStep(world, gen=None):
    ""
    # execute the genome for each pixie in the world
    for pixie in world.getInhabitants():
        pixie.executeGenome()
        pixie.executeMove()

    # execute all actions that have been queued:
    # for pixie in world.queueForMove:
    #     pixie.executeMove() ##THIS GOT MOVED TO THE THE PIXIE LOOP ABOVE
    for pixie in world.queueForKill:
        world.inhabitants.remove(pixie)
        
    world.queueForMove = set() # (obsolete)
    world.queueForKill = set()

    world.updateWorld()

    # create a frame for the gif
    if createGIF != "none":  
        if gen:
            if createGIF == "selected" and gen in createGIFfor:
                render.render(world)
            elif createGIF == "every" and (gen) % createGIFevery == 0:
                render.render(world)
            
        else: 
            render.render(world)

def spawnPixie(world, inheritedDNA=None, newHexColor=None):
    "spawn a single pixie"

    # a pixie needs a world to inhabit, a new name, and optionally a color or inherited DNA
    newPixieName = "Pixie_" + str(random.randint(0,9999))
    if not newHexColor:
        newHexColor = "%06x" % random.randint(0,0xFFFFFF) # maybe obsolete
    t = 0
    while t < 1:
        newYXPos = (random.randint(0, np.size(world.grid, 0)-1), random.randint(0, np.size(world.grid, 0)-1))
        if world.grid[newYXPos]: # check if cell is already inhabited
            continue
        t += 1

    newPixieName = pixie(worldToInhabit=world, name=newPixieName, yxPos=newYXPos, inheritedDNA=inheritedDNA, color=newHexColor)
    world.updateWorld()

def newGeneration(oldWorld=None, existingGenomes=None):
    "spawn a new generation"

    if oldWorld: # inherit genes from the predecessing generation
        oldPopulation = oldWorld.inhabitants
        newWorld = world(size=gridsize)
        #create environment
        environment_dict[environment_key](newWorld)

        if geneticDrift == True:
            for i in range(numberOfPixies):
                predecessor = random.choice(oldPopulation)

                inheritedGenes = [neurolink.DNA for neurolink in predecessor.genome.genes]
                possiblyMutatedDNA = mutateGenes(gene_list=inheritedGenes)

                inheritedColor = predecessor.color # this doesn't allow for color mutations

                spawnPixie(newWorld, inheritedDNA=possiblyMutatedDNA, newHexColor=inheritedColor)
        else:
            for predecessor in oldPopulation:
                "each surviving pixie produces one offspring"
                inheritedGenes = [neurolink.DNA for neurolink in predecessor.genome.genes]
                possiblyMutatedDNA = mutateGenes(gene_list=inheritedGenes)

                inheritedColor = predecessor.color # this doesn't allow for color mutations

                spawnPixie(newWorld, inheritedDNA=possiblyMutatedDNA, newHexColor=inheritedColor)

            while len(newWorld.inhabitants) < numberOfPixies:
                "fill up the rest with randomly chosen pixies"
                predecessor = random.choice(oldPopulation)

                inheritedGenes = [neurolink.DNA for neurolink in predecessor.genome.genes]
                possiblyMutatedDNA = mutateGenes(gene_list=inheritedGenes)

                inheritedColor = predecessor.color # this doesn't allow for color mutations

                spawnPixie(newWorld, inheritedDNA=possiblyMutatedDNA, newHexColor=inheritedColor)

    else: # inherit genes from predetermined Populations
        newWorld = world(size=gridsize)
        # create environment
        environment_dict[environment_key](newWorld)

        if existingGenomes:
            for genome in existingGenomes:
                spawnPixie(newWorld, inheritedDNA=genome)
        else: # generate new genes from scratch
            for i in range(numberOfPixies):
                spawnPixie(newWorld)
    
    return newWorld

def mutateGenes(gene_list):
    "iterate through the DNA bits and change it with a small chance"
    
    for gene in gene_list:
        # for i in range(len(gene)):
        #     if random.random() < mutationRate:
        #         gene[i] = "1" if gene[i] == "0" else "0"
        #         gene = "".join(["1" if bit == "0" else "0" for bit in gene if random.random() < mutationRate])
        gene = "".join(["1" if bit == "0" and random.random() < mutationRate else "0" if bit == "1" and random.random() < mutationRate else bit for bit in gene])
    return gene_list

def saveMetaGenome(world):
    "save the Genomes of all pixies in a csv file"

    # genes contains neurolink objects, which have the attributes .attributedPixie, .DNA, .source, .sink and .weight
    genomes_list = [inhabitant.genome.genes for inhabitant in world.getInhabitants()]

    with open(f"metagenome.txt", "w") as textfile:
        textfile.write("PixieName,DNA,connections\n")
        for genes_list in genomes_list:
            DNA_list = []
            sources_list = []
            sinks_list = []
            weights_list = []
            connections_list = []
            pixieName = "placeholder"
            for neurolink in genes_list:
                pixieName = neurolink.attributedPixie
                DNA_list.append(neurolink.DNA)
                sources_list.append(neurolink.source)
                sinks_list.append(neurolink.sink)
                weights_list.append(neurolink.weight)

            connections = zip(sources_list, sinks_list, weights_list)
            for i in connections:
                connections_list.append(str(i))
            connections_str = ";".join(connections_list)
            DNA_str = ";".join(DNA_list)

            textfile.write(f"{pixieName},{DNA_str},{connections_str}\n")

def readMetaGenome(textfile):
    "read the metagenome textfile and extract the DNA of each Pixie, and save it in a list"

    metagenome = []

    with open(textfile, "r") as metagenome_file:
        for i, line in enumerate(metagenome_file):
            if i > 0:
                elements = line.strip().split(",")
                # the DNA should be in the second column
                genome = elements[1].split(";")

                metagenome.append(genome)

    return metagenome

def applySelectionCriteria(world):
    ""
    # get Function from selection_criteria dict
    i = selectionCriterium
    selectionFunction = selection_criteria[i]

    # execute Function
    selectionFunction(world)
    world.updateWorld()

def calculateDiversity(world):
    if calc_diversity:
            unique_genomes = set()
            for pixie in world.inhabitants: # add the DNA of every gene
                unique_genomes.add(tuple(x.DNA for x in pixie.genome.genes))
            diversity = len(unique_genomes) / numberOfPixies        #len(world.inhabitants) ???
            diversityOverTime.append(diversity)

def calculateSurvivalRate(world):
    if calc_survivalRate:
        survivalRate = len(world.inhabitants) / numberOfPixies       
        survivalRateOverTime.append(survivalRate)

def calculateSexualityRate(world):
    sexualityRate = world.sexualityCount / numberOfPixies
    sexualityOverTime.append(sexualityRate)

def simulateGenerations(startingPopulation=None):
    "Randomly simulate as many generations as specified. Optionally provide a starting Population (metagenome)."

    print("simulating...")
    start_time = time.time()

    if gridsize**2 < numberOfPixies:
        raise OverflowError("too many pixies for the grid!")

    # first generation: 
    firstWorld = newGeneration(existingGenomes=startingPopulation)
    calculateDiversity(firstWorld)
    for i in range(numberOfSimSteps):
        eachSimStep(firstWorld)

    # kill pixies that don't suffice the selection criteria
    applySelectionCriteria(firstWorld)
    if createGIF != "none":
        render.render(firstWorld)
        render.create_gif(filename=f"world_1.gif")
    if not firstWorld.inhabitants:
            print("total extinction!!!")
            return
    
    calculateSexualityRate(firstWorld)
    calculateSurvivalRate(firstWorld)

    # following generations:
    oldWorld = firstWorld
    for num in range(numberOfGenerations-1): # -1 because the first world already got created
        newWorld = newGeneration(oldWorld=oldWorld)
        calculateDiversity(newWorld)

        for i in range(numberOfSimSteps):
            eachSimStep(newWorld, gen=num+2)

        # kill pixies that don't suffice the selection criteria
        applySelectionCriteria(newWorld)
        if not newWorld.inhabitants:
            print("total extinction!!!")
            break

        if createGIF != "none":
            if createGIF == "every" and (num+2) % createGIFevery == 0:
                render.render(newWorld)
            elif createGIF == "selected" and (num+2) in createGIFfor:
                render.render(newWorld)

        # calculate the survival rate
        #calculateSexualityRate(firstWorld)
        calculateSurvivalRate(newWorld)

        # create a GIF
        if createGIF != "none":
            if createGIF == "every":
                if (num+2) % createGIFevery == 0:
                    render.create_gif(filename=f"world_{num+2}.gif")
            elif createGIF == "selected":
                if (num+2) in createGIFfor:
                    render.create_gif(filename=f"world_{num+2}.gif")

        oldWorld = newWorld

        # in the last world, save the metagenome
        if num == numberOfGenerations-2:
            if save_metagenome:
                saveMetaGenome(newWorld)
    
    print("all done!")
    print(f"time elapsed: {time.time() - start_time} seconds")

    if calc_survivalRate or calc_diversity:
        render.calcSurvivalAndDiversity(list_survival=survivalRateOverTime, list_diversity=diversityOverTime)


################################################
# PARAMETERS

# world parameters
gridsize = 30
numberOfGenes = 8
numberOfPixies = 500
numberOfGenerations = 50
numberOfSimSteps = 20
selectionCriterium = 1 # key for selection_criteria dict
environment_key = 0 # key for environment_dict dict

geneticDrift = False # if False, then each surviving pixie automatically produces at least one offspring

# pixie parameters
mutationRate = 0.005
defaultEnergy = 0

# analytics
save_metagenome = False
calc_survivalRate = True
calc_diversity = True
createGIF = "selected"  # "none", "every" or "selected"
createGIFevery = 1
createGIFfor = [numberOfGenerations, 1, 2, 3, 10, 20, 100, 200, 300, 400, 500]

survivalRateOverTime = [] # list containing survivalrate for each gen
diversityOverTime = [] 
sexualityOverTime = []


simulateGenerations()
#simulateGenerations(readMetaGenome("metagenome.txt")) # a metagenome object can be provided as an argument if a previous population 
