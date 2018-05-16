#target_time_variable file 
paradigm_name = 'target_time_cyclone'
paradigm_version = '2.4.2.1'
from psychopy.tools.coordinatetools import pol2cart
from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
from psychopy import visual, event, core, gui, logging, data, sound
#from psychopy import parallel
import numpy as np
import math, time, random, csv, glob, warnings
from itertools import groupby
from target_time_cyclone_log import * 
from target_time_cyclone_parameters import*



exp_datetime = time.strftime("%Y%m%d%H%M%S")

#============================================================
# EXPERIMENTAL VARIABLES
#============================================================
win = visual.Window(size=(1280,1024), fullscr=full_screen, color=(0,0,0),
                    monitor='testMonitor',# screen=screen_to_show,
                    allowGUI=False, units=screen_units, waitBlanking=True);
#NOTE: ECoG-A laptop size = 36cm wide, 20sm tall

frame_dur = win.getMsPerFrame(msg='Please wait, testing frame rate...')
frame_rate = win.getActualFrameRate()
if frame_rate < 60:
    warnings.warn('Frame rate less than 60hz: '+str(frame_rate))
if frame_rate > 60:
    warnings.warn('Frame rate greater than 60hz: '+str(frame_rate))
exp_clock = core.Clock()
if paradigm_type == 'ecog':
    block_order = np.array([0, 0, 1, 1])
else:
    block_order = np.random.permutation([b for b in [0, 1] for _ in range(n_blocks)])   #!!! consider counterbalancing future participants
def repeat_cnt(sequence):
    # count the number of equivalent neighbors in a sequence
    # e.g., repeat_cnt([4 2 3 3 6 10 7 7 7]) = [1 1 2 1 1 3]
    return [sum(1 for _ in group) for _, group in groupby(sequence)]

# Check for 3 or more consecutive same numbers; if present, recompute permutation until less than 3 present
block_repeat_cnt = repeat_cnt(block_order)
while any([cnt>=3 for cnt in block_repeat_cnt]):
    block_order = np.random.permutation([b for b in [0, 1] for _ in range(n_blocks)])
    block_repeat_cnt = repeat_cnt(block_order)

#-------------------------------------------------------------------
# Determine surprise trial numbers
# Draw surprise trial numbers from CSVs
surprise_sequence = set(random.sample(range(n_rand_blocks), n_rand_blocks))
surp_csv =  "surp_csvs/{0}_{1}_randomized_list.csv".format(paradigm_type, str(n_trials))
if debug_mode:
    surp_csv = "surp_csvs/debug_randomized_list.csv"
with open(surp_csv, 'r') as read:
    reader = csv.reader(read)
    desired_rows = [row for row_number, row in enumerate(reader)
                    if row_number in surprise_sequence]
surprise_trials = [[int(float(trl)) for trl in row] for row in desired_rows]


#============================================================
# FEEDBACK STIMULI
#============================================================
points = np.zeros(n_blocks*len(conditions))       # point total for each block
resp_marker = visual.Line(win, start=(-resp_marker_width/2, 0),
                                end=(resp_marker_width/2, 0),
                                lineColor='black', lineWidth=resp_marker_thickness)
outcome_win = visual.TextStim(win,text='Win!',height=2,units='cm',
                                name='feedback_win', color='green',pos=(0,0))
outcome_loss = visual.TextStim(win,text='Lose!',height=2,units='cm',
                                name='feedback_loss', color='red',pos=(0,0))#wrapWidth=550,
feedback_str = 'B{0}_T{1}: Outcome={2}; RT = {3}; condition = {4}; tolerance = {5}'
feedback_txt = visual.TextStim(win,text='',height=1,units='cm',
                                name='feedback_timing', color='black',pos=(0,-3),wrapWidth=14)

instr_pic_dict = {0:'grey.jpg', 
                  1:'target_arrow.jpg',
                  2:'direction_arrow.jpg',
                  3:'target_arrow.jpg',
                  4:'win.jpg', 
                  5:'loss.jpg',
                  6:'surprise.jpg',
                  'easy':'easy.jpg',
                  'hard':'hard.jpg'}
instr_pic = visual.ImageStim(win, image='cyclone_pics/{0}'.format(instr_pic_dict[0]), flipHoriz=False, pos=(0, -2), units='cm')

training_score = { "easy" : 0, "hard": 0 }


#======================================
#           SOUND STIMULI 
#======================================
win_sound = "new_win_sound.wav"
#              
loss_sound = "new_loss_sound.wav"

