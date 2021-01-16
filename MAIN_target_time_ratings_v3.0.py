from psychopy import logging, prefs
prefs.general['audioLib'] = ['PTB']
#logging.console.setLevel(logging.DEBUG)  # get messages about the sound lib as it loads

from psychopy import visual, event, core, gui, data, sound
from psychopy.tools.coordinatetools import pol2cart
import sys, os

import numpy as np
import math, time, random, copy
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
print('Using {0}(with {1}) for audioLib(with audioDriver)'.format(sound.audioLib, sound.audioDriver))
bad_fb_onset_cnt = 0

#============================
# DEFINE PARADIGM FUNCTIONS
#============================
def instruction_loop(instrs, intro=False):
    image_index = 0
    # displays instructions for current trial type
    # If intro=True, instrs won't be used (can just be '') 
    if instrs == rating_intro_str:
        print('Rating instr loop: ', instrs)
        instr_txt.text = instrs[0]
        instr_pic.image = 'cyclone_pics/rating_scale.png'
        instr_pic.draw()
        instr_txt.draw()
        adv_btn.draw()
        adv_screen_txt.draw()
        win.flip()
        instr_key_check()
    elif instrs!= main_str:
        for instr_str in instrs:
            instr_txt.text = instr_str
            if image_index <= 6 and intro:
                instr_pic.image = 'cyclone_pics/{0}'.format(instr_pic_dict[image_index])
                instr_pic.draw()
                image_index += 1
            if not intro:
                instr_pic.image = 'cyclone_pics/{0}'.format(instr_pic_dict[condition])
                instr_pic.draw()
            
            instr_txt.draw()
            adv_btn.draw()
            adv_screen_txt.draw()
            win.flip()
            instr_key_check()
    else:
        print('Main instr loop: ', instrs)
        instr_txt.text = instrs[0]
        instr_txt.pos = (0,2)
        instr_txt.draw()
        adv_btn.draw()
        adv_screen_txt.draw()
        win.flip()
        instr_key_check()
        core.wait(post_instr_delay)     # let them prep before hitting them with interval_dur

#===================================================
def instr_key_check(check_time=0.05):
    event.clearEvents()
    mouse.clickReset()
    mouse.setPos([0,-8])    # move mouse off the button so they can't just click through super fast
    while not mouse.isPressedIn(adv_btn):
        # Check for quit keys
        for press in event.getKeys(keyList=['escape','q']):
            if press:
                clean_quit()
        core.wait(check_time)
    core.wait(check_time)

#===================================================
def moving_ball(block_n, trial_n, training=False):
    # Reset mouse times on stim onset
    win.callOnFlip(mouse.clickReset)
    win.callOnFlip(event.clearEvents)
    buttons = []
    rts = []
    prev_btn_status = [0, 0, 0]
    curr_btn_status = [0, 0, 0]
    
    # Draw Stimuli
    for circ_xi in range(n_circ-1):# - sum(hidden_pos[covered])):
        target_zone_draw()
        if circ_xi == 0:
            circ_colors[n_circ-1] = (1,1,1)
        if circ_xi >= (n_circ - sum(hidden_pos[covered])):
            circ_colors[circ_xi] = (0,0,0)
        else:
            circ_colors[circ_xi] = (1,1,1)      # Turn light on
        circles.colors = circ_colors
        circles.draw()
        win.flip()
        if circ_xi==0:
            trial_start = exp_clock.getTime()
        
        circ_colors[n_circ-1] = (-1,-1,-1)
        circ_colors[circ_xi] = flip_list[circ_xi]  # Turn light back off
        circles.colors = circ_colors
        
        # Check for responses until this light should turn off
        while exp_clock.getTime() < trial_start + circ_start[circ_xi]:
            curr_btn_status, tmp_rt = mouse.getPressed(getTime=True)
            if curr_btn_status != prev_btn_status:    # Check if button status changed
                # Log which button and RT only if clicked down (not released)
                for b_ix, b in enumerate(curr_btn_status):
                    if b == 1 and b != prev_btn_status[b_ix]:
                        buttons.append(b_ix)
                        rts.append(tmp_rt)
                prev_btn_status = curr_btn_status
    
    #========================================================
    # Rating Delay- wait to capture as many responses as possible before starting rating
    # Turn off stimuli for feedback_delay
    target_zone_draw()
    win.flip()
    while exp_clock.getTime() < trial_start + interval_dur + rating_delay - feedback_compute_dur:
        curr_btn_status, tmp_rt = mouse.getPressed(getTime=True)
        if curr_btn_status != prev_btn_status:    # Check if button status changed
            # Log which button and RT only if clicked down (not released)
            for b_ix, b in enumerate(curr_btn_status):
                if b == 1 and b != prev_btn_status[b_ix]:
                    buttons.append(b_ix)
                    rts.append(tmp_rt)
            prev_btn_status = curr_btn_status
    
    print('mouse data for B{0} T {1}:'.format(block_n, trial_n), buttons, rts)
    return trial_start, buttons, rts

