

#!/usr/bin/env python
"""
This simple example is used for the line-by-line tutorial
that comes with pygame. It is based on a 'popular' web banner.
Note there are comments here, but for the full explanation,
follow along in the tutorial.
"""




#Import Modules
import os, pygame
import copy
import sys
import numpy
from pygame.locals import *
from pygame.compat import geterror


#functions to create our resources
def load_image(name, colorkey=None):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error:
        print ('Cannot load image:', fullname)
        raise SystemExit(str(geterror()))
    image = image.convert()
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((0,0))
        image.set_colorkey(colorkey, RLEACCEL)
    return image, image.get_rect()

def load_sound(name):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print ('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    return sound


DEATHMODE = 1
XSTART = 15
YSTART = 15
SCROLLING_DEATHX = 100 

MATCH_VIEWX = 10
MATCH_VIEWY = 10

# Ellipsoidal patch for matching search
PATCH = numpy.zeros((MATCH_VIEWY*2,MATCH_VIEWX*2))
for j in range(PATCH.shape[0]):
    for i in range(PATCH.shape[1]):
        if (i-MATCH_VIEWX+0.5)**2.0/MATCH_VIEWX**2.0 + (j-MATCH_VIEWY+0.5)**2/MATCH_VIEWY**2.0 <= 1:
            PATCH[j,i] = 1
            

HSCREEN = 800
VSCREEN = 600

LARGE_TIME = sys.maxsize

FADE_WAIT = 10
KEYBOARD_WAIT = 70
PROBA_HIT = 0.4

HBLOCK = 40
VBLOCK = 50

DELTAX = 32
DELTAY = 32

SCROLLING_MINX = 200 if DEATHMODE == 0 else 1
SCROLLING_MAXX = HSCREEN - 200
SCROLLING_MINY = 200
SCROLLING_MAXY = VSCREEN - 200
assert(DEATHMODE == 0 or SCROLLING_DEATHX > SCROLLING_MINX)

SCORING_ROW = 1000

HITBOXX = 0.7*(DELTAX+1)*0.5
HITBOXY = 0.7*(DELTAY+1)*0.5

SPEEDSEQ = numpy.array([0,4,5,6,7,7.5,8,8.5,9])*1.2

fontsize = 30
NKEYS = 16

tilenames = ['blocks/ore'+str(i)+'.png' for i in range(1,9)] + ['blocks/rock'+str(i)+'.png' for i in range(1,9)]

def get_ticks():
    return(pygame.time.get_ticks())

if not pygame.font: print ('Warning, fonts disabled')
if not pygame.mixer: print ('Warning, sound disabled')

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')

class SpriteMan(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image("dwarf_face.png", -1)
        center = self.rect.center
        self.image = pygame.transform.scale(self.image, ((int)(0.7*(DELTAX+1)), (int)(0.7*(DELTAY+1))))
        self.rect = self.image.get_rect()

class SpriteTile(pygame.sprite.Sprite):
    def __init__(self, img, rect):
        pygame.sprite.Sprite.__init__(self)
        #self.image, self.rect = load_image(filename, -1)
        self.image, self.rect = img, rect
        center = self.rect.center
        self.image = pygame.transform.scale(self.image, (DELTAX+1, DELTAY+1))
        self.rect = self.image.get_rect()
    
    def dig(self, group):
        self.remove(group)


def coord_to_tiles(x, y):
    cx = HSCREEN/2.0 - (HBLOCK/2.0) * DELTAX
    cy = VSCREEN/2.0 - (VBLOCK/2.0) * DELTAY   
    i = (int)((float)(x-cx)/(float)(DELTAX))
    j = (int)((float)(y-cy)/(float)(DELTAY))
    return i, j
    
CX = HSCREEN/2.0 - HBLOCK/2.0 * DELTAX
CY = VSCREEN/2.0 - VBLOCK/2.0 * DELTAY
        
        
class Speedseq():
    def __init__(self):
        self.idx = 0
    def increase_speed(self):
        self.idx += 1
        if self.idx > len(SPEEDSEQ) - 1:
            self.idx = len(SPEEDSEQ) - 1
    
    def decrease_speed(self, nb = 1):
        self.idx -= nb
        if self.idx < 0:
            self.idx = 0
    def reset_speed(self):
        self.idx = 0
    @property
    def speed(self):
        return(SPEEDSEQ[self.idx])

class Hero():
    def __init__(self, board):

        if DEATHMODE == 1:
            print(XSTART, YSTART)
            print( board.SCROLLX,  board.SCROLLY)
            self.x = CX + XSTART*DELTAX + board.SCROLLX
            self.y = CY + YSTART*DELTAY + board.SCROLLY
        else:
            self.x = CX + 10*HBLOCK
            self.y = CY
        
        
        self.vx = 0
        self.vy = 0
        self.speedseq = []
        for i in range(4):
            self.speedseq.append(Speedseq())
        self.sprite = SpriteMan()
        #self.updateposition(board)
        
    def updateposition(self, board):
        
        # scrolling
        if DEATHMODE == 1 and board.playing == True:
            if self.x + board.SCROLLX < SCROLLING_DEATHX:
                print("DEAD")
        
        
        if self.x + board.SCROLLX < SCROLLING_MINX:
            board.scrolling(-(self.x + board.SCROLLX - SCROLLING_MINX), 0)
        
        if self.x + board.SCROLLX > SCROLLING_MAXX:
            board.scrolling(-(self.x + board.SCROLLX - SCROLLING_MAXX), 0)
            
        if self.y + board.SCROLLY < SCROLLING_MINY:
            board.scrolling(0,-(self.y + board.SCROLLY - SCROLLING_MINY))
        
        if self.y + board.SCROLLY > SCROLLING_MAXY:
            board.scrolling(0,-(self.y + board.SCROLLY - SCROLLING_MAXY)) 
        
        self.sprite.rect.center = \
            (self.x + board.SCROLLX, self.y + board.SCROLLY)
    
    def updateposition_nockeck(self, board):
        self.sprite.rect.center = \
            (self.x + board.SCROLLX, self.y + board.SCROLLY)
    
    
    
    def get_speed(self, dx, dy):
        return(self.speedseq[2].speed \
            - self.speedseq[3].speed, \
            + self.speedseq[1].speed \
            - self.speedseq[0].speed )
        
    def accelerate(self, dx, dy):
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
        if dx!=0:
            self.speedseq[2].reset_speed()
            self.speedseq[3].reset_speed()
        if dy!=0:
            self.speedseq[0].reset_speed()
            self.speedseq[1].reset_speed()

    def moving(self, dx, dy):
        self.accelerate(dx, dy)
        deltax, deltay = self.get_speed(dx, dy)
        self.x = self.x + deltax
        self.y = self.y + deltay
    
    def moving_digging(self, dx, dy):
        if dy == -1:
            self.speedseq[0].decrease_speed(5)
        if dy == 1:
            self.speedseq[1].decrease_speed(5)
        if dx == 1:
            self.speedseq[2].decrease_speed(5)
        if dx == -1:
            self.speedseq[3].decrease_speed(5)
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
    
    def empty_hit(self):
    
        # reset combo timer
        self.combo_timer = get_ticks()
        self.in_a_row = 0
        
        # reset combo timer
        if numpy.random.rand() <= PROBA_HIT:
            self.health = self.health - 10 - numpy.random.randint(10)
            return True
        return False
    
    
    def register_dig(self):
        next_timer = get_ticks()
        if self.combo_timer - next_timer < SCORING_ROW:
            self.in_a_row += 1
        else:
            self.in_a_row = 0
        self.combo_timer = next_timer
        if self.in_a_row >= 3:
            return True
        return False

    def increase_deathscroll(self):
        if get_ticks() - self.deathtimer > 1000:
            self.deathscroll += 0.01
            self.deathtimer = get_ticks()
            

class Move():
    #UP, DOWN, RIGHT, LEFT: 273, 274, 275, 276
    def __init__(self):
        self.push = numpy.array([0,0,0,0])
        self.when = numpy.array([1,1,1,1])*LARGE_TIME
    
    def key_up(self, key, hero):
        if not(self.is_a_move(key)):
            return
        self.push[key-273] = 0
        self.when[key-273] = LARGE_TIME
        if key == K_UP or key == K_DOWN:
            hero.stopping(0,1)
        if key == K_LEFT or key == K_RIGHT:
            hero.stopping(1,0)
            
            
        
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
        return(key == K_LEFT or key == K_RIGHT \
        or key == K_UP or key == K_DOWN)


class Sound():
        
    def __init__(self):
        self.digsounds = []
        self.digsounds.append(load_sound("ROCKS1.WAV"))
        self.digsounds.append(load_sound("ROCKS2.WAV"))
        self.digsounds.append(load_sound("ROCKS3.WAV"))
        self.digsounds.append(load_sound("ROCKS4.WAV"))
        self.hitsounds = []
        self.hitsounds.append(load_sound("DIG1.WAV"))
        self.hitsounds.append(load_sound("DIG2.WAV"))
        self.hitsounds.append(load_sound("DIG3.WAV"))
        self.hitsounds.append(load_sound("DIG4.WAV"))
        self.hitsounds.append(load_sound("DIG5.WAV"))
        self.hitsounds.append(load_sound("DIG6.WAV"))
        self.hitsounds.append(load_sound("DIG7.WAV"))
        self.hitsounds.append(load_sound("DIG8.WAV"))
        self.stepsounds = []
        self.stepsounds.append(load_sound("FOOT1A.WAV"))
        self.stepsounds.append(load_sound("FOOT2A.WAV"))
        self.stepsounds.append(load_sound("FOOT3A.WAV"))
        self.stepsounds.append(load_sound("FOOT4A.WAV"))
        self.hurtsounds = []
        self.hurtsounds.append(load_sound("PINBALL.WAV"))
        self.hurtsounds.append(load_sound("punch.wav"))
        self.combosounds = []
        self.combosounds.append(load_sound("WOOO.WAV"))
        self.combosounds.append(load_sound("TNT Barrel.wav"))
        
    
    def play_digsound(self):
        self.digsounds[numpy.random.randint(0,4)].play()
        
    def play_hitsound(self):
        self.hitsounds[numpy.random.randint(0,8)].play()
        
    def play_stepsound(self):
        self.stepsounds[numpy.random.randint(0,4)].play()
        
    def play_hurtsound(self):
        self.hurtsounds[numpy.random.randint(0,2)].play()
    
    def play_combosound(self):
        self.combosounds[numpy.random.randint(0,2)].play()
        

class Board():
    def __init__(self, blocks_loaded, nkeys=NKEYS):
    
        self.blocks_loaded = blocks_loaded
        self.playing = False
        self.SCROLLX = 0
        self.SCROLLY = 0
    
        self.tiles = numpy.random.randint(0, nkeys, size=(VBLOCK,HBLOCK))
        if DEATHMODE == 0:
            self.tiles[0,:] = -1
            self.tiles[-1,:] = -1
            self.tiles[:,0] = -1
            self.tiles[:,-1] = -1
        self.tilesid = numpy.zeros((VBLOCK,HBLOCK))
        
        if DEATHMODE == 1:
            self.tiles[YSTART-5:YSTART+5,XSTART-5:XSTART+5] = -1
        
        
        self.scoring = Scoring()
        
        self.hour = get_ticks()
        self.hero = Hero(self)
        self.sound = Sound()
        self.spritegroup = pygame.sprite.Group()
        self.spritegroup.add(self.hero.sprite)
 
        self.build_blocks_sprites()
        self.place_tiles()
        self.hero.updateposition(self)
        
    def build_blocks_sprites(self):
        self.spritelist = []
        current_id = 0
        for j in range(VBLOCK):
            for i in range(HBLOCK):
                if self.tiles[j,i] != -1:
                    self.tilesid[j,i] = current_id
                    current_id = current_id + 1
                    img, rect = self.blocks_loaded[self.tiles[j,i]]
                    self.spritelist.append(SpriteTile(img, rect))
                        #SpriteTile(tilenames[self.tiles[j,i]]) )
                        
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
            print("Time to circulate! ")
            # This should be optimized: do not recreate ALL sprites but just the last column...
            self.perform_circular_warping()
            
    # used in DEATHMODE
    def perform_circular_warping(self):
        
        self.tiles[:,0:-1] = self.tiles[:,1:]
        self.tiles[:,-1] = numpy.random.randint(0, NKEYS, size=(VBLOCK))
        self.spritegroup.empty()
        self.spritegroup.add(self.hero.sprite)
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
        

        if collision == True and self.tiles[l, k] == -1:
            collision = False
       

        # step in an empty space
        #if self.tiles[j+dy,i+dx] == -1:
        if collision == False:
            self.hero.moving(dx, dy)
            #self.hero.x = self.hero.x + dx
            #self.hero.y = self.hero.y + dy
            self.sound.play_stepsound()
            self.hero.updateposition(self)

        # Attempt to dig
        if collision == True:
        #if self.tiles[j+dy,i+dx] != -1:
            if self.find_match_to_one_tile(k, l, i, j):
                #self.hero.x = self.hero.x + dx
                #self.hero.y = self.hero.y + dy
                self.hero.moving_digging(dx, dy)
                self.hero.updateposition(self)
                if self.scoring.register_dig():
                    print("combo")
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
                if self.tiles[j,i] != -1:
                    dx = i*DELTAX
                    dy = j*DELTAY
                    currentid = self.tilesid[j,i]
                    self.spritelist[currentid].rect.center = \
                        (cx + dx + self.SCROLLX, cy + dy + self.SCROLLY)

    def find_match_to_one_tile(self, i, j, io, jo):
        #reduced view
        imin = io - MATCH_VIEWX if io - MATCH_VIEWX >= 0 else 0
        imax = io + MATCH_VIEWX if io + MATCH_VIEWX < HBLOCK-1 else HBLOCK - 1
        jmin = jo - MATCH_VIEWY if jo - MATCH_VIEWY >= 0 else 0
        jmax = jo + MATCH_VIEWY if jo + MATCH_VIEWY < VBLOCK-1 else HBLOCK - 1
        # position of the tile of interest in the view
        i, j = i - imin, j - jmin
        io, jo = io - imin, jo - jmin
        
        local_tiles = copy.deepcopy(self.tiles[jmin:jmax, imin:imax])
        # Just use a memorized patch if the view is full. Else, search in the square. Can be fixed later or never.
        if jmax-jmin == 2*MATCH_VIEWY and imax-imin == 2*MATCH_VIEWX:
            local_tiles[PATCH == 0] = -2          
        
       
        idx_list = numpy.argwhere(local_tiles == local_tiles[j,i])
        
        list_match = []
        
        for idx in range(idx_list.shape[0]):
            k = idx_list[idx, 1]
            l = idx_list[idx, 0]
            connect = find_connection(i, j, k, l, local_tiles)
            if connect == True and (i != k or j != l):
                list_match.append([k, l])
        
        if list_match == []:
            return False
            
        distances = []
        for pair in list_match:
            distances.append(((i-pair[0])**2.0 + (j-pair[1])**2.0)**0.5)
        
        rank = numpy.argmin(distances)
        k = list_match[rank][0]
        l = list_match[rank][1]
        
        self.group_dig(i+imin, j+jmin)
        self.group_dig(k+imin, l+jmin)
        return True
        
    def group_dig(self,i,j):
        index = self.tilesid[j,i]
        self.spritelist[index].dig(self.spritegroup)
        self.tiles[j,i] = -1

def testing():
    tiles = numpy.random.randint(0,NKEYS,size=(6,6))
    tiles[1,:] = -1
    tiles[1,0] = 5
    
    assert(is_free_cw_angle_from_to(0,1,4,1,tiles))
    assert(is_free_ccw_angle_from_to(0,1,4,1,tiles))
    assert(is_free_cw_angle_from_to(4,1,0,1,tiles))
    assert(is_free_cw_angle_from_to(0,1,4,2,tiles))
    assert(is_free_cw_angle_from_to(0,1,4,3,tiles) == False)
    
    tiles[2,4] = -1
    assert(is_free_cw_angle_from_to(0,1,4,3,tiles))
    
    tiles[:,3] = -1
    
    assert(is_free_cw_angle_from_to(0,1,3,5,tiles))
    assert(is_free_ccw_angle_from_to(0,1,3,5,tiles) == False)

    tiles = numpy.random.randint(0,NKEYS,size=(6,6))
    tiles[:,1] = -1
    assert(is_free_cw_angle_from_to(1,1,1,4,tiles))
    assert(is_free_ccw_angle_from_to(1,1,1,4,tiles))
    assert(is_free_ccw_angle_from_to(1,4,1,1,tiles))


    
def find_connection(i, j, it, jt, tiles):
    #print("searching :", i,j , "  to ", it, jt)
    # Always flip array such that it >= i and jt >= j (LAZY)
    hblock = tiles.shape[1]
    vblock = tiles.shape[0]
    
    if i > it:
        tiles = numpy.flip(tiles, axis=1)
        i,it = hblock-1-i, hblock-1-it
    if j > jt:
        tiles = numpy.flip(tiles, axis=0)
        j,jt = vblock-1-j, vblock-1-jt
    
    
    found = False
    
    if (abs(i-it) == 1 and j==jt) or (abs(j-jt) == 1 and i==it):
        return(True)
       
    if is_free_cw_angle_from_to(i, j, it, jt, tiles) or \
        is_free_ccw_angle_from_to(i, j, it, jt, tiles):
        #print("direct")
        return(True)

    # Bug case of aligned horizontally
    if jt == j:
        if numpy.all(tiles[j,i+1:it] == -1):
            return(True)
        

    # Case left
    il = i - 1
    while (tiles[j,il] == -1):
        if is_free_ccw_angle_from_to(il, j, it, jt, tiles):
            found = True
            break
        il = il - 1
        if il<0:
            break

    
    # Case right
    il = i + 1
    while (tiles[j,il] == -1):
    
        if il <= it:
            if is_free_ccw_angle_from_to(il, j, it, jt, tiles):
                found = True
               # print("ccw right", il,j,it,jt)
                break
        else:
            if is_free_cw_angle_from_to(il, j, it, jt, tiles):
                found = True
               # print("cw right", il,j,it,jt)
                break
        il = il + 1
        if il>hblock-1:
            break
    #if found == True:
     #   print('right')
        
    # Case up
    jl = j - 1
    while (tiles[jl,i] == -1):
        if is_free_cw_angle_from_to(i, jl, it, jt, tiles):
            found = True
            break
        jl = jl - 1
        if jl<0:
            break

        
    # Case down
    jl = j + 1
    while (tiles[jl,i] == -1):
        if jl <= jt:
            if is_free_cw_angle_from_to(i, jl, it, jt, tiles):
                found = True
                break
        else:
            if is_free_ccw_angle_from_to(i, jl, it, jt, tiles):
                found = True
                break
        jl = jl + 1
        if jl>vblock-1:
            break

        
    return(found)
            
    
def is_free_cw_angle_from_to(i, j, it, jt, tiles):
 
 # O>-|    or   O
 #    v         v
 #    X     X-<--
 
    if jt<j:
        print("unexpected in cw")
    if i <= it:
#        trace = numpy.all(tiles[j,i+1:it] == -1) and \
#            numpy.all(tiles[j:jt,it] == -1)
         trace = is_free_horizontal(i+1,it,j,tiles) and \
                is_free_vertical(j+1,jt-1,it,tiles)
            
    else:
        trace = is_free_vertical(j+1,jt,i,tiles) and \
                is_free_horizontal(it+1,i-1,jt,tiles)
#        trace = numpy.all(tiles[j+1:jt+1,i] == -1) and \
#            numpy.all(tiles[jt,it+1:i] == -1)
    
    return(trace)


def is_free_ccw_angle_from_to(i, j, it, jt, tiles):
 
 #     X    or   O
 #     |         v
 # 0->--         -->-X
    if it<i:
        print("unexpected in ccw")
    if jt <= j:
#        trace = numpy.all(tiles[j,i+1:it+1] == -1) and \
#            numpy.all(tiles[jt+1:j,it] == -1)
        trace = is_free_horizontal(i+1,it,j,tiles) and \
                is_free_vertical(jt+1,j-1,it,tiles)
            
    else:
#        trace = numpy.all(tiles[j+1:jt+1,i] == -1) and \
#            numpy.all(tiles[jt,i:it] == -1)
        trace = is_free_vertical(j+1,jt,i,tiles) and \
                is_free_horizontal(i,it-1,jt,tiles)
        
    
    return(trace)
            
def is_free_horizontal(i,it,j,tiles):
    if it<i:
        return True
    return(numpy.all(tiles[j,i:it+1]==-1))
            
def is_free_vertical(j,jt,i,tiles):
    if jt<j:
        return True
    return(numpy.all(tiles[j:jt+1,i]==-1) )



def main():
    """this function is called when the program starts.
       it initializes everything it needs, then runs in
       a loop until the function returns."""
#Initialize Everything
    pygame.init()
    screen = pygame.display.set_mode((HSCREEN, VSCREEN))
    pygame.display.set_caption('Matchit_Digit')
    pygame.mouse.set_visible(0)

#Create The Backgound
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((50, 20, 10))

   
    

#Create font
    if pygame.font:
        font = pygame.font.Font(None, fontsize)
        
#Display The Background
    screen.blit(background, (0, 0))
    pygame.display.flip()

#Prepare Game Objects
    clock = pygame.time.Clock()

    blocks_loaded = [load_image(i) for i in tilenames]
    board = Board(blocks_loaded)
    move = Move()
    
    if DEATHMODE == 1:
        board.scrolling(500,0)
    board.playing = True

#Main Loop
    going = True
    sound_loop = 0
    current_key = -1
    
    while going:
        clock.tick(30)

        move.launch_mem(board)
        
        #Handle Input Events
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
        
        board.scrolling(0,0)
        
        if DEATHMODE == 1:
            board.scoring.increase_deathscroll()
            board.scrolling(-board.scoring.deathscroll,0)
            board.circular_warping()
        
        allsprites.update()

        #Draw Everything
        screen.blit(background, (0, 0))
        board.spritegroup.draw(screen)
        pygame.display.flip()


    pygame.quit()

#Game Over


#this calls the 'main' function when this script is executed
if __name__ == '__main__':
    main()

    