surprise_sounds = {'breaks': glob.glob("surprise_sounds/breaks/*.wav"),
                   'cymbols': glob.glob("surprise_sounds/cymbols/*.wav"),
                   'oddball': glob.glob("surprise_sounds/oddball/*.wav"),
                   'valves': glob.glob("surprise_sounds/valves/*.wav"),
                   'horns': glob.glob("surprise_sounds/horns/*.wav"),
                   'smash': glob.glob("surprise_sounds/smash/*.wav"),
                   'snares': glob.glob("surprise_sounds/snares/*.wav"),
                   'stabs': glob.glob("surprise_sounds/stabs/*.wav"),
                   'squeaks': glob.glob("surprise_sounds/squeaks/*.wav")}


turn_sound = {"WIN!": sound.Sound(value='paradigm_sounds/{0}'.format(win_sound), sampleRate=44100, blockSize=2048, secs=0.8, stereo=True),  # Switch sound sample once sounds present
             "LOSE!":sound.Sound(value='paradigm_sounds/{0}'.format(loss_sound), sampleRate=44100, blockSize=2048,secs=0.8, stereo=True),
             "SURPRISE!": sound.Sound(value= surprise_sounds['breaks'][0], sampleRate=44100, blockSize=2048,secs=0.8, stereo=True),
             'None': sound.Sound(value='paradigm_sounds/{0}'.format(loss_sound), sampleRate=44100, blockSize=2048, secs=0.8, stereo=True)}

turn_sound["WIN!"].setVolume(0.8)
turn_sound["LOSE!"].setVolume(0.8)
turn_sound["SURPRISE!"].setVolume(0.8)
turn_sound["None"].setVolume(0.8)


#===================================================
# CIRCLE & TARGET ZONE PARAMETERS
#===================================================
trial_dur = interval_dur + feedback_delay + feedback_dur
angle_ratio = 360/float(interval_dur)

#---------------------------------------------------
# "Light" Stimuli
circ_angles = np.linspace(-90,270,n_circ) #np.array([float(pos_ix)*(360/float(n_circ))-90 for pos_ix in range(n_circ)])
circ_radius = [loop_radius] * n_circ
circ_X, circ_Y = pol2cart(circ_angles,circ_radius)
circ_start = [circ_ix * (interval_dur/float(n_circ)) for circ_ix in range(n_circ)]  # onset time of each light
hidden_pos = {True: [(circ_start[circ_xi] > (1-covered_portion)*interval_dur) for circ_xi in range(n_circ)],
              False: [(False) for circ_xi in range(n_circ)]}

circ_default = [(-1,-1,-1)] * n_circ          # Sets black circles
fill_default = [(1,1,1)] * n_circ              # Sets white fillColor
circ_colors = [i for i in circ_default]       # Coppies default to prevent mutability issues
circ_covers = [(0,0,0)] *(n_circ - (n_circ - sum(hidden_pos[True])))
circ_cover_list = []
circ_fill_list = []
circ_cover_list[:(n_circ - sum(hidden_pos[True]))] = circ_default         # Sets up list of black and grey inner dots for "empty socket" effect
circ_cover_list[(n_circ - sum(hidden_pos[True])):] = circ_covers
circ_fill_list[:(n_circ - sum(hidden_pos[True]))] = fill_default
circ_fill_list[(n_circ - sum(hidden_pos[True])):] = circ_covers 
re_fill_color = {False:fill_default, True:circ_fill_list}                 # Sets up fill colors for covered/uncovered trial
re_flip_color = {False:circ_default, True:circ_cover_list}                # Sets up flip colors for covered/uncovered trial 
socket_colors = circ_colors


circles = visual.ElementArrayStim(win, nElements=n_circ,sizes=circ_size,xys = zip(circ_X, circ_Y),       # Circle object inset ontop of sockets 
                           elementTex = None, elementMask = "circle",
                           colors=circ_colors)
sockets = visual.ElementArrayStim(win, nElements=n_circ,sizes=socket_size,xys = zip(circ_X, circ_Y),     # "Sockets" providing outter black ring for circles.
                           elementTex = None, elementMask = "circle",                                   # always present behind circle stim
                           colors=socket_colors)

#=========================
# Target Zone
#=========================

target_upper_bound = {'easy': angle_ratio * (tolerances['easy']*2),  # Get angle of +/- tolerance from interval_dur
                      'hard': angle_ratio * (tolerances['hard']*2)}
target_origin = {'easy': 180 - (tolerances['easy'] * angle_ratio),   # zero starts at 12 oclock for radial stim.  
                 'hard': 180 - (tolerances['hard'] * angle_ratio)}   #!!! Ian comment: Strange indexing, -0 ending sets too far to right

target_zone = visual.RadialStim(win, tex='sqrXsqr', color='dimgrey', size=(loop_radius*2) + target_width, # size = diameter
    visibleWedge=[0, target_upper_bound['easy']], radialCycles=1, angularCycles=0, interpolate=False,   # radialCycles=1 to avoid color flip
    autoLog=False, units='cm', angularRes=1000)
