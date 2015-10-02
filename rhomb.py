def lying(x, y, latticeWidth, latticeHeight):
    """Vertex coordinates for a lying rhomb."""
    """      v4
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
    """Vertex coordinates for a rhomb with a high vertice on the left side."""
    """ v3
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
    """Vertex coordinates for a rhomb with a high vertice on the right side."""
    """ v3
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