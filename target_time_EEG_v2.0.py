# target_time_EEG_v2.0
paradigm_version = '2.0'
# 2.0: functions brought back into main script
# 1.9.2.test: modularized parameters, log, and variables to cut down on file length 
# 1.9.2: different trigger codes for stim (1) and feedback (2); stim trigger lasts until feedback_delay; adv_scr_txt moved down to avoid overlap
# 1.9.1: EEG triggers actually work after troubleshooting on 135D (must use WinXP)
# 1.9: EEG triggers; no photodiode, screen size 
# 1.8.5: ITIs=[0.2,0.4,0.7,1.0]; feedback_dur=0.8; log:(paradigm_version,n_fullvis,n_training);
#   Adi-prevent 3 blocks of same type in a row; quit on title screen
# 1.8.4: response marker is wider; block left during break; fixed resp_marker_width bug
# 1.8.3: ITIs=[0.3,0.65,1]; four blocks per condition; break min = 30s; advance option only appears after break_min_dur;
#       added total blocks to block start screen (e.g., 1/8); changed speed/distance instructions to be simpler (it's always the same time)
# 1.8.2: 15 training trials, tolerance_init = {'easy': 0.125, 'hard': 0.05}, block order = e e h h; fix block_order bug
# 1.8.1: Optimized for ECoG Laptops
# 1.8 fixes:
#   -more clear instructions
#   -screen delay following block start for preparation
#   -fixed quit checks (stopped calling responses "key")
#   -bullseye color switch, block score +1 correction
# 1.7 many fixes:
#   -cuts down the MASSIVE log file (hopefully avoids crashes)
#   -tolerance limits, adjustments during training, adjust after logging, center bullseye = tolerance min
#   -display point total after blocks (previous block and total)
#   -more spaced out ITIs to reduce rhythm
#   -wider response marker, breaks after all blocks (maybe v1.6 too?), mention time out on break instructions
# 1.6 implements logging and saving the data
# 1.5 implements block structure to whole experiment, instructions, training (covered=False examples)
# 1.4 got skipped (handler nonsense)
# 1.3 added photodiode trigger rectangle, basic logging
#   (incomplete logging, to be finished once trail/exp ahndelres are done)
# 1.2 has more comments than 1.1
# implements staircase adjustments to target intervals
# dict for all variables changing across trial types (easy/hard)

from psychopy import visual, event, core, gui, logging, data
from psychopy import parallel
import numpy as np
import math, time, random, shelve   #!!! WTF is shelve?
#from psychopy.tools.coordinatetools import pol2cart
random.seed()
core.wait(0.5)      # give the system time to settle
core.rush(True)     # might give psychopy higher priority in the system (maybe...)
exp_datetime = time.strftime("%Y%m%d%H%M%S")
paradigm_name = 'target_time'

#!!! Ideal order: log to get the param name, param module to pull the right version, then varaibles to use that to set everything up
#============================================================
# EXPERIMENT PARAMETERS
#============================================================
from target_time_EEG_parameters import*
#============================================================
# SET UP LOG FILE
#============================================================
import target_time_EEG_log


#============================================================
# SET EXPERIMENTAL VARIABLES
#============================================================
from target_time_EEG_variables import*
#============================
# DEFINE PARADIGM FUNCTIONS
#============================
#==============================================
# instruction_loop 
# displays instructions for current trial type
#==============================================

def instruction_loop(instrs, intro=False):#instr_strs=instr_strs, key=key):
    # If intro=True, instrs won't be used (can just be '') 
    if intro:
        for instr_str in instr_strs:
            instr_txt.text = instr_str
            instr_txt.draw()
            adv_screen_txt.draw()
            win.flip()
            # !!! place for key resp loop
            adv = event.waitKeys(keyList=[key, 'escape', 'q'])
            # !!! delete this?: `print adv`
            if adv[0] in ['escape','q']:
                win.close()
                core.quit()
    else:
        instr_txt.text = instrs
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        # !!! place for key resp loop
        adv = event.waitKeys(keyList=[key, 'escape', 'q'])
        if adv[0] in ['escape','q']:
            win.close()
            core.quit()
        core.wait(post_instr_delay)     # let them prep before hitting them with interval_dur
        
#============================       
# Trial timer function
#============================

