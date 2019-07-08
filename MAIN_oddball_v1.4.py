from psychopy import logging, prefs
prefs.general['audioLib'] = ['sounddevice']
#logging.console.setLevel(logging.DEBUG)  # get messages about the sound lib as it loads

from psychopy import visual, event, core, gui, data, parallel, sound
from psychopy.tools.coordinatetools import pol2cart
import sys, os; sys.path.append(os.getcwd())    # necessary to get RTBox.py

import numpy as np
import math, time, random, copy
import RTBox
random.seed()
core.wait(0.5)      # give the system time to settle
#os.system("sudo /home/knight_lab/Startup_Scripts/python_priority_rush_on.sh")    # to enable core.rush on Linux
#core.rush(True)     # might give psychopy higher priority in the system (maybe...)

#============================================================
# SET UP LOG FILE, SELECT PARAMETERS, & INITIALIZE VARAIBLES
#============================================================
import oddball_log
from oddball_parameters import*
from oddball_variables import*
print 'Using %s(with %s) for audioLib(with audioDriver)' % (sound.audioLib, sound.audioDriver)

#============================
# DEFINE PARADIGM FUNCTIONS
#============================
def instruction_loop(instrs, instrp, intro=False):
    # Display instructions for current trial type
    #   instrs is list of strings
    #   instrp is list of names of .jpg files
    for instr_ix, instr_str in enumerate(instrs):
        instr_txt.text = instr_str
        instr_txt.draw()
        if intro and len(instrp[instr_ix])>0:
            if instrp[instr_ix]=='combo':
                for ix in range(len(conditions)):
                    instr_summ_imgs[ix].draw()
                    instr_condlab_txts[ix].draw()
                instr_resp_txt.draw()
            else:
                instr_img.image = 'cyclone_pics/{0}'.format(instrp[instr_ix])
                instr_img.draw()
        if intro and len(instr_sound_names[instr_ix])>0:
            instr_sound = sound.Sound(value=instr_sound_names[instr_ix], sampleRate=sound_srate,
                            blockSize=block_szs[0], secs=stim_dur, stereo=1, volume=volumes[0])
            win.callOnFlip(instr_sound.play)
        adv_screen_txt.draw()
        win.flip()
        instr_key_check()


#===================================================
def instr_key_check(check_time=0.2):
    if use_rtbox:
        (adv_time, adv) = rtbox.secs()
        while adv == [] or adv[0] not in [key, 'escape', 'q']:
            (adv_time, adv) = rtbox.secs()
            if adv == []:
                adv = event.getKeys(keyList=[key, 'escape', 'q'])
            core.wait(check_time)
    else:
        adv = event.waitKeys(keyList=[key, 'escape', 'q'])
    if adv[0] in ['escape','q']:
        clean_quit()
    core.wait(check_time)
    rtbox.clear()

#===================================================
def present_stim(trial_type, next_trial_start):
    # Set visual stimulus
    target_zone.setColor(target_zone_colors[v_idx[trial_type]])
    
    # Set Sound
    if conditions[trial_type]=='tar':
        sound_name = tar_name
        block_sz = block_szs[0]
        volume = volumes[0]
    elif conditions[trial_type]=='std':
        sound_name = std_name
        block_sz = block_szs[0]
        volume = volumes[0]
    else:                       # Oddball
        sound_name = odd_names[odd_idx.pop()]
        block_sz = block_szs[1]
        volume = volumes[1]
    play_sound = sound.Sound(value=sound_name, sampleRate=sound_srate, blockSize=block_sz,
                            secs=stim_dur, stereo=1, volume=volume)
    
    # Send trigger, set up sound
    if paradigm_type=='eeg':
        win.callOnFlip(port.setData, 1)  # sets just this pin to be high
        sound_played = False
    else:
        win.callOnFlip(play_sound.play)
        sound_played = True
    
    # Present stimuli
    for frameN in range(int(round(stim_dur * 60))): #assuming frame_rate is close enough it would round to 60 (this must be an int)
        # Draw visual stimuli
        target_zone_draw()
        if paradigm_type=='ecog':
            trigger_rect.draw()
    
        # Wait until 1.5 frames before desired presentation time, then create fixed timing between this flip and sound/draw onsets
        if frameN==0:
            while exp_clock.getTime() < next_trial_start - 0.5/frame_rate:
                # Hard coded delay for EEG:
                if not sound_played and exp_clock.getTime() > next_trial_start - 0.16:
                    play_sound.play()
                    sound_played = True
                core.wait(0.00002)
        win.flip()
        if frameN==0:
            trial_start = exp_clock.getTime()
    
    # Turn off stimuli
    if paradigm_type=='eeg':
        win.callOnFlip(port.setData, 0)
    win.flip()
    
    return trial_start

