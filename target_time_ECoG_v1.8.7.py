# target_time_ECoG_v1.8.7
paradigm_version = '1.8.7'
# 1.8.7: added pause function (based on Aditya edits); small instr clarification about restarting for more practice
# 1.8.6: transition to ECoG specific; n_blocks=2; block_order=EEHH; photodiode square
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
n_examples = 2#5                     # number of EASY examples to start (large tolerance, full window)
n_training = 2#15                     # number of training trials PER CONDITION
n_blocks = 2                        # number of blocks of trials PER CONDITION
n_trials = 2#75                       # number of trials PER BLOCK

interval_dur = 1                    # duration (in sec) of target time interval
feedback_delay = 0.8                # duration (in s) of delay between end of interval and feedback onset
feedback_dur = 0.8                    # duration (in s) of feedback presentation
ITIs = [0.2, 0.4, 0.7, 1.0]         # length of inter-trial intervals (in s)
break_min_dur = 30                  # minimum length (in s) for the break between blocks
post_instr_delay = 1                # duration of delay (in s) after instructions/break to make sure they're ready
post_pause_delay = 0.5              # duration of delay (in s) after unpausing to make sure they're ready
block_start_dur = 2                 # duration (in s) to display block start text (e.g., "Level _: type")

tolerances = {'easy':0.125,           # Tolerance (in s) on either side of the target interval 
             'hard':0.05}            # e.g., interval-tolerance < correct_RT < interval+ tolerance
tolerance_step = {'easy': [-0.003,0.012],
                    'hard': [-0.012,0.003]} # adjustment (in s) for [correct,incorrect] responses
tolerance_lim = [0.2, 0.015]

key = 'space'                       # Response key (eventually will be assigned in dialogue box)
full_screen = True                 # Make the window full screen? (True/False)
#screen_to_show = 1                 # Select which screen to display the window on
screen_units = 'cm'                 # Set visual object sizes in cm (constant across all screens)

# Stimulus Parameters
game_height = 25                    # amount of screen for plotting
interval_height = 0.7*game_height   # % of game_height over which interval_dur occurs
target_y = 5                        # position of target in y coordinates
#use_window = True                   # if False, all ball positions are visible (e.g., goes on top of bullseye)
covered_portion = 0.6               # % of interval height obscured by the window when use_window=True
tower_width = 0.4*interval_height   # Width of the tower containing the window (with target at top)
ball_radius = 0.35                  # Radius of the moving ball stimulus
window_width = 0.8                  # Width of the window around the ball (ideally > ball_radius)
#xhr_thickness = 5                  # Thickness of the crosshair on top of the bullseye
resp_marker_width = ball_radius*3   # Width of the response marker (marks where they pressed the button)
resp_marker_thickness = 4           # Thickness of the response marker
n_rings = {'easy': 7,               # number of rings in the bullseye for each condition
           'hard': 5}
trial_types = ['easy', 'hard']      # labels of the trial conditions
color_list = ['white','black']      # alternating colors of the bullseye: [center, next_level, center, ...]
trigger_rect_height = 150           # height of the photodiode trigger rectangle IN PIXELS (based on 1920x1080 screen)
trigger_dur = 0.3
point_fn = [100, -100]              # reward function determining points awarded for [correct, incorrect]

#============================================================
# SET UP LOG FILE
#============================================================
file_dlg = gui.Dlg(title="Run Information")
file_dlg.addField('SBJ Code:')
#file_dlg.addField('Response Key:') # Ideally space bar? something more accurate?

file_dlg.show()
if gui.OK:
    dlg_resp = file_dlg.data
    log_prefix = dlg_resp[0]
    #key = dlg_resp[1] !!! fix this!!!
    log_filename = '../logs/{0}_response_log_{1}.txt'.format(log_prefix,exp_datetime)
else: 
    print 'User Cancelled'
    win.close()
    core.quit()


#============================================================
# SET EXPERIMENTAL VARIABLES
#============================================================
# Environment Variables
win = visual.Window(size=(1920,1080), fullscr=full_screen, color=(0,0,0),
                    monitor='testMonitor',# screen=screen_to_show,
                    allowGUI=False, units=screen_units)#, waitBlanking=False); # !!! check on this waitBlank parameter!
