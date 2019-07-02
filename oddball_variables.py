paradigm_name = 'oddball'
paradigm_version = '1.3'
from psychopy.tools.coordinatetools import pol2cart
from psychopy import prefs
prefs.general['audioLib'] = ['sounddevice']
from psychopy import visual, event, core, gui, logging, data, sound
import numpy as np
import math, time, random, csv, glob, warnings
from itertools import groupby, permutations
from oddball_log import * 
from oddball_parameters import*

#============================================================
#           EXPERIMENTAL DESIGN VARIABLES
#============================================================
# Randomly assign visual, auditory, and response mappings
np.random.seed()
if paradigm_type == 'ecog':
    # Randomly permute index for stimuli/responses
    v_idx = np.random.permutation(np.arange(len(conditions)))   # [standard, target, distractor]
    a_idx = np.random.permutation([0, 1])
    r_idx = np.random.permutation([0, 1])  # [Target, Reject]
else:
    # Assign permutation based on SBJ #
    vis_opts = list(permutations(np.arange(len(conditions))))
    resp_opts = list(permutations([0, 1])) # same for auditory
    v_idx = vis_opts[eeg_seq_num % len(vis_opts)]
    a_idx = resp_opts[eeg_seq_num % 2]
    r_idx = resp_opts[eeg_seq_num % 2]  # [Target, Reject]

# Randomize block order
block_order = np.random.permutation(np.arange(8))   # randomize amongst all 8 possible blocks
block_order = block_order[:n_blocks]
# Determine trial order
odd_csv =  "oddball_trial_order_csvs/block_{0}_trial_randomized_orders.csv".format(str(n_trials))
if debug_mode:
    odd_csv = "oddball_trial_order_csvs/debug_10_trial_randomized_orders.csv"
with open(odd_csv, 'r') as read:
    reader = csv.reader(read)
    block_cond_n = [row for row_number, row in enumerate(reader)
                    if row_number in block_order]
# Convert to int, which can be used as index
odd_cnt = 0
for b_ix in range(n_blocks):
    for t_ix in range(n_trials):
        block_cond_n[b_ix][t_ix] = int(float(block_cond_n[b_ix][t_ix]))
        if block_cond_n[b_ix][t_ix]==2:
            odd_cnt += 1

# Randomize oddball stimuli (50 total available)
odd_idx = np.random.permutation(np.arange(50)).tolist()

# Select training order
train_csv = "oddball_trial_order_csvs/debug_10_trial_randomized_orders.csv"
train_ix = np.random.choice(np.arange(8))
with open(train_csv, 'r') as read:
    reader = csv.reader(read)
    train_cond_n = [row for row_number, row in enumerate(reader)
                    if row_number==train_ix]
train_cond_n = train_cond_n[0]  # only need single training block
# Convert to int, which can be used as index
for t_ix in range(len(train_cond_n)):
    train_cond_n[t_ix] = int(float(train_cond_n[t_ix]))
    if train_cond_n[t_ix]==2:
        odd_cnt += 1

# Check if sufficient oddball sounds
print 'odd_cnt = ', odd_cnt
assert odd_cnt <= 50

#-------------------------------------------------------------------
# Create experiment clock
exp_clock = core.Clock()

# Create monitor window
if paradigm_type == 'ecog':
    monitor_name = 'Built_in'
else:
    monitor_name = '135D_monitor'
win = visual.Window(size=(1920,1080), fullscr=full_screen, color=(0,0,0),
                    monitor=monitor_name,# screen=screen_to_show,
                    allowGUI=False, units=screen_units, waitBlanking=True);
#NOTE: ThinkPad P51 (ECoG-1/Klay/etc.) = 34.5cm wide, 19.5cm tall
#   ECoG-A laptop size = 36cm wide, 20sm tall

frame_dur = win.getMsPerFrame(msg='Please wait, testing frame rate...')
frame_rate = win.getActualFrameRate()
if frame_rate < 60:
    warnings.warn('Frame rate less than 60hz: '+str(frame_rate))