#===================================================
def subjective_rating(block_n, trial_n, condition, trial_start, training=False):
#    event.clearEvents()
#    mouse.clickReset()
#    rating_scale.reset()
#    
#    # Show scale & update until a response has been made or max_rating_time
#    rating_scale.draw()
#    rating_instr_txt.draw()
#    win.flip()
#    
#    rating_time_out = False
#    while rating_scale.noResponse and not rating_time_out:
#        core.wait(0.1)
#        if exp_clock.getTime() > trial_start + interval_dur + rating_delay + max_rating_time:
#            rating_time_out = True
#        for press in event.getKeys(keyList=['escape','q']):
#            if press:
#                clean_quit()
#    
#    # Check for responses
#    rating_data = rating_scale.getRating()
#    rating_rt = rating_scale.getRT()
#    if rating_time_out:
#        rating_rt = max_rating_time
#        if training:
#            win.logOnFlip(rating_time_out_str.format('T',trial_n),logging.DATA)
#        else:
#            win.logOnFlip(rating_time_out_str.format(block_n,trial_n),logging.DATA)
#    
#    # Log rating data
#    if training:
#        win.logOnFlip(rating_str.format('T',trial_n,rating_data,rating_rt,condition,tolerances[condition]),logging.DATA)
#    else:
#        win.logOnFlip(rating_str.format(block_n,trial_n,rating_data,rating_rt,condition,tolerances[condition]),logging.DATA)
#    win.flip()
    rating_rt = 1
    return rating_rt

#===================================================
def feedback_fn(block_n, condition, trial_n, trial_start, rating_rt, buttons, rts, training=False):
    global training_score
    global bad_fb_onset_cnt
    surp = False
    
    # Process responses
    if any(rts):
        if len(rts)>1:          # Warning if more than one button was pressed
            win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: responses = {2}'.format(
                            block_n, trial_n, rts),logging.WARNING)
        
        rt = rts[0]             # take only first response
        error = rt - interval_dur
        error_angle = error*angle_ratio
        if not training and trial_n in surprise_trials[block_n]:          # Surprise on if not in training and if in list of surprise trials  
            target_zone.setColor('blue')
            resp_marker.setLineColor(None)
            outcome_str = 'SURPRISE!'
            sound_file = select_surp_sound()
            surp = True
        elif np.abs(error)<tolerances[condition]:             # WIN
            target_zone.setColor('green')
            outcome_str = 'WIN!'
            sound_file = 'paradigm_sounds/{0}'.format(win_sound)
            win_flag = 0
        else:                                   # LOSS
            target_zone.setColor('red')
            outcome_str = 'LOSE!'
            sound_file = 'paradigm_sounds/{0}'.format(loss_sound)
            win_flag = 1
        resp_marker.setStart(pol2cart(error_angle+270, loop_radius-resp_marker_width/2))
        resp_marker.setEnd(pol2cart(error_angle+270, loop_radius+resp_marker_width/2))
    else:   # No response detected
        target_zone.setColor('red')
        outcome_str = 'None'
        rt=-1
        resp_marker.setLineColor(None)
        sound_file = 'paradigm_sounds/{0}'.format(loss_sound)
#        no_response_time = exp_clock.getTime()-trial_start
#        # Not adjusting tolerance for this type of trial...
    outcome_sound = sound.Sound(value=sound_file, sampleRate=44100, blockSize=block_sz, secs=0.8, stereo=1)
    outcome_sound.setVolume(0.8)
    
    # Present feedback
