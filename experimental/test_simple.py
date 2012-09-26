from astropy.wcs import WCS
from astropy.io import fits

import matplotlib.pyplot as plt

from aplpy2.axes import HostAxes
from aplpy2.transforms.wcs import WcsPixel2WorldTransform
from aplpy2.transforms.galactic import Equatorial2GalacticTransform
from aplpy2.angle import Angle


# Read in image
hdu = fits.open('MSX_E.fits.gz')[0]
# wcs = WCS('1904-66_AZP.fits')

# Set up WCS transformation
wcs = WCS(hdu.header)
wcs_trans = WcsPixel2WorldTransform(wcs)


# Set up Galactic/Equatorial transformation
coord = Equatorial2GalacticTransform()

# Create plot and axes
fig = plt.figure()

# Initialize axes
ax = HostAxes(fig, [0.1, 0.1, 0.8, 0.8], wcs_trans,
              xcoord_type='longitude',
              ycoord_type='latitude')

# Set tick spacing since no automatic method yet
ax.set_xspacing(Angle(0.2))
ax.set_yspacing(Angle(0.2, latitude=True))

# Set view limits
# ax.set_xlim(0.5, 192.5)
# ax.set_ylim(0.5, 192.5)

# Show image
ax.imshow(hdu.data, origin='lower', cmap=plt.cm.binary, interpolation='nearest', vmax=0.0001)

# Save to file
fig.savefig('test.png', bbox_inches='tight')
