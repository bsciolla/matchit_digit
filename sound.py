import os
import pygame
import numpy

main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, 'data')


def load_sound(name, volume = 1.0):
    class NoneSound:
        def play(self): pass
    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()
    fullname = os.path.join(data_dir, name)
    try:
        sound = pygame.mixer.Sound(fullname)
    except pygame.error:
        print('Cannot load sound: %s' % fullname)
        raise SystemExit(str(geterror()))
    sound.set_volume(volume)
    return sound



class Sound():

    def __init__(self):
        self.digsounds = []
        self.digsounds.append(load_sound("ROCKS1.WAV",0.4))
        self.digsounds.append(load_sound("ROCKS2.WAV",0.4))
        self.digsounds.append(load_sound("ROCKS3.WAV",0.4))
        self.digsounds.append(load_sound("ROCKS4.WAV",0.4))
        self.hitsounds = []
        self.hitsounds.append(load_sound("DIG1.WAV",0.4))
        self.hitsounds.append(load_sound("DIG2.WAV",0.4))
        self.hitsounds.append(load_sound("DIG3.WAV",0.4))
        self.hitsounds.append(load_sound("DIG4.WAV",0.4))
        self.hitsounds.append(load_sound("DIG5.WAV",0.4))
        self.hitsounds.append(load_sound("DIG6.WAV",0.4))
        self.hitsounds.append(load_sound("DIG7.WAV",0.4))
        self.hitsounds.append(load_sound("DIG8.WAV",0.4))
        self.stepsounds = []
        self.stepsounds.append(load_sound("FOOT1A.WAV",0.2))
        self.stepsounds.append(load_sound("FOOT2A.WAV",0.2))
        self.stepsounds.append(load_sound("FOOT3A.WAV",0.2))
        self.stepsounds.append(load_sound("FOOT4A.WAV",0.2))
        self.hurtsounds = []
        self.hurtsounds.append(load_sound("PINBALL.WAV",0.4))
        self.hurtsounds.append(load_sound("punch.wav",0.4))
        self.combosounds = []
        # self.combosounds.append(load_sound("WOOO.WAV"))
        self.combosounds.append(load_sound("TNT Barrel.wav"))
        self.out_of_timesound = load_sound("Trekker2.wav")

    def play_digsound(self):
        self.digsounds[numpy.random.randint(0, 4)].play()

    def play_hitsound(self):
        self.hitsounds[numpy.random.randint(0, 8)].play()

    def play_stepsound(self):
        if numpy.random.randint(0, 9) == 0:
            self.stepsounds[numpy.random.randint(0, 4)].play()

    def play_hurtsound(self):
        self.hurtsounds[numpy.random.randint(0, 2)].play()

    def play_combosound(self):
        self.combosounds[numpy.random.randint(0, 1)].play()

    def play_outoftimesound(self):
        self.out_of_timesound.play()

