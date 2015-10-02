from PIL import Image
from PIL import ImageDraw
import math
import random

DEFAULT_GRIDSIZE = 45
# 1/2 gets tri next to hex #--> For calculating the height of the hexagon
DEFAULT_GRIDHEIGHT = 1/2 * 2 * math.sqrt((DEFAULT_GRIDSIZE / 2) ** 2 -
                                   (DEFAULT_GRIDSIZE / 2 * math.cos(math.radians(60))) ** 2)

# good values: gridsize = 20, points = 160, size = (1200, 1200)

def draw_grid(a, b):
    image = Image.new('RGB', (1000, 1000), 'white')
    draw = ImageDraw.Draw(image)
    dots = 44
    lattice = generate_lattice(dots)

    for y in range(dots):
        for x in range(int(dots / (y % 2 + 1))):
            # rhomb_at_kagome(draw, x, y)
            # draw.polygon(rhomb_right(200, 200), outline=0)
            draw.point(kag_to_screen(x, y), 'black')

    #x = random.randint(0,dots)
    #y = random.randint(0,dots)
    x=a
    y=b
    rhomb_at_kagome(draw, x, y, 'red')
    indices = get_nearest_neighbor_index(lattice, dots, x, y)
    c=0
    colors=('blue', 'yellow', 'lime', 'fuchsia')
    for i in indices:
        rhomb_at_kagome(draw, lattice[i].kx, lattice[i].ky, colors[c])
        c+=1

    image.show()


def get_nearest_neighbor_index(lattice, dots, x, y):
    # method is only poorly adjusted for the boundary regions,
    # this is compensated by a try/exept lateron
    indices = []
    for i in range(len(lattice)):
        # grid points are stored in a linear array, therefore such complicated calculations
        # in order to find the nearest neighbourghs
        dimer = lattice[i]
        if dimer.kx == x and dimer.ky == y:
            if y % 2 == 1:
                shiftup = int(i % (dots/2))
                shiftdown = i % dots
                if y % 4 == 3:
                    shiftup += 1
                    shiftdown -= int(dots / 2) - 1
                # lower right
                indices.append(i + shiftup + int(dots/2))
                # lower left
                if x != 0 or y % 4 == 3: indices.append(i + shiftup + int(dots/2) - 1)
                # upper right
                indices.append(i - dots + shiftdown - x % 2)
                # upper left
                if x != 0 or y % 4 == 3: indices.append(i - dots - 1 + shiftdown  + x % 2)
            else:
                # right
                if x < dots - 1: indices.append(i+1)
                # left
                if x > 0: indices.append(i-1)
                # lower
                shiftup = int(-x/2 + dots)
                if y % 4 == 0 and x % 2 == 1:
                    shiftup += 1
                shift = int(i+shiftup)
                if shift < len(lattice): indices.append(shift)
                # upper
                shiftdown = int(x/2 + dots/2 +x%2)
                if y % 4 == 2 and x % 2 == 1:
                    shiftdown -= 1
                shift = int(i-shiftdown)
                if shift > 0: indices.append(shift)
            break
    return indices


def model_nucleation(size, dots, timerange, omega, bonds):
    image, draw = generate_image(size)
    lattice = generate_lattice (dots)
    for i in bonds:
        lattice[i].reacted = True
        rhomb_at_kagome(draw, lattice[i].kx, lattice[i].ky, 'blue')

    ntotal = len(lattice)
    for t in range(timerange):
        p = probability_nucleation(ntotal, t, omega)
        model_nucleation_cycle(t, draw, lattice, dots, p)
        image.save("%i.png" % t)


def probability_nucleation(ntotal, t, omega):
    return 1 / ntotal * (1 + 2 * math.sqrt(math.pi) * omega * (t + 1) + math.pi * (omega * (t + 1)) ** 2)


