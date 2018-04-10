from psychopy import logging, prefs
prefs.general['audioLib'] = ['sounddevice']
#logging.console.setLevel(logging.DEBUG)  # get messages about the sound lib as it loads
#from psychopy import sound
#print sound.Sound

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
import target_time_cyclone_log
from target_time_cyclone_parameters import*
from target_time_cyclone_variables import*

#============================
# DEFINE PARADIGM FUNCTIONS
#============================
def instruction_loop(instrs, intro=False):
    image_index = 0
    # displays instructions for current trial type
    # If intro=True, instrs won't be used (can just be '') 
    if instrs!= main_str:
        for instr_str in instrs:
            instr_txt.text = instr_str
            if image_index < 6 and intro:
                instr_pic.image = 'cyclone_pics/{0}'.format(instr_pic_dict[image_index])
                instr_pic.draw()
                image_index += 1
            if not intro:
                instr_pic.image = 'cyclone_pics/{0}'.format(instr_pic_dict[condition])
                instr_pic.draw()
            
            instr_txt.draw()
            adv_screen_txt.draw()
            win.flip()
            instr_key_check()
    else:
        instr_txt.text = instrs
        instr_txt.pos = (0,2)
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        instr_key_check()
        core.wait(post_instr_delay)     # let them prep before hitting them with interval_dur

#===================================================
def instr_key_check(check_time=0.2):
    waiting = True
    while waiting:
        press = event.getKeys(keyList=['escape','q'])
        if press:
            clean_quit()
        (time,btn) = rtbox.secs(check_time)
        if len(btn)>0:
            waiting = False
        core.wait(check_time)
    rtbox.clear()


#===================================================
def moving_ball(block_n, trial_n, training=False):
    # Draw Stimuli
    for circ_xi in range(n_circ-1):# - sum(hidden_pos[covered])):
        target_zone_draw()
        if circ_xi == 0:
            circ_colors[n_circ-1] = (1,1,1)
        if paradigm_type=='ecog' and circ_start[circ_xi] < trigger_dur:
            trigger_rect.draw()
        if circ_xi >= (n_circ - sum(hidden_pos[covered])):
            circ_colors[circ_xi] = (0,0,0)
        else:
            circ_colors[circ_xi] = (1,1,1)      # Turn light on
        circles.colors = circ_colors
        circles.draw()
        if circ_xi==1 and paradigm_type=='eeg':
            win.callOnFlip(port.setData, 1)  # sets just this pin to be high
        win.flip()
        if circ_xi==0:
            trial_start = exp_clock.getTime()
        
        circ_colors[n_circ-1] = (-1,-1,-1)
        circ_colors[circ_xi] = flip_list[circ_xi]  # Turn light back off
        circles.colors = circ_colors
        while exp_clock.getTime() < trial_start + circ_start[circ_xi]:  # wait until this light should turn off
            core.wait(0.001)
    
    # Turn off stimuli for feedback_delay
    target_zone_draw()
    circles.draw()
    if paradigm_type=='eeg':
        win.callOnFlip(port.setData, 0)
    win.flip()
    
#    # Log any responses
#    if not response:
#        response = event.getKeys(keyList=key, timeStamped=trial_clock)  #!!! responses here still tied to flips?
#    if len(response)>0:
#        responses.append(response)
#        if not training:
#            win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block_n,trial_n,response,win.lastFrameT),logging.DATA)
#        else:
#            win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial_n,response,win.lastFrameT),logging.DATA)
#        response = []
    return trial_start


