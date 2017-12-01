#target_time parameter file 
#part of modularization 
paradigm_version = '2.1'

from psychopy import visual, event, core, gui, logging, data
#from psychopy import parallel
import numpy as np
import math, time, random, shelve

exp_datetime = time.strftime("%Y%m%d%H%M%S")
paradigm_name = 'target_time'
paradigm_type = 'debug'                        # Choose either 'debug' 'eeg' or 'ecog' depending on desired 
                                               # duration parameters for trials.  

#============================================================
# EXPERIMENT PARAMETERS
#============================================================


def experiment_parameters(type):                        #function that selects correct parameter from corresponding dicts 
    if type == 'debug':
        return n_fullvis[type], n_training[type], n_blocks[type], n_trials[type], break_min_dur[type], game_height['eeg']
    return n_fullvis[type], n_training[type], n_blocks[type], n_trials[type], break_min_dur[type], game_height[type]



#==============================
#  TRIAL DURATION PARAMETERS  
#==============================

# probably need debug y/n and eeg/ecog input from the log file, which will then determine the values below
#   eeg/ecog is needed even if in debug mode, because you need to avoid calls to the parallel port for ECoG and trigger rectangle should appear in ECoG version

n_fullvis = {'debug':1, 'eeg':5, 'ecog':5}                     # number of EASY examples to start (large tolerance, full window)
    
n_training = {'debug':2, 'eeg':15, 'ecog':15}                     # number of training trials PER CONDITION
    
n_blocks = {'debug':1, 'eeg':4, 'ecog':2}                        # number of blocks of trials PER CONDITION
    
n_trials = {'debug':2, 'eeg':75, 'ecog':75}                       # number of trials PER BLOCK
    
break_min_dur = {'debug':1, 'eeg':30, 'ecog':30}                  # minimum length (in s) for the break between blocks

#======================================
#  TOLERANCE AND INTERVAL PARAMETERS  
#======================================


interval_dur = 1                    # duration (in sec) of target time interval
feedback_delay = 0.8                # duration (in s) of delay between end of interval and feedback onset
feedback_dur = 0.8                    # duration (in s) of feedback presentation
ITIs = [0.2, 0.4, 0.7, 1.0]         # length of inter-trial intervals (in s)
post_instr_delay = 1                # duration of delay (in s) after instructions/break to make sure they're ready
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

#======================
# STIMULUS PARAMETERS  
#======================

#CIRCLE PARAMETERS

n_circ = 10
circ_size = 1
loop_radius = 9
loop_circum = 7

game_height = {'eeg':20, 'ecog':25}                    # amount of screen for plotting

n_fullvis, n_training, n_blocks, n_trials, break_min_dur, game_height = experiment_parameters(paradigm_type)
            #!!! Must be called here so game_height is an int for interval_height

interval_height = 0.7*game_height   # % of game_height over which interval_dur occurs
target_y = 5                        # position of target in y coordinates
covered_portion = 0.6               # % of interval height obscured by the window when covered=True
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


