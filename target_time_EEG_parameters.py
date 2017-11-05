#target_time parameter file 
#part of modularization 
paradigm_version = '1.9.2'


from psychopy import visual, event, core, gui, logging, data
#from psychopy import parallel
import numpy as np
import math, time, random, shelve
#random.seed()
#core.wait(0.5)      # give the system time to settle
#core.rush(True)     # might give psychopy higher priority in the system (maybe...)
exp_datetime = time.strftime("%Y%m%d%H%M%S")
paradigm_name = 'target_time'


#============================================================
# EXPERIMENT PARAMETERS
#============================================================


n_examples = 5                     # number of EASY examples to start (large tolerance, full window)
n_training = 15                     # number of training trials PER CONDITION
n_blocks = 4                        # number of blocks of trials PER CONDITION
n_trials = 75                       # number of trials PER BLOCK
break_min_dur = 30                  # minimum length (in s) for the break between blocks

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

# Stimulus Parameters
game_height = 20                    # amount of screen for plotting
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