#===================================================
def feedback_fn(block_n, condition, trial_n, trial_start, training=False):
    global training_score
    surp = False
    
    # Check for and process responses
    if use_rtbox:
        (rts, btns) = rtbox.secs()
    else:
        responses = event.getKeys(keyList=[key],timeStamped=exp_clock)
        try:
            btns, rts = zip(*responses)     # unpack [(key1,time1),(key2,time2)] into (key1,key2) and (time1,time2)
        except ValueError:
            btns = []
            rts = []
    
    if len(rts)>0:
        if len(rts)>1:          # Warning if more than one button was pressed
            win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: responses = {2}'.format(
                            block_n, trial_n, rts),logging.WARNING)
        
        rt = rts[0]-trial_start             # take only first response
        btn = btns[0]
        error = rt - interval_dur
        error_angle = error*angle_ratio
        if not training and trial_n in surprise_trials[surp_cnt]:          # Surprise on if not in training and if in list of surprise trials  
            target_zone.setColor('blue')
            resp_marker.setLineColor(None)
            outcome_str = 'SURPRISE!'
            select_surp_sound()
            surp = True
        elif np.abs(error)<tolerances[condition]:             # WIN
            target_zone.setColor('green')
            outcome_str = 'WIN!'
            outcome_sound = win_sound
            win_flag = 0
        else:                                   # LOSS
            target_zone.setColor('red')
            outcome_str = 'LOSE!'
            outcome_sound = loss_sound
            win_flag = 1
        resp_marker.setStart(pol2cart(error_angle+270, loop_radius-resp_marker_width/2))
        resp_marker.setEnd(pol2cart(error_angle+270, loop_radius+resp_marker_width/2))
    else:   # No response detected
        target_zone.setColor('red')
        outcome_str = 'None'
        resp_marker.setLineColor(None)
        # Not adjusting tolerance for this type of trial...
        if not training:
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,-1,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format(block_n,trial_n,win.lastFrameT),logging.INFO)
        else:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,-1,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format('T',trial_n,win.lastFrameT),logging.INFO)
    
    # Present feedback
    win.flip()      # create fixed timing between this flip and sound/draw onsets
#    win.callOnFlip(turn_sound[outcome_str].play)
    if paradigm_type=='eeg': 
        win.callOnFlip(port.setData, 2)
    for frameN in range(feedback_dur * 60): #!!! change to frame_rate variable
        if paradigm_type=='ecog': 
            trigger_rect.draw()
        if frameN == 0:
            turn_sound[outcome_str].play()
        target_zone_draw()                      # Using our defined target_zone_draw, not .draw to have correct visual.  
        resp_marker.draw()
        win.flip()
        if frameN==0:
            print 'just flipped feedback: {0}'.format(exp_clock.getTime()-trial_start)
    win.flip()
    
    if not surp and outcome_str != 'None':
        tolerances[condition]+= tolerance_step[condition][win_flag]      # Update tolerances based on feedback. Needs to be here.   
        if tolerances[condition] > tolerance_lim[0]:                      #!!! Won't work if moved to staircase. Would need new implementation.
            tolerances[condition] = tolerance_lim[0]
        elif tolerances[condition] < tolerance_lim[1]:
            tolerances[condition] = tolerance_lim[1]
        if training and trial_n>=n_fullvis:
            training_score[condition] += point_fn[win_flag]
            
        elif not training:
            points[block_n]+= point_fn[win_flag]
        if training:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,rt,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} SOUND = {2} feedback start: FRAME TIME = {3}'.format('T', trial_n, outcome_sound, win.lastFrameT),logging.DATA)
        else:
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,rt,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} SOUND = {2} feedback start: FRAME TIME = {3}'.format(block_n, trial_n, outcome_sound, win.lastFrameT),logging.DATA)
            
    resp_marker.setLineColor('black')
    target_zone.setColor('dimgrey')
    while exp_clock.getTime() < trial_start + trial_dur:
        for press in event.getKeys(keyList=['escape','q']):
            if press:
                clean_quit()


#===================================================
def staircase(condition): 
    target_origin[condition] = 180 - (tolerances[condition] * angle_ratio)
    target_upper_bound[condition] =  2*tolerances[condition]*angle_ratio
    target_zone.visibleWedge = [0, target_upper_bound[condition]]
    target_zone.ori = target_origin[condition]


#===================================================
def block_break(block_n, training=False): 
    point_calc(block_n)
    # If not the last block, print feedback
    if block_n<n_blocks*len(conditions)-1:
        instr_txt.text = break_str.format(n_blocks*len(conditions)-block_n-1,break_min_dur)
        instr_txt.draw()
        win.flip()
        core.wait(break_min_dur)
        block_point_txt.draw()
        total_point_txt.draw()
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        instr_key_check()


