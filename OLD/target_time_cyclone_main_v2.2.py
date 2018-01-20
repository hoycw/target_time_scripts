from psychopy import visual, event, core, gui, logging, data
from psychopy import parallel
from psychopy.tools.coordinatetools import pol2cart

import numpy as np
import math, time, random
random.seed()
core.wait(0.5)      # give the system time to settle
core.rush(True)     # might give psychopy higher priority in the system (maybe...)

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
# displays instructions for current trial type
    # If intro=True, instrs won't be used (can just be '') 
    if intro:
        for instr_str in instr_strs:
            instr_txt.text = instr_str
            instr_img.draw()
            instr_txt.draw()
            adv_screen_txt.draw()
            win.flip()
            adv = event.waitKeys(keyList=[key, 'escape', 'q'])
            if adv[0] in ['escape','q']:
                win.close()
                core.quit()
    else:
        if instrs != main_str:
            train_img.draw()
        instr_txt.text = instrs
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        adv = event.waitKeys(keyList=[key, 'escape', 'q'])
        if adv[0] in ['escape','q']:
            win.close()
            core.quit()
        core.wait(post_instr_delay)     # let them prep before hitting them with interval_dur


#===================================================
def set_trial_timing(trial_clock, block_n, trial_type, trial_n, training=False):
    # for training mode, input block_n=None
    trial_clock.reset()
    trial_start = trial_clock.getTime()
    target_time = trial_start + interval_dur
    feedback_start = target_time + feedback_delay
    feedback_end = feedback_start + feedback_dur
    ITI = random.choice(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
    if training:   # !!! do we want to get rid of this and make training and block logging uniform style?
        win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial_n,win.lastFrameT),logging.INFO)
    else:
        win.logOnFlip('B{0}_T{1} start: FRAME TIME = {2}'.format(block_n,trial_n,win.lastFrameT),logging.INFO)


#===================================================
def moving_ball(block_n, trial_n, training=False):
    response = False
    
    for circ_xi in range(n_circ-1):# - sum(hidden_pos[covered])):
        # Draw stimuli
        target_zone_draw()
        if circ_xi == 0:
            circ_colors[n_circ-1] = (1,1,1)
        #if trial_clock.getTime() < trigger_dur:
            #trigger_rect.draw()
        if circ_xi >= (n_circ - sum(hidden_pos[covered])):
            circ_colors[circ_xi] = (0,0,0)
        else:
            circ_colors[circ_xi] = (1,1,1)      # Turn light on
        circles.colors = circ_colors
        circles.draw()
        win.flip()
        circ_colors[n_circ-1] = (-1,-1,-1)
        circ_colors[circ_xi] = flip_list[circ_xi]  # Turn light back off
#        print covered, circ_xi, circ_colors[circ_xi],re_flip_color[covered][circ_xi]
        circles.colors = circ_colors
        while trial_clock.getTime() < trial_start + circ_start[circ_xi]:
            for press in event.getKeys(keyList=[key,'escape','q'], timeStamped=trial_clock):
                if press in ['escape','q']:
                    win.close();
                    core.quit();
                else:
                    response = [press]
                #!!! Responses captured here were not getting registered.  Initialized response at top of function to capture response in this loop. 
#            if pos_ix==1 and experiment_type=='EEG'
    #                port.setData(1)  # sets just this pin to be high
    if not response:
        response = event.getKeys(keyList=key, timeStamped=trial_clock)  #!!! responses here still tied to flips?
    if len(response)>0:
        responses.append(response)
        if not training:
            win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block_n,trial_n,response,win.lastFrameT),logging.DATA)
        else:
            win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial_n,response,win.lastFrameT),logging.DATA)
        response = []


#===================================================
def feedback_delay_func(responses, block_n, trial_n, training=False):
    target_zone_draw()
    circles.draw()
    # !!! Do we need these delay starts? If we're not testing timing, no...
#    if not training:
#        win.logOnFlip('B{0}_T{1} feedback_delay starts: total time = {2:.3f}, trial time = {3:.3f}'.format(
#                                    block_n,trial_n,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
#    else:
#        win.logOnFlip('TRAINING T{0} feedback_delay starts: total time = {1:.3f}, trial time = {2:.3f}'.format(
#                                                trial_n,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
    win.flip()
    #        if exp_type=='EEG': port.setData(0)
    # Catch responses during delay before feedback onset
    while trial_clock.getTime() < feedback_start:
        response = event.getKeys(keyList=key, timeStamped=trial_clock)
        if len(response)>0:
            responses.append(response)
            if not training:
                win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block_n,trial_n,response,win.lastFrameT),logging.DATA)
            else:
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial_n,response,win.lastFrameT),logging.DATA)
            response = []
            
    # !!! Timing test, can be removed later
