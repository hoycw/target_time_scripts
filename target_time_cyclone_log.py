# target_time log suite
paradigm_name = 'target_time_ratings'
paradigm_version = '3.0'

from psychopy import visual, event, core, gui, logging, data
import numpy as np
import math, time, random, os

exp_datetime = time.strftime("%Y%m%d%H%M%S")

#=====================================
#=====================================
# CHECK VERSION NUMBER CONSISTENCY
files = [f for f in os.listdir('.') if f[-3:]=='.py' and f.startswith('MAIN_'+paradigm_name)]
# Check for clean directory with only 1 main script
assert len(files)==1
# Check that filename matches paradigm_version coded above
for f in files:
    file_ver = f[f.rfind('_v')+2:-3]
    assert file_ver==paradigm_version


#============================================================
# SET UP LOG FILE
#============================================================
file_dlg = gui.Dlg(title="Run Information")
file_dlg.addText('Paradigm Version: '+paradigm_version, color='Blue')
file_dlg.addField(label='SBJ Code:')
file_dlg.addField(label='Debug Mode:',initial=False)
file_dlg.addField(label='Starting Block:',initial=1)

file_dlg.show()
if file_dlg.OK:
    dlg_resp   = file_dlg.data
    log_prefix = dlg_resp[0]
    debug_mode = dlg_resp[1]
    starting_block = dlg_resp[2]
    log_filename = '../logs/{0}_response_log_{1}.txt'.format(log_prefix,exp_datetime)
else: 
    print('User Cancelled')
#    win.close()
    core.quit()

from target_time_cyclone_parameters import*

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
win.logOnFlip('debug_mode = '+str(debug_mode), logging.DATA)
win.logOnFlip('starting_block = '+str(starting_block), logging.DATA)
win.logOnFlip('n_blocks = '+str(n_blocks), logging.DATA)
win.logOnFlip('n_trials = '+str(n_trials), logging.DATA)
win.logOnFlip('n_fullvis = '+str(n_fullvis), logging.DATA)
win.logOnFlip('n_training = '+str(n_training), logging.DATA)
win.logOnFlip('surp_rate = '+str(surp_rate), logging.DATA)
win.logOnFlip('n_surp = '+str(n_surp), logging.DATA)
win.logOnFlip('surprise_sequence = '+str(surprise_sequence), logging.DATA)
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
win.logOnFlip('full_screen = '+str(full_screen), logging.DATA)
win.logOnFlip('screen_units = '+str(screen_units), logging.DATA)
win.logOnFlip('covered_portion = '+str(covered_portion), logging.DATA)
win.logOnFlip('resp_marker_thickness = '+str(resp_marker_thickness), logging.DATA)
win.logOnFlip('resp_marker_width = '+str(resp_marker_width), logging.DATA)
win.logOnFlip('conditions = '+str(conditions), logging.DATA)
win.logOnFlip('win.size = '+str(win.size), logging.DATA)
win.logOnFlip('point_fn = '+str(point_fn), logging.DATA)

win.logOnFlip('rating_ticks = '+str(rating_ticks), logging.DATA)
win.logOnFlip('rating_labels = '+str(rating_labels), logging.DATA)
win.logOnFlip('rating_width = '+str(rating_width), logging.DATA)
win.logOnFlip('rating_size = '+str(rating_size), logging.DATA)
win.logOnFlip('accept_size = '+str(accept_size), logging.DATA)

exp_clock.reset()
win.flip()

