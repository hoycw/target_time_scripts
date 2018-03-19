from psychopy import prefs
prefs.general['audioLib'] = ['pygame']
from psychopy import visual, event, core, gui, logging, data, sound, parallel
from psychopy.tools.coordinatetools import pol2cart

import numpy as np
import math, time, random, copy
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
            adv = event.waitKeys(keyList=[key, 'escape', 'q'])
            if adv[0] in ['escape','q']:
                win.close()
                core.quit()

    else:
        instr_txt.text = instrs
        instr_txt.pos = (0,2)
        instr_txt.draw()
        adv_screen_txt.draw()
        win.flip()
        adv = event.waitKeys(keyList=[key, 'escape', 'q'])
        if adv[0] in ['escape','q']:
            win.close()
            core.quit()
        core.wait(post_instr_delay)     # let them prep before hitting them with interval_dur


#===================================================
def set_trial_timing(trial_clock, block_n, trial_n, training=False):#!!! why is condition here if it's not used? 
    # for training mode, input block_n=None
    win.flip()                                   # !!! to lock timing before first frame.
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
#        if circ_xi==1 and paradigm_type=='eeg':
#            win.callOnFlip(port.setData, 1)  # sets just this pin to be high
        win.flip()

        
        circ_colors[n_circ-1] = (-1,-1,-1)
        circ_colors[circ_xi] = flip_list[circ_xi]  # Turn light back off
        circles.colors = circ_colors
        while trial_clock.getTime() < trial_start + circ_start[circ_xi]:
            for press in event.getKeys(keyList=[key,'escape','q'], timeStamped=trial_clock):
                if press[0] in ['escape','q']:
                    win.close()
                    core.quit()
                response = [press]
                    #!!! Responses captured here were not getting registered.  Initialized response at top of function to capture response in this loop. 
        
    # Log any responses
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
    
#    if paradigm_type=='eeg': 
#        win.callOnFlip(port.setData, 0)
    win.flip()
    
    # Catch responses during delay before feedback onset
    while trial_clock.getTime() < feedback_start:
        response = event.getKeys(keyList=key, timeStamped=trial_clock)
        if len(response)>0:
            responses.append(response)
            if not training:
                win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block_n,trial_n,response,win.lastFrameT),logging.DATA)
            else:
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}, TRIAL START = {3}'.format(trial_n,response,win.lastFrameT,trial_start),logging.DATA)
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
def calc_feedback(block_n, condition, trial_n, training=False):
    global training_score
    target_zone_draw()
    surp = False
    if len(responses)>0:
        if len(responses)>1:
            win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: responses = {2}'.format(
                            block_n, trial_n, responses),logging.WARNING)
        response = responses[0]         # take the first response
        RT = response[0][1]-trial_start
        error = RT - interval_dur 
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
        target_zone_draw()
        outcome_str = 'None'
        resp_marker.setLineColor(None)
        # Not adjusting tolerance for this type of trial...
        if not training:
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,-1,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format(block_n,trial_n,win.lastFrameT),logging.INFO)
        else:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,-1,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format('T',trial_n,win.lastFrameT),logging.INFO)
    if paradigm_type=='ecog': 
       trigger_rect.draw()
    
    # Present feedback
    win.callOnFlip(turn_sound[outcome_str].play)
#    if paradigm_type=='eeg': 
#        win.callOnFlip(port.setData, 2)
    for frameN in range(feedback_dur * 60):        # softcode 60 to framerate later. 
        target_zone_draw()                      # Using our defined target_zone_draw, not .draw to have correct visual.  
        resp_marker.draw()
        win.flip()
    win.flip()

    if not surp and outcome_str != 'None':
        tolerances[condition]+= tolerance_step[condition][win_flag]      # Update tolerances based on feedback. Needs to be here.   
        if tolerances[condition] > tolerance_lim[0]:                      #!!! Won't work if moved to staircase. Would need new implementation.
            tolerances[condition] = tolerance_lim[0]
        elif tolerances[condition] < tolerance_lim[1]:
            tolerances[condition] = tolerance_lim[1]
        if training and trial_n>=n_fullvis:
            training_score[condition] += point_fn[win_flag]