if frame_rate > 60:
    warnings.warn('Frame rate greater than 60hz: '+str(frame_rate))


#======================================
#           SOUND STIMULI
#======================================
std_name = 'oddball_sounds/440Hz_44100Hz_16bit_200ms.wav'
tar_name = 'oddball_sounds/1kHz_44100Hz_16bit_200ms.wav'
odd_names = glob.glob("oddball_sounds/P3A*.WAV")

block_sz = 256
# Create a sound just so the stream gets initialized...
tmp_sound = sound.Sound(value=tar_name, sampleRate=44100, blockSize=block_sz, secs=sound_dur, stereo=1, volume=1.0)

#===================================================
#           VISUAL STIMULI
#===================================================
# "Light" Stimuli
#---------------------------------------------------
circ_angles = np.linspace(-90,270,n_circ) #np.array([float(pos_ix)*(360/float(n_circ))-90 for pos_ix in range(n_circ)])
circ_radius = [loop_radius] * n_circ
circ_X, circ_Y = pol2cart(circ_angles,circ_radius)
circ_start = [circ_ix * (1/float(n_circ)) for circ_ix in range(n_circ)]  # onset time of each light
hidden_pos = [(circ_start[circ_xi] > (1-covered_portion)) for circ_xi in range(n_circ)]

socket_colors = [(-1,-1,-1)] * n_circ          # Sets black circles
circ_colors = [(-1,-1,-1)] * (n_circ - sum(hidden_pos)) + [(0, 0, 0)] * sum(hidden_pos) # 13 black + 17 gray

circles = visual.ElementArrayStim(win, nElements=n_circ, sizes=circ_size, xys = zip(circ_X, circ_Y),       # Circle object inset ontop of sockets 
                           elementTex = None, elementMask = "circle",
                           colors=circ_colors)
sockets = visual.ElementArrayStim(win, nElements=n_circ,sizes=socket_size,xys = zip(circ_X, circ_Y),     # "Sockets" providing outter black ring for circles.
                           elementTex = None, elementMask = "circle",                                   # always present behind circle stim
                           colors=socket_colors)

#---------------------------------------------------
# Target Zone
#---------------------------------------------------
target_zone_colors = ['green', 'red', 'blue']
# Fixed target zone parameters (no staircase)
target_upper_bound = 360 * 0.2  # Get angle of +/- tolerance from interval_dur
target_origin = 180 - (0.1 * 360)   # zero starts at 12 oclock for radial stim

target_zone = visual.RadialStim(win, tex='sqrXsqr', color='dimgrey', size=(loop_radius*2) + target_width, # size = diameter
    visibleWedge=[0, target_upper_bound], radialCycles=1, angularCycles=0, interpolate=False,   # radialCycles=1 to avoid color flip
    autoLog=False, units='cm', angularRes=1000)
target_zone.ori = target_origin
target_zone_cover = visual.Circle(win, radius = loop_radius - target_width/2, edges=100,
                lineColor=None, fillColor=[0, 0, 0]) # Covers center of wedge used to draw taret zone

#---------------------------------------------------
# Photodiode Trigger Rectangle
#---------------------------------------------------
trigger_rect = visual.Rect(win, width=trigger_rect_height, height=trigger_rect_height, units='pix',  #pos based on 1920x1080 pixel screen
                            fillColor='white', pos=(trigger_rect_height/2-win.size[0]/2,trigger_rect_height/2-win.size[1]/2))

#===================================================
#           INSTRUCTIONS
#===================================================
# Response instructions
#---------------------------------------------------
outcome_pics = ['win.jpg', 'loss.jpg', 'surprise.jpg']
keys = ['left', 'right']
actions = ['COLLECT', 'REJECT']
adv_key = 'right'

if use_rtbox:
    resp_str_prefix = 'any of the'
    resp_strs = ['Response Time Box','WHITE buttons (1,2)', 'BLACK buttons (3,4)']
    resp_pic = 'RTBox_LR_instruction_img.jpg'
