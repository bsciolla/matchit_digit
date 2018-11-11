

#!/usr/bin/env python
"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation,
follow along in the tutorial.
"""
HSCREEN = 640
VSCREEN = 400
#Import Modules
import os, pygame
import sys
import numpy
from pygame.locals import *
from pygame.compat import geterror

from scipy import ndimage
import imageio
import matplotlib.pyplot as plt

img = imageio.imread("data/dwarf.png")
img = img[445:484,10:480]

#for i in range(13):
#    img[:,1+i*29,:] = 0

# pas encore ça...


imageio.imsave("data/dwarf_face.png",img[:,151:176,:])

plt.imshow(img[:,151:176])
plt.show()



