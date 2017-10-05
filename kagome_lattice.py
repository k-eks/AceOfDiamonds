import rhomb
import reactivityModifier
import math
import log
import corr
import random
import os.path
import warnings
import numpy as np
from PIL import Image
from PIL import ImageDraw

class Kagome():
    """Creates a two-dimensional Kagome lattice and all tools for drawing on it."""

    def deprecated(func):
        """
        This is a decorator which is used to mark functions as deprecated. It will result in a warning being emitted when the function is used.
        taken from: https://wiki.python.org/moin/PythonDecoratorLibrary#CA-03ade855b8be998a2a4befd0f5f810b63abcfd7d_3
        """
        def new_func(*args, **kwargs):
            warnings.warn("Call to deprecated function {}.".format(func.__name__),
                          category=DeprecationWarning)
            print("\nCall to deprecated function: {}.\n".format(func.__name__))
            return func(*args, **kwargs)
        new_func.__name__ = func.__name__
        new_func.__doc__ = func.__doc__
        new_func.__dict__.update(func.__dict__)
        return new_func

    def __init__(self, latticeWidth, latticePoints, imageSize, outputFolder):
        """Constructor
        latticeWidth ... int width of rhombs in pixel
        latticePoints ... (int, int) lattice points in x and y direction
        imageSize ... (int, int) dimension of the resulting output images
        outputFolder ... str location of the folder to save images"""

        # logging related stuff
        self.outputFolder = outputFolder
        # check if outputfolder exists and create it if not
        if not os.path.exists(self.outputFolder):
            os.makedirs(self.outputFolder)
            print("created %s" % self.outputFolder)
        # create a name for the model
        self.modelName = os.path.basename(os.path.normpath(self.outputFolder))
        # start the loggers
        self.log = log.Logger("Log", self.outputFolder)
        self.log.log_text("Program initialized")
        self.log_conversion = log.Logger("conversion", self.outputFolder)
        self.log.log_text("Conversion log created")

        # set pixel dimensions for drawing
        self.latticeWidth = latticeWidth
        # this is a simple mathematical relation of hexagon width to height
        self.latticeHeight = 1/2 * 2 * math.sqrt((latticeWidth / 2) ** 2 -
                            (latticeWidth / 2 * math.cos(math.radians(60))) ** 2)

        # generate the dimensions of the lattice, always even
        self.latticePointsX = latticePoints[0]
        if self.latticePointsX % 2 == 1: self.latticePointsX += 1
        self.latticePointsY = latticePoints[1]
        if self.latticePointsY % 2 == 1: self.latticePointsY += 1

        # stuff for drawing and image saving
        self.image = Image.new('RGB', imageSize, 'white')
        self.draw = ImageDraw.Draw(self.image)
        self.rhombColor = 'red'

        # centering the image on the tiling
        self.imageXOffset = int((self.latticePointsX / 2 * self.latticeWidth - self.image.size[0]) / 2)
        self.imageYOffset = int((self.latticePointsY * self.latticeHeight - self.image.size[1]) / 2)


        # generate rhomb lattice
        self.numberAllLatticePoints = 0
        self.lattice = self.generate_lattice_array()
        for y in range(len(self.lattice)):
            for x in range(len(self.lattice[y])):
                self.lattice[y][x] = rhomb.Rhomb(x, y, self.latticePointsX, self.latticePointsY)
                self.numberAllLatticePoints += 1
        self.rhombCount = self.latticePointsY * self.latticePointsX / 2 + self.latticePointsY * self.latticePointsX / 4
        self.log.log_text("Lattice created")
        self.log.log_text("Created %i rhombs" % self.rhombCount)

    def __del__(self):
        """Destructor, cleaning up :) """
        self.log.log_text("Destructor called")


    def debug_draw_neighbors(self, x, y):
        """
        Debug function. Draws all first neighbors.
        x ... int x coordinate in the lattice
        y ... int y coordinate in the lattice
        """
        neighbors = self.lattice[y][x].fn
        for t in neighbors:
            self.rhomb_at_kagome(t[0], t[1])

    def getRhomb(self, x, y):
        """
        Gets a rhomb at the specific coordinates. This also ensures the torus like shape of the sheet.
        x ... int x coordinate in the lattice
        y ... int y coordinate in the lattice
        retruns Rhomb a rhomb at the given lattice points
        """
        # check y
        if y < 0:
            y = y + self.latticePointsY
        else:
            y = y % self.latticePointsY

        if x >= self.latticePointsX:
            x = x % self.latticePointsX
        # # check x
        if y % 2 == 1:
            divisor = 2
        else:
            divisor = 1
        if x >= (self.latticePointsX / divisor):
            x = x % (self.latticePointsX / divisor)

        return self.lattice[y][x]


    def calculate_Nth_neighbor(self, nMinus1, nMinus2):
        """
        Calculates the second and higher neighbors. The order of the neighbors is given by N
        nMinus1 ... array of tuples of the N - 2 neighbors
        nMinus2 ... array of tuples of the N - 2 neighbors
        returns a tuple array of the coordinates of the Nth neighbors
        """
        everything = [] # holds all neighbors of the first nightbors
        toremove = [] # holds all items which should be removed
        for t in nMinus2:
            # tuples get turned into string for numpy to handle it
            toremove.append(str(t))
        for t in nMinus1:
            # tuples get turned into string for numpy to handle it
            toremove.append(str(t))
            for t2 in self.getRhomb(t[0], t[1]).fn:
                everything.append(str(t2)) # tuples get turned into string for numpy to handle it
        everything = np.array(everything)
        toremove = np.array(toremove)
        reduced = np.setdiff1d(everything, toremove) # this numpy function cant handle tuples

        # reversing the string array into a tuple array
        complete = np.empty(len(reduced), dtype=object)
        for i in range(len(reduced)):
            complete[i] = eval(reduced[i])
        return complete


    def generate_lattice_array(self):
        """
        Creates an empty numpy array with all lattice points.
        return ... array[array] emtpy array with correct indices
        """
        lattice = np.empty(self.latticePointsY, dtype=object)
        for y in range(len(lattice)):
            lattice[y] = np.empty(int(self.latticePointsX / (y % 2 + 1)), dtype=object)
        return lattice


    def kag_to_screen(self, x, y):
        """
        Transforms a kagome coordinate to a point on screen.
        x ... int x-coordinate of the Kagome lattice point
        y ... int y-coordinate of the Kagome lattice point
        returns a tuple of (x, y) coordinates to draw on an image.
        """
        if y % 2 == 0:
            indent = self.latticeWidth / 4
            step = self.latticeWidth / 2
        else:
            indent = 0
            step = self.latticeWidth
        if (y + 1) % 4 == 0:
            indent = self.latticeWidth / 2
        return (x * step + indent - self.imageXOffset,
                y * self.latticeHeight - self.imageYOffset)


    def rhomb_at_kagome(self, x, y):
        """
        Draws a rhomb in the correct orientation at a given kagome lattice point.
        x ... int x-coordinate of the Kagome lattice point
        y ... int y-coordinate of the Kagome lattice point
        """
        draw_x, draw_y = self.kag_to_screen(x, y) # converting to drawing coordinates
        # figure out the right orientation
        if y % 2 == 1:
            self.draw.polygon(rhomb.lying(draw_x, draw_y, self.latticeWidth, self.latticeHeight), self.rhombColor)
        elif ((y % 2 == 0 and x % 2 == 1 and y % 4 == 0) or
              (y % 2 == 0 and x % 2 == 0 and y % 4 == 2)):
            self.draw.polygon(rhomb.right(draw_x, draw_y, self.latticeWidth, self.latticeHeight), self.rhombColor)
        else:
            self.draw.polygon(rhomb.left(draw_x, draw_y, self.latticeWidth, self.latticeHeight), self.rhombColor)


    def get_random_point(self):
        """
        Generates a random coordinate from the lattice.
        return ... (int, int) kagome lattice coordinates
        """
        y = random.randint(0, len(self.lattice) - 1)
        x = random.randint(0, len(self.lattice[y]) - 1)
        return (x, y)


    def draw_tiling(self):
        """
        Creates an outline overlay of the rhombille tiling and fills it with reacted rhombs.
        """
        for y in range(len(self.lattice)):
            for x in range(len(self.lattice[y])):
                draw_x, draw_y = self.kag_to_screen(x, y) # converting to drawing coordinates
                # determine the orientation
                if y % 2 == 1:
                    self.draw.polygon(rhomb.lying(draw_x, draw_y, self.latticeWidth, self.latticeHeight), outline=1)
                elif ((y % 2 == 0 and x % 2 == 1 and y % 4 == 0) or
                      (y % 2 == 0 and x % 2 == 0 and y % 4 == 2)):
                    self.draw.polygon(rhomb.right(draw_x, draw_y, self.latticeWidth, self.latticeHeight), outline=1)
                else:
                    self.draw.polygon(rhomb.left(draw_x, draw_y, self.latticeWidth, self.latticeHeight), outline=1)


    def draw_image(self):
        """
        Draws an image of the current state.
        """
        for y in range(len(self.lattice)):
            for x in range(len(self.lattice[y])):
                r = self.lattice[y][x]
                if r.reacted:
                    self.rhomb_at_kagome(r.x, r.y)
        self.draw_tiling()


    def save_image(self, cycle):
        """
        Saves the current image.
        cycle ... int number of the image, i.e. position number of the current Monte Carlo cycle.
        """
        self.image.save(self.outputFolder + "%s.png" % cycle)


    def model_neighbor_correlations(self, reactivityModifiers, MCcycleMax, seeds=0, imageCycle=0):
        """Run a Monte Carlo Simulation with neighbor correlations.
        correlations ... array of Correlation objecta of the desired neighbor correlations
        MCcycleMax ... int number of how many time steps the simulation should run, -1 runs until 100 percent concersion is reached
        omega ... float base propability for dimerization
        pairCorrelations ... int number for how many neighbors pair correlations should be plotted, 0 -> derive from correlations
        seeds ... int number of randomly created seeds before the model should run
        imageCycle ... int determines after how many Monte Carlo iterations an image of the current state should be created and saved, a value of 0 turns it of"""
        # calculating the highest neighbor correlations
        maxNeighborOrder = 1
        for modifier in reactivityModifiers:
            maxNeighborOrder = max(maxNeighborOrder, modifier.neighborOrder)

        # calculating higher neighbors of rhombs and building the grid
        if maxNeighborOrder > 1:
            count = 0
            for y in range(len(self.lattice)):
                for x in range(len(self.lattice[y])):
                    count += 1
                    rhomb = self.getRhomb(x, y)
                    completeShells = 1 # first neighbor are already known
                    # run through increasing neighboring shells and fill them with neighbors
                    while completeShells < maxNeighborOrder:
                        print("Working on neighbor %i of rhomb %i of %i      " % (completeShells + 1, count, self.rhombCount), end='\r')
                        # special case for the second neighbors
                        if completeShells == 1:
                            nMinus1 = rhomb.neighbors[0]
                            nMinus2 = rhomb.identifier
                        else:
                            nMinus1 = rhomb.neighbors[completeShells - 1]
                            nMinus2 = rhomb.neighbors[completeShells - 2]
                        # remove duplicate and lower neighbors
                        nth = self.calculate_Nth_neighbor(nMinus1, nMinus2)
                        rhomb.neighbors[completeShells] = nth
                        completeShells += 1
        print("\nFinished with neighbors!")

        converted = 0
        if seeds > 0:
            print("Generating seeds")
            self.generate_seeds(seeds)
            converted += seeds

        print("Starting MC simulation...")
        runSimulation = True
        MCcycle = 0
        self.log.log_text("Starting MC simulation")
        while runSimulation:
            # each run is a single time step
            if MCcycleMax == -1:
                print("Current step: %i, conversion is %0.02f" % (MCcycle, converted / self.numberAllLatticePoints), end='\r')
            else:
                print("Current step: %i of %i" % (MCcycle + 1, MCcycleMax), end='\r')

            # select a rhomb a do stuff with it
            x, y = self.get_random_point()
            currentRhomb = self.getRhomb(x, y)
            if not currentRhomb.reacted:
                chanceToReact = 1 # when a photon arrives, it reacts
                # applying all modifiers to reactivity
                for modifier in reactivityModifiers:
                    if self.modifierApplies(currentRhomb, modifier):
                        chanceToReact *= modifier.r

                if random.random() <= chanceToReact:
                    self.lattice[y][x].reacted = True
                    converted += 1

            # save an image after ever imageCycle Monte Carlo interations
            if imageCycle > 0:
                if MCcycle % imageCycle == 0:
                    self.log_conversion.log_xy(MCcycle, converted / self.numberAllLatticePoints)
                    self.image = Image.new('RGB', self.image.size, 'white')
                    self.draw = ImageDraw.Draw(self.image)
                    self.draw_image()
                    self.save_image(MCcycle)

            # step up in the Monte Carlo cycle
            MCcycle += 1
            # check if the simulation should continue or end
            if MCcycleMax == -1:
                if converted >= self.numberAllLatticePoints:
                    runSimulation = False
            else:
                if MCcycle >= MCcycleMax:
                    runSimulation = False
        # writing out the last state
        self.log_conversion.log_xy(MCcycle, converted / self.numberAllLatticePoints)
        self.image = Image.new('RGB', self.image.size, 'white')
        self.draw = ImageDraw.Draw(self.image)
        self.draw_image()
        self.save_image(MCcycle)

        print("\nDone!")
        self.log.log_text("MC ended")

        # ****************************************************************************
        # old code snippet about bond breaking
        # destroy a reacted dimer but only if there was a change in the crystal
        # if random.random() < destroy:
        #     converted -= 1
        #     allreacted = []
        #     for y in range(len(self.lattice)):
        #         for x in range(len(self.lattice[y])):
        #             if self.lattice[y][x].reacted:
        #                 allreacted.append((x,y))
        #     x, y = random.choice(allreacted)
        #     self.lattice[y][x].reacted = False
        #     self.getRhomb(x, y).reacted = False
        #     self.reactionSites[y][x] = False
        # ****************************************************************************


    def modifierApplies(self, currentRhomb, modifier):
        """
        Verifies wether or not a given modifer apllies to a given rhomb.
        currentRhomb ... rhomb the rhomb for which the reactivity conditions should be tested for
        modifier ... ReactivityModifier the rule set which is tested
        returns bool wether or not the given rule should be applied
        """
        reactedNeighbors, allNeighbors = self.count_reacted_neighbors(currentRhomb, modifier.neighborOrder)
        unreactedNeighbors = allNeighbors - reactedNeighbors

        # nan means that the modifier does not care about the number of neighbors
        return ((math.isnan(modifier.reactedLateralNeighborsRequired) or (modifier.reactedLateralNeighborsRequired <= reactedNeighbors)) and
               (math.isnan(modifier.unreactedLateralNeighborsRequired) or (modifier.unreactedLateralNeighborsRequired <= unreactedNeighbors)))



    def count_reacted_neighbors(self, rhomb, order):
        """Counts how mean of the neighbors of a given order have reacted.
        rhomb ... rhomb center of neighbor finding
        order ... order of the nearest neighbor
        returns (int, int) a tuple with the number of reacted neighbors and the total amount of neighbors
        """
        neighborRhombs = rhomb.neighbors[order - 1]
        reactedNeighbors = 0
        allNeighbors = 0
        # count through the neighbors
        for currentRhomb in neighborRhombs:
            allNeighbors += 1 # counts all possible neighbors, independent of their state
            if self.getRhomb(currentRhomb[0], currentRhomb[1]).reacted:
                reactedNeighbors += 1 # counts all reacted neighbors
        return reactedNeighbors, allNeighbors


    def generate_seeds(self, seeds):
        """
        Turns a given number of rhombs at random locations into a reacted state.
        seeds ... int number of how many rhombs should be turned into the reacted state
        """
        self.rhombColor = 'blue' # change of color to highlight the random seeds
        for i in range(seeds):
            coords = self.get_random_point()
            # set the new state and mark it
            self.lattice[coords[1]][coords[0]].reacted = True
            self.rhomb_at_kagome(coords[0], coords[1])
        self.rhombColor = 'red' # revert color
        self.draw_tiling()
        self.save_image("start.png")