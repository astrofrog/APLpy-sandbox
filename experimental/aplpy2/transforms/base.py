# This code is based off code included in pywcsgrid2

from matplotlib.transforms import Transform
from matplotlib.path import Path


class CurvedTransform(Transform):
    
    def __init__(self):
        """
        Create a new WCS transform.
        """
        Transform.__init__(self)

    def transform_path(self, path):
        return Path(self.transform(path.vertices), path.codes)

    transform_path.__doc__ = Transform.transform_path.__doc__

    transform_path_non_affine = transform_path
    transform_path_non_affine.__doc__ = Transform.transform_path_non_affine.__doc__