#    preflip = exp_clock.getTime()-trial_start
    win.callOnFlip(outcome_sound.play)
    for frameN in range(round(feedback_dur * 60)): #assuming frame_rate is close enough it would round to 60 (this must be an int)
        target_zone_draw()                      # Using our defined target_zone_draw, not .draw to have correct visual.  
        resp_marker.draw()
        win.flip()
        if frameN==0:
            feedback_onset = exp_clock.getTime()-trial_start
#            if feedback_onset > 1.793 or feedback_onset < 1.792:
#                bad_fb_onset_cnt += 1
#                print '{0} --> B{1}T{2} times:\n\tpreflip    {3}\n\tprewait    {4}\n\tdesired    {5}\n\tfeedback = {6}'.format(
#                    bad_fb_onset_cnt,block_n,trial_n,preflip,prewait,desired,feedback_onset)
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
    
    # Log outcomes and behavioral data
    if training:
        win.logOnFlip(feedback_str.format('T',trial_n,outcome_str,rt,condition,tolerances[condition]),logging.DATA)
        win.logOnFlip('B{0}_T{1} responses/times = {2} / {3}'.format('T', trial_n, buttons, rts),logging.DATA)
        win.logOnFlip('B{0}_T{1} SOUND = {2} feedback start: TIME = {3}'.format('T', trial_n, sound_file, feedback_onset),logging.DATA)
    else:
        win.logOnFlip(feedback_str.format(block_n,trial_n,outcome_str,rt,condition,tolerances[condition]),logging.DATA)
        win.logOnFlip('B{0}_T{1} responses/times = {2} / {3}'.format(block_n, trial_n, buttons, rts),logging.DATA)
        win.logOnFlip('B{0}_T{1} SOUND = {2} feedback start: TIME = {3}'.format(block_n, trial_n, sound_file, feedback_onset),logging.DATA)
    resp_marker.setLineColor('black')
    target_zone.setColor('dimgrey')
    while exp_clock.getTime() < trial_start + min_trial_dur + rating_rt:
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
    if block_n<len(block_order)-1:
        instr_txt.text = break_str.format(len(block_order)-block_n-1,break_min_dur)
        instr_txt.draw()
        win.flip()
        core.wait(break_min_dur)
        block_point_txt.draw()
        total_point_txt.draw()
        instr_txt.draw()
        adv_btn.draw()
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
    total_point_txt.text = total_point_str.format(sum(training_score.values()))
    if training_score[condition] >= 0:
        score_demo_txt.color = 'green'
        total_point_txt.color = 'green'
    else:
        score_demo_txt.color = 'red'
        total_point_txt.color = 'red'
    
    score_demo_txt.draw()
    total_point_txt.draw()
    if trial_n==n_fullvis+n_training-1:
        point_instr_txt.draw()
    adv_btn.draw()    
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
    sound_type = np.random.choice(list(block_sounds.keys()))                      # Selects the subfolder to draw sounds from (ie. 'breaks').
    sound_file = block_sounds[sound_type][block_n]                 # Selects the specific wav file from the subfolder.
    block_sounds.pop(sound_type)                                            # Don't use this sound type again in this block
    return sound_file

#===================================================
def clean_quit():
#    os.system("sudo /home/knight_lab/Startup_Scripts/python_priority_rush_off.sh")     # If using core.rush in Linux
    print('====================== CLEAN QUIT CALLED ======================')
    win.logOnFlip('---------- CLEAN QUIT CALLED ----------',logging.DATA)
    win.flip()
    
    win.close()
    core.quit()


#============================================================
# INSTRUCTIONS
#============================================================
welcome_txt.draw()
adv_btn.draw()
adv_screen_txt.draw()
win.flip()
instr_key_check()

instruction_loop(instr_strs, intro=True)
win.flip()

#============================================================
# TRAINING
#============================================================
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
        
    win.logOnFlip('TRAINING T{0}: window={1}; condition={2}'.format(trial_n,covered,condition),logging.DATA)
    event.clearEvents()
