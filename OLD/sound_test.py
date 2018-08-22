from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
prefs.general['audioDriver'] = [u'jack']
from psychopy import  sound, event 

import sounddevice as sd

win_sound = sound.Sound(value='paradigm_sounds/new_win_sound.wav', sampleRate=44100, secs=.8, blockSize=2048, stereo=True)
win_sound.setVolume(0.8) 

#while not event.getKeys():
win_sound.play()  