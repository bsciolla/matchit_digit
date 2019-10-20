
import os
import pygame
from pygame.locals import *
from pygame.compat import geterror

from globals import DELTAX, DELTAY


main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()



class Imageloader():
    def __init__(self):

        tilenames = ['blocks/ore'+str(i)+'.png' for i in range(1, 15)] + \
            ['blocks/rock'+str(i)+'.png' for i in range(1, 19)]
        exanames = ['exa'+str(i)+'.png' for i in range(1, 10)]
        firenames = ['fire'+str(i)+'.png' for i in range(1, 5)]
        heronames = ['hero'+str(i)+'.png' for i in range(1, 8)]
        lumina = ['lumina.png']

        self.blocks_loaded = [load_image(i) for i in tilenames]
        self.anim_loaded = [load_image(i, -1) for i in exanames]
        self.fire_loaded = [load_image(i, -1) for i in firenames]
        self.hero_loaded = [load_image(i, -1) for i in heronames]
        self.lumina_loaded = [load_image('lumina.png', -1)]



