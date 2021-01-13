#target_time parameter file 
paradigm_name = 'target_time_ratings'
paradigm_version = '3.0'

from psychopy import visual, event, core, gui, logging, data
from target_time_cyclone_log import*
import numpy as np
import math, time, random

exp_datetime = time.strftime("%Y%m%d%H%M%S")

#============================================================
# EXPERIMENT STRUCTURE PARAMETERS
#============================================================
n_fullvis     = 5                   # number of EASY examples to start (large tolerance, full window)
n_training    = 15                  # number of training trials PER CONDITION
n_blocks      = 2                   # number of blocks of trials PER CONDITION
n_trials      = 75                  # number of trials PER BLOCK
break_min_dur = 15                  # minimum length (in s) for the break between blocks
#!!! check if n_trials/N-blocks==integer

#======================================
#  TOLERANCE AND INTERVAL PARAMETERS  
#======================================
interval_dur = 1                    # duration (in s) of target time interval
rating_delay = 1                  # duration (in s) of delay between end of interval and rating scale onset
max_rating_time = 20                # max time allowed for rating response
feedback_delay = 0.8                # duration (in s) of delay between rating response and feedback onset
feedback_compute_dur = 0.2          # time (in s) given to compute feedback before being ready to present (will not collect responses in this time!)
feedback_dur = 0.8                    # duration (in s) of feedback presentation
ITIs = [0.7, 1.0]         # length of inter-trial intervals (in s)
post_instr_delay = 1                # duration of delay (in s) after instructions/break to make sure they're ready
block_start_dur = 2                 # duration (in s) to display block start text (e.g., "Level _: type")
end_screen_dur = 10                 # duration (in s) of the ending "thank you all done" screen

tolerances = {'easy':0.125,           # Tolerance (in s) on either side of the target interval 
             'hard':0.05}            # e.g., interval-tolerance < correct_RT < interval+ tolerance
tolerance_step = {'easy': [-0.003,0.012],
                    'hard': [-0.012,0.003]} # adjustment (in s) for [correct,incorrect] responses
tolerance_lim = [0.4, 0.015]

n_flicker   = 10                     # number of times to flicker the photodiode on at initial task start
flicker_dur = 0.1                   # duration of each flicker in start sequence
flicker_brk = 5                     # break the sequence after this many flickers (breaks up continuous flickering)

instr_img_size = (13,10)
instr_img_pos = (5, -2)

#======================
# STIMULUS PARAMETERS  
#======================
full_screen = True                  # Make the window full screen? (True/False)
#screen_to_show = 1                 # Select which screen to display the window on
screen_units = 'cm'                 # Set visual object sizes in cm (constant across all screens)

n_circ = 30                         # number of "lights" in the loop
circ_size = .3                      # size of "lights"
socket_size = .5                    # size of empty "lights" (when covered)
loop_radius = 7                     # size of loop of "lights"
target_width = 1.25                    # thickness of target zone IN CM 

covered_portion = 0.6               # % of interval time obscured when covered=True
resp_marker_width = 2               # Width of the response marker (marks where they pressed the button)
resp_marker_thickness = 4           # Thickness of the response marker
conditions = ['easy', 'hard']       # labels of the trial conditions
point_fn = [100, -100]              # reward function determining points awarded for [correct, incorrect, surprise]

rating_ticks = [0, 50, 100]
rating_labels = ['Definitely Lost', '', 'Definitely Won']
rating_width = 10
rating_size = 1
accept_size = 1

#========================
#  SURPRISE PARAMETERS
#========================
# Design Parameters
surp_rate = 0.12              # proportion of trials with surprising outcomes (12% = 9/75)
n_surp = int(np.floor(surp_rate*n_trials))
# Randomization Constraints
first_possible = 10    # first trial that can be surprise
min_gap = 4            # minimum trials between surprising outcomes
min_uniq = 6           # minimum number of unique gaps to avoid predictability of surprise
max_repeat_spacing = 1 # max number of times the same spacing can be used back-to-back

#========================
#  ADJUST IF DEBUGGING
#========================
if debug_mode:
    # Cut down design parameters
    n_fullvis = 1
    n_training = 2
    n_blocks = 2
    n_trials = 5
    break_min_dur = 1
    # Change surprise parameters
    n_surp = 2
    first_possible = 1
    min_gap = 1
    min_uniq = 1
    max_repeat_spacing = 1
else:
    assert first_possible < n_trials-(n_surp*min_gap)