else:
    resp_str_prefix = 'the'
    resp_strs = ['keyboard','LEFT ARROW', 'RIGHT ARROW']
    resp_pic = ''

resp_instr_str = 'You will be responding using the {0}.\n'.format(resp_strs[0]) +\
                 'Please only use the index and middle finger of whichever hand the experimenter tells you.\n' +\
                 'To COLLECT targets, press {0} {1}.\n'.format(resp_str_prefix,resp_strs[r_idx[0]+1]) +\
                 'To REJECT standards and distracers, press {0} {1}.'.format(resp_str_prefix,resp_strs[r_idx[1]+1])

feedback_str = 'B{0}_T{1}: Outcome = {2}; RT = {3}; condition = {4}'

#---------------------------------------------------
# Instruction Strings
#---------------------------------------------------
# Main instructions
instr_strs = ['Welcome! In this game, we will show you a series of pictures and sounds.'+\
              'Your job is to earn points by collecting the rare target stimulus,'+\
              'but rejecting the standard and distracter stimuli.',
              resp_instr_str,
              'Most of the time, this standard stimulus will appear.\n'+\
              'It will always be the first stimulus in every block.\n'+\
              'REJECT these to win points by pressing {0} {1}.'.format(resp_str_prefix,resp_strs[r_idx[1]+1]),
              'Pay attention for this rare target!\n'+\
              'COLLECT the targets and win points by pressing {0} {1}.'.format(resp_str_prefix,resp_strs[r_idx[0]+1]),
              'Beware of distracters like this!\nThey are rare, and will sound different every time.\n'+\
              'Just like standard stimuli, REJECT these by pressing {0} {1}.'.format(resp_str_prefix,resp_strs[r_idx[1]+1]),
              'To summarize, press the correct response for each stimulus:',
              "Let's try a few examples..."]
# Strings for instruction summary reminder
instr_sound_names = ['','',std_name,tar_name,'','','']
instr_pic_names = ['',resp_pic,outcome_pics[v_idx[0]],outcome_pics[v_idx[1]],outcome_pics[v_idx[2]],'combo','']
instr_cond_strs = ['Standard (REJECT)','Target (COLLECT)','Distracter (REJECT)']
instr_resp_strs = [resp_strs[r_idx[1]+1], resp_strs[r_idx[0]+1], resp_strs[r_idx[1]+1]]
# Starting the task
main_str = ["Ready to try the real deal?\nWe'll reset your score to 0 and start counting for real now.\n"+\
            "You'll do {0} blocks, each lasting {1} trials.\n\n".format(n_blocks,n_trials)+\
            'Press Q/escape to try more practice rounds, '+\
            'or press {0} to start playing!'.format(adv_key)]

# Between blocks
score_demo_str  = 'You scored {0} points this round.'
point_instr_str = "After each block, you'll see your score from this round.\nPoints also add up across rounds."

block_start_str = 'Level {0}/{1}'
break_str       = 'Great work! {0} blocks left. Take a break to stretch and refresh yourself for at least {1} seconds.'
block_point_str = 'Level {0} Score: {1}'
total_point_str = 'Total Score: {0}'

end_game_str    = "Nice job!!! You finished this game. Thank you so much for participating!"

#---------------------------------------------------
# Instruction Text Objects
#---------------------------------------------------
if paradigm_type == 'ecog':
    instr_txt_pos = (0,6)
else:
    instr_txt_pos = (0,8)    
instr_txt = visual.TextStim(win,text=instr_strs[0],height=0.8,units='cm', alignVert='center',
                                name='instr', color='black',pos=instr_txt_pos,wrapWidth=30)
