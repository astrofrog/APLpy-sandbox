import matplotlib as mpl
from matplotlib.ticker import Formatter


class TransformFormatter(Formatter):
    """
    Custom formatter for arbitrary transforms, with support for angles

    Parameters
    ----------
    coord : str
        The coordinate for which to look for ticks. Should be one of 'x' or
        'y'.
    transform : :class:`~matplotlib.transforms.Transform`
        The pixel to world transformation
    """

    def __init__(self, locator=None, format='dd:mm:ss', style='plain'):
        self.locator = locator
        self.format = format
        self.style = style

    @property
    def format(self):
        return self._format

    @format.setter
    def format(self, value):
        self._format = value

    @property
    def style(self):
        return self._style

    @style.setter
    def style(self, value):
        if value is None or value in ['plain', 'colons']:
            self._style = value
        else:
            raise ValueError("style should be either 'plain' or 'colons'")

    @property
    def spacing(self):
        return self.locator.spacing

    @property
    def coord_type(self):
        return self.locator.coord_type

    @property
    def coord(self):
        return self.locator.coord

    def __call__(self, x, pos=None):
        'Return the format for tick val x at position pos; pos=None indicated unspecified'

        if self.coord_type in ['longitude', 'latitude']:

            hours = 'h' in self.format

            if self.style == 'plain':
                if mpl.rcParams['text.usetex']:
                    label_style = 'plain_tex'
                else:
                    label_style = 'plain_notex'
            else:
                label_style = self.style

            if label_style == 'plain_notex':
                sep = (u'\u00b0', u"'", u'"')
                if hours:
                    sep = ('h', 'm', 's')
            elif label_style == 'colons':
                sep = (':', ':', '')
            elif label_style == 'plain_tex':
                if hours:
                    sep = ('^{h}', '^{m}', '^{s}')
                else:
                    sep = ('^{\circ}', '^{\prime}', '^{\prime\prime}')

            label = self.spacing * self.locator._cache_world[pos]
            if hours:
                label = label.tohours()
            label = label.tostringlist(format=self.format, sep=sep)

            if self.coord == 'x' or self.locator._cache_world[pos] > 0:
                comp_ipos = pos - 1
            else:
                comp_ipos = pos + 1

            if comp_ipos >= 0 and comp_ipos <= len(self.locator._cache_pix) - 1:

                comp_label = self.spacing * self.locator._cache_world[comp_ipos]
                if hours:
                    comp_label = comp_label.tohours()
                comp_label = comp_label.tostringlist(format=self.format, sep=sep)

                for iter in range(len(label)):
                    if comp_label[0] == label[0]:
                        label.pop(0)
                        comp_label.pop(0)
                    else:
                        break

        else:

            label = self.spacing * self.locator._cache_world[pos]
            label = self.format % label

        if mpl.rcParams['text.usetex']:
            return "$" + "".join(label) + "$"
        else:
            return "".join(label)