#    offset_error = trial_clock.getTime()-interval_dur-feedback_delay-trial_start #this should tell us how accurate the timing of the feedback_delay and total trial was
#    if not training:
#        win.logOnFlip('B{0}_T{1} feedback delay end: {2:.5f}; offset error = {3:.5f}'.format(block_n,trial_n,trial_clock.getTime(),
#                                                            offset_error),logging.INFO)
#    else:                                                    
#        win.logOnFlip('TRAINING T{0} feedback delay end: {1:.5f}; offset error = {2:.5f}'.format(trial_n,trial_clock.getTime(),
#                                                            offset_error),logging.INFO)


#===================================================
def calc_feedback(block_n, trial_type, trial_n, training=False):
    target_zone_draw()
    circles.draw()
    surp = False
    if len(responses)>0:
        if len(responses)>1:
            win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: repsonses = {2}'.format(
                            block_n, trial_n, responses),logging.WARNING)
        response = responses[0]         # take the first response
        RT = response[0][1]-trial_start
        error =  RT - interval_dur 
        error_angle = error*angle_ratio
        if not training and trial_n in surprise_trials[surp_cnt]:          # Surprise on if not in training and if in list of surprise trials  
            surprise_trial()
            resp_marker.setLineColor(None)
            outcome_str = 'SURPRISE!'
            surp = True
        elif np.abs(error)<tolerances[trial_type]:             # WIN
#            outcome_win.draw()
            outcome_win_pic.draw()
            resp_marker.setLineColor('green')
            outcome_str = 'WIN!'
            win_flag = 0
        else:                                   # LOSS
#            outcome_loss.draw()
            outcome_loss_pic.draw()
            resp_marker.setLineColor('red')
            outcome_str = 'LOSE!'
            win_flag = 1
#        resp_marker.setStart(pol2cart(error_angle+270, loop_radius-resp_marker_width/2))
#        resp_marker.setEnd(pol2cart(error_angle+270, loop_radius+resp_marker_width/2))
#        resp_marker.draw()
#        print resp_marker.start, resp_marker.end, loop_radius-resp_marker_width/2, error_angle+270, loop_radius+resp_marker_width/2, error_angle+270
#        print error, error_angle, response, RT
        if not training and not surp:
            points[block_n]+= point_fn[win_flag]
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)
        else:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)
            
        if not surp:
            tolerances[trial_type]+= tolerance_step[trial_type][win_flag]      # Update tolerances based on feedback. Needs to be here.   
            if tolerances[trial_type] > tolerance_lim[0]:                      #!!! Won't work if moved to staircase. Would need new implementation.
                tolerances[trial_type] = tolerance_lim[0]
            elif tolerances[trial_type] < tolerance_lim[1]:
                tolerances[trial_type] = tolerance_lim[1]

    else:   # No response detected
#        outcome_loss.draw()
        outcome_loss_pic.draw()
        outcome_str = 'None'
        # Not adjusting tolerance for this type of trial...
        if not training:
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format(block_n,trial_n,win.lastFrameT),logging.INFO)
        else:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format('T',trial_n,win.lastFrameT),logging.INFO)
    #if experiment_type=='ECoG': trigger_rect.draw()
    win.flip()
#        if experiment_type=='EEG': port.setData(2)
    while trial_clock.getTime() < feedback_end:
        for press in event.getKeys(keyList=[key,'escape','q']):
            if press in ['escape','q']:
                win.close();
                core.quit();


#===================================================
def staircase(trial_type): 
    target_origin[trial_type] = 180 - (tolerances[trial_type] * angle_ratio)
    target_upper_bound[trial_type] =  2*tolerances[trial_type]*angle_ratio
    target_zone.visibleWedge = [0, target_upper_bound[trial_type]]
    target_zone.ori = target_origin[trial_type]
#    print 'origin = ', target_origin[trial_type], 'upper =' ,target_upper_bound[trial_type], 'origin+upper=',target_origin[trial_type]+target_upper_bound[trial_type]
#    print 'tolerances = ' ,tolerances[trial_type], '180+(tolerances*angle)=', 180+(tolerances[trial_type]*angle_ratio)
#    print 'visibleWEdge = ', target_zone.visibleWedge, 'tz.ori = ', target_zone.ori


#===================================================
def block_break(block_n): #trial_types, n_blocks=n_blocks, break_min_dur=break_min_dur, key=key):
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
    # If not the last block, print feedback
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


#===================================================
def target_zone_draw():
    target_zone.draw()
    target_zone_cover.draw()
    sockets.draw()
    crosshair.draw()

