"This file contains all Neuron classes"
import math
import numpy as np
import random



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
    
class random(sensorN):
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
            moveVector = self.attributedPixie.getNormalizedDirection(facing_angle+math.pi) # turn 180 degrees 

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
            moveVector = self.attributedPixie.getNormalizedDirection(facing_angle) # same direction

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
            moveVector = self.attributedPixie.getNormalizedDirection(facing_angle-math.pi/2) # turn 90 degrees to the left 

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
            moveVector = self.attributedPixie.getNormalizedDirection(facing_angle+math.pi/2) # turn 90 degrees to the left

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

        if random.random() < abs(normed_input):
            moveVector = (random.randint(-1, 1), random.randint(-1, 1))

            self.attributedPixie.moveY = moveVector[0]
            self.attributedPixie.moveX = moveVector[1]
        
        self.clearInput()
        self.attributedPixie.worldToInhabit.queueForMove.add(self.attributedPixie)

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
