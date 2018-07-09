# Minimal script to reproduce buzzing sound
from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
from psychopy import sound, core
print sound.Sound
print sound.__file__

block_sz = 512#2048
win_sound = sound.Sound(value='paradigm_sounds/new_loss_sound.wav', sampleRate=44100, blockSize=block_sz, secs=0.8, stereo=True)
print 'sound initialized! waiting 1 sec...'
core.wait(1)

for i in range(3):
    print i
    if i==1:
        win_sound.play()
    core.wait(1)