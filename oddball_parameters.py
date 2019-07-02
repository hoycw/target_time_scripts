#target_time parameter file 
paradigm_name = 'oddball'
paradigm_version = '1.3'

from psychopy import visual, event, core, gui, logging, data
from oddball_log import*
#from psychopy import parallel
import numpy as np
import math, time, random
from oddball_log import use_rtbox

exp_datetime = time.strftime("%Y%m%d%H%M%S")

#============================================================
# EXPERIMENT STRUCTURE PARAMETERS
#============================================================
conditions = ['std', 'tar', 'odd']       # labels of the trial conditions

def experiment_parameters(type):                        #function that selects correct parameter from corresponding dicts 
    return n_training[type], n_blocks[type], n_trials[type], break_min_dur[type]

# probably need debug y/n and eeg/ecog input from the log file, which will then determine the values below
#   eeg/ecog is needed even for debug mode, because of parallel port for EEG and trigger rectangle for ECoG
n_training    = {'eeg':10, 'ecog':10}                  # number of training trials PER CONDITION
n_blocks      = {'eeg':4,  'ecog':3}                   # number of blocks of trials PER CONDITION
n_trials      = {'eeg':100, 'ecog':100}                # number of trials PER BLOCK
break_min_dur = {'eeg':15, 'ecog':15}                  # minimum length (in s) for the break between blocks
n_training, n_blocks, n_trials, break_min_dur = experiment_parameters(paradigm_type)
#!!! check if n_trials/N-blocks==integer

point_amt = 100                                         # Amount to increase/decrease score per trial

#======================================
#  TIMING PARAMETERS  
#======================================
stim_dur = 1                        # duration stimulus is on screen
sound_dur = 0.2                     # duration of sounds
ITIs = [0.5, 0.7]              # duration between stimuli
resp_proc_dur = 0.1                 # duration of window to check for responses at end of trial
post_instr_delay = 1                # duration of delay (in s) after instructions/break to make sure they're ready
block_start_dur = 2                 # duration (in s) to display block start text (e.g., "Level _: type")
end_screen_dur = 10                 # duration (in s) of the ending "thank you all done" screen

n_flicker   = 6                     # number of times to flicker the photodiode on at initial task start
flicker_dur = 0.15                  # duration of each flicker in start sequence
flicker_brk = 3                     # break the sequence after this many flickers (breaks up continuous flickering)

#======================
# STIMULUS PARAMETERS  
#======================
full_screen = True                  # Make the window full screen? (True/False)
#screen_to_show = 1                 # Select which screen to display the window on
screen_units = 'cm'                 # Set visual object sizes in cm (constant across all screens)

# Sounds
#sound_freqs = [440, 880]            # frequency of standard and target tones (randomized)

# Visual
n_circ = 30                         # number of "lights" in the loop
circ_size = .3                      # size of "lights"
socket_size = .5                    # size of empty "lights" (when covered)
loop_radius = 7                     # size of loop of "lights"
target_width = 1.25                    # thickness of target zone IN CM 

# interval_dur = 1, assuming this for computing circle covers
covered_portion = 0.6               # % of interval time obscured when covered=True
trigger_rect_height = 150           # height of the photodiode trigger rectangle IN PIXELS (based on 1920x1080 screen)

#========================
#  ADJUST IF DEBUGGING
#========================
if debug_mode:
    # Cut down design parameters
    n_training = 2
    n_blocks = 2
    n_trials = 10
    break_min_dur = 1