#NOTE: ECoG laptop size = 36cm wide, 20sm tall
print 'Window size = ', win.size
exp_clock = core.Clock()
trial_clock = core.Clock()
block_order = np.array([0, 0, 1, 1])#np.random.permutation([b for b in [0, 1] for _ in range(n_blocks)])
#!!! consider counterbalancing future participants
#def count_check(some_array):    #function that takes an array as argument and returns an array with the count of 
#    result_list = np.array([])  #consecutive numbers that are same. For eg [0,0,0,1,0,1,1] would return [3,1,1,2]
#    current = some_array[0]
#    count = 0 
#    for value in some_array:
#        if value == current:
#            count += 1
#        else:
#            result_list = np.append(result_list, count)
#            current = value
#            count = 1 
#    result_list = np.append(result_list,count)
#    return result_list
#
#result_list = count_check(block_order)
#while len(result_list[result_list >= 3]) != 0:      #checks for 3 or more consecutive same numbers. If present, will recompute permutation till less than 3 present
#            block_order = np.random.permutation([b for b in [0, 1] for _ in range(4)])
#            result_list = count_check(block_order)
print 'block_order = ', block_order

# Feedback Stimuli
bullseyes       = {}
bullseye_height = {}   # height of target+/- tolerance in screen_units
bullseye_radii  = {}
min_bullseye_radius = tolerance_lim[1]*interval_height/interval_dur
bullseye_colors = [color_list[np.mod(ix,2)] for ix in range(n_rings['easy'])]   # use longer list for both
for trial_type in trial_types:
    bullseye_height[trial_type] = interval_height*tolerances[trial_type]/interval_dur
    bullseye_radii[trial_type] = np.linspace(min_bullseye_radius, bullseye_height[trial_type], num=n_rings[trial_type])
#    print trial_type, ' bullseye: ', zip(bullseye_radii[trial_type],bullseye_colors)
    bullseyes[trial_type] = [visual.Circle(win, radius=radius, pos=[0,target_y],
                            fillColor=color, lineColor=None,
                            name='bullseye_{0}'.format(trial_type))\
                            for radius, color in zip(bullseye_radii[trial_type],bullseye_colors)]

# Aditya code here:
# xhr = _____

points = np.zeros(n_blocks*len(trial_types))       # point total for each block
outcome_win = visual.TextStim(win,text='Win!',height=2,units='cm',  #{'easy': 
                                name='feedback_win', color='green',pos=(0,0))
#               'hard': visual.TextStim(win,text='+300',height=2,units='cm',
#                                name='feedback_win', color='green',pos=(0,0))}
outcome_loss = visual.TextStim(win,text='Lose!',height=2,units='cm',
                                name='feedback_loss', color='red',pos=(0,0))#wrapWidth=550,
feedback_str = 'B{0}_T{1}: Outcome={2}; RT = {3}; trial_type = {4}; tolerance = {5}'
feedback_txt = visual.TextStim(win,text='',height=1,units='cm',
                                name='feedback_timing', color='black',pos=(0,-3),wrapWidth=14)
resp_marker = visual.Line(win, start=(-resp_marker_width/2, target_y),
                                end=(resp_marker_width/2, target_y),
                                lineColor='blue', lineWidth=resp_marker_thickness)
# Aditya , modify what's down here:
#late_arrow = []
#late_arrow.append(visual.Rect(win, lineColor='red', fillColor='red', lineWidth=2.0,
#                 width=ball_radius/2, height=0.05, pos= [0,(game_height/2)-0.1], ori=0))
#print 'late_arrow pos and height: ', late_arrow[0].pos, late_arrow[0].height
#late_arrow.append(visual.Polygon(win, edges=3, lineColor='red', fillColor='red',# lineWidth=2.0,
#                 radius=ball_radius*1.5, pos= [0,late_arrow[0].pos[1]-late_arrow[0].height/2], ori=0))

# Tower
tower = visual.Rect(win, width=tower_width, height=interval_height,
                        pos=(0,target_y-interval_height/2),
                        fillColor='gray', lineColor='black',
                        opacity=0.75, name='tower')

# Window into tower
windows = {True: visual.Rect(win, width=window_width, height=interval_height*(1-covered_portion),
                        pos=(0,target_y-(interval_height*covered_portion)-(interval_height*(1-covered_portion)/2)),
                        fillColor='black', lineColor=None,
                        opacity=0.5, name='window'),
           False: visual.Rect(win, width=window_width, height=interval_height,
                        pos=(0,target_y-interval_height/2),
                        fillColor='black', lineColor=None,
                        opacity=0.5, name='window')}
window_tops = {True: target_y-(interval_height*covered_portion),
                False: target_y}
assert not bullseyes['easy'][-1].contains(x=0,y=window_tops[True])     # top of window doesn't hit the bullseye

# Ball Timing
frame_len = win.monitorFramePeriod                                      # time for one window flip in this system
n_int_flips = int(np.ceil(float(interval_dur)/frame_len))               # number of flips in interval_dur
#!!! this is very bad!!! I need to make sure everyone has the exact same interval!!!
print 'Visual interval  = {0}; n_interval_flips = {1}'.format(n_int_flips*frame_len, n_int_flips)
#!!! check if n_trials/N-blocks==integer

# Ball Stimuli
interval_vlim = [target_y-interval_height, target_y]        # vertical limits of the interval in screen units
assert interval_vlim[0] >= -game_height/2                   # make sure interval is within the game screen