#===============================================
def point_calc(block_n):
    block_point_txt.text = block_point_str.format(block_n+1,points[block_n])
    if points[block_n]>=0:
        block_point_txt.color = 'green'
    else:
        block_point_txt.color = 'red'
    total_point_txt.text = total_point_str.format(np.sum(points))
    if np.sum(points)>=0:
        total_point_txt.color = 'green'
    else:
        total_point_txt.color = 'red'
    block_point_txt.draw()
    total_point_txt.draw()

#===================================================
def score_instr():
    global training_score
    score_demo_txt.text = score_demo_str.format(training_score[condition])
    total_point_txt.text = total_point_str.format(np.sum(training_score.values()))
    if training_score[condition] > 0:
        score_demo_txt.color = 'green'
        total_point_txt.color = 'green'
    
    if training_score[condition] <= 0:
        score_demo_txt.color = 'red'
        total_point_txt.color = 'red'
    
    score_demo_txt.draw()
    total_point_txt.draw()
    if trial_n==n_fullvis+n_training-1:
        point_instr_txt.draw()
    adv_screen_txt.draw()
    win.flip()
    instr_key_check()


#===================================================
def target_zone_draw():
    target_zone.draw()
    target_zone_cover.draw()
    sockets.draw()
    circles.draw()

#===================================================
def select_surp_sound():
    sound_type = np.random.choice(block_sounds.keys())                      # Selects the subfolder to draw sounds from (ie. 'breaks').
    sound_file = block_sounds[sound_type][surp_sound_index]                 # Selects the specific wav file from the subfolder.
    turn_sound['SURPRISE!'] = sound.Sound(value= sound_file, sampleRate=44100, secs=0.8)
    win.logOnFlip('B{0}_T{1} SOUND = {2}   feedback start: FRAME TIME = {3}'.format(block_n, trial_n, sound_file, win.lastFrameT),logging.DATA)
    block_sounds.pop(sound_type)

#===================================================
def clean_quit():
#    os.system("sudo /home/knight_lab/Startup_Scripts/python_priority_rush_off.sh")     # If using core.rush in Linux
    rtbox.close()
    win.close()
    core.quit()


#============================================================
# INSTRUCTIONS
#============================================================
if paradigm_type=='eeg':
   port = parallel.ParallelPort(address=53504)

# Initialize RT Button Box
if use_rtbox:
    rtbox = RTBox.RTBox(host_clock=exp_clock.getTime)
else:
    rtbox = RTBox.RTBox(boxID='')#,host_clock=exp_clock.getTime)
# rt_clock_ratio = rtbox.clockRatio()           # get ratio between system and rtbox clocks, maybe not necessary
# win.logOnFlip('rtbox_clock_ratio = '+str(rt_clock_ratio), logging.DATA)
rtbox.buttonNames([key, key, key, key])    # make all 4 buttons have same name as the key variable
rtbox.disable('all')
rtbox.enable('press')
rtbox.clear()

welcome_txt.draw()
adv_screen_txt.draw()
win.flip()
instr_key_check()
instruction_loop(instr_strs, intro=True)
win.flip()

#============================================================
# TRAINING
#============================================================
if paradigm_type=='eeg':
    port.setData(0) # sets all pins low
print 'Using %s(with %s) for sounds' % (sound.audioLib, sound.audioDriver)

