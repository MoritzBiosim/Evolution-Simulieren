"This file contains all Neuron classes"
import math
import numpy as np
import random
import Biosim_sandbox_environment as env


# Superclasses for the different Neurons
class sensorN():
    ""
    def __init__(self, attributedPixie):
        self.attributedPixie = attributedPixie # this is crucial so that each instantiated function can reference its own pixie
        self.output = 0
        self.numInputs = 0
        self.numOutputs = 0
        self.numSelfInputs = 0

        self.ownSinks = [] # contains tuples with (sink_object, weight)

    def __str__(self):
        return f"pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def transferOutput(self):
        ""
        for sink_weight in self.ownSinks:
            sink_weight[0].input += self.output * sink_weight[1]
            sink_weight[0].inputTracker += 1
            sink_weight[0].checkIfExecute()
    
class internalN():
    ""

    def __init__(self, attributedPixie):
        self.attributedPixie = attributedPixie
        self.input = 0
        self.output = 0
        self.numInputs = 0
        self.numOutputs = 0
        self.numSelfInputs = 0
        self.inputTracker = 0

        self.ownSinks = [] # contains tuples with (sink_object, weight)

    def __str__(self):
        return f"pixie {self.attributedPixie}, input {self.input}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def checkIfExecute(self):
        if self.inputTracker >= (self.numInputs - self.numSelfInputs):
            self.execute()

    def transferOutput(self):
        ""
        for sink_weight in self.ownSinks:
            sink_weight[0].input += self.output * sink_weight[1]
            if sink_weight[0] != self:
                sink_weight[0].inputTracker += 1
                sink_weight[0].checkIfExecute()

    def clearInput(self):
        ""
        self.input = 0
        self.inputTracker = 0

class actionN():
    ""

    def __init__(self, attributedPixie):
        self.attributedPixie = attributedPixie
        self.input = 0
        self.numInputs = 0
        self.numOutputs = 0
        self.numSelfInputs = 0
        self.inputTracker = 0

    def __str__(self):
        return f"pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def checkIfExecute(self):
        if self.inputTracker >= (self.numInputs - self.numSelfInputs):
            self.execute()

    def clearInput(self):
        ""
        self.input = 0
        self.inputTracker = 0


################ SENSOR NEURONS
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
        # print(f"xPosition output: {out}")
        self.output = out

        self.transferOutput()
    
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
        self.transferOutput()

class inverseXPosition(sensorN):
    "output of xPosition, but 1-output"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"inverseXPosition: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"


    def execute(self):
        ""
        xPos = self.attributedPixie.yxPos[1]
        world_width = self.attributedPixie.worldToInhabit.size

        out = xPos / world_width
        # print(f"xPosition output: {out}")
        self.output = 1 - out

        self.transferOutput()

