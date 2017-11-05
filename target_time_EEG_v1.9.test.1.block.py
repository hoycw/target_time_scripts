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
def instruction_loop(adv=adv, instr_strs=instr_strs, instrs=None, block=None, key=key, trial_type=trial_type, train_str=train_str, intro=False):

    if intro:
        for instr_str in instr_strs:
            instr_txt.text = instr_str
            instr_txt.draw()
            adv_screen_txt.draw()
            win.flip()
            adv = event.waitKeys(keyList=[key, 'escape', 'q'])
            print adv
            if adv[0] in ['escape','q']:
                win.close()
                core.quit()
    else:
        instr_txt.text = instrs
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        adv = event.waitKeys(keyList=[key, 'escape', 'q'])
        if adv[0] in ['escape','q']:
            win.close()
            core.quit()
        core.wait(post_instr_delay)
instruction_loop(intro=True)
#win.logOnFlip('Instruction Response: {0}, FRAME TIME = {1} for response, win.lastFrameT={2}'.format(
#                response[0][0], response[0][1], win.lastFrameT), logging.DATA);
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
        instruction_loop(instrs=train_str[trial_type])
# 
        
    #========================================================
    # Set Trial Timing
    trial_clock.reset()
    trial_start = trial_clock.getTime()
    target_time = trial_start + interval_dur
    target_tlim = [target_time-tolerances[trial_type], target_time+tolerances[trial_type]]
    feedback_start = trial_start + interval_dur + feedback_delay
    feedback_end = feedback_start + feedback_dur
    ITI = np.max(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
    win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial,win.lastFrameT),logging.INFO)
    def set_trial_timing(trial_clock=trial_clock, interval_dur=interval_dur, trial_type=trial_type, tolerances=tolerances, feedback_delay=feedback_delay, feedback_dur=feedback_dur, ITIs=ITIs, trial=trial, block=None, train=False):
        trial_clock.reset()
        trial_start = trial_clock.getTime()
        target_time = trial_start + interval_dur
        target_tlim = [target_time-tolerances[trial_type], target_time+tolerances[trial_type]]
        feedback_start = trial_start + interval_dur + feedback_delay
        feedback_end = feedback_start + feedback_dur
        ITI = random.choice(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
        if train:
            win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial,win.lastFrameT),logging.INFO)
        else:
            win.logOnFlip('B{0}_T{1} start: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.INFO)
    set_trial_timing(train=True)
    #========================================================
    # Moving Ball
    def moving_ball(n_int_flips=n_int_flips, use_window=use_window, bullseye=bullseye, trial_clock=trial_clock, key=key, trial=trial, win=win, exp_type=False):
        for pos_ix in range(n_int_flips-sum(hidden_pos[use_window])):
            # Drawing Order (back-to-front): (outlines?), tower, window, ball, bullseye 
            tower.draw()
            window.draw()
            for eye in reversed(bullseye):  #draw them all in reverse order
                eye.draw()
            balls[pos_ix].draw()
            if exp_type:
                 if pos_ix==n_int_flips-1:       #!!! check what time the last ball of interval is drawn (assuming use_cover=False)
                    win_in.callOnFlip(print_time, trial_clock.getTime(), 'last pos drawn! use_cover={0}'.format(use_cover))
            #if trial_clock.getTime() < trigger_dur:
                #trigger_rect.draw()
            win.flip()
        #            if pos_ix==1:
        #                port.setData(1)  # sets just this pin to be high
            response = event.getKeys(keyList=key, timeStamped=trial_clock)  #!!! responses here still tied to flips?
            if len(response)>0:
                responses.append(response)
                if exp_type:
                   win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block,trial,response,win.lastFrameT),logging.DATA)
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial,response,win.lastFrameT),logging.DATA)
                response = []
    moving_ball(n_int_flips, use_window, bullseye, trial_clock, key, trial, win, exp_type=False)
    #========================================================
    # Feedback Delay
    def feedback_delay_func(bullseye=bullseye, block=None, trial_clock=trial_clock, feedback_start=feedback_start, key=key, trial=trial, exp_type=False, interval_dur=interval_dur, feedback_delay=feedback_delay, trial_start=trial_start):
        tower.draw()
        window.draw()
        offset_error = trial_clock.getTime()-interval_dur-feedback_delay-trial_start
        for eye in reversed(bullseye):  #draw them all in reverse order
            eye.draw()
        if exp_type:
            win.logOnFlip('B{0}_T{1} feedback_delay starts: total time = {2:.3f}, trial time = {3:.3f}'.format(
                                        block,trial,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
        win.logOnFlip('TRAINING T{0} feedback_delay starts: total time = {1:.3f}, trial time = {2:.3f}'.format(
                                                    trial,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
        win.flip()
        #        port.setData(0)
        while trial_clock.getTime() < feedback_start:
            response = event.getKeys(keyList=key, timeStamped=trial_clock)
            if len(response)>0:
                responses.append(response)
                if exp_type:
                   win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block,trial,response,win.lastFrameT),logging.DATA)
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial,response,win.lastFrameT),logging.DATA)
                response = []
        if exp_type:
            win.logOnFlip('B{0}_T{1} feedback delay end: {2:.5f}; offset error = {3:.5f}'.format(block,trial,trial_clock.getTime(),
                                                             offset_error),logging.INFO)
        win.logOnFlip('TRAINING T{0} feedback delay end: {1:.5f}; offset error = {2:.5f}'.format(trial,trial_clock.getTime(),
                                                                offset_error),logging.INFO)
    feedback_delay_func(bullseye, None, trial_clock, feedback_start, key, trial, False, interval_dur, feedback_delay, trial_start)
    #========================================================
    # Feedback
    # Calculate Feedback
    def tower_ball_draw(bullseye=bullseye):
        tower.draw()
        window.draw()
        for eye in reversed(bullseye):  #draw them all in reverse order
            eye.draw()
    def calc_feedback(responses=responses, block=None, trial=trial, trial_clock=trial_clock, trial_type=trial_type, resp_marker_width=resp_marker_width, interval_vlim=interval_vlim, key=key):
            tower_ball_draw(bullseye)
            if len(responses)>0:
                if len(responses)>1:
                    win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: repsonses = {2}'.format(
                                    block, trial, responses),logging.WARNING)
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
                points[block]+= point_fn[tolerance_step_ix]
                
                win.logOnFlip(feedback_str.format(block,trial,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)
                tolerances[trial_type]+= tolerance_step[trial_type][tolerance_step_ix]
                if tolerances[trial_type] > tolerance_lim[0]:
                    tolerances[trial_type] = tolerance_lim[0]
                elif tolerances[trial_type] < tolerance_lim[1]:
                    tolerances[trial_type] = tolerance_lim[1]


            else:
                outcome_loss.draw()
                outcome_str = 'None'
                #!!! adjust tolerance for this type of trial?
                if block==None:
                    win.logOnFlip(feedback_str.format('T',trial,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
            
                    #trigger_rect.draw()
                    win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format('T',trial,win.lastFrameT),logging.INFO)
                    win.flip()
                else:
                    win.logOnFlip(feedback_str.format(block,trial,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
                    win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.INFO)
                    win.flip()    

    #        port.setData(2)
            while trial_clock.getTime() < feedback_end:
                for press in event.getKeys(keyList=[key,'escape','q']):
                    if press in ['escape','q']:
                        win.close();
                        core.quit();
    calc_feedback(responses, None, trial, trial_clock, trial_type, resp_marker_width, interval_vlim, key)
    #========================================================
    # ITI
#    print 'ITI ({0}) start = {1:.5f}; error = {2:.5f}'.format(ITI, trial_clock.getTime(),
#                                   trial_clock.getTime()-interval_dur-feedback_delay-feedback_dur-trial_start)
    win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format('T',trial,ITI,win.lastFrameT),logging.INFO)
    win.flip()
#    port.setData(0)
    # Staircase Tolerance
    def staircase(trial_type=trial_type, interval_height=interval_height, tolerances=tolerances, interval_dur=interval_dur, min_bullseye_radius=min_bullseye_radius, ITI=ITI, trial_clock=trial_clock, key=key, feedback_end=feedback_end):
        bullseye_height[trial_type] = interval_height*tolerances[trial_type]/interval_dur
        bullseye_radii[trial_type] = np.linspace(min_bullseye_radius, bullseye_height[trial_type], num=n_rings[trial_type])
        for eye_ix, eye in enumerate(bullseyes[trial_type]):
            eye.radius = bullseye_radii[trial_type][eye_ix]
        
        while trial_clock.getTime() < feedback_end + ITI:
            for press in event.getKeys(keyList=[key,'escape','q']):
                if press in ['escape','q']:
                    win.close();
                    core.quit();
    staircase(trial_type, interval_height, tolerances, interval_dur, min_bullseye_radius, ITI, trial_clock, key, feedback_end)
#============================================================
# EXPERIMENT
#============================================================

instruction_loop(main_str)

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
#
        set_trial_timing(block=block)
        #========================================================
        # Moving Ball
        moving_ball(n_int_flips, use_window, bullseye, trial_clock, key, trial, win, True)

        #========================================================
        # Feedback Delay
        feedback_delay_func(bullseye, block, trial_clock, feedback_start, key, trial, True, interval_dur, feedback_delay, trial_start)
        #========================================================
        # Feedback
        # Calculate Feedback
#
        calc_feedback(responses, block, trial, trial_clock, trial_type, resp_marker_width, interval_vlim, key)
        #========================================================
        # ITI
#        print 'ITI ({0}) start = {1:.5f}; error = {2:.5f}'.format(ITI, trial_clock.getTime(),
#                                       trial_clock.getTime()-interval_dur-feedback_delay-feedback_dur-trial_start)
        win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format(block,trial,ITI,win.lastFrameT),logging.INFO)
        win.flip()
#        port.setData(0)
        # Staircase Tolerance
#     
        staircase(trial_type, interval_height, tolerances, interval_dur, min_bullseye_radius, ITI, trial_clock, key, feedback_end)
    #========================================================
    # Break Between Blocks
    def block_break(block=block, trial_types=trial_types, n_blocks=n_blocks, break_min_dur=break_min_dur, key=key):
        block_point_txt.text = block_point_str.format(block+1,points[block])
        if points[block]>=0:
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
        if block<n_blocks*len(trial_types)-1:
            instr_txt.text = break_str.format(n_blocks*len(trial_types)-block-1,break_min_dur)
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
    block_break(block, trial_types, n_blocks, break_min_dur, key)

endgame_txt.draw()
win.flip()
core.wait(10)

win.close()
core.quit()

