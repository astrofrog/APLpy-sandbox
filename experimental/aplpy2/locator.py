import numpy as np

from matplotlib.ticker import Locator
from matplotlib.transforms import Transform


class TransformLocator(Locator):
    """
    Custom locator for arbitrary transforms

    Parameters
    ----------
    coord : str
        The coordinate for which to look for ticks. Should be one of 'x' or
        'y'.
    location : str
        The axis on which to look for ticks. Should be one of 'left', 'top',
        'right', or 'bottom'
    transform : :class:`~matplotlib.transforms.Transform`
        The pixel to world transformation
    spacing : float
        The initial spacing to use for the ticks. If set to ``None``, then a
        default spacing will be chosen.
    coord_type : str
        The type of coordinate. This can be either ``scalar`` (no special
        treatment), ``longitude`` (in the range 0 to 360, with wrap-around),
        or ``latitude`` (in the range -90 to 90).
    """

    def __init__(self, coord=None, location=None, transform=None,
                 spacing=None, coord_type='scalar'):

        self.coord = coord
        self.location = location
        self.transform = transform
        self.spacing = spacing
        self.coord_type = coord_type

    def __call__(self):

        # Get the Axes object
        ax = self.axis.get_axes()

        # Get the current view interval in pixel coordinates
        ymin, ymax = ax.yaxis.get_view_interval()
        xmin, xmax = ax.xaxis.get_view_interval()

        # TODO: if spacing is None, find default spacing

        if self.coord_type in ['longitude', 'latitude']:
            tick_spacing = self.spacing.todegrees()
        else:
            tick_spacing = self.spacing

        # Fine the tick positions for the given spacing
        px, py, wx = tick_positions(ax, self.transform,
                                    self.location, self.coord,
                                    self.coord_type, tick_spacing)

        self._cache_pix = px if self.coord == 'x' else py
        self._cache_world = wx

        # Return the pixel positions of the ticks
        return px if self.coord == 'x' else py

    @property
    def spacing(self):
        return self._spacing

    @spacing.setter
    def spacing(self, value):
        self._spacing = value

    @property
    def coord_type(self):
        return self._coord_type

    @coord_type.setter
    def coord_type(self, value):
        if value in ['scalar', 'longitude', 'latitude']:
            self._coord_type = value
        else:
            raise ValueError("coord_type should be one of 'scalar'/'longitude'/'latitude'")

    @property
    def transform(self):
        return self._transform

    @transform.setter
    def transform(self, value):
        if isinstance(value, Transform):
            self._transform = value
        else:
            raise TypeError("transform should be a Transform object")

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        if value in ['left', 'top', 'right', 'bottom']:
            self._location = value
        else:
            raise ValueError("location shold be one of 'left'/'top'/'right'/'bottom'")

    @property
    def coord(self):
        return self._coord

    @coord.setter
    def coord(self, value):
        if value in ['x', 'y']:
            self._coord = value
        else:
            raise ValueError("coord should be either 'x' or 'y'")


def tick_positions(ax, transform, location, coord, coord_type, spacing):
    """
    Return the position of ticks

    Parameters
    ----------
    ax : Axes instance
        The axes object in which to look for tick locations
    transform : Transform instance
        The pixel-to-world transformation of the system
    location : str
        One of 'bottom/left/top/right, the axis on which to look for ticks
    coord : str
        Whether to look for intersections with the x or y coordinate
    coord_type : str
        The type of coordinate, one of 'longitude/latitude/scalar'
    spacing : float
        The tick spacing
    """

    # First get a fine sampling of positions along the axis
    px, py, wx, wy = axis_positions(ax, transform, location)

    # Separate world coordinates between primary and secondary

    if coord == 'x':
        warr, walt = wx, wy
    else:
        warr, walt = wy, wx

    if coord_type in ['longitude', 'latitude']:

        # Check for 360 degree transition, and if encountered,
        # change the values so that there is continuity

        for i in range(0, len(warr) - 1):
            if(abs(warr[i] - warr[i + 1]) > 180.):
                if(warr[i] > warr[i + 1]):
                    warr[i + 1:] = warr[i + 1:] + 360.
                else:
                    warr[i + 1:] = warr[i + 1:] - 360.

    # Convert warr to units of the spacing, then ticks are at integer values
    warr = warr / spacing

    # TODO: optimize the following with C code? Or simply smarter Python code?

    # Create empty arrays for tick positions
    iall = []
    wall = []

    # Loop over ticks which lie in the range covered by the axis
    for w in np.arange(np.floor(min(warr)), np.ceil(max(warr)), 1.):

        # Find all the positions at which to interpolate
        inter = np.where(((warr[:-1] <= w) & (warr[1:] > w)) | ((warr[:-1] > w) & (warr[1:] <= w)))[0]

        # If there are any intersections, keep the indices, and the position
        # of the interpolation
        if len(inter) > 0:
            iall.append(inter.astype(int))
            wall.append(np.repeat(w, len(inter)).astype(float))

    if len(iall) > 0:
        iall = np.hstack(iall)
        wall = np.hstack(wall)
    else:
        return np.array([]), np.array([]), np.array([])

    # Now we can interpolate as needed
    dwarr = warr[1:] - warr[:-1]
    px_out = px[:-1][iall] + (px[1:][iall] - px[:-1][iall]) * (wall - warr[:-1][iall]) / dwarr[iall]
    py_out = py[:-1][iall] + (py[1:][iall] - py[:-1][iall]) * (wall - warr[:-1][iall]) / dwarr[iall]

    warr_out = wall

    return np.array(px_out), np.array(py_out), np.array(warr_out)


def axis_positions(ax, transform, location, n_samples=100):
    """
    Return pixel and world positions for a single axis.

    Given an Axes instance, a pixel-to-world transformation, and the
    location of the axis along which to get positions from, return the
    pixel and world positions along the axis.
    """

    # Get axes limits in pixel coordinates
    xmin, xmax = ax.xaxis.get_view_interval()
    ymin, ymax = ax.yaxis.get_view_interval()

    # Generate pixel positions
    if location in ['bottom', 'top']:
        x_pix = np.linspace(xmin, xmax, n_samples)
        if location == 'bottom':
            y_pix = np.repeat(ymin, n_samples)
        else:
            y_pix = np.repeat(ymax, n_samples)
    elif location in ['left', 'right']:
        if location == 'left':
            x_pix = np.repeat(xmin, n_samples)
        else:
            x_pix = np.repeat(xmax, n_samples)
        y_pix = np.linspace(ymin, ymax, n_samples)
    else:
        raise Exception("location should be one of 'left'/'top'/'right'/'bottom'")

    # Convert pixel to world coordinates
    world = transform.transform(np.vstack([x_pix, y_pix]).transpose())
    x_world, y_world = world[:, 0], world[:, 1]

    # Return positions along axes
    return x_pix, y_pix, x_world, y_world
