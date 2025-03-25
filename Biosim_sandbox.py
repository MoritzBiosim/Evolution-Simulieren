import random
import numpy as np
import math
import Biosim_sandbox_render as render


class world():
    """class containing the grid. Multiple grids are possible, but most of the times the
    simulation takes place in only one world ("grid0")."""

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
        
        return f"\"{self.name}\" at {self.yxPos}"
    
    def getPosition(otherObject):
        "returns the absolute coordinates of the referenced object"

        return otherObject.yxPos

class pixie(object):
    """class containing the pixies which roam the world.
    A pixie can scan its surroundings and sense nearby other objects (pixies or other),
    move to the left of the grid and thats pretty much it by now"""

    # listOfFunctions = []

    def __init__(self, worldToInhabit, name, yxPos, color="FF0000", genome=None):
        ""
        super().__init__(worldToInhabit, name, yxPos)
        #   List of all functions for idividual genes to choose from
        self.energy = defaultEnergy
        self.color = color
        self.genome = genome
        self.shape = "round"

        # variables to track the "movement urge" in each simstep. These get reset every new simstep
        self.moveX = 0
        self.moveY = 0

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
        self.genome=genome(attributedPixie=self)

    def executeGenome(self):
        ""
        self.genome.executeGenes()

    ## moving around

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
            return
        if self.yxPos[0]+vector[0] < 0 or self.yxPos[0]+vector[0] > np.size(world.grid, 0)-1:
            return
        else:
            self.yxPos = (self.yxPos[0]+vector[0], self.yxPos[1]+vector[1]) # moving
            world.updateWorld()
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

    def getNormalizedDirection(self, object=None, vector=None):
        """return the direction of a referenced object OR vector as a vector tuple by checking 
        if the calculated angle is within 22.5° of any cardinal direction"""

        if not vector and not object:
            raise ValueError("neither an object or vector was provided")
        
        if vector:
            angle = self.getRelativeAngle(relVector=vector)
        elif object:
            angle = self.getRelativeAngle(otherObject=object)

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

        world = self.worldToInhabit # this makes providing the argument "world" obsolete

        foundObjects = []
        gridSize = np.size(world.grid, 0) # edge length of the grid (only works for square grids)

        for x in range(max(0, self.yxPos[1] - self.searchRadius), min(gridSize, self.yxPos[1] + self.searchRadius)):
            for y in range(max(0, self.yxPos[0] - self.searchRadius), min(gridSize, self.yxPos[0] + self.searchRadius)):
                if math.sqrt((x-self.yxPos[1])**2 + (y - self.yxPos[0])**2) <= self.searchRadius:
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
            if i[0] in world.inhabitants:
                neighbouring_pixies.append(i)

        if neighbouring_pixies:
            nearest = min(neighbouring_pixies, key=lambda x: x[1])
            return nearest[0]
        else:
            print("mäp")
            pass

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
    
    def getRelativeAngle(self, otherObject):
        """returns the angle of the referenced object in relation to self, angles
        are expressed as radiant with range (-pi/pi), going clockwise from the right"""

        relVector = self.getRelativeVector(otherObject)
        relAngle = math.atan2(relVector[0],relVector[1])
        if relAngle < 0 : 
            relAngle += 2*math.pi # angle now runs counterclockwise starting east

        return relAngle
 
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

################################################
# GENOME CLASSES

"""when a new genome object is instantiated, this actually means that a fixed number of new neurolinks have to be
generated (as a 32bit integer). This neurolink has a source and sink attribute linked to a specific neuron,
which can be found by looking in the 'list of functions/neurons'. For each unique source and sink function in the
whole genome, a Neuron object has to be instantiated for the individual pixie (((First it could be checked if the
link even results in a connection with an action output or if internal neurons only link to themselves, and if yes
be discarded to save memory))). All individual neuron objects are tracked in a set{} in the genome object.

Additionally all neurolinks are stored in three separate lists: One for all neurolinks starting from a sensor and
going to a internal neuron, one for internal-internal connections (neccessary?) and one for internal
neurons/sensors going to action neurons.

For each simstep the genome then iterates through the sensor-set and stores the output values in the object itself,
then iterates through the neurolinks to transfer the source-outputs into the sink-neuron (if multiple inputs arrive
they are added up). After all sensor-linked neurolinks are computed, the internal neurons are called up, and after
they have computed their input values all action-linked neurolinks are computed to transfer all input values to
the action neurons, which can finally be executed.

If no functional genome arises (only invalid connections), the executeGenome Function should pass - this could be
controlled via a 'validNeuralNetwork' bool."""

