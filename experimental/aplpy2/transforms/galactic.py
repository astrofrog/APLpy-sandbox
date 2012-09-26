# Exploring transformations in matplotlib - based on pywcsgrid2 code

import numpy as np

from matplotlib.transforms import Transform

from .base import CurvedTransform

# Galactic conversion constants
RA_NGP = np.radians(192.859508333333)
DEC_NGP = np.radians(27.1283361111111)
L_CP = np.radians(122.932)
L_0 = L_CP - np.pi / 2.
RA_0 = RA_NGP + np.pi / 2.
DEC_0 = np.pi / 2. - DEC_NGP


def gal2fk5(l, b):

    l = np.radians(l)
    b = np.radians(b)

    sind = np.sin(b) * np.sin(DEC_NGP) + np.cos(b) * np.cos(DEC_NGP) * np.sin(l - L_0)

    dec = np.arcsin(sind)

    cosa = np.cos(l - L_0) * np.cos(b) / np.cos(dec)
    sina = (np.cos(b) * np.sin(DEC_NGP) * np.sin(l - L_0) - np.sin(b) * np.cos(DEC_NGP)) / np.cos(dec)

    dec = np.degrees(dec)

    ra = np.arccos(cosa)
    ra[np.where(sina < 0.)] = -ra[np.where(sina < 0.)]

    ra = np.degrees(ra + RA_0)

    ra = np.mod(ra, 360.)
    dec = np.mod(dec + 90., 180.) - 90.

    return ra, dec


def fk52gal(ra, dec):

    ra, dec = np.radians(ra), np.radians(dec)

    np.sinb = np.sin(dec) * np.cos(DEC_0) - np.cos(dec) * np.sin(ra - RA_0) * np.sin(DEC_0)

    b = np.arcsin(np.sinb)

    cosl = np.cos(dec) * np.cos(ra - RA_0) / np.cos(b)
    sinl = (np.sin(dec) * np.sin(DEC_0) + np.cos(dec) * np.sin(ra - RA_0) * np.cos(DEC_0)) / np.cos(b)

    b = np.degrees(b)

    l = np.arccos(cosl)
    l[np.where(sinl < 0.)] = - l[np.where(sinl < 0.)]

    l = np.degrees(l + L_0)

    l = np.mod(l, 360.)
    b = np.mod(b + 90., 180.) - 90.

    return l, b


class Galactic2EquatorialTransform(CurvedTransform):
    """
    """
    input_dims = 2
    output_dims = 2
    is_separable = False

    def __init__(self):
        CurvedTransform.__init__(self)

    def transform(self, galactic):
        xg, yg = galactic[:, 0], galactic[:, 1]
        xe, ye = gal2fk5(xg, yg)
        equatorial = np.concatenate((xe[:, np.newaxis], ye[:, np.newaxis]), 1)
        return equatorial

    transform.__doc__ = Transform.transform.__doc__

    transform_non_affine = transform
    transform_non_affine.__doc__ = Transform.transform_non_affine.__doc__

    def inverted(self):
        return Equatorial2GalacticTransform()

    inverted.__doc__ = Transform.inverted.__doc__


class Equatorial2GalacticTransform(CurvedTransform):
    """
    """
    input_dims = 2
    output_dims = 2
    is_separable = False

    def __init__(self):
        CurvedTransform.__init__(self)

    def transform(self, equatorial):
        xe, ye = equatorial[:, 0], equatorial[:, 1]
        xg, yg = fk52gal(xe, ye)
        galactic = np.concatenate((xg[:, np.newaxis], yg[:, np.newaxis]), 1)
        return galactic

    transform.__doc__ = Transform.transform.__doc__

    transform_non_affine = transform
    transform_non_affine.__doc__ = Transform.transform_non_affine.__doc__

    def inverted(self):
        return Galactic2EquatorialTransform()

    inverted.__doc__ = Transform.inverted.__doc__
