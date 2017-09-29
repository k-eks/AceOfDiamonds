import numpy as np

class Rhomb():
    """
    Representation of a node on the Kagome lattice.
    """

    # maximum possible number of neighbors by neighbor order a single rhomb can have
    MAXNEIGHBORS = [4, 8, 14, 18, 22, 28, 30, 38, 38, 48]

    def __init__(self, x, y, latticeWidth, latticeHeight):
        self.x = x
        self.y = y
        self.identifier = [(x, y)]
        self.reacted = False

        # calculate the location of all first neighbors
        self.fn = np.empty(4, dtype=object)
        # identify line
        """
        _________________   0
        \/  \/  \/  \/  \   1
        /\__/\__/\__/\__/   2
        ‾‾\/‾‾\/‾‾\/‾‾\/‾   3
        __/\__/\__/\__/\_
        """
        if y % 4 == 0:
            self.fn[0] = (x - 1, y)
            self.fn[1] = (x + 1, y)
            self.fn[2] = (int(x / 2), y - 1)
            self.fn[3] = (int(x / 2) + (x % 2), y + 1)
        elif y % 4 == 1:
            self.fn[0] = (x * 2 - 1, y - 1)
            self.fn[1] = (x * 2, y - 1)
            self.fn[2] = (x * 2 - 1, y + 1)
            self.fn[3] = (x * 2, y + 1)
        elif y % 4 == 2:
            self.fn[0] = (x - 1, y)
            self.fn[1] = (x + 1, y)
            self.fn[2] = (int(x / 2) + (x % 2), y - 1)
            self.fn[3] = (int(x / 2), y + 1)
        elif y % 4 == 3:
            self.fn[0] = (x * 2, y - 1)
            self.fn[1] = (x * 2 + 1, y - 1)
            self.fn[2] = (x * 2, y + 1)
            self.fn[3] = (x * 2 + 1, y + 1)

        # make torus
        for i in range(len(self.fn)):
            t = self.fn[i]
            if t[0] < 0:
                self.fn[i] = (int(latticeWidth / int(1 + t[1] % 2) - 1), t[1])
            elif t[0] >= latticeWidth / int(1 + t[1] % 2):
                self.fn[i] = (0, t[1])
            if t[1] < 0:
                self.fn[i] = (t[0], latticeHeight - 1)
            elif t[1] >= latticeHeight:
                self.fn[i] = (t[0], 0)

        # "set up" of other neighbors
        self.neighbors = np.empty(10, dtype=object)
        self.neighbors[0] = self.fn


def lying(x, y, latticeWidth, latticeHeight):
    """
    Vertex coordinates for a lying rhomb.
    x ... int x-coordinate in the rhombile tiling
    y ... int y-coordinate in the rhombile tiling
    latticeWdith ... width of the image which on which is drawn
    latticeHeight ... height of the image which on which is drawn
    returns (int, int, int, int, int, int, int, int) four pairs of coordinates that define the polygon

            v4
          __,.__
    v1  <´__  __`>  v3
            `´
    """
    v1x = int(x - latticeWidth / 2)
    v1y = int(y)

    v2x = int(x)
    v2y = int(y - latticeHeight * 2 / 3)

    v3x = int(x + latticeWidth / 2)
    v3y = int(y)

    v4x = int(x)
    v4y = int(y + latticeHeight * 2 / 3)

    return (v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y)


def left(x, y, latticeWidth, latticeHeight):
    """
    Vertex coordinates for a rhomb with a high vertice on the left side.
    x ... int x-coordinate in the rhombile tiling
    y ... int y-coordinate in the rhombile tiling
    latticeWdith ... width of the image which on which is drawn
    latticeHeight ... height of the image which on which is drawn
    returns (int, int, int, int, int, int, int, int) four pairs of coordinates that define the polygon

        v3
       |\
       | \  v2
       \ |
        \|
        v1
    """
    v1x = int(x + latticeWidth / 4)
    v1y = int(y + latticeHeight)

    v2x = int(x + latticeWidth / 4)
    v2y = int(y - latticeHeight / 3)

    v3x = int(x - latticeWidth / 4)
    v3y = int(y - latticeHeight)

    v4x = int(x - latticeWidth / 4)
    v4y = int(y + latticeHeight / 3)

    return (v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y)


def right(x, y, latticeWidth, latticeHeight):
    """
    Vertex coordinates for a rhomb with a high vertice on the right side.
    x ... int x-coordinate in the rhombile tiling
    y ... int y-coordinate in the rhombile tiling
    latticeWdith ... width of the image which on which is drawn
    latticeHeight ... height of the image which on which is drawn
    returns (int, int, int, int, int, int, int, int) four pairs of coordinates that define the polygon

        v3
        /|
       / | v2
       | /
       |/
       v1
    """
    v1x = int(x - latticeWidth / 4)
    v1y = int(y + latticeHeight)

    v2x = int(x - latticeWidth / 4)
    v2y = int(y - latticeHeight / 3)

    v3x = int(x + latticeWidth / 4)
    v3y = int(y - latticeHeight)

    v4x = int(x + latticeWidth / 4)
    v4y = int(y + latticeHeight / 3)

    return (v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y)