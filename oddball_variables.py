paradigm_name = 'oddball'
paradigm_version = '1.6'
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
# Create experiment clock
exp_clock = core.Clock()
block_len_min = (stim_dur + max(ITIs)) * n_trials / 60

#-------------------------------------------------------------------
# Randomly assign visual, auditory, and response mappings
np.random.seed()
if paradigm_type == 'ecog':
    # Randomly permute index for stimuli/responses
    v_idx = np.random.permutation(np.arange(len(conditions)))   # [standard, target, distractor]
else:
    # Assign permutation based on SBJ #
    vis_opts = list(permutations(np.arange(len(conditions))))
    v_idx = list(vis_opts[eeg_seq_num % len(vis_opts)])

#-------------------------------------------------------------------
# Randomize block order
block_order = np.random.permutation(np.arange(3))   # randomize amongst all 8 possible blocks
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

#-------------------------------------------------------------------
# Randomize oddball stimuli (50 total available)
odd_idx = np.random.permutation(np.arange(50)).tolist()

#-------------------------------------------------------------------
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
std_name = 'oddball_sounds/440Hz_22050Hz_200ms.wav'
tar_name = 'oddball_sounds/1760Hz_22050Hz_200ms.wav'
odd_names = glob.glob("oddball_sounds/P3A*.WAV")

eeg_delay = 0.15
if paradigm_type == 'eeg':
    assert eeg_delay < resp_proc_dur
volumes = [1.0, 1.0]    # [tones, oddballs]
if paradigm_type == 'ecog':
    block_szs = [256, 256]  # [tones (come on too fast), oddballs (come on slower)]
else:
    block_szs = [512, 512]
sound_srate = 22050
stereo_val = 1
# Create a sound just so the stream gets initialized...
tmp_sound = sound.Sound(value=tar_name, sampleRate=sound_srate, blockSize=block_szs[0],
			 secs=stim_dur, stereo=stereo_val, volume=volumes[0])

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
outcome_pics = ['cropped green.jpg', 'cropped red.jpg', 'cropped blue.jpg']

if use_rtbox:
    key = 'any button'
    resp_method_str = 'Response Time Box'
    rtbox_added_str = 'You can press any of the four buttons.'
else:
    key = 'space'
    resp_method_str = 'keyboard'
    rtbox_added_str = ''
    resp_str_prefix = 'the'
if paradigm_type == 'ecog':
    effector_str = 'the THUMB of whichever hand the experimenter tells you'
else:
    effector_str = 'your RIGHT THUMB'

resp_instr_str = 'You will be responding using the {0}.\n'.format(resp_method_str) +\
                 'Please only use {0}.\n{1}'.format(effector_str, rtbox_added_str)

feedback_str = 'B{0}_T{1}: Outcome = {2}; RT = {3}; condition = {4}'
outcome_sound_str = 'B{0}_T{1}: condition = {2}; sound={3}'

#---------------------------------------------------
# Instruction Strings
#---------------------------------------------------
# Main instructions
instr_strs = ['Welcome! In this game, we will show you a series of pictures and sounds.'+\
              'Your job is to respond when the rare target stimulus appears to earn points.',
              'This is the target stimulus. Press {0} on the {1}\n'.format(key, resp_method_str)+\
              "when it appears. You win {0} points for each correct target response.".format(point_amt),
              'Most of the time, this standard stimulus will appear.\n'+\
              "You don't need to respond on these trials.",
              "Watch out! Do NOT press anything for distracters like this!\nThey are also rare, but will sound different every time.\n",
              resp_instr_str,
              "To summarize, press {0} only when a target appears,\nand otherwise don't respond.".format(key),
              "Let's try a few examples..."]
# Strings for instruction summary reminder
instr_sound_names = ['',tar_name,std_name,'','','','']
instr_pic_names = ['',outcome_pics[v_idx[1]],outcome_pics[v_idx[0]],outcome_pics[v_idx[2]],'','combo','']
instr_cond_strs = ['Target','Standard','Distracter']
instr_resp_str  = 'Press {0}'.format(key)
instr_no_resp_str = 'Do nothing'
# Starting the task
main_str = ["Ready to try the real deal?\nWe'll reset your score to 0 and start counting for real now.\n"+\
            "You'll do {0} blocks, each lasting {1:.1f} minutes.\n\n".format(n_blocks,block_len_min)+\
            'Press Q/escape to try more practice rounds, '+\
            'or press {0} to start playing!'.format(key)]