#                print training_score
            
        elif not training:
            points[block_n]+= point_fn[win_flag]
        if training:
            win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,RT,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} SOUND = {2} feedback start: FRAME TIME = {3}'.format('T', trial_n, outcome_sound, win.lastFrameT),logging.DATA)
        else:
            win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,RT,condition,tolerances[condition]),logging.DATA)
            win.logOnFlip('B{0}_T{1} SOUND = {2} feedback start: FRAME TIME = {3}'.format(block_n, trial_n, outcome_sound, win.lastFrameT),logging.DATA)
            
    resp_marker.setLineColor('black')
    target_zone.setColor('dimgrey')
    while trial_clock.getTime() < feedback_end:
        for press in event.getKeys(keyList=[key,'escape','q']):
            if press in ['escape','q']:
                win.close()
                core.quit()


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
        adv = event.waitKeys(keyList=[key, 'escape','q'])
        if adv[0] in ['escape','q']:
            win.close()
            core.quit()

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
    adv = event.waitKeys(keyList=[key, 'escape', 'q'])
    if adv[0] in ['escape','q']:
        win.close()
        core.quit()

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


#============================================================
# INSTRUCTIONS
#============================================================
#if paradigm_type=='eeg':
#   port = parallel.ParallelPort(address=53504)

welcome_txt.draw()
adv_screen_txt.draw()
win.flip()
adv = event.waitKeys(keyList=[key, 'escape', 'q'])
if adv[0] in ['escape', 'q']:
        win.close()
        core.quit()
instruction_loop(instr_strs, intro=True)
win.flip()

#============================================================
# TRAINING
#============================================================
#if paradigm_type=='eeg':
#    port.setData(0) # sets all pins low
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
    responses = []
    resp_pos = []
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
    #   NOTE: need to run this outside the function the first time to initialize
    win.flip                                # !!! to lock timing before first frame.
    trial_clock.reset()                                                       # In loop as temp variables, may exg to variable file
    trial_start = trial_clock.getTime()    
    target_time = trial_start + interval_dur
    feedback_start = trial_start + interval_dur + feedback_delay
    feedback_end = feedback_start + feedback_dur
    ITI = np.max(ITIs)
    win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial_n,win.lastFrameT),logging.INFO)

    #========================================================
    # Moving Ball
    moving_ball(None, trial_n, training=True)
    
    #========================================================
    # Feedback Delay
    feedback_delay_func(responses, None, trial_n, training=True)
    
    #========================================================
    # Calculate Feedback
    calc_feedback(None, condition, trial_n, training=True)
    
    #========================================================
    # ITI
    win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format('T',trial_n,ITI,win.lastFrameT),logging.INFO)
    
#    if paradigm_type=='eeg':
#        win.callOnFlip(port.setData, 0)
    win.flip()
    # Staircase Tolerance
    staircase(condition)
    while trial_clock.getTime() < feedback_end + ITI:
        for press in event.getKeys(keyList=[key,'escape','q']):
            if press in ['escape','q']:
                win.close();
                core.quit();
    if (trial_n==n_fullvis+n_training-1) or (trial_n==n_fullvis+2*n_training-1):                    #Score instructions with score after easy training
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
        responses = []
        resp_pos = []
        
        #========================================================
        # Set Trial Timing
        set_trial_timing(trial_clock, block_n, condition, trial_n)
        
        #========================================================
        # Moving Ball
        moving_ball(block_n, trial_n, training=False)
        
        #========================================================
        # Feedback Delay
        feedback_delay_func(responses, block_n, trial_n, training=False)
        
        #========================================================
        # Feedback
        # Calculate Feedback
        calc_feedback(block_n, condition, trial_n, False)
        
        #========================================================
        # ITI
        win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format(block_n,trial_n,ITI,win.lastFrameT),logging.INFO)
        
#        if paradigm_type=='eeg':
#            win.callOnFlip(port.setData, 0)
        win.flip()
        staircase(condition)
        while trial_clock.getTime() < feedback_end + ITI:
            for press in event.getKeys(keyList=[key,'escape','q']):
                if press in ['escape','q']:
                    win.close();
                    core.quit();
    
    #========================================================
    # Break Between Blocks
    surp_cnt += 1
    surp_sound_index += 1 
    block_break(block_n)

endgame_txt.draw()
win.flip()
core.wait(10)

win.close()
core.quit()

