# target_time log suite
paradigm_name = 'oddball'
paradigm_version = '1.1'

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
file_dlg.addText('Oddball Version: '+paradigm_version, color='Blue')
file_dlg.addField(label='SBJ Code:')
file_dlg.addField(label='Parameter Version:',choices=['ecog','eeg'])
file_dlg.addField(label='Use RT Box:',initial=True)
file_dlg.addField(label='Debug Mode:',initial=False)
file_dlg.addField(label='Starting Block:',initial=1)
#file_dlg.addField('Response Key:') # Ideally space bar? something more accurate?

file_dlg.show()
if file_dlg.OK:
    dlg_resp   = file_dlg.data
    log_prefix = dlg_resp[0]
    paradigm_type  = dlg_resp[1]
    use_rtbox = dlg_resp[2]
    debug_mode = dlg_resp[3]
    starting_block = dlg_resp[4]
    log_filename = '../logs/{0}_oddball_log_{1}.txt'.format(log_prefix,exp_datetime)
else: 
    print 'User Cancelled'
#    win.close()
    core.quit()

# Get correct stimulus/response mappings
if paradigm_type == 'eeg':
    ord_gui = gui.Dlg(title='Subject Number')
    ord_gui.addText('EEG Oddball Stimulus/Response Mappings')
    ord_gui.addFiled(label='SBJ Number:')
    ord_gui.show()
    if ord_gui.OK:
        ord_gui_data = ord_gui.data
        eeg_seq_num = ord_gui_data[0]
    else:
        print 'User Cancelled'
        core.quit()

from oddball_parameters import*
from oddball_variables import*


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
win.logOnFlip('paradigm_type = '+str(paradigm_type), logging.DATA)
win.logOnFlip('use_rtbox = '+str(use_rtbox), logging.DATA)
win.logOnFlip('debug_mode = '+str(debug_mode), logging.DATA)
win.logOnFlip('starting_block = '+str(starting_block), logging.DATA)
win.logOnFlip('n_blocks = '+str(n_blocks), logging.DATA)
win.logOnFlip('n_trials = '+str(n_trials), logging.DATA)
win.logOnFlip('n_training = '+str(n_training), logging.DATA)
win.logOnFlip('block_order = '+str(block_order), logging.DATA)
win.logOnFlip('stim_dur = '+str(stim_dur), logging.DATA)
win.logOnFlip('sound_dur = '+str(sound_dur), logging.DATA)
win.logOnFlip('ITIs = '+str(ITIs), logging.DATA)
win.logOnFlip('break_min_dur = '+str(break_min_dur), logging.DATA)
win.logOnFlip('post_instr_delay = '+str(post_instr_delay), logging.DATA)
win.logOnFlip('block_start_dur = '+str(block_start_dur), logging.DATA)
win.logOnFlip('n_flicker = '+str(n_flicker), logging.DATA)
win.logOnFlip('flicker_brk = '+str(flicker_brk), logging.DATA)
win.logOnFlip('flicker_dur = '+str(flicker_dur), logging.DATA)
win.logOnFlip('keys = '+str(keys), logging.DATA)
win.logOnFlip('visual assignment = '+str(v_idx), logging.DATA)
win.logOnFlip('auditory assignment = '+str(a_idx), logging.DATA)
win.logOnFlip('response assignment = '+str(r_idx), logging.DATA)
win.logOnFlip('oddball order = '+str(odd_idx), logging.DATA)
win.logOnFlip('full_screen = '+str(full_screen), logging.DATA)
win.logOnFlip('screen_units = '+str(screen_units), logging.DATA)
win.logOnFlip('covered_portion = '+str(covered_portion), logging.DATA)
win.logOnFlip('conditions = '+str(conditions), logging.DATA)
win.logOnFlip('trigger_rect_height = '+str(trigger_rect_height), logging.DATA)
win.logOnFlip('win.size = '+str(win.size), logging.DATA)

exp_clock.reset()
win.flip()

