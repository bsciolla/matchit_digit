

#!/usr/bin/env python


# Import Modules
import os
import pygame
import copy
import sys
import numpy
import math
from pygame.locals import *
from pygame.compat import geterror
import match_func
import sound
import imageloader
from spriteclass import *
from speedseq import Speedseq
# functions to create our resources

from globals import DELTAX, DELTAY, ANIMRATE, SLOWED_TIME

from globals import MATCH_VIEWX, MATCH_VIEWY
from globals import DEATHMODE, XSTART, YSTART, SCROLLING_DEATHX

from globals import HSCREEN, VSCREEN, HBLOCK, VBLOCK

from globals import LARGE_TIME, FADE_WAIT, KEYBOARD_WAIT, PROBA_HIT, DELAY_HURT, SCORING_ROW_TIME

from globals import NKEYS

from globals import HITBOXX, HITBOXY

from globals import SPEEDSEQ

# Ellipsoidal patch for matching search
PATCH = numpy.zeros((MATCH_VIEWY*2, MATCH_VIEWX*2))
for j in range(PATCH.shape[0]):
    for i in range(PATCH.shape[1]):
        if (i-MATCH_VIEWX+0.5)**2.0/MATCH_VIEWX**2.0 +\
                (j-MATCH_VIEWY+0.5)**2/MATCH_VIEWY**2.0 <= 1:
            PATCH[j, i] = 1





SCROLLING_MINX = 200 if DEATHMODE == 0 else 1
SCROLLING_MAXX = HSCREEN - 200
SCROLLING_MINY = 200
SCROLLING_MAXY = VSCREEN - 200
assert(DEATHMODE == 0 or SCROLLING_DEATHX > SCROLLING_MINX)

fontsize = 30



def get_ticks():
    return(pygame.time.get_ticks())


if not pygame.font:
    print('Warning, fonts disabled')
if not pygame.mixer:
    print('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')



def coord_to_tiles(x, y):
    cx = HSCREEN/2.0 - (HBLOCK/2.0) * DELTAX
    cy = VSCREEN/2.0 - (VBLOCK/2.0) * DELTAY
    i = (int)((float)(x-cx)/(float)(DELTAX))
    j = (int)((float)(y-cy)/(float)(DELTAY))
    return i, j


CX = HSCREEN/2.0 - HBLOCK/2.0 * DELTAX
CY = VSCREEN/2.0 - VBLOCK/2.0 * DELTAY



class MotionHandler():
    def __init__(self):
        self.factor = 1
        self.timer = 0

    def slowing(self):
        self.factor = 0.3
        self.timer = get_ticks()

    def refresh(self):
        if get_ticks() - self.timer > SLOWED_TIME:
            self.factor = 1