target_zone_cover = visual.Circle(win, radius = loop_radius - target_width/2, edges=100,
                lineColor=None, fillColor=[0, 0, 0]) # Covers center of wedge used to draw taret zone

#---------------------------------------------------
# Photodiode Trigger Rectangle
trigger_rect = visual.Rect(win, width=trigger_rect_height, height=trigger_rect_height, units='pix',  #pos based on 1920x1080 pixel screen
                            fillColor='white', pos=(trigger_rect_height/2-win.size[0]/2,trigger_rect_height/2-win.size[1]/2))
#---------------------------------------------------

#===================================================
# INSTRUCTIONS
#===================================================
instr_strs = ['This is a simple (but not easy!) timing game.\nA light will move around this circle.',
               'Your goal is to respond at the exact moment when it completes the circle.',
               "The light always starts at the bottom and moves at the same speed, "+\
               'so the perfect response is always at the same time: the Target Time!',
               'The gray bar at the bottom is the target zone.',
               'If you respond in the target zone, it turns green and you win points!',
               'If you miss the target zone, it turns red and you lose points.',
               'Every once in a while, the target zone will turn blue.  ' +\
               "Ignore this, it won't affect your score.",
               "Let's get started with a few examples..."]
train_str = {'easy': ["Good job! From now on, only the first part of the circle will light up.",
                    "That means you need to time your response without seeing the light go all the way around.",
                    "Let's try some more examples..."],
             'hard': ["Great! Now you're ready to try the hard level.",
                    "Don't get discouraged - hard levels are designed to make you miss most of the time.\n"+\
                    "Try your best to see how much you can win!",
                    "Let's try some examples..."]}
main_str = "Ready to try the real deal? We'll reset your score to 0 and start counting for real now. "+\
            "You'll do {0} easy and {0} hard blocks, each lasting {1} trials.\n\n".format(n_blocks,n_trials)+\
            'Press Q/escape to try more practice rounds, '+\
            'or press {0} to start playing Target Time!'.format(key)

block_start_str = 'Level {0}/{1}: {2}'
break_str = 'Great work! {0} blocks left. Take a break to stretch and refresh yourself for at least {1} seconds.'
block_point_str = 'Level {0} Score: {1}'
total_point_str = 'Total Score: {0}'
score_demo_str = "You scored {0} points this round."

point_instr_str = "After each block, you'll see your score from this round. Points also add up across rounds."
times_demo_called = 1

welcome_txt = visual.TextStim(win,text='Welcome to\nTarget Time!',height=4,units='cm',alignHoriz='center',alignVert='center',
                                name='welcome', color='black', bold=True, pos=(0,2),wrapWidth=30)

instr_txt = visual.TextStim(win,text=instr_strs[0],height=1.5,units='cm', alignVert='center',
                                name='instr', color='black',pos=(0,7),wrapWidth=30)

adv_screen_txt = visual.TextStim(win,text='Press {0} to advance or Q/escape to quit...'.format(key),
                                height=1.5,units='cm',name='adv_screen', color='black', pos=(0,-10),wrapWidth=40)

block_start_txt = visual.TextStim(win,text=block_start_str,height=3,units='cm',alignHoriz='center',alignVert='center',
                                name='block_start', color='black', bold=True, pos=(0,2),wrapWidth=30)

block_point_txt = visual.TextStim(win,text=block_point_str,height=1.5,units='cm', alignVert='center',
                                name='block_points', color='black',pos=(0,8),wrapWidth=20)

score_demo_txt =  visual.TextStim(win,text=score_demo_str,height=1.5,units='cm', alignVert='center',
                                name='score_demo', color='green',pos=(0,8),wrapWidth=30)

point_instr_txt = visual.TextStim(win,text=point_instr_str, height=1.5,units='cm', alignVert='center',
                                name='point_instr', color='black',pos=(0,0),wrapWidth=30)

total_point_txt = visual.TextStim(win,text=total_point_str,height=1.5,units='cm', alignVert='center',
                                name='total_points', color='black',pos=(0,6),wrapWidth=20)

pause_txt = visual.TextStim(win,text='Paused', height=4,units='cm',alignHoriz='center',alignVert='center',
                                name='pause', color='black', bold=True, pos=(0,2),wrapWidth=30)

endgame_txt = visual.TextStim(win,text="Fantastic!!! You're all done. Thank you so much for participating in this experiment!",
                            height=2,units='cm',alignHoriz='center',alignVert='center',
                            name='endgame', color='black', bold=False, pos=(0,-4),wrapWidth=30)

instr_img = visual.ImageStim(win, image='cyclone_pics/grey.jpg', flipHoriz=False, 
                                pos=instr_img_pos, size=instr_img_size, units='cm')

train_img = visual.ImageStim(win, image='cyclone_pics/easy.jpg', flipHoriz=False, 
                                pos=instr_img_pos, size=instr_img_size, units='cm')