def set_trial_timing(block_n, trial_type, trial_n, tolerances, training=False):#, trial_clock=trial_clock, interval_dur=interval_dur, feedback_delay=feedback_delay, feedback_dur=feedback_dur, ITIs=ITIs):
    # for training mode, input block_n=None
    # !!! can we get rid of train? If so, drop loop below
    trial_clock.reset()
    trial_start = trial_clock.getTime()
    target_time = trial_start + interval_dur
    target_tlim = [target_time-tolerances[trial_type], target_time+tolerances[trial_type]]
    feedback_start = target_time + feedback_delay
    feedback_end = feedback_start + feedback_dur
    ITI = random.choice(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
    if training:   # !!! do we want to get rid of this and make training and block logging uniform style?
        win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial_n,win.lastFrameT),logging.INFO)
    else:
        win.logOnFlip('B{0}_T{1} start: FRAME TIME = {2}'.format(block_n,trial_n,win.lastFrameT),logging.INFO)

#===========================
# Moving ball function
#===========================

def moving_ball(block_n=None, trial_n=None, training=False):#bullseye=None, covered=None, n_int_flips=n_int_flips, window=None, responses=None, trial_clock=trial_clock, key=key, win=win, 
    for pos_ix in range(n_int_flips-sum(hidden_pos[covered])):
        # Drawing Order (back-to-front): (outlines?), tower, window, ball, bullseye 
        tower.draw() #!!! can become tower_draw_fn
        window.draw()
        for eye in reversed(bullseye):  #draw them all in reverse order
            eye.draw()
        balls[pos_ix].draw()
        #if trial_clock.getTime() < trigger_dur:
            #trigger_rect.draw()
        win.flip()
    #            if pos_ix==1:
    #                port.setData(1)  # sets just this pin to be high
        response = event.getKeys(keyList=key, timeStamped=trial_clock)  #!!! responses here still tied to flips?
        if len(response)>0:
            responses.append(response)
            if not training:
                win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block_n,trial_n,response,win.lastFrameT),logging.DATA)
            else:
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial_n,response,win.lastFrameT),logging.DATA)
            response = []
        
#============================
#  Feedback Delay 
#============================
#!!! start back here
def feedback_delay_func(bullseye=None, responses=None, block_n=None, window=None, trial_clock=trial_clock, trial_start=None, key=key, trial_n=None, training=False, interval_dur=interval_dur, feedback_start=None, feedback_delay=feedback_delay):
    tower.draw() #!!! can become tower_draw_fn
    window.draw()
    # should below line be after flip? does that matter?
    offset_error = trial_clock.getTime()-interval_dur-feedback_delay-trial_start #this should tell us how accurate the timing of the feedback_delay and total trial was
    for eye in reversed(bullseye):  #draw them all in reverse order
        eye.draw()
    if not training:
        win.logOnFlip('B{0}_T{1} feedback_delay starts: total time = {2:.3f}, trial time = {3:.3f}'.format(
                                    block_n,trial_n,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
    else:
        win.logOnFlip('TRAINING T{0} feedback_delay starts: total time = {1:.3f}, trial time = {2:.3f}'.format(
                                                trial_n,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
    win.flip()
    #        port.setData(0)
    while trial_clock.getTime() < feedback_start:# shouldn't this be feedback_end?
        response = event.getKeys(keyList=key, timeStamped=trial_clock)
        if len(response)>0:
            responses.append(response)
            if not training:
                win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block_n,trial_n,response,win.lastFrameT),logging.DATA)
            else:
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial_n,response,win.lastFrameT),logging.DATA)
            response = []
    if not training:
        win.logOnFlip('B{0}_T{1} feedback delay end: {2:.5f}; offset error = {3:.5f}'.format(block_n,trial_n,trial_clock.getTime(),
                                                            offset_error),logging.INFO)
    else:                                                    
        win.logOnFlip('TRAINING T{0} feedback delay end: {1:.5f}; offset error = {2:.5f}'.format(trial_n,trial_clock.getTime(),
                                                            offset_error),logging.INFO)


#===========================
#  Feedback Calculator
#===========================

