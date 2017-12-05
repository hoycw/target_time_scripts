# target_time log suite
paradigm_name = 'target_time_cyclone'
paradigm_version = '1.1'

from psychopy import visual, event, core, gui, logging, data
import numpy as np
import math, time, random

exp_datetime = time.strftime("%Y%m%d%H%M%S")

#============================================================
# SET UP LOG FILE
#============================================================
file_dlg = gui.Dlg(title="Run Information")
file_dlg.addField('SBJ Code:')
file_dlg.addField('Parameter Version:')
file_dlg.addField('Debug Mode? (Y/N):')
#file_dlg.addField('Response Key:') # Ideally space bar? something more accurate?

file_dlg.show()
if gui.OK:
    dlg_resp   = file_dlg.data
    log_prefix = dlg_resp[0]
    param_ver  = dlg_resp[1]
    debug_mode = dlg_resp[2]    #!!! need a logic check that this is y/Y/n/N value
    #key = dlg_resp[1] !!! fix this!!!
    log_filename = '../logs/{0}_response_log_{1}.txt'.format(log_prefix,exp_datetime)
else: 
    print 'User Cancelled'
    win.close()
    core.quit()

from target_time_cyclone_parameters import*
#try: key = pradigm_ver
#actual= var_chanign[key]

from target_time_cyclone_variables import*


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
win.logOnFlip('covered_portion = '+str(covered_portion), logging.DATA)
win.logOnFlip('resp_marker_thickness = '+str(resp_marker_thickness), logging.DATA)
win.logOnFlip('resp_marker_width = '+str(resp_marker_width), logging.DATA)
win.logOnFlip('trial_types = '+str(trial_types), logging.DATA)
win.logOnFlip('trigger_rect_height = '+str(trigger_rect_height), logging.DATA)
win.logOnFlip('trigger_dur = '+str(trigger_dur), logging.DATA)
win.logOnFlip('win.size = '+str(win.size), logging.DATA)
win.logOnFlip('point_fn = '+str(point_fn), logging.DATA)

exp_clock.reset()
win.logOnFlip('CLOCK RESET FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA)
win.flip()