class Hero():
    def __init__(self, board):

        if DEATHMODE == 1:
            print(XSTART, YSTART)
            print(board.SCROLLX,  board.SCROLLY)
            self.x = CX + XSTART*DELTAX + board.SCROLLX
            self.y = CY + YSTART*DELTAY + board.SCROLLY
        else:
            self.x = CX + 10*HBLOCK
            self.y = CY

        self.vx = 0
        self.vy = 0
        self.speedseq = []
        self.motionHandler = MotionHandler()
        for i in range(4):
            self.speedseq.append(Speedseq())

        self.sprite = SpriteMan()
        # self.companion1 = SpriteCompanion("undine.png")
        # self.companion2 = SpriteCompanion("lumina.png")

    def updatecompanions(self, board):
        angular_speed = 3.14/5000.
        self.companion1.rect.center = \
            (self.x + board.SCROLLX + MATCH_VIEWX*DELTAX*math.cos(get_ticks()*angular_speed),
             self.y + board.SCROLLY + MATCH_VIEWY*DELTAY*math.sin(get_ticks()*angular_speed))
        self.companion2.rect.center = \
            (self.x + board.SCROLLX + MATCH_VIEWX*DELTAX*math.cos(get_ticks()*angular_speed + math.pi),
             self.y + board.SCROLLY + MATCH_VIEWY*DELTAY*math.sin(get_ticks()*angular_speed + math.pi))

    def updateposition(self, board):

        # scrolling
        if DEATHMODE == 1 and board.playing is True:
            if self.x + board.SCROLLX < SCROLLING_DEATHX:
                print("DEAD")

        if self.x + board.SCROLLX < SCROLLING_MINX:
            board.scrolling(-(self.x + board.SCROLLX - SCROLLING_MINX), 0)

        if self.x + board.SCROLLX > SCROLLING_MAXX:
            board.scrolling(-(self.x + board.SCROLLX - SCROLLING_MAXX), 0)

        if self.y + board.SCROLLY < SCROLLING_MINY:
            board.scrolling(0, -(self.y + board.SCROLLY - SCROLLING_MINY))

        if self.y + board.SCROLLY > SCROLLING_MAXY:
            board.scrolling(0, -(self.y + board.SCROLLY - SCROLLING_MAXY))

        self.updateposition_nockeck(board)

    def updateposition_nockeck(self, board):
        self.sprite.rect.center = \
            (self.x + board.SCROLLX, self.y + board.SCROLLY)
        # self.updatecompanions(board)


    def get_speed(self, dx, dy):
        return(self.speedseq[2].speed*self.motionHandler.factor -
               self.speedseq[3].speed*self.motionHandler.factor,
               self.speedseq[1].speed*self.motionHandler.factor -
               self.speedseq[0].speed*self.motionHandler.factor)

    def accelerate(self, dx, dy):
        if self.motionHandler.factor<1:
            return
        if dy == -1:
            self.speedseq[0].increase_speed()
        if dy == 1:
            self.speedseq[1].increase_speed()
        if dx == 1:
            self.speedseq[2].increase_speed()
        if dx == -1:
            self.speedseq[3].increase_speed()
        return

    def stopping(self, dx, dy):
        if dx != 0:
            self.speedseq[2].reset_speed()
            self.speedseq[3].reset_speed()
        if dy != 0:
            self.speedseq[0].reset_speed()
            self.speedseq[1].reset_speed()

    def moving(self, dx, dy):
        self.accelerate(dx, dy)
        deltax, deltay = self.get_speed(dx, dy)
        self.x = self.x + deltax
        self.y = self.y + deltay
        self.motionHandler.refresh()

    def moving_digging(self, dx, dy):
        self.motionHandler.slowing()
        if dy == -1:
            self.speedseq[0].cut_speed(3)
        if dy == 1:
            self.speedseq[1].cut_speed(3)
        if dx == 1:
            self.speedseq[2].cut_speed(3)
        if dx == -1:
            self.speedseq[3].cut_speed(3)
        deltax, deltay = self.get_speed(dx, dy)
        self.x = self.x + deltax
        self.y = self.y + deltay


class Scoring():
    def __init__(self):

        self.health = 100

        self.combo_timer = get_ticks()
        self.in_a_row = 0
        self.deathscroll = 0.1
        self.deathtimer = get_ticks()
        self.factor = 1
        self.timer_hurt =  get_ticks()

    def empty_hit(self):

        self.combo_timer = get_ticks()
        self.in_a_row = 0
        self.factor = 1

        if numpy.random.rand() <= PROBA_HIT and get_ticks() - self.timer_hurt > DELAY_HURT :
            self.health = self.health - 5 - numpy.random.randint(5)
            self.timer_hurt = get_ticks()
            return True
        return False

    def out_of_time(self):
        return(get_ticks() - self.combo_timer > SCORING_ROW_TIME/self.factor)

    def register_dig(self):
        next_timer = get_ticks()
        if self.in_a_row >= 1:
            if next_timer - self.combo_timer < SCORING_ROW_TIME/self.factor:
                self.in_a_row += 1
                self.combo_timer = next_timer
        else:
            self.in_a_row = 1
            self.combo_timer = next_timer

        if self.in_a_row >= 4:
            self.in_a_row = 0
            self.factor += 0.2
            self.health = self.health + 3*self.factor

            return True
        return False

    def increase_deathscroll(self):
        if get_ticks() - self.deathtimer > 1000:
            self.deathscroll += 0.01
            self.deathtimer = get_ticks()