class inverseYPosition(sensorN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"inverseYPosition: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        yPos = self.attributedPixie.yxPos[0]
        world_width = self.attributedPixie.worldToInhabit.size

        out = yPos / world_width

        self.output = 1 - out
        self.transferOutput()
    
class randomOutput(sensorN):
    "outputs a random value between 0 and 1"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"random: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self):
        ""
        out = random.random()

        self.output = out
        self.transferOutput()

class oscillator(sensorN):
    "outputs an oscillating signal"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
        self.oscillatorPhase = 0

    def __str__(self):
        return f"oscillator: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):

        out = math.sin(self.oscillatorPhase)
        self.oscillatorPhase + (2*math.pi / self.attributedPixie.genome.oscillatorPeriod) # every simStep the value gets added

        self.output = out
        self.transferOutput()

class popDensityFwd(sensorN):
    "senses the population density around the pixie, with highest output directly in front"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"popDensityFwd: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self): 
        # get the view axis, compute the denstity 'quantum' for each pixie and sum it up
        # divide the sum by twice the search-Radius to get a value between 0 and 1

        cache = []

        viewAxis = self.attributedPixie.facing
        neighbourhood = self.attributedPixie.getAllEuclidianDistances()
        for tuple in neighbourhood:
            dist = tuple[1]
            if dist > 0:
                relAngle = self.attributedPixie.getRelativeAngle(otherObject=tuple[0])
                factor = math.cos(relAngle - viewAxis)
                cache.append(1 / dist * factor)
        
        self.output = sum(cache) / (1.9*(self.attributedPixie.genome.searchRadius-0.5)) # norming factor
        self.transferOutput()

class blockageFwd(sensorN):
    "checks if the field in facing direction is blocked and returns 1 if it is, 0 otherwise"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"blockageFwd: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        proximateObject = self.attributedPixie.searchProximateField()
        if proximateObject == None:
            self.output = 0
        else:
            self.output = 1
        self.transferOutput()
    
class barrierFwd(sensorN):
    "checks for a barrier in facing direction and returns 1 if there is one, 0 otherwise"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"barrierFwd: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        proximateObject = self.attributedPixie.searchProximateField()
        if proximateObject.__class__.__name__ == "stone":
            self.output = 1
        else:
            self.output = 0
        self.transferOutput()

class nextPixie(sensorN):
    "returns the inverse of the distance of the nearest Pixie in facing direction"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"pixieFwd: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        distances = []
        allFwdPixies = self.attributedPixie.getFwdPixies()
        if not allFwdPixies:
            self.output = 0
        else:
            nearestFwdPixie = allFwdPixies[0]
            d = self.attributedPixie.getEuclidianDistance(nearestFwdPixie)
            self.output = 1/d
        
        self.transferOutput()
    
class nextObject(sensorN):
    "returns the inverse of the distance of the nearest Object in facing direction"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"nextObject: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        distances = []
        allFwdObjects = self.attributedPixie.getFwdObjects()
        if not allFwdObjects:
            self.output = 0
        else:
            nearestFwdObject = allFwdObjects[0]
            d = self.attributedPixie.getEuclidianDistance(nearestFwdObject)
            self.output = 1/d
        
        self.transferOutput()

class borderDst(sensorN):
    "output 1 if the border is very near and 0 if it is very far"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"barrierFwd: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        # take the vector from the .facing attribute of the attributed pixie
        facingV = self.attributedPixie.getNormalizedDirection(angle=self.attributedPixie.facing)

        # while-loop: check if the facing-vector from the position of the pixie is inside the world borders.
        # if yes, multiply the facing vector by ++1 and check again
        # if no, break and return the length of the facing vector
        
        probingV = facingV
        worldSize = self.attributedPixie.worldToInhabit.size - 1
        
        for i in range(worldSize):
            yProbe = self.attributedPixie.yxPos[0] + probingV[0]*i
            xProbe = self.attributedPixie.yxPos[1] + probingV[1]*i

            if yProbe < 0 or yProbe > worldSize or xProbe < 0 or xProbe > worldSize:
                # out of bounds
                borderDistance = math.sqrt((probingV[0]*i)**2 + (probingV[1]*i)**2) 
                break
            else: 
                pass

        self.output = 1 - (borderDistance / worldSize)
        self.transferOutput()

class geneticSimilarity(sensorN):
    "compute the genetic similarity by using the sets of all neuron classes as hamming distance proxy"
    "outputs 1 if identical, zero if totally different"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"geneticSimilarity: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "get the respective sets of all neuron Classes of the attributed and the other pixie. "
        "Compute the number of neuron classes that overlap by combining the sets. "
        "Divide this number (reverse proxy for hamming distance) "
        "by the number of neuron Classes attributed Pixie has in total "
        "to get a value between 0 and 1. Output is highest for identical neuronClass sets. "
        "If no nearest Pixie is found, it returns 0 too"
        nearestPixie = self.attributedPixie.getNearestPixie()
        if nearestPixie is not None:
            otherNeurons = nearestPixie.genome.allNeuronClasses
            ownNeurons = self.attributedPixie.genome.allNeuronClasses
            combinedLength = len(ownNeurons) + len(otherNeurons)
            combinedNeurons = ownNeurons.union(otherNeurons)
            hammingDistance = combinedLength - len(combinedNeurons)
            self.output = hammingDistance/len(ownNeurons)
        else:
            self.output = 0
        
        if not 0 <= self.output <=1:
            raise ValueError("Output not normalized!")
        self.transferOutput()

class OnOff(sensorN):
    "alway return 1.0 or 0.0"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"OnOff: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):

        if self.attributedPixie.genome.isOn:
            self.output = 1.0
        else:
            self.output = 0.0
        
        self.transferOutput()

class nextFood(sensorN):
    "returns the inverse of the distance of the nearest Food Object in facing direction"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"nextFood: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        ""
        allFwdObjects = self.attributedPixie.getFwdObjects()
        allFwdFood = [obj for obj in allFwdObjects if isinstance(obj, env.food)]
        if not allFwdFood:
            self.output = 0
        else:
            #print("<<DEBUG neurons.nextFood>> food found!")
            #print("<<DEBUG neurons.nextFood>> food found!")
            nearestFwdObject = allFwdFood[0]
            d = self.attributedPixie.getEuclidianDistance(nearestFwdObject)
            self.output = 1/d
        
        self.transferOutput()

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

        self.clearInput()
        self.transferOutput()

class InterNeuron2(internalN):
    "run the input through a tanh function and return the value"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"Internal Neuron 2: pixie {self.attributedPixie}, input {self.input}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "run the input through a tanh function and return the value"

        out = math.tanh(self.input)

        self.output = out

        self.clearInput()
        self.transferOutput()

class InterNeuron3(internalN):
    "run the input through a tanh function and return the value"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"Internal Neuron 3: pixie {self.attributedPixie}, input {self.input}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "run the input through a tanh function and return the value"

        out = math.tanh(self.input)

        self.output = out

        self.clearInput()
        self.transferOutput()

class AbsNeuron1(internalN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"Absolute Neuron 1: pixie {self.attributedPixie}, input {self.input}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self):
        "run the input through a tanh function and return the value"

        out = math.tanh(self.input)

        self.output = abs(out)

        self.clearInput()
        self.transferOutput()

class PosNeuron1(internalN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def execute(self):
        "if the input is positive, run it through a tanh function and return the value. else return 0"

        if self.input <= 0:

            self.output = 0

        else:
            out = math.tanh(self.input)

            self.output = out

        self.clearInput()
        self.transferOutput()

class NegNeuron1(internalN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def execute(self):
        "if the input is negative, run it through a tanh function and return the value. else return 0"

        if self.input >= 0:

            self.output = 0

        else:
            out = math.tanh(self.input)
        out = math.tanh(self.input)

        self.output = out

        self.clearInput()
        self.transferOutput()

class AbsNeuron1(internalN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"Absolute Neuron 1: pixie {self.attributedPixie}, input {self.input}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self):
        "run the input through a tanh function and return the value"

        out = math.tanh(self.input)

        self.output = abs(out)

        self.clearInput()
        self.transferOutput()

class PosNeuron1(internalN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def execute(self):
        "if the input is positive, run it through a tanh function and return the value. else return 0"

        if self.input <= 0:

            self.output = 0

        else:
            out = math.tanh(self.input)

            self.output = out

        self.clearInput()
        self.transferOutput()

class NegNeuron1(internalN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def execute(self):
        "if the input is negative, run it through a tanh function and return the value. else return 0"

        if self.input >= 0:

            self.output = 0

        else:
            out = math.tanh(self.input)

            self.output = out
            self.output = out

        self.clearInput()
        self.transferOutput()

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

        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

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
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

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

        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

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
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

class moveB(actionN):
    "move backwards in respect to the 'facing'-direction"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"moveB: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "input gets converted into a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            facing_angle = self.attributedPixie.facing
            moveVector = self.attributedPixie.getNormalizedDirection(angle=facing_angle+math.pi) # turn 180 degrees 

            self.attributedPixie.moveY = moveVector[0] * sign
            self.attributedPixie.moveX = moveVector[1] * sign
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

class moveF(actionN):
    "move forward in respect to the 'facing'-direction"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"moveF: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "input gets converted into a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            facing_angle = self.attributedPixie.facing
            moveVector = self.attributedPixie.getNormalizedDirection(angle=facing_angle) # same direction

            self.attributedPixie.moveY = moveVector[0] * sign
            self.attributedPixie.moveX = moveVector[1] * sign
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

class moveR(actionN):
    "move backwards in respect to the 'facing'-direction"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"moveR: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "input gets converted into a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            facing_angle = self.attributedPixie.facing
            moveVector = self.attributedPixie.getNormalizedDirection(angle=facing_angle-math.pi/2) # turn 90 degrees to the left 

            self.attributedPixie.moveY = moveVector[0] * sign
            self.attributedPixie.moveX = moveVector[1] * sign
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

class moveL(actionN):
    "move backwards in respect to the 'facing'-direction"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"moveL: pixie {self.attributedPixie}, input {self.input}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "input gets converted into a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            facing_angle = self.attributedPixie.facing
            moveVector = self.attributedPixie.getNormalizedDirection(angle=facing_angle+math.pi/2) # turn 90 degrees to the left

            self.attributedPixie.moveY = moveVector[0] * sign
            self.attributedPixie.moveX = moveVector[1] * sign
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

class moveRandom(actionN):
    "move in a random direction"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"setOscPeriod: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self):
        "input gets converted to a probability, then executed"
        normed_input = math.tanh(self.input)

        if random.random() < normed_input:
            moveVector = (random.randint(-1, 1), random.randint(-1, 1))

            self.attributedPixie.moveY = moveVector[0]
            self.attributedPixie.moveX = moveVector[1]
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

class turnRight(actionN):
    "change facing direction by pi/2 -> turnRight"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"turnRight: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self):
        "input gets converted to a probability, then executed"
        normed_input = math.tanh(self.input)

        if random.random() < normed_input:
            viewAxis = self.attributedPixie.facing
            newAngle = (viewAxis + math.pi / 2) % (2 * math.pi)  # Normalize angle to [0, 2*pi]
            self.attributedPixie.facing = newAngle
        
        self.clearInput()

class turnLeft(actionN):
    "change facing direction by -pi/2 -> turnLeft"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"turnLeft: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self):
        "input gets converted to a probability, then executed"
        normed_input = math.tanh(self.input)

        if random.random() < normed_input:
            viewAxis = self.attributedPixie.facing
            newAngle = (viewAxis - math.pi / 2) % (2 * math.pi)  # Normalize angle to [0, 2*pi]
            self.attributedPixie.facing = newAngle
        
        self.clearInput()

class setOscPeriod(actionN):
    "double or halve the Period of the oscillator-neuron. Max value is a period of 100 simsteps"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"setOscPeriod: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"
    
    def execute(self):
        "inputs get converted to a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            if self.attributedPixie.genome.oscillatorPeriod > 100:
                self.attributedPixie.genome.oscillatorPeriod = 100
            else:
                self.attributedPixie.genome.oscillatorPeriod = self.attributedPixie.genome.oscillatorPeriod * 2**sign

        self.clearInput()

class setSearchRadius(actionN):
    ""

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"setSearchRadius: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "inputs get converted to a probability, then executed"
        normed_input = math.tanh(self.input)
        sign = np.sign(normed_input)

        if random.random() < abs(normed_input):
            if self.attributedPixie.genome.searchRadius > 100:
                self.attributedPixie.genome.searchRadius = 100
            elif self.attributedPixie.genome.searchRadius < 0:
                self.attributedPixie.genome.searchRadius = 0
            else:
                self.attributedPixie.genome.searchRadius +=  1*sign

        self.clearInput()

class setOnOff(actionN):
    "flip the state of the isOn genome variabe"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"setOnOff: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "inputs get converted to a probability, then executed"
        normed_input = math.tanh(self.input)

        if random.random() < normed_input:
            "flip the boolean isOn variable"
            self.attributedPixie.genome.isOn = not self.attributedPixie.genome.isOn

        self.clearInput()

class kill(actionN):
    "if the nearest pixie is within killing distance, it is added to the queueForKill"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"kill: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "input gets converted into a probability, then executed"
        normed_input = math.tanh(self.input)

        if random.random() < normed_input:

            potentialVictim = self.attributedPixie.getNearestPixie()

            if potentialVictim is not None:
                distance = self.attributedPixie.getEuclidianDistance(potentialVictim)
                if distance <= self.attributedPixie.genome.killRadius:
                    # kill
                    # kill
                    self.attributedPixie.worldToInhabit.queueForKill.add(potentialVictim)
                    # feed (gain half the pixies energy)
                    self.attributedPixie.energy += int(potentialVictim.energy/2)
                    # feed (gain half the pixies energy)
                    self.attributedPixie.energy += int(potentialVictim.energy/2)
                else:
                    pass
        
        self.clearInput()

class eatFood(actionN):
    "if neighbouring a food object, consume it and gain energy"

    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)

    def __str__(self):
        return f"kill: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "input gets converted into a probability, then executed"
        normed_input = math.tanh(self.input)

        if random.random() < normed_input:
            nearFood = [obj for obj in self.attributedPixie.getAllEuclidianDistances() if isinstance(obj[0], env.food)]
            if nearFood:
                nearestFood = min(nearFood, key=lambda x: x[1])
                if nearestFood[1] <= math.sqrt(2): # if food is in a neighbouring cell

                    self.attributedPixie.energy += nearestFood[0].energyValue
                    self.attributedPixie.worldToInhabit.environment.remove(nearestFood[0])
                    self.attributedPixie.worldToInhabit.updateWorld()

        self.clearInput()

            
class initiateSex(actionN):
    "if the pixie encounters another pixie in the proximate field in facing direction, it can iniate sex, "
    "meaning it is added to the other pixie's qeueForMate set. Only if both Pixies have not mated yet "
    "and they are in each others qeue, is mating iniatiated. Each parent Pixie contributes "
    "a random 50% of its genes to the offspring"
    "The new DNA gets relevant when the genome gets loaded again in the next generation"
    def __init__(self, attributedPixie):
        super().__init__(attributedPixie)
    
    def __str__(self):
        return f"initiateSex: pixie {self.attributedPixie}, output {self.output}, numInputs {self.numInputs}, numOutputs {self.numOutputs}, numSelfInputs {self.numSelfInputs}"

    def execute(self):
        "input gets converted into a probability, then executed"
        if not self.attributedPixie.genome.hasAlreadyMated:
            normed_input = math.tanh(self.input)
            if random.random() < abs(normed_input):

                proximateObject = self.attributedPixie.searchProximateField()

                if proximateObject is not None and proximateObject.__class__.__name__ == "pixie":
                    proximateObject.genome.wantsToMate.add(self.attributedPixie)

                    if proximateObject not in self.attributedPixie.genome.wantsToMate:
                        pass
                    else:
                        if proximateObject.genome.hasAlreadyMated == False:
                            newOwnGenome = []
                            newOtherGenome = []
                            start = random.randint(0,1)

                            ##PROBLEM: The length of a genome can vary because useless genes are removed while loading the genome
                            # --> only if genomes are the same size
                            if len(proximateObject.genome.genes) == len(self.attributedPixie.genome.genes):
                                for gene in range(len(self.attributedPixie.genome.genes)-1):

                                    if (gene-start)%2 == 0:
                                        #recieving another pixie's gene
                                        newOwnGenome.append(proximateObject.genome.genes[gene])
                                        newOtherGenome.append(self.attributedPixie.genome.genes[gene])
                                    else:
                                        #keeping your own gene                          
                                        newOwnGenome.append(self.attributedPixie.genome.genes[gene])
                                        newOtherGenome.append(proximateObject.genome.genes[gene])

                                self.attributedPixie.genome.genes = newOwnGenome
                                proximateObject.genome.genes = newOtherGenome
                                    
                                self.attributedPixie.genome.hasAlreadyMated = True
                                proximateObject.genome.hasAlreadyMated = True
                                self.attributedPixie.worldToInhabit.sexualityCount += 2
                                
                            else:
                                pass
       ### Wenn die Gene tauschen, ist dann attributedPixie von neurolink noch korrekt?!?!? Muss man das updaten?  
       #        unwichtig, da attributedPixie nur im Moment von loadGenome verwendet wird   
        self.clearInput()

            