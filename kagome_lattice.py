import rhomb
import math
import log
import corr
import random
import os.path
import numpy as np
from PIL import Image
from PIL import ImageDraw

class Kagome():
    """Creates a two-dimensional Kagome lattice and all tools for drawing on it."""

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
        self.log_pair = log.Logger("pair_%s" % self.modelName, self.outputFolder)
        self.log.log_text("Pair correlation log created")

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

        # generate reaction points
        self.reactionSites = self.generate_lattice_array()
        self.reset_reaction_sites()


    def __del__(self):
        """Destructor, cleaning up :) """
        self.log.log_text("Destructor called")


    def debug_draw_neighbors(self, x, y):
        """Debug function. Draws all first neighbors."""
        neighbors = self.lattice[y][x].fn
        for t in neighbors:
            self.rhomb_at_kagome(t[0], t[1])

    def getRhomb(self, x, y):
        """Gets a rhomb at the specific coordinates. This also ensures the torus like shape of the sheet.
        x ... int x coordinate
        y ... int y coordinate
        retruns a rhomb at the given lattice points"""
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
        """Calculates the second and higher neighbors. The order of the neighbors is given by N
        nMinus1 ... array of tuples of the N - 2 neighbors
        nMinus2 ... array of tuples of the N - 2 neighbors
        returns a tuple array of the coordinates of the Nth neighbors"""
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


    def reset_reaction_sites(self):
        """Resets the array which keeps track of the reactions that have taken place in a cycle."""
        for y in range(len(self.lattice)):
            self.reactionSites[y][:] = False


    def generate_lattice_array(self):
        """Creates an empty numpy array with all lattice points.
        return ... array[array] emtpy array with correct indices"""
        lattice = np.empty(self.latticePointsY, dtype=object)
        for y in range(len(lattice)):
            lattice[y] = np.empty(int(self.latticePointsX / (y % 2 + 1)), dtype=object)
            pass
        return lattice


    def kag_to_screen(self, x, y):
        """Transforms a kagome coordinate to a point on screen.
        x ... int x-coordinate of the Kagome lattice point
        y ... int y-coordinate of the Kagome lattice point
        returns a tuple of (x, y) coordinates to draw on an image."""
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
        """Draws a rhomb in the correct orientation at a given kagome lattice point.
        x ... int x-coordinate of the Kagome lattice point
        y ... int y-coordinate of the Kagome lattice point"""
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
        """Generates a random coordinate pair from the lattice.
        return ... tuple x,y kagome lattice coordinates"""
        y = random.randint(0, len(self.lattice) - 1)
        x = random.randint(0, len(self.lattice[y]) - 1)
        return (x, y)


    def draw_tiling(self):
        """Creates an outline overlay of the rhombille tiling."""
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
        """Draws an image of the current state."""
        for y in range(len(self.lattice)):
            for x in range(len(self.lattice[y])):
                r = self.lattice[y][x]
                if r.reacted:
                    self.rhomb_at_kagome(r.x, r.y)
        self.draw_tiling()


    def save_image(self, cycle):
        """Saves the current image.
        cycle ... int number of the image, i.e. position in cycle"""
        self.image.save(self.outputFolder + "%s.png" % cycle)


    def model_neighbor_correlations(self, correlations, tMax, omega, plotPairCorrelations=0, seeds=0, destroy=0):
        """Run a Monte Carlo Simulation with neighbor correlations.
        correlations ... array of Correlation objecta of the desired neighbor correlations
        tMax ... int number of how many time steps the simulation should run, -1 runs until 100 percent concersion is reached
        omega ... float base propability for dimerization
        pairCorrelations ... int number for how many neighbors pair correlations should be plotted, 0 -> derive from correlations
        seeds ... int number of randomly created seeds before the model should run"""
        # calculating the highest neighbor correlations
        maxc = 1
        for i in correlations:
            maxc = max(maxc, i.order)
        # side check against the plotting
        if plotPairCorrelations > 0:
            maxc = max(maxc, plotPairCorrelations)
        print("Highest order of neighbors is %i, calculating neighbors..." % maxc)

        # calculating higher neighbors of rhombs
        if maxc > 1:
            count = 0
            for y in range(len(self.lattice)):
                for x in range(len(self.lattice[y])):
                    count += 1
                    rhomb = self.getRhomb(x, y)
                    completeShells = 1 # first neighbor are already known
                    # run through increasing neighboring shells and fill them with neighbors
                    while completeShells < maxc:
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
        # write header
        self.log_pair.log_simple_text("t_%s;conversion" % self.modelName)
        runSimulation = True
        t = 0
        while runSimulation:
            # each run is a single time step
            if tMax == -1:
                print("Current step: %i, conversion is %0.02f" % (t, converted / self.numberAllLatticePoints), end='\r')
            else:
                print("Current step: %i of %i" % (t + 1, tMax), end='\r')
            # for y in range(len(self.lattice)):
            #     for x in range(len(self.lattice[y])):
            x, y = self.get_random_point()
            r = self.getRhomb(x, y)
            if not r.reacted:
                p = omega
                # modifiy omega according to correlations
                for c in correlations:
                    count, amount = self.count_reacted_neighbors(r, c.order)
                    #print(c.order, count, amount)
                    # not counting amount yet
                    if count >= c.multR and count <= c.maxiR:
                        p = p * c.propR
                    else:
                        p = p * c.propU
                if random.random() < p:
                    self.reactionSites[y][x] = True
                    self.lattice[y][x].reacted = True
                    converted += 1
                    #self.rhomb_at_kagome(r.x, r.y)
                    # destroy a reacted dimer but only if there was a change in the crystal *************************
                    if random.random() < destroy:
                        converted -= 1
                        allreacted = []
                        for y in range(len(self.lattice)):
                            for x in range(len(self.lattice[y])):
                                if self.lattice[y][x].reacted:
                                    allreacted.append((x,y))
                        x, y = random.choice(allreacted)
                        self.lattice[y][x].reacted = False
                        self.getRhomb(x, y).reacted = False
                        self.reactionSites[y][x] = False
                    # ********************************************
            # let the reaction take place
            # for y in range(len(self.reactionSites)):
            #     for x in range(len(self.reactionSites[y])):
            #         if self.reactionSites[y][x]:
            #             self.lattice[y][x].reacted = True
            self.reset_reaction_sites()
            # write the convesion out
            if t % 100 == 0:
                self.log_conversion.log_xy(t, converted / self.numberAllLatticePoints)
                self.image = Image.new('RGB', self.image.size, 'white')
                self.draw = ImageDraw.Draw(self.image)
                self.draw_image()
                self.save_image(t)
            # draw the image
            # self.draw_tiling()
            # self.save_image(t)

            # log the pair correlations
            # conversion = converted / self.numberAllLatticePoints
            # logstring = "%s;%s"  % (t, conversion)
            # # set up pair correlation counting array
            # neighborPairs = np.empty(maxc, dtype=object)
            # for i in range(maxc):
            #     neighborPairs[i] = np.zeros(rhomb.MAXNEIGHBORS[i] + 1)

            # # counting reacted pairs
            # for n in range(maxc):
            #     for y in range(len(self.lattice)):
            #         for x in range(len(self.lattice[y])):
            #             r = self.getRhomb(x, y)
            #             if r.reacted:
            #                 count, amount = (self.count_reacted_neighbors(r, n + 1))
            #                 neighborPairs[n][count] += 1
            # # calculate percentage of neighbor pairs
            # for i in range(maxc):
            #     liedetector = - conversion # for error checking
            #     for n in range(len(neighborPairs[i])):
            #         propability = neighborPairs[i][n] / self.numberAllLatticePoints
            #         logstring += ";%s" % propability
            #         liedetector += propability # if everything works fine, all propabilities sum up to 0
            #     logstring += ";%s" % liedetector
            # self.log_pair.log_simple_text(logstring)

            t += 1
            # check if the simulation should continue
            if tMax == -1:
                if converted >= self.numberAllLatticePoints:
                    runSimulation = False
            else:
                if t >= tMax:
                    runSimulation = False
        print("\nDone!")
        self.log.log_text("MC ended")



    def count_reacted_neighbors(self, rhomb, order):
        """Counts how mean of the neighbors of a given order have reacted.
        rhomb ... rhomb center of neighbor finding
        order ... order of the nearest neighbor
        returns a tuple with the number of reacted neighbors and the total amount of neighbors"""
        n = rhomb.neighbors[order - 1]
        count = 0
        amount = 0
        # count through the neighbors
        for t in n:
            amount += 1 # counts all possible neighbors, independent of their state
            if self.getRhomb(t[0], t[1]).reacted:
                count += 1 # counts all reacted neighbors
        return count, amount


    def generate_seeds(self, seeds):
        """Turns a given number of rhombs at random locations to a reacted state.
        seeds ... int number of how many rhombs should be turned into the reacted state"""
        self.rhombColor = 'blue' # change of color to highlight the random seeds
        for i in range(seeds):
            coords = self.get_random_point()
            # set the new state and mark it
            self.lattice[coords[1]][coords[0]].reacted = True
            self.rhomb_at_kagome(coords[0], coords[1])
        self.rhombColor = 'red'
        self.draw_tiling()
        self.save_image("start")