class MenuLife(Scoring):
    def __init__(self, group):
        Scoring.__init__(self)
        self.spritelist = []
        self.group = group

        img, rect = imageloader.load_image("life.png", -1)
        for i in range(20):
            sprite = SpriteTool(img)
            self.spritelist.append(sprite)
            group.add(sprite)
            sprite.place(10*i , 10)

    

    def show(self):
        j = (int)(self.health/100*20)
        if j < 0:
            j = 0
        if j > 20:
            j = 20
        [self.spritelist[i].remove(self.group) for i in range(j,20)]
        [self.spritelist[i].add(self.group) for i in range(0,j)]
            


class Move():
    # UP, DOWN, RIGHT, LEFT: 273, 274, 275, 276
    def __init__(self):
        self.push = numpy.array([0, 0, 0, 0])
        self.when = numpy.array([1, 1, 1, 1])*LARGE_TIME

    def key_up(self, key, hero):
        if not(self.is_a_move(key)):
            return
        self.push[key-273] = 0
        self.when[key-273] = LARGE_TIME
        if key == K_UP or key == K_DOWN:
            hero.stopping(0, 1)
        if key == K_LEFT or key == K_RIGHT:
            hero.stopping(1, 0)

    def key_down(self, key, hero):
        if not(self.is_a_move(key)):
            return
        self.push[key-273] = 1
        self.when[key-273] = get_ticks()
        if key == K_UP:
            hero.vy = -5
        if key == K_DOWN:
            hero.vy = 5
        if key == K_LEFT:
            hero.vx = -5
        if key == K_RIGHT:
            hero.vx = 5

    def launch_mem(self, board):
        if numpy.all(self.push == 0):
            return
        key = numpy.argmin(self.when) + 273

        if (get_ticks() - self.when[key-273]) > KEYBOARD_WAIT:
            board.move(key)
            self.when[key-273] = get_ticks()

    def is_a_move(self, key):
        return(key == K_LEFT or key == K_RIGHT or
               key == K_UP or key == K_DOWN)