ball_ys, ball_step = np.linspace(interval_vlim[0], interval_vlim[1], n_int_flips, retstep=True)
balls = [visual.Circle(win, radius=ball_radius, fillColor='blue', lineColor='white',
                        pos=[0,ball_y], autoDraw=False) for ball_y in ball_ys]
hidden_pos = {True: [(ball_y > window_tops[True]-ball_radius/2) for ball_y in ball_ys],
              False: [(ball_y > window_tops[False]-ball_radius/2) for ball_y in ball_ys]}

# Photodiode Trigger Rectangle
trigger_rect = visual.Rect(win, width=trigger_rect_height, height=trigger_rect_height, units='pix',
                            fillColor='white', pos=(trigger_rect_height/2-win.size[0]/2,trigger_rect_height/2-win.size[1]/2)) #pos based on 1920x1080 pixel screen

# Instructions
instr_strs = ['This game starts with a ball moving up the tower towards a bullseye target.\n'+\
               'Your goal is to respond at the exact moment when the ball hits the middle of the target.',
               "The time from the ball's start to the center of the target is always the same, "+\
               'so the perfect response will always be at that exact time: the Target Time!',
               'You win points if you respond when the ball is on the target.\n',#+\
#               'Responding closer to the target time gets you more points!',
               'You lose points if you respond too early or too late and the ball misses the target.',
               "Let's get started with a few examples..."]
train_str = {'easy': "Good job! From now on, the last part of the ball's movement will be hidden.\n"+\
                    "That means you need to respond at the target time without seeing the ball go all the way up.\n"+\
                    "Let's try some more examples...",
             'hard': "Great, now you're ready to try the hard level!\n"+\
                    "Don't get discouraged - hard levels are designed to make you miss most of the time.\n"+\
                    "Challenge yourself to see how many you can win!\nLet's try some examples..."}
main_str = "Ready to try the real deal and start keeping score?\n"+\
            "You'll do {0} easy and {0} hard blocks of {1} trials each.\n".format(n_blocks,n_trials)+\
            'Press Q/escape to restart for more practice rounds,\n'+\
            'or press {0} to start playing Target Time!'.format(key)
block_start_str = 'Level {0}/{1}: {2}'
break_str = 'Great work! {0} blocks left. Take a break to stretch and refresh yourself for at least {1} seconds.'
block_point_str = 'Level {0} Score: {1}'
total_point_str = 'Total Score: {0}'

welcome_txt = visual.TextStim(win,text='Welcome to\nTarget Time!',height=4,units='cm',alignHoriz='center',alignVert='center',
                                name='welcome', color='black', bold=True, pos=(0,2),wrapWidth=30)
instr_txt = visual.TextStim(win,text=instr_strs[0],height=2,units='cm', alignVert='center',
                                name='instr', color='black',pos=(0,0),wrapWidth=50)
adv_screen_txt = visual.TextStim(win,text='Press {0} to advance or Q/escape to quit...'.format(key),
                                height=1.5,units='cm',name='adv_screen', color='black', pos=(0,-7),wrapWidth=50)
pause_screen_txt = visual.TextStim(win,text="Game paused, press P to continue or Q/esc to quit.".format(key),
                                height=1.5,units='cm',name='adv_screen', color='black', pos=(0,0),wrapWidth=50)
block_start_txt = visual.TextStim(win,text=block_start_str,height=3,units='cm',alignHoriz='center',alignVert='center',
                                name='block_start', color='black', bold=True, pos=(0,2),wrapWidth=40)
block_point_txt = visual.TextStim(win,text=block_point_str,height=1.5,units='cm', alignVert='center',
                                name='block_points', color='black',pos=(0,8),wrapWidth=20)
total_point_txt = visual.TextStim(win,text=total_point_str,height=1.5,units='cm', alignVert='center',
                                name='total_points', color='black',pos=(0,4),wrapWidth=20)
endgame_txt = visual.TextStim(win,text="Fantastic!!! You're all done. Thank you so much for participating in this experiment!",
                            height=2,units='cm',alignHoriz='center',alignVert='center',
                            name='endgame', color='black', bold=False, pos=(0,-4),wrapWidth=40)

#!!! come back and rethink what I need here for checks and printing to save out
#print 'interval_vlim = ', interval_vlim
#print 'tower_vlim = ', cover_vlim
#print 'target_vlim = ', target_vlim
#print 'ball_ys = [{0} - {1}]; len(ball_ys) = {2}'.format(ball_ys[0],ball_ys[-1], len(ball_ys))
#print 'interval_vlim top - int_flips*ball_step = ',\
#                interval_vlim[0]+(ball_step*n_int_flips), '(', n_int_flips, ',', ball_step, ')'
#assert np.max(ball_ys) <= cover_vlim[1]             # all balls hidden
#assert cover_vlim[1] >= np.max(np.max(target_vlim)) # make sure the bottom of the interval is covered