for trial_n in range(n_fullvis+2*n_training):
    #========================================================
    # Initialize Trial
    if trial_n < n_fullvis:                  # Examples w/o window
        covered = False
    else:
        covered = True
    if trial_n < n_fullvis+n_training:       # Easy Training
        condition = 'easy'
    else:                                   # Hard Training
        condition = 'hard'
        
    win.logOnFlip('TRAINING T{0}: window={1}; condition={2}'.format(trial_n,covered,condition),logging.INFO)
    event.clearEvents()
    rtbox.clear()
    surp_cnt = 0
    outcome_str = ''
    target_zone.visibleWedge = [0, target_upper_bound[condition]]
    target_zone.ori = target_origin[condition]
    if covered:
        circ_colors = [i for i in circ_cover_list]
        circles.colors = circ_colors
    fill_list = re_fill_color[covered]
    flip_list = re_flip_color[covered]
        
    # Instructions
    if (trial_n==n_fullvis) or (trial_n==n_fullvis+n_training):                    # First Easy/Hard Training
        instruction_loop(train_str[condition])
    
    #========================================================
    # Set Trial Timing
    win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial_n,win.lastFrameT),logging.INFO)

    #========================================================
    # Moving Ball
    trial_start = moving_ball(None, trial_n, training=True)
    
    #========================================================
    # Feedback Delay- wait until 1.5 frames before desired feedback onset
    while exp_clock.getTime() < trial_start + trial_dur - feedback_dur - 1/frame_rate:
        core.wait(0.001)
    
    #========================================================
    # Feedback
    print 'about to call calc_feedback; time into trial =  {0}'.format(exp_clock.getTime()-trial_start) #!!! remove after testing
    feedback_fn(None, condition, trial_n, trial_start, training=True)
    
    #========================================================
    # ITI
    ITI = np.max(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
    win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format('T',trial_n,ITI,win.lastFrameT),logging.INFO)
    
    if paradigm_type=='eeg':
        win.callOnFlip(port.setData, 0)
    win.flip()
    
    # Staircase Tolerance
    staircase(condition)
    while exp_clock.getTime() < trial_start + trial_dur + ITI:
        for press in event.getKeys(keyList=['escape','q']):
            if press:
                clean_quit()
    if (trial_n==n_fullvis+n_training-1) or (trial_n==n_fullvis+2*n_training-1):    #Score instructions with score after easy training
        score_instr()


#============================================================
# EXPERIMENT
#============================================================
instruction_loop(main_str)                    # Main instruction call 
# Constant Reward Function (start awarding points)
outcome_win.text = '+{0}'.format(point_fn[0])
outcome_loss.text = '{0}'.format(point_fn[1])
for block_n, block_type in enumerate(block_order):
    block_sounds = surprise_sounds.copy()
    surp_sound_index = 0
    condition = conditions[block_type]
    target_zone.visibleWedge = [0, target_upper_bound[condition]]
    target_zone.ori = target_origin[condition]
    block_start_txt.text = block_start_str.format(block_n+1, n_blocks*len(conditions), condition)
    block_start_txt.draw()
    win.logOnFlip('B{0} ({1}) Start Text: FRAMETIME = {2}'.format(block_n,condition,win.lastFrameT),logging.INFO)
    win.flip()
    core.wait(block_start_dur)
    win.flip()
    core.wait(post_instr_delay)                                         # Delay so they aren't caught off guard
    
    for trial_n in range(n_trials):
        #========================================================
        # Initialize Trial
        event.clearEvents()
        rtbox.clear()
        
        #========================================================
        # Set Trial Timing
        
        #========================================================
        # Moving Ball
        trial_start = moving_ball(block_n, trial_n, training=False)
        
        #========================================================
        # Feedback Delay
        while exp_clock.getTime() < trial_start + trial_dur - feedback_dur - 1/frame_rate:
            core.wait(0.001)
        
        #========================================================
        # Feedback
        print 'about to call calc_feedback; time into trial =  {0}'.format(exp_clock.getTime()-trial_start)
        feedback_fn(block_n, condition, trial_n, trial_start, False)
        
        #========================================================
        # ITI
        ITI = random.choice(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
        win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format(block_n,trial_n,ITI,win.lastFrameT),logging.INFO)
        
        if paradigm_type=='eeg':
            win.callOnFlip(port.setData, 0)
        win.flip()
        staircase(condition)
        while exp_clock.getTime() < trial_start + trial_dur + ITI:#!!!feedback_end + ITI:
            for press in event.getKeys(keyList=['escape','q']):
                if press:
                    clean_quit()
    
    #========================================================
    # Break Between Blocks
    surp_cnt += 1
    surp_sound_index += 1 
    block_break(block_n)

endgame_txt.draw()
win.flip()
core.wait(end_screen_dur)

clean_quit()
