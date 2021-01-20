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
rating_trial_ratio = 3              # ask for ratings after every X trials

#======================================
#  TOLERANCE AND INTERVAL PARAMETERS  
#======================================
interval_dur = 1                    # duration (in s) of target time interval
rating_delay = 1                  # duration (in s) of delay between end of interval and rating scale onset
max_rating_time = 20                # max time allowed for rating response
feedback_delay = 0.8                # duration (in s) of delay between rating response and feedback onset
feedback_compute_dur = 0.2          # time (in s) given to compute feedback before being ready to present (will not collect responses in this time!)
feedback_dur = 1                    # duration (in s) of feedback presentation
ITIs = [0.7, 1.0]         # length of inter-trial intervals (in s)
post_instr_delay = 1                # duration of delay (in s) after instructions/break to make sure they're ready
block_start_dur = 2                 # duration (in s) to display block start text (e.g., "Level _: type")
end_screen_dur = 7                 # duration (in s) of the ending "thank you all done" screen

tolerances = {'easy':0.125,           # Tolerance (in s) on either side of the target interval 
             'hard':0.05}            # e.g., interval-tolerance < correct_RT < interval+ tolerance
tolerance_step = {'easy': [-0.003,0.012],
                    'hard': [-0.012,0.003]} # adjustment (in s) for [correct,incorrect] responses
tolerance_lim = [0.4, 0.015]

#======================
# STIMULUS PARAMETERS  
#======================
full_screen = True                  # Make the window full screen? (True/False)
#screen_to_show = 1                 # Select which screen to display the window on
#screen_units = 'cm'                 # Set visual object sizes in cm (constant across all screens)
screen_units = 'height'                 # Set visual object sizes in "height" (relative to screen size)
# Explaining "height" units:
#   "...the dimensions of a screen with standard 4:3 aspect ratio will range (-0.6667,-0.5) in the bottom left
#   to (+0.6667,+0.5) in the top right. For a standard widescreen (16:10 aspect ratio) the bottom left 
#   of the screen is (-0.8,-0.5) and top-right is (+0.8,+0.5)."

# audio latency: 1 = share low-latency acces; 2 = exclusive low-latency acces; 3 = aggressive exclusive mode (rec)
audio_latency_mode = '3'
bad_fb_tolerance = 0.01 # 10 ms is okay

n_circ = 30                         # number of "lights" in the loop
#circ_size = .3                      # size of "lights"
#socket_size = .5                    # size of empty "lights" (when covered)
#loop_radius = 7                     # size of loop of "lights"
#target_width = 1.25                    # thickness of target zone IN CM 
circ_size = .015                      # size of "lights"
socket_size = .02                    # size of empty "lights" (when covered)
loop_radius = 0.25                     # size of loop of "lights"
target_width = 0.04                    # thickness of target zone

covered_portion = 0.6               # % of interval time obscured when covered=True
#resp_marker_width = 2               # Width of the response marker (marks where they pressed the button)
#resp_marker_thickness = 4           # Thickness of the response marker
resp_marker_width = 0.1               # Width of the response marker (marks where they pressed the button)
resp_marker_thickness = 4           # Thickness of the response marker
conditions = ['easy', 'hard']       # labels of the trial conditions
point_fn = [100, -100]              # reward function determining points awarded for [correct, incorrect, surprise]

rating_ticks = [0, 100]     # 50,
rating_labels = ['Definitely Lost', 'Definitely Won']   # ''
# use PsychoPy defaults for ratingScale size
#rating_size = 0.5
#accept_size = 0.2

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