class genome():
    """class containing all existing genomes. 
    Each genome has a corresponding Object it belongs to (currently only Pixies can have genomes)
    and a number of genes=Neurolinks"""

    def __init__(self, attributedPixie):
        ""
        self.attributedPixie = attributedPixie
        self.length = numberOfGenes
        self.genes = []
        self.functioningGenome = True

        self.allNeuronClasses = set() # includes all neuron class objects
        self.sources = set() # includes the class objects of all source neurons     # obsolete?
        self.sinks = set() # includes the class objects of all sink neurons         # obsolete?

        self.allNeurons = set() # includes all neuron objects    
        self.sourceNeurons = [] # contains the actual neuron objects
        self.sinkNeurons = []
        
        self.sensorToInternal = []
        self.internalToInternal = []
        self.sensor_InternalToAction = []

        # instantiate new Neurolink objects
        for i in range(0, self.length):
            self.genes.append(Neurolink(self.attributedPixie))
        
        self.loadGenome()

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

        # sort Neurolinks by starting point/destination
        self.sortNeurolinks()

        # last step: evaluate if the genome is functioning or not
        self.checkFunctioningGenome()

    def sortNeurolinks(self):
        "sort Neurolinks by starting point / destination"
        for neurolink in self.genes: 
            if neurolink.DNA[0] == "1" and neurolink.DNA[8] == "0": # sensor to internal
                self.sensorToInternal.append(neurolink)
            elif neurolink.DNA[0] == "0" and neurolink.DNA[8] == "0": # internal to internal
                self.internalToInternal.append(neurolink)
            elif neurolink.DNA[0] == "1" and neurolink.DNA[8] == "1": # sensor to action
                self.sensor_InternalToAction.append(neurolink)
            elif neurolink.DNA[0] == "0" and neurolink.DNA[8] == "1": # internal to action
                self.sensor_InternalToAction.append(neurolink)

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
                    print("removed", neuron)
                    try:
                        self.allNeurons.remove(neuron)
                    except ValueError:
                        pass
                    selfLinks_to_remove = [neurolink for neurolink in self.genes if neurolink.sink == neuron.__class__]
                    if selfLinks_to_remove:
                        for selfLink_to_remove in selfLinks_to_remove:
                            self.genes.remove(selfLink_to_remove)
                            print("removed link", selfLink_to_remove)
                # remove all internal neurons which have numInputs 0 and the neurolinks that lead from it
                if neuron.numInputs == 0:
                    self.sinkNeurons.remove(neuron)
                    print("removed", neuron)
                    try:
                        self.allNeurons.remove(neuron)
                    except ValueError:
                        pass
                    links_to_remove = [neurolink for neurolink in self.genes if neurolink.source == neuron.__class__]
                    if links_to_remove:
                        for selfLink_to_remove in links_to_remove:
                            self.genes.remove(selfLink_to_remove)
                            print("removed link", selfLink_to_remove)
                # remove all internal neurons which have numSelfInputs = numOutputs, + its neurolinks
                elif neuron.numOutputs == neuron.numSelfInputs and neuron.numSelfInputs > 0:
                    self.sinkNeurons.remove(neuron)
                    print("removed", neuron)
                    try:
                        self.sourceNeurons.remove(neuron)
                        self.allNeurons.remove(neuron)
                    except ValueError:
                        pass
                    selfLinks_to_remove = [neurolink for neurolink in self.genes if neurolink.source == neuron.__class__ or neurolink.sink == neuron.__class__]
                    if selfLinks_to_remove:
                        for selfLink_to_remove in selfLinks_to_remove:
                            self.genes.remove(selfLink_to_remove)
                            print("removed link", selfLink_to_remove)
        # now check if there are any sources left with numOutputs 0 and if yes, remove them
        self.calculateConnectivity()
        for neuron in self.sourceNeurons:
            if neuron.numOutputs == 0:
                self.sourceNeurons.remove(neuron)
                print("removed", neuron)
                try:
                    self.allNeurons.remove(neuron)
                except ValueError:
                    pass
        # also check if there are any sinks left with numInputs 0
        for neuron in self.sinkNeurons:
            if neuron.numInputs == 0:
                self.sinkNeurons.remove(neuron) 
                print("removed", neuron)
                try:
                    self.allNeurons.remove(neuron)
                except ValueError:
                    pass
        self.calculateConnectivity()

        # NOTE: This could lead to problems if there are longer chains of internal neurons that link each other..
        # and don't resolve in an action neuron: The last internal neuron will get removed along with its neurolink,
        # the next internal neuron as well, but if there is another previous connection leading to that neuron it will
        # probably generate an error because it can't find its sink neuron. Should only pop up when multiple internal
        # neurons are enabled.

        #print(f"sources: {self.sources}, sinks: {self.sinks}")

    def checkFunctioningGenome(self):
        "check whether there is any content in the sourceNeurons or sinkNeurons lists"

        if self.sourceNeurons or self.sinkNeurons:
            self.functioningGenome = True
        else: 
            self.functioningGenome = False

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
    def executeGenes(self):
        "main loop for each pixie in each simstep"

        print("-----------execute round 0")
        print("sources:", self.sourceNeurons)
        print("sinks:", self.sinkNeurons)
        print("s_i_neurolinks", self.sensorToInternal)
        print("i_i_neurolinks", self.internalToInternal)
        print("si_a_neurolinks", self.sensor_InternalToAction)
        self.printNeurons()
        # execute all sensor neurons
        print("-----------execute round 1 (sensors)")
        for source_neuron in self.sourceNeurons:
            if source_neuron.__class__ in sensor_dict.values():
                print("sensor neurons getting computed")
                source_neuron.execute()
        self.printNeurons()
        # channel the outputs to the next internal neuron
        print("------------transfer output values s->i")
        for s_i_neurolink in self.sensorToInternal:                               
            sensor_output = next((obj.output for obj in self.sourceNeurons if obj.__class__ == s_i_neurolink.source), 100)
            print(sensor_output)           
            sink_obj = next((obj for obj in self.sinkNeurons if obj.__class__ == s_i_neurolink.sink), None)
            sink_obj.input += sensor_output
            print(f"{s_i_neurolink.source}->{s_i_neurolink.sink}")
        # execute all internal neurons
        print("-----------execute round 2 (internals)")
        for int_neuron in self.sourceNeurons:
            if int_neuron.__class__ in internal_dict.values():
                print("internal neurons getting computed")
                int_neuron.execute()
        self.printNeurons()
        # clear the input values of each internal neuron
        print("------------clear all internal input values")
        for int_neuron in self.sinkNeurons:
            if int_neuron.__class__ in internal_dict.values():
                int_neuron.input = 0
        # feed the outputs of internal neurons linked to another internal neurons into themselves
        print("-------------transfer all outputs i->i")
        for i_i_neurolink in self.internalToInternal:
            internal_output = next((obj.output for obj in self.sourceNeurons if obj.__class__ == i_i_neurolink.source), 100)
            sink_obj = next((obj for obj in self.sinkNeurons if obj.__class__ == i_i_neurolink.sink), None)
            # for obj in self.sinkNeurons:
            #     print(f"Comparing: {obj.__class__} == {i_i_neurolink.sink}")
            #     print(f"id(obj.__class__): {id(obj.__class__)}, id(i_i_neurolink.sink): {id(i_i_neurolink.sink)}")

            #     if obj.__class__ == i_i_neurolink.sink:
            #         print("MATCH FOUND ✅")
            #         sink_obj = obj
            #         break
            # else:
            #     print("❌ Kein Match gefunden!")
            #     sink_obj = None
            # print(f"🚀 sink_obj gefunden: {sink_obj}, input-Wert: {sink_obj.input}")
            sink_obj.input += internal_output
        # pull all outputs as inputs into the action neurons
        print("----------transfer all outputs si->a")
        for si_a_neurolink in self.sensor_InternalToAction:
            si_output = next((obj.output for obj in self.sourceNeurons if obj.__class__ == si_a_neurolink.source), 100)
            sink_obj = next((obj for obj in self.sinkNeurons if obj.__class__ == si_a_neurolink.sink), None)
            print("sink input", sink_obj)
            sink_obj.input += si_output
        # execute all action neurons
        print("-----------execute round 3 (actions)")
        for action_neuron in self.sinkNeurons:
            if action_neuron.__class__ in action_dict.values():
                print("computing action neurons")
                action_neuron.execute()
        self.printNeurons()
        # clear all input values of each action neuron
        print("-------------clear all input values for action neurons")
        for action_neuron in self.sinkNeurons:
            if action_neuron.__class__ in action_dict.values():
                action_neuron.input = None
            