#===================================================
def surprise_trial():
    pic_cnt = np.random.randint(0, len(surprise_pic_list))
    outcome_surprise_pic.draw()
    outcome_surprise_pic.image = 'stimuli/{0}'.format(surprise_pic_list[pic_cnt])


#============================================================
# INSTRUCTIONS
#============================================================
# if experiment_type=='EEG'
#   port = parallel.ParallelPort(address=53504)

welcome_txt.draw()
adv_screen_txt.draw()
win.flip()
adv = event.waitKeys(keyList=[key, 'escape', 'q'])
if adv[0] in ['escape', 'q']:
        win.close()
        core.quit()
instruction_loop(None, intro=True)
win.flip()

#============================================================
# TRAINING
#============================================================
# if experiment_type=='EEG':
#   port.setData(0) # sets all pins low
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
    responses = []
    resp_pos = []
    surp_cnt = 0 
    outcome_str = ''
    target_zone.visibleWedge = [0, target_upper_bound[trial_type]]
    target_zone.ori = target_origin[trial_type]
#    print 'origin = ', target_origin[trial_type], 'upper =' ,target_upper_bound[trial_type], 'tolerances = ' ,tolerances[trial_type]
    if covered:
        circ_colors = [i for i in circ_cover_list]
        circles.colors = circ_colors
    fill_list = re_fill_color[covered]
    flip_list = re_flip_color[covered]
#    print flip_list
        
    # Instructions
    if (trial_n==n_fullvis) or (trial_n==n_fullvis+n_training):                    # First Easy/Hard Training
        instruction_loop(train_str[trial_type])
    
    #========================================================
    # Set Trial Timing
    #   NOTE: need to run this outside the function the first time to initialize
    trial_clock.reset()                                                       # In loop as temp variables, may export to variable file
    trial_start = trial_clock.getTime()
    target_time = trial_start + interval_dur
    feedback_start = trial_start + interval_dur + feedback_delay
    feedback_end = feedback_start + feedback_dur
    ITI = np.max(ITIs)
    win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial_n,win.lastFrameT),logging.INFO)
    # Below shouldn't need params because they're all defaults, but if you don't have them here it somehow logs the wrong thing (both if/else statements??)
#    set_trial_timing(trial_clock, None, trial_type, trial_n, training=True)    # Trial time function Call, not needed because of previous lines
   
    #========================================================
    # Moving Ball
    moving_ball(None, trial_n, training=True)
    
    #========================================================
    # Feedback Delay
    feedback_delay_func(responses, None, trial_n, training=True)
    
    #========================================================
    # Calculate Feedback
    calc_feedback(None, trial_type, trial_n, training=True)
    
    #========================================================
    # ITI
    win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format('T',trial_n,ITI,win.lastFrameT),logging.INFO)
    win.flip()
# if experiment_type=='EEG':
#    port.setData(0)
    
    # Staircase Tolerance
    staircase(trial_type)
    while trial_clock.getTime() < feedback_end + ITI:
        for press in event.getKeys(keyList=[key,'escape','q']):
            if press in ['escape','q']:
                win.close();
                core.quit();


#============================================================
# EXPERIMENT
#============================================================
instruction_loop(main_str)                    # Main instruction call 
# Constant Reward Function (start awarding points)
outcome_win.text = '+{0}'.format(point_fn[0])
outcome_loss.text = '{0}'.format(point_fn[1])
for block_n, block_type in enumerate(block_order):
    trial_type = trial_types[block_type]
    target_zone.visibleWedge = [0, target_upper_bound[trial_type]]
    target_zone.ori = target_origin[trial_type]
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
        set_trial_timing(trial_clock, block_n, trial_type, trial_n)
        
        #========================================================
        # Moving Ball
        moving_ball(block_n, trial_n, training=False)
        
        #========================================================
        # Feedback Delay
        feedback_delay_func(responses, block_n, trial_n, training=False)
        
        #========================================================
        # Feedback
        # Calculate Feedback
        calc_feedback(block_n, trial_type, trial_n, False)
        
        #========================================================
        # ITI
        win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format(block_n,trial_n,ITI,win.lastFrameT),logging.INFO)
        win.flip()
        staircase(trial_type)
        while trial_clock.getTime() < feedback_end + ITI:
            for press in event.getKeys(keyList=[key,'escape','q']):
                if press in ['escape','q']:
                    win.close();
                    core.quit();
    
    #========================================================
    # Break Between Blocks
    surp_cnt += 1
    block_break(block_n)
     

endgame_txt.draw()
win.flip()
core.wait(10)

win.close()
core.quit()

