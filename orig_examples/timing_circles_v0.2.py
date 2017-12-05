from psychopy import visual, event, core, gui, logging
import numpy as np
import math, time
from psychopy.tools.coordinatetools import pol2cart
core.wait(0.5)#give the system time to settle

n_blocks = 1
n_trials = 3
#frames_per_circ = 5
interval_len = 1
feedback_delay = 2
feedback_len = 2
ITI = 1.5
#total_time = 5

key = 'm'
full_screen = False
screen_to_show = 1
n_circ = 20
n_occluded = 0
circ_size = 20
loop_radius = 200
loop_circum = 128

# Environment Variables
win = visual.Window(size=[800,600], fullscr=full_screen,
                    monitor='testMonitor', screen=screen_to_show,
                    allowGUI=True, units='pix')#, waitBlanking=False); # !!! check on this waitBlank parameter!
clock = core.Clock();

# Timing Variables
time_per_circ = float(interval_len) / float(n_circ)
frame_len = win.monitorFramePeriod
frames_per_circ = int(math.ceil(time_per_circ/frame_len))
print frame_len, frames_per_circ
# calculate frames_per_circ #this doesn't have to be perfect, just within limits of perception
estimate_win = interval_len + feedback_delay
#!!! check if n_trials/N-blocks==integer

# Light Stimuli
circ_angles = np.array([pos_ix*(360/n_circ)-90 for pos_ix in range(n_circ)])
circ_radius = [loop_radius] * n_circ
circ_X, circ_Y = pol2cart(circ_angles,circ_radius)
circ_colors = [(0,0,0)] * n_circ
circles = visual.ElementArrayStim(win, nElements=n_circ,sizes=circ_size,xys = zip(circ_X, circ_Y),
                           elementTex = None, elementMask = "circle",
                           colors=circ_colors)#, autoDraw=True) 
#circle = visual.Circle(win,radius=100,lineWidth=5,pos=(0,0),autoDraw=True);#,lineWith=3,lineColor='white',color='red');

#occluder
loop_angles = np.array([pos_ix*(360/n_circ)-90 for pos_ix in range(loop_circum)])
loop_X, loop_Y = pol2cart(circ_angles,loop_radius)
#occluder = 

# Instructions
instr_txt = 'Start trial by pressing {0}.\nPress again to stop the light on the target'
instr_str = visual.TextStim(win,text=instr_txt,height=25,units='pix',name='intro', color='black',wrapWidth=550,pos=(0,100))

# Feedback Stimuli
feedback_str = visual.TextStim(win,text='yay',height=25,units='pix',name='feedback', color='black',wrapWidth=550,pos=(0,100))
#resp_marker = line(win, color='red')
#target_marker = line(win, color='black')
#target_range = visual.PatchStim(win, tex=None, mask=None,
#    size=[target_width,0.05],color='green',pos=[0,-0.9],
#    autoLog=False)

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
    #key = dlg_resp[1]
    log_filename = '../logs/{0}_response_log_{1}.txt'.format(log_prefix,time.strftime("%Y%m%d%H%M%S"))
else: 
    print 'User Cancelled'
    win.close()
    core.quit()

# LOG KEY
#============================
logging.setDefaultClock(clock)                                       #use this for
logging.console.setLevel(logging.DATA)                               #set the console to receive nearly all messges
#logging.INFO to print every frame time
logger = logging.LogFile(log_filename,logging.DATA,'w')
win.setRecordFrameIntervals(True)                                    #capture frame intervals
win.saveFrameIntervals(fileName=log_filename, clear=False)           #write frame intervals to log_filename
win.logOnFlip('Key = '+str(key), logging.DATA)
clock.reset()
win.logOnFlip('CLOCK RESET FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA)
win.flip()

#============================================================
# INSTRUCTIONS
#============================================================
win.logOnFlip('Instructions FRAME TIME = {0}'.format(win.lastFrameT),logging.DATA)
instr_str.draw()
win.flip()
response = event.waitKeys(keyList=key, timeStamped=clock)
print response
win.logOnFlip('Instruction Response: {0}, FRAME TIME = {1} for response, win.lastFrameT={2}'.format(
                response[0][0], response[0][1], win.lastFrameT), logging.DATA);
win.flip()

#============================================================
# EXPERIMENT
#============================================================

# Draw circles
circles.setAutoDraw(True)
#for block in range(n_blocks):
block = 0
for trial in range(n_trials):
    win.logOnFlip('B{0}_T{1} start: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.DATA)
    elapsed_time = clock.getTime()
    elapsed_time = elapsed_time + estimate_win
    # Visible Circles
    for circ_ix in range(n_circ-n_occluded):
        circ_colors[circ_ix] = (1,1,1)
        circles.colors = circ_colors
        circles.draw()
        win.flip()
        for f in xrange(frames_per_circ): win.flip()
    # Occluded Circles
    t = clock.getTime()
    if (n_occluded > 0) & (t<elapsed_time):
        while clock.getTime()<elapsed_time:
            response = event.getKeys(keyList=key, timeStamped=clock)
            if len(response)>0:
                win.logOnFlip('B{0}_T{1} Response: {2}, FRAME TIME = {3}'.format(block,trial,response,win.lastFrameT),logging.DATA)
    circ_colors = [(0.5,0.5,0.5)] * n_circ
    circles.colors = circ_colors
    circles.draw()
    feedback_str.draw()
    win.logOnFlip('B{0}_T{1} feedback: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.DATA)
    win.flip()
    # draw random ITI
    elapsed_time = elapsed_time + feedback_len
    while clock.getTime() < elapsed_time:
        pass
        #check for quit
    circ_colors = [(0,0,0)] * n_circ
    circles.colors = circ_colors
    circles.draw()
    win.logOnFlip('B{0}_T{1} ITI: FRAME TIME = {2}'.format(block,trial,win.lastFrameT),logging.DATA)
    win.flip()
    elapsed_time = elapsed_time + ITI
    while clock.getTime() < elapsed_time:
        pass
        #check for quit



win.close()
core.quit()

