import numpy as np
import kagome_lattice
import os
import os.path
from PIL import Image

def doFourierTransform(rhombGrid, newFolder, cycle):
    toFourier = np.zeros([rhombGrid.image.size[0], rhombGrid.image.size[1]])

    path = os.path.join(rhombGrid.outputFolder, newFolder)
    if not os.path.exists(path):
        os.makedirs(path)

    for y in range(len(rhombGrid.lattice)):
        for x in range(len(rhombGrid.lattice[y])):
            rhomb = rhombGrid.getRhomb(x, y)
            if rhomb.reacted:
                point = rhombGrid.kag_to_screen(rhomb.x, rhomb.y)
                if pointVisible(point, rhombGrid.image.size):
                    toFourier[int(point[0]), int(point[1])] = 1

    image = Image.fromarray(toFourier)
    image.save(os.path.join(path, "grid_%s.tif" % cycle))
    toFourier = np.real(np.fft.fftshift(np.fft.fftn(np.fft.fftshift(toFourier))))
    image = Image.fromarray(toFourier)
    image.save(os.path.join(path, "fourier_%s.tif" % cycle))


def pointVisible(point, imageSize):
    return point[0] >= 0 and point[1] >= 0 and point[0] < imageSize[0] and point[1] < imageSize[1]