instr_condlab_txts = [visual.TextStim(win,text=instr_cond_strs[0],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black',pos=(-8,2),wrapWidth=10),
                  visual.TextStim(win,text=instr_cond_strs[1],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black', bold=True, pos=(0,2), wrapWidth=10),
                  visual.TextStim(win,text=instr_cond_strs[2],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black',pos=(8,2),wrapWidth=10)]
instr_resp_txts = [visual.TextStim(win,text=instr_resp_strs[0],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black',pos=(-8,-5),wrapWidth=10),
                  visual.TextStim(win,text=instr_resp_strs[1],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black', bold=True, pos=(0,-5), wrapWidth=10),
                  visual.TextStim(win,text=instr_resp_strs[2],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black',pos=(8,-5),wrapWidth=10)]
instr_action_txts = [visual.TextStim(win,text=actions[r_idx[0]],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black',pos=(-2,3),wrapWidth=10),
                  visual.TextStim(win,text=actions[r_idx[1]],height=0.6,units='cm', alignVert='center',
                                name='instr', color='black',pos=(2,3),wrapWidth=10)]

if paradigm_type == 'ecog':
    adv_txt_pos = (0,-8)
else:
    adv_txt_pos = (0,-12)
adv_screen_txt = visual.TextStim(win,text='Press {0} ({1}) to advance or Q/escape to quit...'.format(adv_key, resp_strs[2]),
                                height=0.5,units='cm',name='adv_screen', color='black', pos=adv_txt_pos,wrapWidth=20)#short no need wrap

block_start_txt = visual.TextStim(win,text=block_start_str,height=2,units='cm',alignHoriz='center',alignVert='center',
                                name='block_start', color='black', bold=True, pos=(0,2),wrapWidth=30)#short no need wrap

block_point_txt = visual.TextStim(win,text=block_point_str,height=0.8,units='cm', alignVert='center',
                                name='block_points', color='black',pos=(0,3),wrapWidth=20)#short no need wrap

score_demo_txt =  visual.TextStim(win,text=score_demo_str,height=0.8,units='cm', alignVert='center',
                                name='score_demo', color='green',pos=(0,6),wrapWidth=30)#short no need wrap

point_instr_txt = visual.TextStim(win,text=point_instr_str, height=0.8,units='cm', alignVert='center',
                                name='point_instr', color='black',pos=(0,0),wrapWidth=30)#built in line break

total_point_txt = visual.TextStim(win,text=total_point_str,height=0.8,units='cm', alignVert='center',
                                name='total_points', color='black', bold=True, pos=(0,0),wrapWidth=20)#short no need wrap

pause_txt = visual.TextStim(win,text='Paused', height=2,units='cm',alignHoriz='center',alignVert='center',
                                name='pause', color='black', bold=True, pos=(0,2),wrapWidth=30)#short no need wrap

endgame_txt = visual.TextStim(win,text=end_game_str,
                            height=1.25,units='cm',alignHoriz='center',alignVert='center',
                            name='endgame', color='black', bold=False, pos=(0,-4),wrapWidth=30)

#---------------------------------------------------
# Instruction Images
#---------------------------------------------------
# Instructions
instr_img_pos = (0, -2.5)
instr_img_size = (10,10)
instr_summ_pos = [(-8,-2), (0,-2), (8,-2)]
instr_summ_size = (6,6)

instr_img = visual.ImageStim(win, image='cyclone_pics/'+outcome_pics[0], flipHoriz=False, 
                                pos=instr_img_pos, size=instr_img_size, units='cm')

instr_summ_imgs = [visual.ImageStim(win, image='cyclone_pics/'+outcome_pics[v_idx[0]], flipHoriz=False, 
                                pos=instr_summ_pos[0], size=instr_summ_size, units='cm'),
                  visual.ImageStim(win, image='cyclone_pics/'+outcome_pics[v_idx[1]], flipHoriz=False, 
                                pos=instr_summ_pos[1], size=instr_summ_size, units='cm'),
                  visual.ImageStim(win, image='cyclone_pics/'+outcome_pics[v_idx[2]], flipHoriz=False, 
                                pos=instr_summ_pos[2], size=instr_summ_size, units='cm')]