def calc_feedback(bullseye=None, window=None, responses=None, block_n=None, exper=False, trial_n=None, trial_clock=trial_clock, trial_type=None, trial_start=None, resp_marker_width=resp_marker_width, interval_vlim=interval_vlim, feedback_end=None, key=key):
    tower_ball_draw(bullseye, window)
    if len(responses)>0:
        if len(responses)>1:
            win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: repsonses = {2}'.format(
                            block_n, trial_n, responses),logging.WARNING)
        response = responses[0]         # take the first response
        RT = response[0][1]-trial_start
        error = interval_dur-RT
        error_height = error*interval_height/interval_dur

        if np.abs(error)<tolerances[trial_type]:             # WIN
            outcome_win.draw()
            resp_marker.setLineColor('green')
            outcome_str = 'WIN!'
            tolerance_step_ix = 0
        else:                                   # LOSS
            outcome_loss.draw()
            resp_marker.setLineColor('red')
            outcome_str = 'LOSE!'
            tolerance_step_ix = 1
        resp_marker.setStart((-resp_marker_width/2, interval_vlim[1]-error_height))
        resp_marker.setEnd((resp_marker_width/2, interval_vlim[1]-error_height))
        resp_marker.draw()
        
        if exper:
            points[block_n]+= point_fn[tolerance_step_ix]
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)
        else:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)

        tolerances[trial_type]+= tolerance_step[trial_type][tolerance_step_ix]
        if tolerances[trial_type] > tolerance_lim[0]:
            tolerances[trial_type] = tolerance_lim[0]
        elif tolerances[trial_type] < tolerance_lim[1]:
            tolerances[trial_type] = tolerance_lim[1]


    else:
        outcome_loss.draw()
        outcome_str = 'None'
        #!!! adjust tolerance for this type of trial?
        if block_n:
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format(block_n,trial_n,win.lastFrameT),logging.INFO)
        else:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)                    #trigger_rect.draw()
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format('T',trial_n,win.lastFrameT),logging.INFO)
    win.flip()
#        port.setData(2)
    while trial_clock.getTime() < feedback_end:
        for press in event.getKeys(keyList=[key,'escape','q']):
            if press in ['escape','q']:
                win.close();
                core.quit();

#==============================
# Tower, Bullseye, ball Draw
#==============================

def tower_ball_draw(bullseye, window):
    tower.draw()
    window.draw()
    for eye in reversed(bullseye):  #draw them all in reverse order
        eye.draw()
        
#==============================
# Difficulty Staircase Function
#==============================

def staircase(trial_type=trial_type, interval_height=interval_height, tolerances=tolerances, interval_dur=interval_dur, min_bullseye_radius=min_bullseye_radius, trial_clock=trial_clock, feedback_end=None, key=key, ITI=None):
    bullseye_height[trial_type] = interval_height*tolerances[trial_type]/interval_dur
    bullseye_radii[trial_type] = np.linspace(min_bullseye_radius, bullseye_height[trial_type], num=n_rings[trial_type])
    for eye_ix, eye in enumerate(bullseyes[trial_type]):
        eye.radius = bullseye_radii[trial_type][eye_ix]
    
    #!!! this can go back in the outer loop
    while trial_clock.getTime() < feedback_end + ITI:
        for press in event.getKeys(keyList=[key,'escape','q']):
            if press in ['escape','q']:
                win.close();
                core.quit();
                    
#==============================
# Break Between Trial Blocks
#==============================

def block_break(block_n=None, trial_types=trial_types, n_blocks=n_blocks, break_min_dur=break_min_dur, key=key):
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
    if block_n<n_blocks*len(trial_types)-1:
        instr_txt.text = break_str.format(n_blocks*len(trial_types)-block_n-1,break_min_dur)
        instr_txt.draw()
        win.flip()
        core.wait(break_min_dur)
        block_point_txt.draw()
        total_point_txt.draw()
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        adv = event.waitKeys(keyList=[key, 'escape','q'])
        if adv[0] in ['escape','q']:
            win.close()
            core.quit()

#============================================================
# INSTRUCTIONS
#============================================================
#port = parallel.ParallelPort(address=53504)

#win.logOnFlip('Instructions FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA)
welcome_txt.draw()
adv_screen_txt.draw()
win.flip()
adv = event.waitKeys(keyList=[key, 'escape', 'q'])
if adv[0] in ['escape', 'q']:
        win.close()
        core.quit()
