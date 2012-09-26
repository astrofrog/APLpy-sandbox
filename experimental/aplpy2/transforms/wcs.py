# This code is based off code included in pywcsgrid2

import numpy as np

from matplotlib.transforms import Transform

from .base import CurvedTransform


class WcsWorld2PixelTransform(CurvedTransform):
    """
    """
    input_dims = 2
    output_dims = 2
    is_separable = False

    def __init__(self, wcs):
        CurvedTransform.__init__(self)
        self.wcs = wcs

    def transform(self, world):

        xw, yw = world[:, 0], world[:, 1]

        xp, yp = self.wcs.wcs_world2pix(xw, yw, 1)
        xp, yp = xp - 1, yp - 1
        pixel = np.concatenate((xp[:, np.newaxis], yp[:, np.newaxis]), 1)

        return pixel

    transform.__doc__ = Transform.transform.__doc__

    transform_non_affine = transform
    transform_non_affine.__doc__ = Transform.transform_non_affine.__doc__

    def inverted(self):
        return WcsPixel2WorldTransform(self.wcs)

    inverted.__doc__ = Transform.inverted.__doc__


class WcsPixel2WorldTransform(CurvedTransform):
    """
    """
    input_dims = 2
    output_dims = 2
    is_separable = False

    def __init__(self, wcs):
        CurvedTransform.__init__(self)
        self.wcs = wcs

    def transform(self, pixel):

        xp, yp = pixel[:, 0], pixel[:, 1]

        xp, yp = xp + 1, yp + 1
        xw, yw = self.wcs.wcs_pix2world(xp, yp, 1)
        world = np.concatenate((xw[:, np.newaxis], yw[:, np.newaxis]), 1)

        return world

    transform.__doc__ = Transform.transform.__doc__

    transform_non_affine = transform
    transform_non_affine.__doc__ = Transform.transform_non_affine.__doc__

    def inverted(self):
        return WcsWorld2PixelTransform(self.wcs)

    inverted.__doc__ = Transform.inverted.__doc__