#===================================================
def check_resp(block_n, trial_n, block_score, training=False):
    if training:
        condition = conditions[train_cond_n[trial_n]]
    else:
        condition = conditions[block_cond_n[block_n][trial_n]]
    # Check for responses
    if use_rtbox:
        (rts, btns) = rtbox.secs()
    else:
        responses = event.getKeys(keyList=key,timeStamped=exp_clock)
        try:
            btns, rts = zip(*responses)     # unpack [(key1,time1),(key2,time2)] into (key1,key2) and (time1,time2)
        except ValueError:
            btns = []
            rts = []
    
    # Process responses
    if len(rts)>0:
        if len(rts)>1:          # Warning if more than one button was pressed
            win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: responses = {2}'.format(
                            block_n, trial_n, rts),logging.WARNING)
        rt = rts[0]-trial_start             # take only first response
        btn = btns[0]
        if btn==key and condition=='tar':             # WIN
            outcome_str = 'correct'
            block_score += point_amt
        else:                                   # LOSS
            outcome_str = 'incorrect'
            # block_score -= point_amt  # decided not to penalize misses
    else:   # No response detected
        outcome_str = 'none'
        rt=-1
    
    win.logOnFlip('B{0}_T{1} responses/times = {2} / {3}'.format(block_n, trial_n, btns, rts),logging.DATA)
    win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,rt,condition),logging.DATA)
    
    return block_score


#===================================================
def block_break(block_n, block_score, total_score, training=False):
    win.logOnFlip('B{0} block_score = {1}; total_score = {2}'.format(block_n,block_score,total_score),logging.DATA)
    if training:
        block_point_txt.text = score_demo_str.format(block_score)
        # Print point training string, not total score
        instr_txt.text = point_instr_str
    else:
        block_point_txt.text = block_point_str.format(block_n+1,block_score)
        total_score += block_score
        total_point_txt.text = total_point_str.format(total_score)
        total_point_txt.draw()
        if total_score >= 0:
            total_point_txt.color = 'green'
        else:
            total_point_txt.color = 'red'
    if block_score >= 0:
        block_point_txt.color = 'green'
    else:
        block_point_txt.color = 'red'
    block_point_txt.draw()
    
    # If not the last block, print feedback
    if training:
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        instr_key_check()
    elif block_n != len(block_order)-1:
        # Draw score and wait...
        instr_txt.text = break_str.format(len(block_order)-block_n-1,break_min_dur)
        instr_txt.draw()
        win.flip()
        core.wait(break_min_dur)
        # Draw score and allow advance
        instr_txt.draw()
        block_point_txt.draw()
        total_point_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        instr_key_check()
    
    return total_score


#===================================================
def target_zone_draw():
    target_zone.draw()
    target_zone_cover.draw()
    sockets.draw()
    circles.draw()


#===================================================
def pause_check(block_n, trial_n, training=False):
    for press in event.getKeys(keyList=['escape','q', 'p']):
        if press in ['p']:
            pause_txt.draw()
            win.logOnFlip('PAUSE STARTED: B{0}_T{1}, TIME = {2}'.format(block_n, trial_n, exp_clock.getTime()),logging.DATA)
            win.flip()
            event.waitKeys(keyList=['p'])
            win.logOnFlip('PAUSE ENDED: B{0}_T{1}, TIME = {2}'.format(block_n, trial_n, exp_clock.getTime()),logging.DATA)
            core.wait(block_start_dur)
        else:
            clean_quit()


#===================================================
def clean_quit():
#    os.system("sudo /home/knight_lab/Startup_Scripts/python_priority_rush_off.sh")     # If using core.rush in Linux
    rtbox.close()
    win.close()
    if paradigm_type=='eeg':
        port.setData(255)   # stop EEG recording
    core.quit()