fnc.instruction_loop(intro=True)
win.flip()
#============================================================
# TRAINING
#============================================================
#port.setData(0) # sets all pins low
for trial_n in range(n_fullvis+2*n_training):
    #========================================================
    # Initialize Trial
    if trial_n < n_fullvis:                  # Examples w/o window
        covered = False
    else:
        covered = True
    if trial_n < n_fullvis+n_training:       # Easy Training
        trial_type = 'easy'
    else:                                   # Hard Training
        trial_type = 'hard'
    win.logOnFlip('TRAINING T{0}: window={1}; type={2}'.format(trial_n,covered,trial_type),logging.INFO)
    event.clearEvents()
    bullseye = bullseyes[trial_type]
    window = windows[covered]
    responses = []
    resp_pos = []
    outcome_str = ''
    
    # Instructions
    if (trial_n==n_fullvis) or (trial_n==n_fullvis+n_training):                    # First Easy/Hard Training
        fnc.instruction_loop(train_str[trial_type])
    #========================================================
    # Set Trial Timing
    trial_clock.reset()                                                       # In loop as temp variables, may export to variable file
    trial_start = trial_clock.getTime()
    target_time = trial_start + interval_dur
    target_tlim = [target_time-tolerances[trial_type], target_time+tolerances[trial_type]]
    feedback_start = trial_start + interval_dur + feedback_delay
    feedback_end = feedback_start + feedback_dur
    ITI = np.max(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
    win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial_n,win.lastFrameT),logging.INFO)
    # Below shouldn't need params because they're all defaults, but if you don't have them here it somehow logs the wrong thing (both if/else statements??)
    fnc.set_trial_timing(trial_clock, interval_dur, trial_type, tolerances, feedback_delay, feedback_dur, ITIs, trial_n, None, True)    # Trial time function Call 
    #========================================================
    # Moving Ball
    fnc.moving_ball(bullseye, covered, n_int_flips, window, responses, trial_clock, key, None, trial_n, win, training=False)
    #========================================================
    # Feedback Delay
    fnc.feedback_delay_func(bullseye, responses, None, window, trial_clock, trial_start, key, trial_n, False, interval_dur, feedback_start, feedback_delay)
    #========================================================
    # Feedback
    # Calculate Feedback
    fnc.calc_feedback(bullseye, window, responses, None, False, trial_n, trial_clock, trial_type, trial_start, resp_marker_width, interval_vlim, feedback_end, key)
    #========================================================
    # ITI
    win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format('T',trial_n,ITI,win.lastFrameT),logging.INFO)
    win.flip()
#    port.setData(0)
    # Staircase Tolerance
    fnc.staircase(trial_type, interval_height, tolerances, interval_dur, min_bullseye_radius, trial_clock, feedback_end, key, ITI)
#============================================================
# EXPERIMENT
#============================================================

fnc.instruction_loop(None, main_str, key, False)                    # Main instruction call 
# Constant Reward Function (switch to points)
outcome_win.text = '+{0}'.format(point_fn[0])
outcome_loss.text = '{0}'.format(point_fn[1])
for block_n, block_type in enumerate(block_order):
    trial_type = trial_types[block_type]
    bullseye = bullseyes[trial_type]
    window = windows[covered]
    block_start_txt.text = block_start_str.format(block_n+1, n_blocks*len(trial_types), trial_type)
    block_start_txt.draw()
    win.logOnFlip('B{0} ({1}) Start Text: FRAMETIME = {2}'.format(block_n,trial_type,win.lastFrameT),logging.INFO)
    win.flip()
    core.wait(block_start_dur)
    win.flip()
    core.wait(post_instr_delay)                                         # Delay so they aren't caught off guard
    
    for trial_n in range(n_trials):
        #========================================================
        # Initialize Trial
        event.clearEvents()
        responses = []
        resp_pos = []
        #========================================================
        # Set Trial Timing
        fnc.set_trial_timing(trial_clock, interval_dur, trial_type, tolerances, feedback_delay, feedback_dur, ITIs, trial_n, block_n, False)
        #========================================================
        # Moving Ball
        fnc.moving_ball(bullseye, covered, n_int_flips, window, responses, trial_clock, key, block_n, trial_n, win, True)
        #========================================================
        # Feedback Delay
        fnc.feedback_delay_func(bullseye, responses, block_n, window, trial_clock, trial_start, key, trial_n, True, interval_dur, feedback_start, feedback_delay)
        #========================================================
        # Feedback
        # Calculate Feedback
        fnc.calc_feedback(bullseye, window, responses, block_n, True, trial_n, trial_clock, trial_type, trial_start, resp_marker_width, interval_vlim, feedback_end, key)
        #========================================================
        # ITI
        win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format(block,trial_n,ITI,win.lastFrameT),logging.INFO)
        win.flip()
        fnc.staircase(trial_type, interval_height, tolerances, interval_dur, min_bullseye_radius, trial_clock, feedback_end, key, ITI)
        # wait for ITI code here
    #========================================================
    # Break Between Blocks
    fnc. block_break(block_n, trial_types, n_blocks, break_min_dur, key)
endgame_txt.draw()
win.flip()
core.wait(10)

win.close()
core.quit()

