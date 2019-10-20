
import pygame, numpy
import imageloader
from globals import DELTAX, DELTAY, LIFESPAN, ANIMRATE
from globals import COMBOX, COMBOY, FACTORDISPLAYCOMBO

from globals import TAG_NO_PRESSURE
import copy


def get_ticks():
    return(pygame.time.get_ticks())

class SpriteHero(pygame.sprite.Sprite):
    def __init__(self, imagelist):
        pygame.sprite.Sprite.__init__(self)
        self.imagelist = imagelist
        self.image, self.rect = self.imagelist[0]
        self.ReloadWithSize(0,1)
        self.skin = 0
        self.size = 0.9
        self.imgnum = 0

    def ChangeSkin(self, skin):
        self.skin = skin
        self.IncreaseSkin()
        self.ReloadWithSize(self.imgnum, self.size)


    def ReloadWithSize(self, skin, factor):
        image = self.imagelist[skin][0].copy()
        height = image.get_height()
        width = image.get_width()
        resizing = factor*DELTAY/height if (height/width > DELTAY/DELTAX) else factor*DELTAX/width
        self.image = pygame.transform.scale(
                image, ((int)(resizing*width), (int)(resizing*height)) )
        self.rect = self.image.get_rect()

    def IncreaseSkin(self):
        self.size = 0.9 + (self.skin%3)*0.2
        self.imgnum = self.skin//3
        if self.imgnum > 6:
            self.imgnum = 6
            if self.skin > 7*3:
                self.size = 1.5
        

class SpriteCompanion(pygame.sprite.Sprite):
    def __init__(self, image):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = image
        
        self.image = pygame.transform.scale(
            self.image, ((int)(0.5*(DELTAX+1)), (int)(0.5*(DELTAY+1))))
  #     self.rect = self.image.get_rect()


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

class BallSprite(pygame.sprite.Sprite):
    def __init__(self, name):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = imageloader.load_image("BallSprite.png", -1)
        self.image = pygame.transform.scale(
            self.image, ((int)(0.5*(DELTAX+1)), (int)(0.5*(DELTAY+1))))
        self.rect = self.image.get_rect()
        


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



class ComboSprite(pygame.sprite.Sprite):

    def __init__(self, images, group, xfixed=None):
        pygame.sprite.Sprite.__init__(self)
        self.imagelist = []
        for i in range(len(images)):
            self.imagelist.append((images[i][0].copy(),images[i][1].copy()))
        self.iterframe = 0
        self.image = self.imagelist[self.iterframe][0]
        self.rect = self.imagelist[self.iterframe][1]
        self.x = COMBOX
        self.xfixed = xfixed
        self.y = COMBOY
        self.score = 10
        self.timer = get_ticks() + ANIMRATE
        self.placeTile()
        if TAG_NO_PRESSURE == 0:
            self.add(group)

    def update(self):
        self.placeTile()
        if (get_ticks() > self.timer):
            self.nextTile()

    def nextTile(self):
        self.iterframe += 1
        if self.iterframe > len(self.imagelist) - 1:
            self.iterframe = 0
        self.timer = get_ticks() + ANIMRATE
        self.image = self.imagelist[self.iterframe][0]
        self.rect = self.imagelist[self.iterframe][1]
        self.placeTile()
        self.timer = get_ticks() + ANIMRATE


    def placeTile(self):
        if self.xfixed is None:
            self.rect.center = (self.x + self.score * FACTORDISPLAYCOMBO, self.y)
        else:
            self.rect.center = (self.xfixed, self.y)

class ComboSpriteFixed(pygame.sprite.Sprite):

    def __init__(self, images, group, xfixed):
        pygame.sprite.Sprite.__init__(self)
        self.imagelist = copy.deepcopy(images)
        self.iterframe = 0
        self.image = self.imagelist[self.iterframe][0]
        self.rect = self.imagelist[self.iterframe][1]
        self.xfixed = xfixed
        self.y = COMBOY
        self.timer = get_ticks() + ANIMRATE
        self.placeTile()
        self.add(group)

    def update(self):
    	return
        #self.placeTile()
        #if (get_ticks() > self.timer):
        #    self.nextTile()

    def nextTile(self):
        self.iterframe += 1
        if self.iterframe > len(self.imagelist) - 1:
            self.iterframe = 0
        self.timer = get_ticks() + ANIMRATE
        self.image = self.imagelist[self.iterframe][0]
        self.rect = self.imagelist[self.iterframe][1]
        self.placeTile()
        self.timer = get_ticks() + ANIMRATE


    def placeTile(self):
        self.rect.center = (self.xfixed, self.y)