#============================================================
# INSTRUCTIONS
#============================================================
# Initialize RT Button Box
if use_rtbox:
    rtbox = RTBox.RTBox()
    rtbox.hostClock(exp_clock.getTime)
else:
    rtbox = RTBox.RTBox(boxID='')#,host_clock=exp_clock.getTime)
# rt_clock_ratio = rtbox.clockRatio()           # get ratio between system and rtbox clocks, maybe not necessary
# win.logOnFlip('rtbox_clock_ratio = '+str(rt_clock_ratio), logging.DATA)
rtbox.buttonNames([key, key, key, key])
rtbox.disable('all')
rtbox.enable('press')
rtbox.clear()

# Start recording
if paradigm_type=='ecog':
    # ECoG Photodiode flicker sequence to signal start of data block
    for flick in range(n_flicker):
        trigger_rect.draw()
        win.flip()
        core.wait(flicker_dur)
        win.flip()
        core.wait(flicker_dur)
        if flick%flicker_brk == flicker_brk-1:
            core.wait(flicker_dur*2)
else:
    # EEG trigger to start recording
    port = parallel.ParallelPort(address=53504)
    port.setData(254) # start BioSemi recording
    core.wait(1)      # biosemi needs a pause to read the start trigger
    port.setData(0) # sets all pins low

# Draw initial instructions
instruction_loop(instr_strs, instr_pic_names, intro=True)
win.flip()
next_trial_start = exp_clock.getTime() + post_instr_delay
total_score = 0
block_score = 0

#============================================================
# TRAINING
#============================================================
if paradigm_type=='eeg':
    port.setData(0) # sets all pins low

for trial_n in range(n_training):
    #========================================================
    # Initialize Trial
    event.clearEvents()
    rtbox.clear()
    
    #========================================================
    # Present stimuli
    trial_start = present_stim(train_cond_n[trial_n], next_trial_start)
    iti = np.random.choice(ITIs)
    next_trial_start = trial_start + stim_dur + iti
    win.logOnFlip('B{0}_T{1} condition = {2}; onset = {3}; ITI = {4}'.format(
                    'T',trial_n,conditions[train_cond_n[trial_n]],trial_start,iti),logging.DATA)
    
    #========================================================
    # Wait until end of trial to check for responses
    while exp_clock.getTime() < next_trial_start - resp_proc_dur:
        pause_check('T', trial_n, training=True)
    
    #========================================================
    # Get responses
    block_score = check_resp('T', trial_n, block_score, training=True)

# Present Score feedback
total_score = block_break('T', block_score, total_score, training=True)

#============================================================
# EXPERIMENT
#============================================================
instruction_loop(main_str, [''])
for block_n, block_type in enumerate(block_order[starting_block-1:],starting_block-1):
    block_start_txt.text = block_start_str.format(block_n+1, len(block_order))
    block_start_txt.draw()
    win.logOnFlip('B{0} Start Text: TIME = {1}'.format(block_n,exp_clock.getTime()),logging.DATA)
    win.flip()
    core.wait(block_start_dur)
    win.flip()
    next_trial_start = exp_clock.getTime() + post_instr_delay
    block_score = 0
    
    for trial_n in range(n_trials):
        #========================================================
        # Initialize Trial
        event.clearEvents()
        rtbox.clear()
        
        #========================================================
        # Present stimuli
        trial_start = present_stim(block_cond_n[block_n][trial_n], next_trial_start)
        iti = np.random.choice(ITIs)
        next_trial_start = trial_start + stim_dur + iti
        win.logOnFlip('B{0}_T{1} condition = {2}; onset = {3}; ITI = {4}'.format(
                    block_n,trial_n,conditions[block_cond_n[block_n][trial_n]],trial_start,iti),logging.DATA)
        
        #========================================================
        # Wait until end of trial to check for responses
        while exp_clock.getTime() < next_trial_start - resp_proc_dur:
            pause_check(block_n, trial_n)
        
        #========================================================
        # Get responses
        block_score = check_resp(block_n, trial_n, block_score)
    
    #========================================================
    # Break Between Blocks
    total_score = block_break(block_n, block_score, total_score)

endgame_txt.draw()
win.flip()
core.wait(end_screen_dur)

clean_quit()