class gene(): # OBSOLETE
    """class containing all existing genes. Each gene has a 
    functionality (one of the methods of Pixies) and a floating point probability of being expressed. 
    0 by default, can mutate."""
    
    def __init__(self):
        ""
        #self.DNA = self.generateDNA()

    def __str__(self):

        return


    def executeFunctionality(self):
        "executing the function encoded in the gene with the specific expressionProbaility"
        

################################################
# NEURAL NETWORK

class Neurolink():
    ""

    def __init__(self, attributedPixie):
        self.attributedPixie = attributedPixie
        self.DNA = self.generateDNA()
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

# Superclasses for the different Neurons
class sensorN():
    ""
    def __init__(self, attributedPixie):
        self.attributedPixie = attributedPixie # this is crucial so that each instantiated function can reference its own pixie
        self.output = 0
        self.numInputs = 0
        self.numOutputs = 0
        self.numSelfInputs = 0

    def __str__(self):
        return f"pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    # def getNumOutputs(self):
    #     return self.numOutputs
    # def getNumInputs(self):
    #     return self.numInputs
    # def getNumSelfInputs(self):
    #     return self.numSelfInputs
    
class internalN():
    ""

    def __init__(self, attributedPixie):
        self.attributedPixie = attributedPixie
        self.input = 0
        self.output = 0
        self.numInputs = 0
        self.numOutputs = 0
        self.numSelfInputs = 0

    def __str__(self):
        return f"pixie {self.attributedPixie}, input {self.input}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

