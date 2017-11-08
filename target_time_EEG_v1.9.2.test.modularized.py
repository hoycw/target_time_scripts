# target_time_behavEEG_v1.9.2test
paradigm_version = '1.9.2'
# 1.9.2.test: modularized parameters, log, and variables to cut down on file length 
# 1.9.2: different trigger codes for stim (1) and feedback (2); stim trigger lasts until feedback_delay; adv_scr_txt moved down to avoid overlap
# 1.9.1: EEG triggers actually work after troubleshooting on 135D (must use WinXP)
# 1.9: EEG triggers; no photodiode, screen size 
# 1.8.5: ITIs=[0.2,0.4,0.7,1.0]; feedback_dur=0.8; log:(paradigm_version,n_examples,n_training);
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
# 1.5 implements block structure to whole experiment, instructions, training (use_window=False examples)
# 1.4 got skipped (handler nonsense)
# 1.3 added photodiode trigger rectangle, basic logging
#   (incomplete logging, to be finished once trail/exp ahndelres are done)
# 1.2 has more comments than 1.1
# implements staircase adjustments to target intervals
# dict for all variables changing across trial types (easy/hard)

from psychopy import visual, event, core, gui, logging, data
from psychopy import parallel
import numpy as np
import math, time, random, shelve
#from psychopy.tools.coordinatetools import pol2cart
random.seed()
core.wait(0.5)      # give the system time to settle
core.rush(True)     # might give psychopy higher priority in the system (maybe...)
exp_datetime = time.strftime("%Y%m%d%H%M%S")
paradigm_name = 'target_time'

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
# LOG PARADIGM PARAMETERS
#============================
import target_time_functions as fnc
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
for trial in range(n_examples+2*n_training):
    #========================================================
    # Initialize Trial
    if trial < n_examples:                  # Examples w/o window
        use_window = False
    else:
        use_window = True
    if trial < n_examples+n_training:       # Easy Training
        trial_type = 'easy'
    else:                                   # Hard Training
        trial_type = 'hard'
    win.logOnFlip('TRAINING T{0}: window={1}; type={2}'.format(trial,use_window,trial_type),logging.INFO)
    event.clearEvents()
    bullseye = bullseyes[trial_type]
    window = windows[use_window]
    responses = []
    resp_pos = []
    outcome_str = ''
    
    # Instructions
    if (trial==n_examples) or (trial==n_examples+n_training):                    # First Easy/Hard Training
        fnc.instruction_loop(instrs=train_str[trial_type])
    #========================================================
    # Set Trial Timing
    trial_clock.reset()                                                       # In loop as temp variables, may export to variable file
    trial_start = trial_clock.getTime()
    target_time = trial_start + interval_dur
    target_tlim = [target_time-tolerances[trial_type], target_time+tolerances[trial_type]]
    feedback_start = trial_start + interval_dur + feedback_delay
    feedback_end = feedback_start + feedback_dur
    ITI = np.max(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
    win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial,win.lastFrameT),logging.INFO)
    fnc.set_trial_timing(trial_clock, interval_dur, trial_type, tolerances, feedback_delay, feedback_dur, ITIs, trial, None, True)    # Trial time function Call 
    #========================================================
    # Moving Ball
    fnc.moving_ball(bullseye, use_window, n_int_flips, window, responses, trial_clock, key, None, trial, win, exp_type=False)
    #========================================================
    # Feedback Delay
    fnc.feedback_delay_func(bullseye, responses, None, window, trial_clock, trial_start, key, trial, False, interval_dur, feedback_start, feedback_delay)
    #========================================================
    # Feedback
    # Calculate Feedback
    fnc.calc_feedback(bullseye, window, responses, None, False, trial, trial_clock, trial_type, trial_start, resp_marker_width, interval_vlim, feedback_end, key)
    #========================================================
    # ITI
    win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format('T',trial,ITI,win.lastFrameT),logging.INFO)
    win.flip()
#    port.setData(0)
    # Staircase Tolerance
    fnc.staircase(trial_type, interval_height, tolerances, interval_dur, min_bullseye_radius, trial_clock, feedback_end, key, ITI)
#============================================================
# EXPERIMENT
#============================================================

fnc.instruction_loop(None, main_str, key, False)                    # Main instruction call 
use_window = True   # Just to be sure
# Constant Reward Function (switch to points)
outcome_win.text = '+{0}'.format(point_fn[0])
outcome_loss.text = '{0}'.format(point_fn[1])
for block, block_type in enumerate(block_order):
    trial_type = trial_types[block_type]
    bullseye = bullseyes[trial_type]
    window = windows[use_window]
    block_start_txt.text = block_start_str.format(block+1, n_blocks*len(trial_types), trial_type)
    block_start_txt.draw()
    win.logOnFlip('B{0} ({1}) Start Text: FRAMETIME = {2}'.format(block,trial_type,win.lastFrameT),logging.INFO)
    win.flip()
    core.wait(block_start_dur)
    win.flip()
    core.wait(post_instr_delay)                                         # Delay so they aren't caught off guard
    
    for trial in range(n_trials):
        #========================================================
        # Initialize Trial
        event.clearEvents()
        responses = []
        resp_pos = []
        #========================================================
        # Set Trial Timing
        fnc.set_trial_timing(trial_clock, interval_dur, trial_type, tolerances, feedback_delay, feedback_dur, ITIs, trial, block, False)
        #========================================================
        # Moving Ball
        fnc.moving_ball(bullseye, use_window, n_int_flips, window, responses, trial_clock, key, block, trial, win, True)
        #========================================================
        # Feedback Delay
        fnc.feedback_delay_func(bullseye, responses, block, window, trial_clock, trial_start, key, trial, True, interval_dur, feedback_start, feedback_delay)
        #========================================================
        # Feedback
        # Calculate Feedback
        fnc.calc_feedback(bullseye, window, responses, block, True, trial, trial_clock, trial_type, trial_start, resp_marker_width, interval_vlim, feedback_end, key)
        #========================================================
        # ITI
        win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format(block,trial,ITI,win.lastFrameT),logging.INFO)
        win.flip()
        fnc.staircase(trial_type, interval_height, tolerances, interval_dur, min_bullseye_radius, trial_clock, feedback_end, key, ITI)
    #========================================================
    # Break Between Blocks
    fnc. block_break(block, trial_types, n_blocks, break_min_dur, key)
endgame_txt.draw()
win.flip()
core.wait(10)

win.close()
core.quit()

