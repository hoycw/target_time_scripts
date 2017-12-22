
from psychopy import visual, event, core, gui, logging, data
from psychopy import parallel
import numpy as np
import math, time, random, shelve

from target_time_EEG_parameters import*
import target_time_EEG_log
from target_time_EEG_variables import*

#
#
#bullseye = bullseyes[trial_type]
#responses = []
#resp_pos = []
#outcome_str = ''
#
#trial_start = trial_clock.getTime()
#target_time = trial_start + interval_dur
#target_tlim = [target_time-tolerances[trial_type], target_time+tolerances[trial_type]]
#feedback_start = trial_start + interval_dur + feedback_delay
#feedback_end = feedback_start + feedback_dur

#==============================================
# instruction_loop 
# displays instructions for current trial type
#==============================================

def instruction_loop(instr_strs=instr_strs, instrs=None, key=key, intro=False):
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
        
#============================       
# Trial timer function
#============================

def set_trial_timing(trial_clock=trial_clock, interval_dur=interval_dur, trial_type=trial_type, tolerances=tolerances, feedback_delay=feedback_delay, feedback_dur=feedback_dur, ITIs=ITIs, trial=None, block=None, train=False):
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

#===========================
# Moving ball function
#===========================

def moving_ball(bullseye=None, use_window=None, n_int_flips=n_int_flips, window=None, responses=None, trial_clock=trial_clock, key=key, block=None, trial=None, win=win, exp_type=False):
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
            else:
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial,response,win.lastFrameT),logging.DATA)
            response = []
        
#============================
#  Feedback Delay 
#============================

def feedback_delay_func(bullseye=None, responses=None, block=None, window=None, trial_clock=trial_clock, trial_start=None, key=key, trial=None, exp_type=False, interval_dur=interval_dur, feedback_start=None, feedback_delay=feedback_delay):
    tower.draw()
    window.draw()
    offset_error = trial_clock.getTime()-interval_dur-feedback_delay-trial_start
    for eye in reversed(bullseye):  #draw them all in reverse order
        eye.draw()
    if exp_type:
        win.logOnFlip('B{0}_T{1} feedback_delay starts: total time = {2:.3f}, trial time = {3:.3f}'.format(
                                    block,trial,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
    else:
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
            else:
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial,response,win.lastFrameT),logging.DATA)
            response = []
    if exp_type:
        win.logOnFlip('B{0}_T{1} feedback delay end: {2:.5f}; offset error = {3:.5f}'.format(block,trial,trial_clock.getTime(),
                                                            offset_error),logging.INFO)
    else:                                                    
        win.logOnFlip('TRAINING T{0} feedback delay end: {1:.5f}; offset error = {2:.5f}'.format(trial,trial_clock.getTime(),
                                                            offset_error),logging.INFO)


#===========================
#  Feedback Calculator
#===========================

def calc_feedback(bullseye=None, window=None, responses=None, block=None, exper=False, trial=None, trial_clock=trial_clock, trial_type=None, trial_start=None, resp_marker_width=resp_marker_width, interval_vlim=interval_vlim, feedback_end=None, key=key):
    tower_ball_draw(bullseye, window)
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
        
        if exper:
            points[block]+= point_fn[tolerance_step_ix]
            win.logOnFlip(feedback_str.format(block,trial,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)
        else:
            win.logOnFlip(feedback_str.format('T',trial,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)

        tolerances[trial_type]+= tolerance_step[trial_type][tolerance_step_ix]
        if tolerances[trial_type] > tolerance_lim[0]:
            tolerances[trial_type] = tolerance_lim[0]
        elif tolerances[trial_type] < tolerance_lim[1]:
            tolerances[trial_type] = tolerance_lim[1]


    else:
        outcome_loss.draw()
        outcome_str = 'None'
        #!!! adjust tolerance for this type of trial?
        if block:
            win.logOnFlip(feedback_str.format(block,trial,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.INFO)
        else:
            win.logOnFlip(feedback_str.format('T',trial,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)                    #trigger_rect.draw()
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format('T',trial,win.lastFrameT),logging.INFO)
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
    
    while trial_clock.getTime() < feedback_end + ITI:
        for press in event.getKeys(keyList=[key,'escape','q']):
            if press in ['escape','q']:
                win.close();
                core.quit();
                    
#==============================
# Break Between Trial Blocks
#==============================

def block_break(block=None, trial_types=trial_types, n_blocks=n_blocks, break_min_dur=break_min_dur, key=key):
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