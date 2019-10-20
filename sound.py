import os
import pygame
import numpy
from globals import SOUND_VOLUME

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
        self.digsounds.append(load_sound("ROCKS1.WAV",0.4*SOUND_VOLUME))
        self.digsounds.append(load_sound("ROCKS2.WAV",0.4*SOUND_VOLUME))
        self.digsounds.append(load_sound("ROCKS3.WAV",0.4*SOUND_VOLUME))
        self.digsounds.append(load_sound("ROCKS4.WAV",0.4*SOUND_VOLUME))
        self.hitsounds = []
        self.hitsounds.append(load_sound("DIG1.WAV",0.4*SOUND_VOLUME))
        self.hitsounds.append(load_sound("DIG2.WAV",0.4*SOUND_VOLUME))
        self.hitsounds.append(load_sound("DIG3.WAV",0.4*SOUND_VOLUME))
        self.hitsounds.append(load_sound("DIG4.WAV",0.4*SOUND_VOLUME))
        self.hitsounds.append(load_sound("DIG5.WAV",0.4*SOUND_VOLUME))
        self.hitsounds.append(load_sound("DIG6.WAV",0.4*SOUND_VOLUME))
        self.hitsounds.append(load_sound("DIG7.WAV",0.4*SOUND_VOLUME))
        self.hitsounds.append(load_sound("DIG8.WAV",0.4*SOUND_VOLUME))
        self.stepsounds = []
        self.stepsounds.append(load_sound("FOOT1A.WAV",0.2*SOUND_VOLUME))
        self.stepsounds.append(load_sound("FOOT2A.WAV",0.2*SOUND_VOLUME))
        self.stepsounds.append(load_sound("FOOT3A.WAV",0.2*SOUND_VOLUME))
        self.stepsounds.append(load_sound("FOOT4A.WAV",0.2*SOUND_VOLUME))
        self.hurtsounds = []
        self.hurtsounds.append(load_sound("PINBALL.WAV",0.4*SOUND_VOLUME))
        self.hurtsounds.append(load_sound("punch.wav",0.4*SOUND_VOLUME))
        self.combosounds = []
        self.combosounds.append(load_sound("Barrelbreak.wav",SOUND_VOLUME))
        self.combosounds.append(load_sound("TNT Barrel.wav",SOUND_VOLUME))
        self.out_of_timesounds = []
        self.out_of_timesounds.append(load_sound("Trekker.wav",SOUND_VOLUME))
        self.out_of_timesounds.append(load_sound("Trekker2.wav",SOUND_VOLUME))
        self.youpiesounds = []
        self.youpiesounds.append(load_sound("Youpee.wav",0.4*SOUND_VOLUME))
        self.youpiesounds.append(load_sound("OMerveille.wav",0.4*SOUND_VOLUME))
        self.combostraightsounds = []
        self.combostraightsounds.append(load_sound("Groovy.wav",0.4*SOUND_VOLUME))
        self.combostraightsounds.append(load_sound("Giggle.wav",0.4*SOUND_VOLUME))
        self.loselifesounds = []
        self.loselifesounds.append(load_sound("Euargh.wav",0.2*SOUND_VOLUME))
        self.loselifesounds.append(load_sound("Zap.wav",0.4*SOUND_VOLUME))


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
        self.combosounds[numpy.random.randint(0, 2)].play()

    def play_outoftimesound(self):
        self.out_of_timesounds[numpy.random.randint(0, 2)].play()

    def play_youpiesound(self):
        self.youpiesounds[numpy.random.randint(0, 2)].play()

    def play_loselifesound(self):
        self.loselifesounds[numpy.random.randint(0, 2)].play()

    def play_combostraightsound(self):
        self.combostraightsounds[numpy.random.randint(0, 2)].play()

