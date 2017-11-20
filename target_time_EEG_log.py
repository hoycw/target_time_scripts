# target_time log suite
#for import with target_time_1.9.2
paradigm_version = '1.9.2'

from psychopy import visual, event, core, gui, logging, data
#from psychopy import parallel
import numpy as np
import math, time, random, shelve
from target_time_EEG_parameters import*
  

#random.seed()
#core.wait(0.5)      # give the system time to settle
#core.rush(True)     # might give psychopy higher priority in the system (maybe...)
exp_datetime = time.strftime("%Y%m%d%H%M%S")
paradigm_name = 'target_time'



#============================================================
# SET UP LOG FILE
#============================================================
file_dlg = gui.Dlg(title="Run Information")
file_dlg.addField('SBJ Code:')
#file_dlg.addField('Response Key:') # Ideally space bar? something more accurate?

file_dlg.show()
if gui.OK:
    dlg_resp = file_dlg.data
    log_prefix = dlg_resp[0]
    #key = dlg_resp[1] !!! fix this!!!
    log_filename = '../{0}_response_log_{1}.txt'.format(log_prefix,exp_datetime) #'../logs/{0}_response_log_{1}.txt'.format(log_prefix,exp_datetime)
else: 
    print 'User Cancelled'
    win.close()
    core.quit()



from target_time_EEG_variables import*


#============================
# LOG PARADIGM PARAMETERS
#============================

logging.setDefaultClock(exp_clock)                                       #use this for
logging.console.setLevel(logging.DATA)                               #do NOT set to INFO! Way too much logging, crashes system
logger = logging.LogFile(log_filename,logging.DATA,'w')
win.setRecordFrameIntervals(True)                                    #capture frame intervals
win.saveFrameIntervals(fileName=log_filename, clear=False)           #write frame intervals to log_filename

#Vars to log:
win.logOnFlip('paradigm_name = '+str(paradigm_name), logging.DATA)
win.logOnFlip('paradigm_version = '+str(paradigm_version), logging.DATA)
win.logOnFlip('n_blocks = '+str(n_blocks), logging.DATA)
win.logOnFlip('n_trials = '+str(n_trials), logging.DATA)
win.logOnFlip('n_fullvis = '+str(n_fullvis), logging.DATA)
win.logOnFlip('n_training = '+str(n_training), logging.DATA)
win.logOnFlip('interval_dur = '+str(interval_dur), logging.DATA)
win.logOnFlip('feedback_delay = '+str(feedback_delay), logging.DATA)
win.logOnFlip('feedback_dur = '+str(feedback_dur), logging.DATA)
win.logOnFlip('ITIs = '+str(ITIs), logging.DATA)
win.logOnFlip('break_min_dur = '+str(break_min_dur), logging.DATA)
win.logOnFlip('post_instr_delay = '+str(post_instr_delay), logging.DATA)
win.logOnFlip('block_start_dur = '+str(block_start_dur), logging.DATA)
win.logOnFlip('tolerances = '+str(tolerances), logging.DATA)
win.logOnFlip('tolerance_step = '+str(tolerance_step), logging.DATA)
win.logOnFlip('tolerance_lim = '+str(tolerance_lim), logging.DATA)
win.logOnFlip('Key = '+str(key), logging.DATA)
win.logOnFlip('full_screen = '+str(full_screen), logging.DATA)
win.logOnFlip('screen_units = '+str(screen_units), logging.DATA)
win.logOnFlip('game_height = '+str(game_height), logging.DATA)
win.logOnFlip('interval_height = '+str(interval_height), logging.DATA)
win.logOnFlip('target_y = '+str(target_y), logging.DATA)
win.logOnFlip('covered_portion = '+str(covered_portion), logging.DATA)
win.logOnFlip('tower_width = '+str(tower_width), logging.DATA)
win.logOnFlip('ball_radius = '+str(ball_radius), logging.DATA)
win.logOnFlip('window_width = '+str(window_width), logging.DATA)
win.logOnFlip('resp_marker_thickness = '+str(resp_marker_thickness), logging.DATA)
win.logOnFlip('resp_marker_width = '+str(resp_marker_width), logging.DATA)
win.logOnFlip('n_rings = '+str(n_rings), logging.DATA)
win.logOnFlip('trial_types = '+str(trial_types), logging.DATA)
win.logOnFlip('color_list = '+str(color_list), logging.DATA)
win.logOnFlip('trigger_rect_height = '+str(trigger_rect_height), logging.DATA)
win.logOnFlip('trigger_dur = '+str(trigger_dur), logging.DATA)
win.logOnFlip('win.size = '+str(win.size), logging.DATA)
win.logOnFlip('frame_len = '+str(frame_len), logging.DATA)
win.logOnFlip('point_fn = '+str(point_fn), logging.DATA)

exp_clock.reset()
win.logOnFlip('CLOCK RESET FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA)
win.flip()
