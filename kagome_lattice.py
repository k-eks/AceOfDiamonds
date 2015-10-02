import rhomb
from PIL import Image
from PIL import ImageDraw

class Kagome():
    """Creates a two-dimensional Kagome lattice and all tools for drawing on it."""

    def __init__(self, latticeWidth, imageSize, outputFolder, truncation):
        """Constructor
        latticeWidth ... int width of rhombs in pixel
        imageSize ... (int, int) dimension of the resulting output images
        outputFolder ... str location of the folder to save images
        truncation ... number of lattice points which are outside of the visual part"""
        self.latticeWidth = latticeWidth
        # this is a simple mathematical relation of hexagon width to height
        self.latticeHeight = 1/2 * 2 * math.sqrt((DEFAULT_GRIDSIZE / 2) ** 2 -
                            (DEFAULT_GRIDSIZE / 2 * math.cos(math.radians(60))) ** 2)

        # stuff for drawing and image saving
        self.image = Image.new('RGB', imageSize, 'white')
        self.draw = ImageDraw.Draw(image)
        self.outputFolder = outputFolder
        self.rhombColor = 'red'

        # generate the dimensions of the lattice, always even
        self.latticePointsX = (imageSize[0] / self.latticeWidth + 1)
        if self.latticePointsX % 2 == 1: self.latticePointsX += 1
        self.latticePointsY = (imageSize[0] / self.latticeHeight + 1)
        if self.latticePointsY % 2 == 1: self.latticePointsY += 1


    def kag_to_screen(self, x, y):
        """Transforms a kagome coordinate to a point on screen.
        x ... int x-coordinate of the Kagome lattice point
        y ... int y-coordinate of the Kagome lattice point"""
        if y % 2 == 0:
            indent = self.latticeWidth / 4
            step = self.latticeWidth / 2
        else:
            indent = 0
            step = self.latticeWidth
        if (y + 1) % 4 == 0:
            indent = self.latticeWidth / 2
        return (x * step + indent, y * self.latticeHeight)


    def rhomb_at_kagome(self, x, y):
        """Draws a rhomb in the correct orientation at a given kagome lattice point.
        x ... int x-coordinate of the Kagome lattice point
        y ... int y-coordinate of the Kagome lattice point"""
        draw_x, draw_y = kag_to_screen(x, y) # converting to drawing coordinates
        # figure out the right orientation
        if y % 2 == 1:
            self.draw.polygon(rhomb.lying(draw_x, draw_y), self.rhombColor)
        elif ((y % 2 == 0 and x % 2 == 1 and y % 4 == 0) or
              (y % 2 == 0 and x % 2 == 0 and y % 4 == 2)):
            self.draw.polygon(rhomb.right(draw_x, draw_y), self.rhombColor)
        else:
            self.draw.polygon(rhomb.left(draw_x, draw_y), self.rhombColor)