def model_nucleation_cycle(cycle, draw, lattice, dots, probability):
    reaction = []
    for i in range(len(lattice) - 1):
        dimer = lattice[i]
        if dimer.reacted:
            neighbourghs = get_nearest_neighbor_index(lattice, dots, dimer.kx, dimer.ky)
            for g in neighbourghs:
                if (random.random() < probability):
                    try: # compensate for poor border checks
                        reaction.append(g)
                        rhomb_at_kagome(draw, dimer.kx, dimer.ky, 'red')
                    except IndexError:
                        pass
    draw_tiling(draw, lattice)
    for i in reaction:
        try: # compensate for poor border checks
            lattice[i].reacted = True
        except IndexError:
            pass

def model_mix_randnuc(size, dots, timerange, omega, ratio):
    image, draw = generate_image(size)
    lattice = generate_lattice(dots)
    ntotal = len(lattice)
    for t in range(timerange):
        if random.random() < ratio:
            p = probability_random(t, omega)
            print(t, p)
            model_random_cycle(t, draw, lattice, p)
        else:
            p = probability_nucleation(ntotal, t, omega)
            print(t, p)
            model_nucleation_cycle(t, draw, lattice, dots, p)
        image.save("%i.png" % t)


def model_checker36(size, dots, timerange, omega):
    image, draw = generate_image(size)
    lattice = generate_lattice(dots)
    for t in range(timerange):
        p = probability_checker36(t, omega)
        print(t, p)
        model_checker36_cycle(t, draw, lattice, dots, p)
        image.save("%i.png" % t)

def probability_checker36(t, omega):
    wt = omega * t
    return (wt + 1/6 * wt ** 2 + (wt / 8) ** 4) / (
            1 + 5/3 * wt + 1/6 * wt ** 2 + (wt / 8) ** 4)


def model_checker36_cycle(cycle, draw, lattice, dots, probability):
    for dimer in lattice:
        neighbourghs = get_nearest_neighbor_index(lattice, dots, dimer.kx, dimer.ky)
        reaction = []
        for i in neighbourghs:
            try:
                if lattice[i].reacted: reaction.append(True)
            except IndexError:
                pass
        if True in reaction: chance = random.random() * 1.36
        else: chance = random.random()
        if chance < probability:
            dimer.reacted = True
            rhomb_at_kagome(draw, dimer.kx, dimer.ky, 'red')
    draw_tiling(draw, lattice)


def model_random(size, dots, timerange, omega):
    """Creates an image series for the random model."""
    image, draw = generate_image(size)
    lattice = generate_lattice(dots)
    for t in range(timerange):
        p = probability_random(t, omega)
        model_random_cycle(t, draw, lattice, p)
        image.save("%i.png" % t)

def probability_random(t, omega):
    """Calculates the reaction probability of a bond at a given time step."""
    return 1 - math.exp(-1 / omega * t)


def model_random_cycle(cycle, draw, lattice, probability):
    """Calculates new bonds in the random model and creates a snap shot of the current step."""
    for dimer in lattice:
        if random.random() < probability:
            dimer.reacted = True
            rhomb_at_kagome(draw, dimer.kx, dimer.ky, 'red')
    draw_tiling(draw, lattice)


def generate_image(size):
    """Creates all objects neccessary for drawing an image."""
    image = Image.new('RGB', size, 'white')
    return image, ImageDraw.Draw(image)


def draw_tiling(draw, lattice):
    """creates an overlay of the rhombille tiling."""
    for dimer in lattice:
        draw_x, draw_y = kag_to_screen(dimer.kx, dimer.ky) # converting to drawing coordinates
        if dimer.ky % 2 == 1:
            draw.polygon(rhomb_lying(draw_x, draw_y), outline=1)
        elif ((dimer.ky % 2 == 0 and dimer.kx % 2 == 1 and dimer.ky % 4 == 0) or
              (dimer.ky % 2 == 0 and dimer.kx % 2 == 0 and dimer.ky % 4 == 2)):
            draw.polygon(rhomb_right(draw_x, draw_y), outline=1)
        else:
            draw.polygon(rhomb_left(draw_x, draw_y), outline=1)