#============================
# LOG PARADIGM PARAMETERS
#============================
logging.setDefaultClock(exp_clock)                                       #use this for
logging.console.setLevel(logging.DATA)                               #do NOT set to INFO! Way too much logging, crashes system
logger = logging.LogFile(log_filename,logging.DATA,'w')
win.setRecordFrameIntervals(True)                                    #capture frame intervals
win.saveFrameIntervals(fileName=log_filename, clear=False)           #write frame intervals to log_filename

#Vars to log:
#key,full_screen,screen_to_show,screen_units,use_window,xhr_thickness
win.logOnFlip('paradigm_name = '+str(paradigm_name), logging.DATA)
win.logOnFlip('paradigm_version = '+str(paradigm_version), logging.DATA)
win.logOnFlip('n_blocks = '+str(n_blocks), logging.DATA)
win.logOnFlip('n_trials = '+str(n_trials), logging.DATA)
win.logOnFlip('n_examples = '+str(n_examples), logging.DATA)
win.logOnFlip('n_training = '+str(n_training), logging.DATA)
win.logOnFlip('interval_dur = '+str(interval_dur), logging.DATA)
win.logOnFlip('feedback_delay = '+str(feedback_delay), logging.DATA)
win.logOnFlip('feedback_dur = '+str(feedback_dur), logging.DATA)
win.logOnFlip('ITIs = '+str(ITIs), logging.DATA)
win.logOnFlip('break_min_dur = '+str(break_min_dur), logging.DATA)
win.logOnFlip('post_instr_delay = '+str(post_instr_delay), logging.DATA)
win.logOnFlip('block_start_dur = '+str(block_start_dur), logging.DATA)
win.logOnFlip('tolerances = '+str(tolerances), logging.DATA)
win.logOnFlip('tolerance_step = '+str(tolerance_step), logging.DATA)
win.logOnFlip('tolerance_lim = '+str(tolerance_lim), logging.DATA)
win.logOnFlip('Key = '+str(key), logging.DATA)
win.logOnFlip('full_screen = '+str(full_screen), logging.DATA)
win.logOnFlip('screen_units = '+str(screen_units), logging.DATA)
win.logOnFlip('game_height = '+str(game_height), logging.DATA)
win.logOnFlip('interval_height = '+str(interval_height), logging.DATA)
win.logOnFlip('target_y = '+str(target_y), logging.DATA)
win.logOnFlip('covered_portion = '+str(covered_portion), logging.DATA)
win.logOnFlip('tower_width = '+str(tower_width), logging.DATA)
win.logOnFlip('ball_radius = '+str(ball_radius), logging.DATA)
win.logOnFlip('window_width = '+str(window_width), logging.DATA)
win.logOnFlip('resp_marker_thickness = '+str(resp_marker_thickness), logging.DATA)
win.logOnFlip('resp_marker_width = '+str(resp_marker_width), logging.DATA)
win.logOnFlip('n_rings = '+str(n_rings), logging.DATA)
win.logOnFlip('trial_types = '+str(trial_types), logging.DATA)
win.logOnFlip('color_list = '+str(color_list), logging.DATA)
win.logOnFlip('trigger_rect_height = '+str(trigger_rect_height), logging.DATA)
win.logOnFlip('trigger_dur = '+str(trigger_dur), logging.DATA)
win.logOnFlip('win.size = '+str(win.size), logging.DATA)
win.logOnFlip('frame_len = '+str(frame_len), logging.DATA)
win.logOnFlip('point_fn = '+str(point_fn), logging.DATA)