# Between blocks
score_demo_str  = 'You scored {0} points this round.'
point_instr_str = "After each block, you'll see your score from that round.\nPoints also add up across rounds."

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
    main_str_sz = 0.8
    small_str_sz = 0.6
    adv_str_sz = 0.5
    large_str_sz = 2
    end_str_sz = 1.25
else:
    instr_txt_pos = (0,8)
    main_str_sz = 1
    small_str_sz = 0.8
    adv_str_sz = 0.7
    large_str_sz = 2.5
    end_str_sz = 1.5

instr_txt = visual.TextStim(win,text=instr_strs[0],height=main_str_sz,units='cm', alignVert='center',
                                name='instr', color='black',pos=instr_txt_pos,wrapWidth=30)
instr_condlab_txts = [visual.TextStim(win,text=instr_cond_strs[0],height=small_str_sz,units='cm', alignVert='center',
                                name='instr', color='black', bold=True, pos=(-8,2),wrapWidth=10),
                  visual.TextStim(win,text=instr_cond_strs[1],height=small_str_sz,units='cm', alignVert='center',
                                name='instr', color='black', bold=False, pos=(0,2), wrapWidth=10),
                  visual.TextStim(win,text=instr_cond_strs[2],height=small_str_sz,units='cm', alignVert='center',
                                name='instr', color='black',pos=(8,2),wrapWidth=10)]
instr_resp_txts = [visual.TextStim(win,text=instr_resp_str,height=small_str_sz,units='cm', alignVert='center',
                                name='instr', color='black', bold=True, pos=(-8,-5), wrapWidth=10),
		   visual.TextStim(win,text=instr_no_resp_str,height=small_str_sz,units='cm', alignVert='center',
                                name='instr', color='black', bold=False, pos=(0,-5), wrapWidth=10),
		   visual.TextStim(win,text=instr_no_resp_str,height=small_str_sz,units='cm', alignVert='center',
                                name='instr', color='black', bold=False, pos=(8,-5), wrapWidth=10)]

if paradigm_type == 'ecog':
    adv_txt_pos = (0,-8)
else:
    adv_txt_pos = (0,-12)
adv_screen_txt = visual.TextStim(win,text='Press {0} to advance or Q/escape to quit...'.format(key),
                                height=adv_str_sz,units='cm',name='adv_screen', color='black', pos=adv_txt_pos,wrapWidth=20)#short no need wrap

block_start_txt = visual.TextStim(win,text=block_start_str,height=large_str_sz,units='cm',alignHoriz='center',alignVert='center',
                                name='block_start', color='black', bold=True, pos=(0,2),wrapWidth=30)#short no need wrap

block_point_txt = visual.TextStim(win,text=block_point_str,height=main_str_sz,units='cm', alignVert='center',
                                name='block_points', color='black',pos=(0,3),wrapWidth=20)#short no need wrap

score_demo_txt =  visual.TextStim(win,text=score_demo_str,height=main_str_sz,units='cm', alignVert='center',
                                name='score_demo', color='green',pos=(0,6),wrapWidth=30)#short no need wrap

point_instr_txt = visual.TextStim(win,text=point_instr_str, height=main_str_sz,units='cm', alignVert='center',
                                name='point_instr', color='black',pos=(0,0),wrapWidth=30)#built in line break

total_point_txt = visual.TextStim(win,text=total_point_str,height=main_str_sz,units='cm', alignVert='center',
                                name='total_points', color='black', bold=True, pos=(0,0),wrapWidth=20)#short no need wrap

pause_txt = visual.TextStim(win,text='Paused', height=large_str_sz,units='cm',alignHoriz='center',alignVert='center',
                                name='pause', color='black', bold=True, pos=(0,2),wrapWidth=30)#short no need wrap

endgame_txt = visual.TextStim(win,text=end_game_str,
                            height=end_str_sz,units='cm',alignHoriz='center',alignVert='center',
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

instr_summ_imgs = [visual.ImageStim(win, image='cyclone_pics/'+outcome_pics[v_idx[1]], flipHoriz=False, 
                                pos=instr_summ_pos[0], size=instr_summ_size, units='cm'),
                  visual.ImageStim(win, image='cyclone_pics/'+outcome_pics[v_idx[0]], flipHoriz=False, 
                                pos=instr_summ_pos[1], size=instr_summ_size, units='cm'),
                  visual.ImageStim(win, image='cyclone_pics/'+outcome_pics[v_idx[2]], flipHoriz=False, 
                                pos=instr_summ_pos[2], size=instr_summ_size, units='cm')]
