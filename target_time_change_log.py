#===================================
#  Log of alterations to experiment
#===================================

# cyclone v2.3.3: fixed some timing issues, a typo or two, a littel house cleaning here and there
# cyclone v2.3.2: added EEG parallel port triggers, fixed EEG+debug loop, changed bar to black on surprise trials, fixed outcome sound logging
# cyclone v2.3:   Removed all picture feedback. Implemented surpirse tiral sounds with 9 categories of sounds each holding 8 samples. For each block,
#                 logic randomly selects a category for each surprise trial, then a ound from that category.  
#                 Implemented loging with block, trial, sound and frame time variables.



# cyclone v2.2.3: Implemented sound.Sound function to provide audio feedback for win/loss.  Needs actual audio clips for trials, but will be quick fix.  

# cyclone v2.2.2: Implemented score feedback following Training 

# cyclone v2.2.1: debug csv trial numbers now in correct range, parameters now recieves paradigm_type from _log, csv's now reflect paradigm type and trial number, 
#                 lines 44 and 49 have been updated (the int(float()) thing was for data type conversion but is no longer needed), block loging 'T' error corrected
#                 to show block numbers. 

# cyclone v2.2.1: updated GUI with dropdown menu and check box, logs paradigm_type and debug_mode which are now handled separately, renamed trial_types to conditions

# Cyclone.v.2.2: fully implemented crosshair, cyclone light stimuli, picture feedback, and surprise trials using CSVs.  



# 2.1: added some comments, changed name to fix git version problems
# 2.0: functions brought back into main script

# 1.9.2.test: modularized parameters, log, and variables to cut down on file length 
# 1.9.2: different trigger codes for stim (1) and feedback (2); stim trigger lasts until feedback_delay; adv_scr_txt moved down to avoid overlap
# 1.9.1: EEG triggers actually work after troubleshooting on 135D (must use WinXP)
# 1.9: EEG triggers; no photodiode, screen size 
# 1.8.5: ITIs=[0.2,0.4,0.7,1.0]; feedback_dur=0.8; log:(paradigm_version,n_fullvis,n_training);
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
# 1.5 implements block structure to whole experiment, instructions, training (covered=False examples)
# 1.4 got skipped (handler nonsense)
# 1.3 added photodiode trigger rectangle, basic logging
#   (incomplete logging, to be finished once trail/exp ahndelres are done)
# 1.2 has more comments than 1.1
# implements staircase adjustments to target intervals
# dict for all variables changing across trial types (easy/hard)
