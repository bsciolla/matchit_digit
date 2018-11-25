
import pygame, numpy
import imageloader
from globals import DELTAX, DELTAY, LIFESPAN, ANIMRATE



def get_ticks():
    return(pygame.time.get_ticks())

class SpriteMan(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = imageloader.load_image("dwarf_face.png", -1)
        self.image = pygame.transform.scale(
            self.image, ((int)(0.7*(DELTAX+1)), (int)(0.7*(DELTAY+1))))
        self.rect = self.image.get_rect()


class SpriteCompanion(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = imageloader.load_image(name, -1)
        self.image = pygame.transform.scale(
            self.image, ((int)(0.5*(DELTAX+1)), (int)(0.5*(DELTAY+1))))
        self.rect = self.image.get_rect()


class SpriteTile(pygame.sprite.Sprite):
    def __init__(self, img, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = img, rect
        self.image = pygame.transform.scale(self.image, (DELTAX+1, DELTAY+1))
        self.rect = self.image.get_rect()

    def dig(self, group):
        self.remove(group)

class SpriteTool(pygame.sprite.DirtySprite):
    def __init__(self, img):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()

    def Removing(self, group):
        self.remove(group)

    def hide(self):
        self.dirty = 2
        self.visible = 0

    def show(self):
        self.dirty = 2
        self.visible = 1

    def place(self, x, y):
        self.rect.center = x, y



class ExplosionTile(pygame.sprite.Sprite):

    def __init__(self, img, xini, yini):

        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.image = pygame.transform.scale(self.image, (numpy.random.randint(2, (int)((DELTAX+1)/2.0)),
                                                         numpy.random.randint(2, (int)((DELTAY+1)/2.0))))
        # X, Y = self.image.get_size()
        # self.image = self.image[x1:x2,y1:y2]
        # self.image = pygame.transform.scale(self.image, (DELTAX+1, DELTAY+1))
        self.rect = self.image.get_rect()
        self.vx = (-0.5+numpy.random.rand())*3
        self.vy = (-0.5+numpy.random.rand())*3
        self.x = xini
        self.y = yini
        self.timer = get_ticks() + numpy.random.randint((int)(LIFESPAN/2), LIFESPAN)

    def moving(self, board):

        self.x = self.x + self.vx
        self.y = self.y + self.vy
        # gravity
        self.vy = self.vy + 0.1
        # bounce
        if self.vy > 0 and numpy.random.randint(20) == 0:
            self.vy = -self.vy
            self.vx = self.vx + (-0.5+numpy.random.rand())

        self.rect.center = \
            (self.x + board.SCROLLX, self.y + board.SCROLLY)
        if (get_ticks() > self.timer):
            self.remove(board.spritegroup_other)
            board.explosiontiles.remove(self)


class AnimatedTile(pygame.sprite.Sprite):

    def __init__(self, imglist, xini, yini, board):

        pygame.sprite.Sprite.__init__(self)
        self.imagelist = imglist
        self.iterframe = 0
        self.image = self.imagelist[self.iterframe][0]
        self.rect = self.image.get_rect()
        self.x = xini
        self.y = yini
        self.timer = get_ticks() + ANIMRATE
        self.board = board
        self.rect.center = \
            (self.x + self.board.SCROLLX, self.y + self.board.SCROLLY)

    def update(self):
        self.rect.center = \
            (self.x + self.board.SCROLLX, self.y + self.board.SCROLLY)
        if (get_ticks() > self.timer):
            self.nextTile()

    def nextTile(self):
        self.iterframe += 1
        if self.iterframe > len(self.imagelist) - 1:
            self.ending()
            return
        self.timer = get_ticks() + ANIMRATE
        self.image = self.imagelist[self.iterframe][0]
        self.rect = self.image.get_rect()
        self.rect.center = \
            (self.x + self.board.SCROLLX, self.y + self.board.SCROLLY)
        self.timer = get_ticks() + ANIMRATE

    def ending(self):
        self.remove(self.board.spritegroup_other)

