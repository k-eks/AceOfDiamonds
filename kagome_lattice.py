import rhomb
import math
import log
import random
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
        self.log = log.Logger("Log", self.outputFolder)
        self.log.log_text("Program initialized")
        self.log_conversion = log.Logger("conversion", self.outputFolder)
        self.log.log_text("Conversion log created")

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
        if self.latticePointsX * self.latticeWidth > self.image.size[0]:
            self.imageXOffset = int((self.latticePointsX * self.latticeWidth - self.image.size[0]) / 4)
        else:
            self.imageXOffset = 0
        if self.latticePointsY * self.latticeHeight > self.image.size[0]:
            self.imageYOffset = int((self.latticePointsY * self.latticeHeight - self.image.size[1]) / 2)
        else:
            self.imageYOffset = 0

        # generate rhomb lattice
        self.numberAllLatticePoints = 0
        self.lattice = self.generate_lattice_array()
        for y in range(len(self.lattice)):
            for x in range(len(self.lattice[y])):
                self.lattice[y][x] = rhomb.Rhomb(x, y)
                self.numberAllLatticePoints += 1
        self.log.log_text("lattice created")

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


    def reset_reaction_sites(self):
        """Resets the array which keeps track of the reactions that have taken place in a cycle."""
        for y in range(len(self.lattice)):
            self.reactionSites[y][:] = False


    def generate_lattice_array(self):
        """Creates an empty numpy array with all lattice points.
        return ... array[array] emtpy array with correct indices"""
        lattice = np.empty(self.latticePointsY, dtype=object)
        for y in range(len(lattice)):
            lattice[y] = np.empty(self.latticePointsX / (y % 2 + 1), dtype=object)
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
        self.image.save(self.outputFolder + "%i.png" % cycle)


    def model_random(self, tMax, omega):
        self.log.log_text("Random model started")
        count = 0
        for t in range(tMax):
            # single time step
            for y in range(len(self.lattice)):
                for x in range(len(self.lattice[y])):
                    r = self.lattice[y][x]
                    # only do something if the site is not reacted
                    if not r.reacted:
                        # check if a reaction takes place
                        if random.random() < omega:
                            r.reacted = True
                            count += 1
                            self.rhomb_at_kagome(r.x, r.y)
            self.log_conversion.log_xy(t, count / self.numberAllLatticePoints)
            self.draw_tiling()
            self.save_image(t)
        self.log.log_text("Random model ended")