exp_clock.reset()
win.logOnFlip('CLOCK RESET FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA)
win.flip()


#============================================================
# INSTRUCTIONS
#============================================================
#win.logOnFlip('Instructions FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA)
welcome_txt.draw()
adv_screen_txt.draw()
win.flip()
adv = event.waitKeys(keyList=[key, 'escape', 'q'])
if adv[0] in ['escape', 'q']:
    win.close()
    core.quit()
for instr_str in instr_strs:
    instr_txt.text = instr_str
    instr_txt.draw()
    adv_screen_txt.draw()
    win.flip()
    adv = event.waitKeys(keyList=[key, 'escape','q'])
    print adv
    if adv[0] in ['escape','q']:
        win.close()
        core.quit()
#win.logOnFlip('Instruction Response: {0}, FRAME TIME = {1} for response, win.lastFrameT={2}'.format(
#                response[0][0], response[0][1], win.lastFrameT), logging.DATA);
win.flip()

#============================================================
# TRAINING
#============================================================

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
        instr_txt.text = train_str[trial_type]
        instr_txt.draw()
        instr_txt.draw()                                                # Something crazy here, 1st gets squished so draw again to get squished+real
        adv_screen_txt.draw()
        win.flip()
        adv = event.waitKeys(keyList=[key, 'escape','q'])
        if adv[0] in ['escape','q']:
            win.close()
            core.quit()
        core.wait(post_instr_delay)                                         # Delay so they aren't caught off guard
    
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
    
    #========================================================
    # Moving Ball
    for pos_ix in range(n_int_flips-sum(hidden_pos[use_window])):
        # Drawing Order (back-to-front): (outlines?), tower, window, ball, bullseye 
        tower.draw()
        window.draw()
        for eye in reversed(bullseye):  #draw them all in reverse order
            eye.draw()
        balls[pos_ix].draw()
        if trial_clock.getTime() < trigger_dur:
            trigger_rect.draw()
        win.flip()
        response = event.getKeys(keyList=[key,'p'], timeStamped=trial_clock)  #!!! responses here still tied to flips?
        if len(response)>0:
            if response[0][0]=='p':
                pause_start = exp_clock.getTime()
                pause_trial_time = trial_clock.getTime()
                win.logOnFlip('PAUSED during BT_T{0} moving ball: trial_clock={1} and FRAME TIME = {2}'.format(\
                    trial,pause_trial_time,pause_start),logging.DATA)
                pause_screen_txt.draw()
                win.flip()
                unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                if unpause[0][0] in ['q','escape']:
                    win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                    win.flip()
                    win.close()
                    core.quit()
                else:
                    trial_clock.reset(newT=pause_trial_time)
                    win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                    win.flip()
#                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
            else:
                responses.append(response)
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial,response,win.lastFrameT),logging.DATA)
                response = []
    
    #========================================================
    # Feedback Delay
    tower.draw()
    window.draw()
    for eye in reversed(bullseye):  #draw them all in reverse order
        eye.draw()
    win.logOnFlip('TRAINING T{0} feedback_delay starts: total time = {1:.3f}, trial time = {2:.3f}'.format(
                                                trial,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
    win.flip()
    while trial_clock.getTime()<feedback_start:
        response = event.getKeys(keyList=[key,'p'], timeStamped=trial_clock)
        if len(response)>0:
            if response[0][0]=='p':
                pause_start = exp_clock.getTime()
                pause_trial_time = trial_clock.getTime()
                win.logOnFlip('PAUSED during BT_T{0} feedback_delay: trial_clock={1} and FRAME TIME = {2}'.format(\
                    trial,pause_trial_time,pause_start),logging.DATA)
                pause_screen_txt.draw()
                win.flip()
                unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                if unpause[0][0] in ['q','escape']:
                    win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                    win.flip()
                    win.close()
                    core.quit()
                else:
                    trial_clock.reset(newT=pause_trial_time)
                    # Redraw the delay background
                    tower.draw()
                    window.draw()
                    for eye in reversed(bullseye):  #draw them all in reverse order
                        eye.draw()
                    win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                    win.flip()
#                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
            else:
                responses.append(response)
                win.logOnFlip('TRAINING T{0} Response: {1}, FRAME TIME = {2}'.format(trial,response,win.lastFrameT),logging.DATA)
                response = []
    win.logOnFlip('TRAINING T{0} feedback delay end: {1:.5f}; offset error = {2:.5f}'.format(trial,trial_clock.getTime(),
                                                                trial_clock.getTime()-interval_dur-feedback_delay-trial_start),logging.INFO)
    
    #========================================================
    # Feedback
    # Calculate Feedback
    tower.draw()
    window.draw()
    for eye in reversed(bullseye):  #draw them all in reverse order
        eye.draw()
    if len(responses)>0:
        if len(responses)>1:
            win.logOnFlip('WARNING!!! More than one response detected (taking first) on T{0}: repsonses = {1}'.format(
                                trial, responses),logging.WARNING)
        response = responses[0]         # take the first response
        RT = response[0][1]-trial_start
        error = interval_dur-RT
        error_height = error*interval_height/interval_dur
        
        # Draw Feedback -- No adjustments during training
        #feedback_txt.text = feedback_str.format(RT, interval_dur, tolerances[trial_type])
        if np.abs(error)<tolerances[trial_type]:            # WIN
            outcome_win.draw()
            resp_marker.setLineColor('green')
            outcome_str = 'WIN!'
            tolerance_step_ix = 0
        else:                                               # LOSS
            outcome_loss.draw()
            resp_marker.setLineColor('red')
            outcome_str = 'LOSE!'
            tolerance_step_ix = 1
        resp_marker.setStart((-resp_marker_width/2, interval_vlim[1]-error_height))
        resp_marker.setEnd((resp_marker_width/2, interval_vlim[1]-error_height))
        resp_marker.draw()
        
        # Logging Data
        win.logOnFlip(feedback_str.format('T',trial,outcome_str,RT,trial_type,tolerances[trial_type]),logging.DATA)
        tolerances[trial_type]+= tolerance_step[trial_type][tolerance_step_ix]
        if tolerances[trial_type] > tolerance_lim[0]:
            tolerances[trial_type] = tolerance_lim[0]
        elif tolerances[trial_type] < tolerance_lim[1]:
            tolerances[trial_type] = tolerance_lim[1]
#        print 'resp={0:.3f}, start={1:.3f}, target=[{2:.3f}-{3:.3f}], feedback_start={4:.3f},
#                                                            RT={5:.3f}, flip_time = {6:.3f}'.format(
#                                                            responses[0][0][1], trial_start, target_tlim[0],
#                                                            target_tlim[1], feedback_start,RT, flip_times[resp_pos[0]])
#        print 'target = {0}; resp_marker = {1}'.format(interval_vlim[1],
#                                                interval_vlim[1]-error_height)#, str='; tolerances[trial_type] = [{2}, {3}] = {4}'
#                                                target_zone.vertices[0][1],target_zone.vertices[2][1],
#                                                target_zone.vertices[2][1]/target_zone.vertices[0][1])
    else:
        outcome_loss.draw()
        #feedback_txt.text = 'No response detected!'
        outcome_str = 'None'
        win.logOnFlip(feedback_str.format('T',trial,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
    #feedback_txt.draw()
    trigger_rect.draw()
    win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format('T',trial,win.lastFrameT),logging.INFO)
    win.flip()
    while trial_clock.getTime() < feedback_end:
        for press in event.getKeys(keyList=[key,'escape','q','p']):
            if press=='p':
                pause_start = exp_clock.getTime()
                pause_trial_time = trial_clock.getTime()
                win.logOnFlip('PAUSED during BT_T{0} feedback: trial_clock={1} and FRAME TIME = {2}'.format(\
                    trial,pause_trial_time,pause_start),logging.DATA)
                pause_screen_txt.draw()
                win.flip()
                unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                if unpause[0][0] in ['q','escape']:
                    win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                    win.flip()
                    win.close()
                    core.quit()
                else:
                    trial_clock.reset(newT=pause_trial_time)
                    # Redraw Feedback
                    tower.draw()
                    window.draw()
                    for eye in reversed(bullseye):  #draw them all in reverse order
                        eye.draw()
                    resp_marker.draw()
                    if outcome_str=='WIN!':
                        outcome_win.draw()
                    else:
                        outcome_loss.draw()
                    win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                    win.flip()
#                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
            elif press in ['escape','q']:
                win.close()
                core.quit()
    
    #========================================================
    # ITI
#    print 'ITI ({0}) start = {1:.5f}; error = {2:.5f}'.format(ITI, trial_clock.getTime(),
#                                   trial_clock.getTime()-interval_dur-feedback_delay-feedback_dur-trial_start)
    win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format('T',trial,ITI,win.lastFrameT),logging.INFO)
    win.flip()
    
    # Staircase Tolerance
    bullseye_height[trial_type] = interval_height*tolerances[trial_type]/interval_dur
    bullseye_radii[trial_type] = np.linspace(min_bullseye_radius, bullseye_height[trial_type], num=n_rings[trial_type])
    for eye_ix, eye in enumerate(bullseyes[trial_type]):
        eye.radius = bullseye_radii[trial_type][eye_ix]
    
    while trial_clock.getTime() < feedback_end + ITI:
        for press in event.getKeys(keyList=[key,'escape','q','p']):
            if press=='p':
                pause_start = exp_clock.getTime()
                pause_trial_time = trial_clock.getTime()
                win.logOnFlip('PAUSED during BT_T{0} ITI: trial_clock={1} and FRAME TIME = {2}'.format(\
                    trial,pause_trial_time,pause_start),logging.DATA)
                pause_screen_txt.draw()
                win.flip()
                unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                if unpause[0][0] in ['q','escape']:
                    win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                    win.flip()
                    win.close()
                    core.quit()
                else:
                    trial_clock.reset(newT=pause_trial_time)
                    win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                    win.flip()
#                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
            elif press in ['escape','q']:
                win.close();
                core.quit();

#============================================================
# EXPERIMENT
#============================================================
instr_txt.text = main_str
instr_txt.draw()
adv_screen_txt.draw()
win.flip()
adv = event.waitKeys(keyList=[key, 'escape','q'])
if adv[0] in ['escape','q']:
    win.close()
    core.quit()
core.wait(post_instr_delay)                                         # Delay so they aren't caught off guard

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
        trial_clock.reset()
        trial_start = trial_clock.getTime()
        target_time = trial_start + interval_dur
        target_tlim = [target_time-tolerances[trial_type], target_time+tolerances[trial_type]]
        feedback_start = trial_start + interval_dur + feedback_delay
        feedback_end = feedback_start + feedback_dur
        ITI = random.choice(ITIs)       #!!! probably want specific random sequences to be determined ahead of time
        win.logOnFlip('B{0}_T{1} start: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.INFO)
        
        #========================================================
        # Moving Ball
        for pos_ix in range(n_int_flips-sum(hidden_pos[use_window])):
            # Drawing Order (back-to-front): (outlines?), tower, window, ball, bullseye 
            tower.draw()
            window.draw()
            for eye in reversed(bullseye):  #draw them all in reverse order
                eye.draw()
            balls[pos_ix].draw()
            if pos_ix==n_int_flips-1:       #!!! check what time the last ball of interval is drawn (assuming use_cover=False)
                win.callOnFlip(print_time, trial_clock.getTime(), 'last pos drawn! use_cover={0}'.format(use_cover))
                # This is dumb and useless since the clock doesn't sync to the flip, I should use flip times
            if trial_clock.getTime() < trigger_dur:
                trigger_rect.draw()
            win.flip()
            response = event.getKeys(keyList=[key,'p'], timeStamped=trial_clock)
            #!!! WARNING: colelcting responses here I think will still be tied to the flip rate!
            if len(response)>0: #!!! & (not hidden): stop the ball here
                if response[0][0]=='p':
                    pause_start = exp_clock.getTime()
                    pause_trial_time = trial_clock.getTime()
                    win.logOnFlip('PAUSED during B{0}_T{1} moving ball: trial_clock={2} and FRAME TIME = {3}'.format(\
                        block,trial,pause_trial_time,pause_start),logging.DATA)
                    pause_screen_txt.draw()
                    win.flip()
                    unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                    if unpause[0][0] in ['q','escape']:
                        win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                        win.flip()
                        win.close()
                        core.quit()
                    else:
                        trial_clock.reset(newT=pause_trial_time)
                        win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                        win.flip()
    #                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
                else:
                    responses.append(response)
                    win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block,trial,response,win.lastFrameT),logging.DATA)
                    response = []
        
        #========================================================
        # Feedback Delay
        tower.draw()
        window.draw()
        for eye in reversed(bullseye):  #draw them all in reverse order
            eye.draw()
        win.logOnFlip('B{0}_T{1} feedback_delay starts: total time = {2:.3f}, trial time = {3:.3f}'.format(
                                                block,trial,exp_clock.getTime(),trial_clock.getTime()),logging.INFO)
        win.flip()
        while trial_clock.getTime()<feedback_start:
            response = event.getKeys(keyList=[key,'p'], timeStamped=trial_clock)
            if len(response)>0:
                if response[0][0]=='p':
                    pause_start = exp_clock.getTime()
                    pause_trial_time = trial_clock.getTime()
                    win.logOnFlip('PAUSED during B{0}_T{1} feedback_delay: trial_clock={2} and FRAME TIME = {3}'.format(\
                        block,trial,pause_trial_time,pause_start),logging.DATA)
                    pause_screen_txt.draw()
                    win.flip()
                    unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                    if unpause[0][0] in ['q','escape']:
                        win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                        win.flip()
                        win.close()
                        core.quit()
                    else:
                        trial_clock.reset(newT=pause_trial_time)
                        # Redraw the delay background
                        tower.draw()
                        window.draw()
                        for eye in reversed(bullseye):  #draw them all in reverse order
                            eye.draw()
                        win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                        win.flip()
    #                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
                else:
                    responses.append(response)
                    win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block,trial,response,win.lastFrameT),logging.DATA)
                    response = []
        win.logOnFlip('B{0}_T{1} feedback delay end: {2:.5f}; offset error = {3:.5f}'.format(block,trial,trial_clock.getTime(),
                                                                trial_clock.getTime()-interval_dur-feedback_delay-trial_start),logging.INFO)
        
        #========================================================
        # Feedback
        # Calculate Feedback
        tower.draw()
        window.draw()
        for eye in reversed(bullseye):  #draw them all in reverse order
            eye.draw()
        if len(responses)>0:
            if len(responses)>1:
                win.logOnFlip('WARNING!!! More than one response detected (taking first) on B{0}_T{1}: repsonses = {2}'.format(
                                block, trial, responses),logging.WARNING)
            response = responses[0]         # take the first response
            RT = response[0][1]-trial_start
            error = interval_dur-RT
            error_height = error*interval_height/interval_dur
    #        print 'resp={0:.3f}, start={1:.3f}, target=[{2:.3f}-{3:.3f}], feedback_start={4:.3f},
    #                                                            RT={5:.3f}, flip_time = {6:.3f}'.format(
    #                                                            responses[0][0][1], trial_start, target_tlim[0],
    #                                                            target_tlim[1], feedback_start,RT, flip_times[resp_pos[0]])
            
            # Draw Feedback
            #feedback_txt.text = feedback_str.format(RT, interval_dur, tolerances[trial_type])
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
    #        if interval_vlim[1]-error_height < -game_height/2: # off the screen
    #            late_arrow[0].draw();late_arrow[1].draw()
    #            print 'WARNING!!! late response off screen, drawing late_arrow'
    #        else:
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
            #print 'target = {0}; resp_marker = {1}'.format(interval_vlim[1],
    #                                                interval_vlim[1]-error_height)#, str='; tolerances[trial_type] = [{2}, {3}] = {4}'
    #                                                target_zone.vertices[0][1],target_zone.vertices[2][1],
    #                                                target_zone.vertices[2][1]/target_zone.vertices[0][1])
        else:
            outcome_loss.draw()
            outcome_str = 'None'
            #!!! adjust tolerance for this type of trial?
            win.logOnFlip(feedback_str.format(block,trial,outcome_str,-1,trial_type,tolerances[trial_type]),logging.DATA)
        
        trigger_rect.draw()
        win.logOnFlip('B{0}_T{1} feedback start: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.INFO)
        win.flip()
        while trial_clock.getTime() < feedback_end:
            for press in event.getKeys(keyList=[key,'escape','q','p']):
                if press=='p':
                    pause_start = exp_clock.getTime()
                    pause_trial_time = trial_clock.getTime()
                    win.logOnFlip('PAUSED during B{0}_T{1} feedback: trial_clock={2} and FRAME TIME = {3}'.format(\
                        block,trial,pause_trial_time,pause_start),logging.DATA)
                    pause_screen_txt.draw()
                    win.flip()
                    unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                    if unpause[0][0] in ['q','escape']:
                        win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                        win.flip()
                        win.close()
                        core.quit()
                    else:
                        trial_clock.reset(newT=pause_trial_time)
                        # Redraw Feedback
                        tower.draw()
                        window.draw()
                        for eye in reversed(bullseye):  #draw them all in reverse order
                            eye.draw()
                        resp_marker.draw()
                        if outcome_str=='WIN!':
                            outcome_win.draw()
                        else:
                            outcome_loss.draw()
                        win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                        win.flip()
    #                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
                elif press in ['escape','q']:
                    win.close();
                    core.quit();
        
        #========================================================
        # ITI
#        print 'ITI ({0}) start = {1:.5f}; error = {2:.5f}'.format(ITI, trial_clock.getTime(),
#                                       trial_clock.getTime()-interval_dur-feedback_delay-feedback_dur-trial_start)
        win.logOnFlip('B{0}_T{1} ITI={2}; FRAME TIME = {3}'.format(block,trial,ITI,win.lastFrameT),logging.INFO)
        win.flip()
        
        # Staircase Tolerance
#        print 'old radii: ', bullseye_radii[trial_type]
        bullseye_height[trial_type] = interval_height*tolerances[trial_type]/interval_dur
        bullseye_radii[trial_type] = np.linspace(min_bullseye_radius, bullseye_height[trial_type], num=n_rings[trial_type])
#        print 'new radii: ', bullseye_radii[trial_type]
        for eye_ix, eye in enumerate(bullseyes[trial_type]):
            eye.radius = bullseye_radii[trial_type][eye_ix]
        
        while trial_clock.getTime() < feedback_end + ITI:
            for press in event.getKeys(keyList=[key,'escape','q','p']):
                if press=='p':
                    pause_start = exp_clock.getTime()
                    pause_trial_time = trial_clock.getTime()
                    win.logOnFlip('PAUSED during B{0}_T{1} ITI: trial_clock={2} and FRAME TIME = {3}'.format(\
                        block,trial,pause_trial_time,pause_start),logging.DATA)
                    pause_screen_txt.draw()
                    win.flip()
                    unpause = event.waitKeys(keyList=['q','escape','p'], timeStamped=exp_clock)
                    if unpause[0][0] in ['q','escape']:
                        win.logOnFlip('Quitting after pause; exp_clock={0}'.format(unpause[0][1]),logging.DATA)
                        win.flip()
                        win.close()
                        core.quit()
                    else:
                        trial_clock.reset(newT=pause_trial_time)
                        win.logOnFlip('Resuming after pause; trial_clock={0} and exp_clock={1}'.format(trial_clock.getTime(),exp_clock.getTime()),logging.DATA)
                        win.flip()
    #                    core.wait(post_pause_delay)                                         # Delay so they aren't caught off guard
                elif press in ['escape','q']:
                    win.close();
                    core.quit();
    
    #========================================================
    # Break Between Blocks
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

endgame_txt.draw()
win.flip()
core.wait(10)

win.close()
core.quit()

