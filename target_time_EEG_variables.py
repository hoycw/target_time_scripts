#target_time_variable file 
#part of modularization  
paradigm_version = '1.9.2'

from psychopy import visual, event, core, gui, logging, data
#from psychopy import parallel
import numpy as np
import math, time, random, shelve
#import target_time_EEG_log
from target_time_EEG_parameters import*


#random.seed()
#core.wait(0.5)      # give the system time to settle
#core.rush(True)     # might give psychopy higher priority in the system (maybe...)
exp_datetime = time.strftime("%Y%m%d%H%M%S")
paradigm_name = 'target_time'



#============================================================
# SET EXPERIMENTAL VARIABLES
#============================================================
# Environment Variables
win = visual.Window(size=(1280,1024), fullscr=full_screen, color=(0,0,0),
                    monitor='testMonitor',# screen=screen_to_show,
                    allowGUI=False, units=screen_units)#, waitBlanking=False); # !!! check on this waitBlank parameter!
#NOTE: ECoG laptop size = 36cm wide, 20sm tall
print 'Window size = ', win.size
exp_clock = core.Clock()
trial_clock = core.Clock()
block_order = np.random.permutation([b for b in [0, 1] for _ in range(n_blocks)])   #!!! consider counterbalancing future participants
#np.array([0, 0, 1, 1])
def count_check(some_array):    #function that takes an array as argument and returns an array with the count of 
    result_list = np.array([])  #consecutive numbers that are same. For eg [0,0,0,1,0,1,1] would return [3,1,1,2]
    current = some_array[0]
    count = 0 
    for value in some_array:
        if value == current:
            count += 1
        else:
            result_list = np.append(result_list, count)
            current = value
            count = 1 
    result_list = np.append(result_list,count)
    return result_list

result_list = count_check(block_order)
while len(result_list[result_list >= 3]) != 0:      #checks for 3 or more consecutive same numbers. If present, will recompute permutation till less than 3 present
            block_order = np.random.permutation([b for b in [0, 1] for _ in range(4)])
            result_list = count_check(block_order)
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
#!!! rename this shitty thing
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
            'Press Q/escape to do more practice rounds first,\n'+\
            'or press {0} to start playing Target Time!'.format(key)
block_start_str = 'Level {0}/{1}: {2}'
break_str = 'Great work! {0} blocks left. Take a break to stretch and refresh yourself for at least {1} seconds.'
block_point_str = 'Level {0} Score: {1}'
total_point_str = 'Total Score: {0}'

welcome_txt = visual.TextStim(win,text='Welcome to\nTarget Time!',height=4,units='cm',alignHoriz='center',alignVert='center',
                                name='welcome', color='black', bold=True, pos=(0,2),wrapWidth=30)
instr_txt = visual.TextStim(win,text=instr_strs[0],height=2,units='cm', alignVert='center',
                                name='instr', color='black',pos=(0,0),wrapWidth=30)
adv_screen_txt = visual.TextStim(win,text='Press {0} to advance or Q/escape to quit...'.format(key),
                                height=1.5,units='cm',name='adv_screen', color='black', pos=(0,-10),wrapWidth=40)
block_start_txt = visual.TextStim(win,text=block_start_str,height=3,units='cm',alignHoriz='center',alignVert='center',
                                name='block_start', color='black', bold=True, pos=(0,2),wrapWidth=30)
block_point_txt = visual.TextStim(win,text=block_point_str,height=1.5,units='cm', alignVert='center',
                                name='block_points', color='black',pos=(0,8),wrapWidth=20)
total_point_txt = visual.TextStim(win,text=total_point_str,height=1.5,units='cm', alignVert='center',
                                name='total_points', color='black',pos=(0,4),wrapWidth=20)
endgame_txt = visual.TextStim(win,text="Fantastic!!! You're all done. Thank you so much for participating in this experiment!",
                            height=2,units='cm',alignHoriz='center',alignVert='center',
                            name='endgame', color='black', bold=False, pos=(0,-4),wrapWidth=30)

#!!! come back and rethink what I need here for checks and printing to save out
#print 'interval_vlim = ', interval_vlim
#print 'tower_vlim = ', cover_vlim
#print 'target_vlim = ', target_vlim
#print 'ball_ys = [{0} - {1}]; len(ball_ys) = {2}'.format(ball_ys[0],ball_ys[-1], len(ball_ys))
#print 'interval_vlim top - int_flips*ball_step = ',\
#                interval_vlim[0]+(ball_step*n_int_flips), '(', n_int_flips, ',', ball_step, ')'
#assert np.max(ball_ys) <= cover_vlim[1]             # all balls hidden
#assert cover_vlim[1] >= np.max(np.max(target_vlim)) # make sure the bottom of the interval is covered