class actionN():
    ""

    def __init__(self, attributedPixie):
        self.attributedPixie = attributedPixie
        self.input = 0
        self.numInputs = 0
        self.numOutputs = 0
        self.numSelfInputs = 0

    def __str__(self):
        return f"pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"


############# SENSOR NEURONS

class xPosition(sensorN):
    "senses the x-Position of the pixie and outputs highest values when on the far right and lowest on the far left"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"xPosition: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"


    def execute(self):
        ""
        xPos = self.attributedPixie.yxPos[1]
        world_width = self.attributedPixie.worldToInhabit.size

        out = xPos / world_width
        print(f"xPosition output: {out}")
        self.output = out
    
class yPosition(sensorN):
    "senses the y-Position of the pixie and outputs highest values when on the far north and lowest on the far south"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"yPosition: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        yPos = self.attributedPixie.yxPos[0]
        world_width = self.attributedPixie.worldToInhabit.size

        out = yPos / world_width

        self.output = out

# neuron_dicts are for storing object templates for the corresponding neuron
sensor_dict = {
    0: xPosition,
    1: yPosition,
    2: xPosition
} # first and last index always has to code for the same neuron!

############# INTERNAL NEURONS

class InterNeuron1(internalN):
    "run the input through a tanh function and return the value"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"Internal Neuron 1: pixie {self.attributedPixie}, input {self.input}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "run the input through a tanh function and return the value"

        out = math.tanh(self.input)

        self.output = out
        # self.input = 0

internal_dict = {
    0: InterNeuron1,
    1: InterNeuron1
} # first and last index always has to code for the same neuron!

############# ACTION NEURONS

class moveN(actionN):
    "move one step to the north"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"moveN: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"


    def execute(self):
        "input gets converted to a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            yComponent = -1 * sign # this means that if the weight is negative, the pixie will move in the opposite direction
            self.attributedPixie.moveY += yComponent

class moveS(actionN):
    "move one step to the south"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"moveS: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"


    def execute(self):
        "input gets converted to a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            yComponent = 1 * sign
            self.attributedPixie.moveY += yComponent

class moveE(actionN):
    "move one step to the north"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"moveE: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"


    def execute(self):
        "input gets converted to a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            xComponent = 1 * sign
            self.attributedPixie.moveX += xComponent

class moveW(actionN):
    "move one step to the north"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"moveW: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"


    def execute(self):
        "input gets converted to a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            xComponent = -1 * sign
            self.attributedPixie.moveX += xComponent

action_dict = {
    0: moveN,
    1: moveS,
    2: moveE,
    3: moveW,
    4: moveN
} # first and last index always has to code for the same neuron!



################################################
# PARAMETERS

numberOfGenes = 4

defaultEnergy = 0

################################################
# MANUAL INSTANCING

grid0 = world(size=10)

myPixie = pixie(grid0, "myPixie1", (3, 4))
myGenome = myPixie.getGenome()
myGenes = myGenome.getGenes()
for i in myGenes:
    print(i)
if myGenome.functioningGenome:
    myPixie.executeGenome()
else:
    print("no functioning genome")
print(myPixie.yxPos, myPixie.moveY, myPixie.moveX)