class Board():
    def __init__(self, images, nkeys=NKEYS):

        self.images = images
        self.blocks_loaded = self.images.blocks_loaded
        self.anim_loaded = self.images.anim_loaded
        self.playing = False
        self.SCROLLX = 0
        self.SCROLLY = 0

        self.tiles = numpy.random.randint(0, nkeys, size=(VBLOCK, HBLOCK))
        if DEATHMODE == 0:
            self.tiles[0, :] = -1
            self.tiles[-1, :] = -1
            self.tiles[-2, :] = -1
            self.tiles[:, 0] = -1
            self.tiles[:, -1] = -1
            self.tiles[:, -2] = -1
        self.tilesid = numpy.zeros((VBLOCK, HBLOCK))

        if DEATHMODE == 1:
            self.tiles[YSTART-5:YSTART+5, XSTART-5:XSTART+5] = -1

        

        self.hour = get_ticks()
        self.hero = Hero(self)
        self.sound = sound.Sound()
        self.spritegroup = pygame.sprite.Group()
        self.spritegroup_other = pygame.sprite.Group()

        self.scoring = MenuLife(self.spritegroup_other)
        self.spritegroup_other.add(self.hero.sprite)
        # self.spritegroup_other.add(self.hero.companion1)
        # self.spritegroup_other.add(self.hero.companion2)
        self.explosiontiles = []

        self.build_blocks_sprites()
        self.place_tiles()
        self.hero.updateposition(self)

    def build_blocks_sprites(self):
        self.spritelist = []
        current_id = 0
        for j in range(VBLOCK):
            for i in range(HBLOCK):
                if self.tiles[j, i] != -1:
                    self.tilesid[j, i] = current_id
                    current_id = current_id + 1
                    img, rect = self.blocks_loaded[self.tiles[j, i]]
                    self.spritelist.append(SpriteTile(img, rect))
                    # SpriteTile(tilenames[self.tiles[j,i]]) )

                    self.spritelist[-1].add(self.spritegroup)
        self.tilesid = self.tilesid.astype(int)

    def scrolling(self, dx, dy):
        self.SCROLLX += dx
        self.SCROLLY += dy
        self.hero.updateposition_nockeck(self)
        self.place_tiles()

    # used in DEATHMODE
    def circular_warping(self):

        ibound = (int)((HSCREEN - CX - self.SCROLLX)/DELTAX)
        if ibound >= HBLOCK:
            #            This should be optimized:
            #            do not recreate ALL sprites but just the last column...
            self.perform_circular_warping()

    # used in DEATHMODE
    def perform_circular_warping(self):

        self.tiles[:, 0:-1] = self.tiles[:, 1:]
        self.tiles[:, -1] = numpy.random.randint(0, NKEYS, size=(VBLOCK))
        self.spritegroup.empty()
        self.build_blocks_sprites()

        self.scrolling(DELTAX, 0)
        self.hero.x = self.hero.x - DELTAX

    def move(self, key):
        dx = 0
        dy = 0
        i, j = coord_to_tiles(self.hero.x, self.hero.y)

        if (key == K_LEFT):
            dx = -1
        #   if (self.hero.x == 0):
        #       return
        if (key == K_RIGHT):
            dx = 1
        #    if (i >= HBLOCK-1):
        #        return
        if (key == K_UP):
            dy = -1
        #    if (j==0):
        #        return
        if (key == K_DOWN):
            dy = 1
        #    if (j >= VBLOCK-1):
        #       return

        dist_x = (self.hero.x - (CX + i*DELTAX))
        dist_y = (self.hero.y - (CY + j*DELTAY))
        speed_x, speed_y = self.hero.get_speed(dx, dy)

        collision = False

        if dx == 1 and dist_x + HITBOXX + speed_x >= 0.5*DELTAX:
            collision = True
            if dist_y/DELTAY <= 0.5:
                k, l = i+1, j
            else:
                k, l = i+1, j+1

        if dx == -1 and dist_x - HITBOXX + speed_x <= 0.5*DELTAX:
            collision = True
            if dist_y/DELTAY <= 0.5:
                k, l = i, j
            else:
                k, l = i, j+1

        if dy == 1 and dist_y + HITBOXY + speed_y >= 0.5*DELTAY:
            collision = True
            if dist_x/DELTAX <= 0.5:
                k, l = i, j+1
            else:
                k, l = i+1, j+1

        if dy == -1 and dist_y - HITBOXY + speed_y <= 0.5*DELTAY:
            collision = True
            if dist_x/DELTAX <= 0.5:
                k, l = i, j
            else:
                k, l = i+1, j

        if collision is True and self.tiles[l, k] == -1:
            collision = False

        # step in an empty space
        # if self.tiles[j+dy,i+dx] == -1:
        if collision is False:
            self.hero.moving(dx, dy)
            self.sound.play_stepsound()
            self.hero.updateposition(self)

        # Attempt to dig
        if collision is True:
            # Dig is allowed
            if self.find_match_to_one_tile(k, l, i, j):
                self.hero.moving_digging(dx, dy)
                self.hero.updateposition(self)
                if self.scoring.register_dig():
                    self.sound.play_combosound()
                else:
                    self.sound.play_digsound()
                    self.sound.play_hitsound()

            else:
                self.hero.stopping(dx, dy)

                if self.scoring.empty_hit():
                    self.sound.play_hurtsound()
                else:
                    self.sound.play_hitsound()

    def place_tiles(self):

        cx = HSCREEN/2.0 - HBLOCK/2.0 * DELTAX
        cy = VSCREEN/2.0 - VBLOCK/2.0 * DELTAY

        for j in range(VBLOCK):
            for i in range(HBLOCK):
                if self.tiles[j, i] != -1:
                    dx = i*DELTAX
                    dy = j*DELTAY
                    currentid = self.tilesid[j, i]
                    self.spritelist[currentid].rect.center = \
                        (cx + dx + self.SCROLLX, cy + dy + self.SCROLLY)

    def find_match_to_one_tile(self, i, j, io, jo):
        # reduced view
        imin = io - MATCH_VIEWX if io - MATCH_VIEWX >= 0 else 0
        imax = io + MATCH_VIEWX if io + MATCH_VIEWX < HBLOCK-1 else HBLOCK - 1
        jmin = jo - MATCH_VIEWY if jo - MATCH_VIEWY >= 0 else 0
        jmax = jo + MATCH_VIEWY if jo + MATCH_VIEWY < VBLOCK-1 else VBLOCK - 1
        # position of the tile of interest in the view
        i, j = i - imin, j - jmin
        io, jo = io - imin, jo - jmin

        local_tiles = copy.deepcopy(self.tiles[jmin:jmax, imin:imax])
        # Just use a memorized patch if the view is full.
        # Else, search in the square. Can be fixed later or never.
        if jmax-jmin == 2*MATCH_VIEWY and imax-imin == 2*MATCH_VIEWX:
            local_tiles[PATCH == 0] = -2

        idx_list = numpy.argwhere(local_tiles == local_tiles[j, i])

        list_match = []

        for idx in range(idx_list.shape[0]):
            k = idx_list[idx, 1]
            l = idx_list[idx, 0]
            connect = match_func.find_connection(i, j, k, l, local_tiles)
            if connect is True and (i != k or j != l):
                list_match.append([k, l])

        if list_match == []:
            return False

        distances = []
        for pair in list_match:
            distances.append(((i-pair[0])**2.0 + (j-pair[1])**2.0)**0.5)

        rank = numpy.argmin(distances)
        k = list_match[rank][0]
        l = list_match[rank][1]

        self.do_digging(i+imin, j+jmin, k+imin, l+jmin)
        return True

    def do_digging(self, i, j, k, l):
        self.group_dig(i, j, 'digged')
        self.group_dig(k, l)


    def group_dig(self, i, j, tag='not'):
        xini, yini = (CX + i*DELTAX + self.SCROLLX,
                      CY + j*DELTAY + self.SCROLLY)
        # Heavy explosion where the character is not!
        if tag == 'not':
            self.spritegroup_other.add(AnimatedTile(self.anim_loaded,
                                                xini-self.SCROLLX, yini-self.SCROLLY, self))
            for number in range(3):
                self.add_destroy_sprite(i, j, self.tiles[j, i])

        # Add a modest explosion close to the character
        if tag == 'digged':
            self.spritegroup_other.add(AnimatedTile(self.anim_loaded[:2],
                                                xini-self.SCROLLX, yini-self.SCROLLY, self))
        # Remove tile
        index = self.tilesid[j, i]
        self.spritelist[index].dig(self.spritegroup)
        self.tiles[j, i] = -1


    def add_destroy_sprite(self, i, j, flavor):
        img, rect = self.blocks_loaded[flavor]
        xini, yini = (CX + i*DELTAX + self.SCROLLX,
                      CY + j*DELTAY + self.SCROLLY)
        self.explosiontiles.append(ExplosionTile(
            img, xini-self.SCROLLX, yini-self.SCROLLY))
        self.spritegroup_other.add(self.explosiontiles[-1])

    def updateBoard(self):
        self.scoring.show()
        for t in self.explosiontiles:
            t.moving(self)
        if self.scoring.out_of_time() and self.scoring.in_a_row >= 1:
            self.sound.play_outoftimesound()
            self.scoring.in_a_row = 0