def generate_lattice(points):
    """Creates an iterable object over all lattice points."""
    lattice = []
    for y in range(points):
        for x in range(int(points / (y % 2 + 1))):
            lattice.append(M3O_dimer(x, y, False))
    return lattice


def kag_to_screen(x, y):
    """transforms a kagome coordinate to a point on screen"""
    if y % 2 == 0:
        indent = DEFAULT_GRIDSIZE / 4
        step = DEFAULT_GRIDSIZE / 2
    else:
        indent = 0
        step = DEFAULT_GRIDSIZE
    if (y + 1) % 4 == 0:
        indent = DEFAULT_GRIDSIZE / 2
    return (x * step + indent, y * DEFAULT_GRIDHEIGHT)


def rhomb_at_kagome(draw, x, y, color):
    """Draws a rhomb in the correct orientation at a given kagome lattice point."""
    draw_x, draw_y = kag_to_screen(x, y) # converting to drawing coordinates
    if y % 2 == 1:
        draw.polygon(rhomb_lying(draw_x, draw_y), color)
    elif ((y % 2 == 0 and x % 2 == 1 and y % 4 == 0) or
          (y % 2 == 0 and x % 2 == 0 and y % 4 == 2)):
        draw.polygon(rhomb_right(draw_x, draw_y), color)
    else:
        draw.polygon(rhomb_left(draw_x, draw_y), color)


def rhomb_lying(x, y):
    """Vertex coordinates for a lying rhomb."""
    """      v4
          __,.__
    v1  <´__  __`>  v3
            `´
    """
    v1x = int(x - DEFAULT_GRIDSIZE / 2)
    v1y = int(y)

    v2x = int(x)
    v2y = int(y - DEFAULT_GRIDHEIGHT * 2 / 3)

    v3x = int(x + DEFAULT_GRIDSIZE / 2)
    v3y = int(y)

    v4x = int(x)
    v4y = int(y + DEFAULT_GRIDHEIGHT * 2 / 3)

    return (v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y)


def rhomb_left(x, y):
    """Vertex coordinates for a rhomb with a high vertice on the left side."""
    """ v3
       |\
       | \  v2
       \ |
        \|
        v1
    """
    v1x = int(x + DEFAULT_GRIDSIZE / 4)
    v1y = int(y + DEFAULT_GRIDHEIGHT)

    v2x = int(x + DEFAULT_GRIDSIZE / 4)
    v2y = int(y - DEFAULT_GRIDHEIGHT / 3)

    v3x = int(x - DEFAULT_GRIDSIZE / 4)
    v3y = int(y - DEFAULT_GRIDHEIGHT)

    v4x = int(x - DEFAULT_GRIDSIZE / 4)
    v4y = int(y + DEFAULT_GRIDHEIGHT / 3)

    return (v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y)


def rhomb_right(x, y):
    """Vertex coordinates for a rhomb with a high vertice on the right side."""
    """ v3
        /|
       / | v2
       | /
       |/
       v1
    """
    v1x = int(x - DEFAULT_GRIDSIZE / 4)
    v1y = int(y + DEFAULT_GRIDHEIGHT)

    v2x = int(x - DEFAULT_GRIDSIZE / 4)
    v2y = int(y - DEFAULT_GRIDHEIGHT / 3)

    v3x = int(x + DEFAULT_GRIDSIZE / 4)
    v3y = int(y - DEFAULT_GRIDHEIGHT)

    v4x = int(x + DEFAULT_GRIDSIZE / 4)
    v4y = int(y + DEFAULT_GRIDHEIGHT / 3)

    return (v1x, v1y, v2x, v2y, v3x, v3y, v4x, v4y)

class M3O_dimer():
    """This class holds information about the location and state of a dimer."""
    def __init__(self, kx, ky, reacted):
        self.kx = kx
        self.ky = ky
        self.reacted = reacted