#    surp_cnt = 0
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
    core.wait(post_instr_delay)                                         # Delay so they aren't caught off guard
    
    #========================================================
    # Moving Ball
    trial_start, buttons, rts = moving_ball(None, trial_n, training=True)
    
    #========================================================
    # Get Trial Timing
    win.logOnFlip('TRAINING T{0} start: FRAME TIME = {1}'.format(trial_n,trial_start),logging.DATA)
    
    #========================================================
    # Collect Responses and Subjective Rating
    rating_rt = subjective_rating(None, trial_n, condition, trial_start, training=True)
    
    #========================================================
    # Feedback Delay
    while exp_clock.getTime() < trial_start + interval_dur + rating_delay + rating_rt + feedback_delay - feedback_compute_dur:
        core.wait(0.001)
    
    #========================================================
    # Feedback
    #print 'about to call feedback_fn; time into trial =  {0}'.format(exp_clock.getTime()-trial_start) #!!! remove after testing
    feedback_fn(None, condition, trial_n, trial_start, rating_rt, buttons, rts, training=True)
    
    #========================================================
    # ITI
    ITI = np.max(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
    win.logOnFlip('B{0}_T{1} ITI={2}; TIME = {3}'.format('T',trial_n,ITI,exp_clock.getTime()-trial_start),logging.DATA)
    win.flip()
    
    # Staircase Tolerance
    staircase(condition)
    while exp_clock.getTime() < trial_start + min_trial_dur + rating_rt + ITI:
        for press in event.getKeys(keyList=['escape','q', 'p']):
            if press in ['p']:
                pause_txt.draw()
                win.logOnFlip('PAUSE STARTED: B{0}_T{1}, TIME = {2}'.format('T', trial_n, exp_clock.getTime()),logging.DATA)
                win.flip()
                event.waitKeys(keyList=['p'])
                win.logOnFlip('PAUSE ENDED: B{0}_T{1}, TIME = {2}'.format('T', trial_n, exp_clock.getTime()),logging.DATA)
                core.wait(block_start_dur)
            else:
                clean_quit()
    if (trial_n==n_fullvis+n_training-1) or (trial_n==n_fullvis+2*n_training-1):    #Score instructions with score after easy training
        score_instr()


#============================================================
# EXPERIMENT
#============================================================
instruction_loop(rating_intro_str)                    # Rating instruction call 
instruction_loop(main_str)                    # Main instruction call 
# Constant Reward Function (start awarding points)
outcome_win.text = '+{0}'.format(point_fn[0])
outcome_loss.text = '{0}'.format(point_fn[1])
for block_n, block_type in enumerate(block_order[starting_block-1:],starting_block-1):
    block_sounds = surprise_sounds.copy()
#    surp_sound_index = 0
    condition = conditions[block_type]
    target_zone.visibleWedge = [0, target_upper_bound[condition]]
    target_zone.ori = target_origin[condition]
    block_start_txt.text = block_start_str.format(block_n+1, len(block_order), condition)
    block_start_txt.draw()
    win.logOnFlip('B{0} ({1}) Start Text: TIME = {2}'.format(block_n,condition,exp_clock.getTime()),logging.DATA)
    win.flip()
    core.wait(block_start_dur)
    win.flip()
    core.wait(post_instr_delay)                                         # Delay so they aren't caught off guard
    
    for trial_n in range(n_trials):
        #========================================================
        # Initialize Trial
        event.clearEvents()
        
        #========================================================
        # Moving Ball
        trial_start, buttons, rts = moving_ball(block_n, trial_n, training=False)
        
        #========================================================
        # Collect Responses and Subjective Rating
        rating_rt = subjective_rating(block_n, trial_n, condition, trial_start, training=True)
        
        #========================================================
        # Feedback Delay
        while exp_clock.getTime() < trial_start + interval_dur + rating_delay + rating_rt + feedback_delay - feedback_compute_dur:
            core.wait(0.001)
        
        #========================================================
        # Feedback
        #print 'about to call calc_feedback; time into trial =  {0}'.format(exp_clock.getTime()-trial_start)
        feedback_fn(block_n, condition, trial_n, trial_start, rating_rt, buttons, rts, False)
        
        #========================================================
        # ITI
        ITI = random.choice(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
        win.logOnFlip('B{0}_T{1} ITI={2}; TIME = {3}'.format(block_n,trial_n,ITI, exp_clock.getTime()-trial_start),logging.DATA)
        win.flip()
        
        staircase(condition)
        while exp_clock.getTime() < trial_start + min_trial_dur + rating_rt + ITI:
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
    
    #========================================================
    # Break Between Blocks
#    surp_cnt += 1
#    surp_sound_index += 1 
    block_break(block_n)

endgame_txt.draw()
win.flip()
core.wait(end_screen_dur)

clean_quit()