def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
# Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((HSCREEN, VSCREEN))
    pygame.display.set_caption('Matchit_Digit')
    pygame.mouse.set_visible(0)

# Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((50, 20, 10))


# Create font
    if pygame.font:
        font = pygame.font.Font(None, fontsize)

# Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

# Prepare Game Objects
    clock = pygame.time.Clock()

    images = imageloader.Imageloader()

    board = Board(images)
    move = Move()

    if DEATHMODE == 1:
        board.scrolling(500, 0)
    board.playing = True

# Main Loop
    going = True
    sound_loop = 0
    current_key = -1

    while going:
        clock.tick(30)

        move.launch_mem(board)

        # Handle Input Events
        for event in pygame.event.get():

            if event.type == KEYDOWN:
                move.key_down(event.key, board.hero)

            if event.type == KEYUP:
                move.key_up(event.key, board.hero)

            if event.type == QUIT:
                going = False

            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                going = False

            elif event.type == KEYDOWN and move.is_a_move(event.key):
                board.move(event.key)

        board.scrolling(0, 0)

        if DEATHMODE == 1:
            board.scoring.increase_deathscroll()
            board.scrolling(-board.scoring.deathscroll, 0)
            board.circular_warping()

        # Draw Everything
        board.updateBoard()
        screen.blit(background, (0, 0))
        board.spritegroup.draw(screen)
        board.spritegroup_other.update()
        board.spritegroup_other.draw(screen)
        pygame.display.flip()

    pygame.quit()

# Game Over


# this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()
