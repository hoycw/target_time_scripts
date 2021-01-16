### Test mouse for multiple presses
from psychopy import visual, event, core

win = visual.Window(size=(800,600), fullscr=False, color=(0,0,0),
                    monitor='testMonitor',#monitor_name,# screen=screen_to_show,
                    allowGUI=False, waitBlanking=True);
#NOTE: ThinkPad P51 (ECoG-1/Klay/etc.) = 34.5cm wide, 19.5cm tall
#   ECoG-A laptop size = 36cm wide, 20sm tall

mouse = event.Mouse()  #  will use win by default

check_txt = visual.TextStim(win,text='checking for presses 1',height=2,units='cm',
                                name='welcome', color='black', bold=True, pos=(0,2),wrapWidth=30)

exp_clock = core.Clock()

# ROUND 1
start = exp_clock.getTime()
win.callOnFlip(mouse.clickReset)
win.callOnFlip(event.clearEvents)
down_btns = []
down_rts = []
up_btns = []
up_rts = []
n_presses = 0
prev_btn_status = [0, 0, 0]
curr_btn_status = [0, 0, 0]

check_txt.draw()
win.flip()
while exp_clock.getTime() < start + 10:
    curr_btn_status, tmp_rt = mouse.getPressed(getTime=True)
    if curr_btn_status != prev_btn_status:    # Check if button status changed
        for b_ix, b in enumerate(curr_btn_status):  
            if b == 1 and b != prev_btn_status[b_ix]:  # Log which button was pressed and RT only if clicked down (not released)
                down_btns.append(b_ix)
                down_rts.append(tmp_rt)
                n_presses += 1
            elif b==0 and b != prev_btn_status[b_ix]:
                up_btns.append(b_ix)
                up_rts.append(tmp_rt)
        prev_btn_status = curr_btn_status

# Collect responses
final_buttons, final_rts = mouse.getPressed(getTime=True)
print('final mouse data for round 1:', final_buttons, final_rts)
print('n_presses = ', n_presses)
print('down mouse btns for round 1:', down_btns)
print('down mouse rts for round 1:', down_rts)
print('up mouse btns for round 1:', up_btns)
print('up mouse rts for round 1:', up_rts)

## ROUND 2
#start2 = exp_clock.getTime()
#win.callOnFlip(mouse.clickReset)
#win.callOnFlip(event.clearEvents)
#
#check_txt.text = 'round 2'
#check_txt.draw()
#win.flip()
#while exp_clock.getTime() < start2 + 10:
#    core.wait(0.001)
#print('start2, end: ',start2, exp_clock.getTime())
#
## Collect responses
#buttons2, rts2 = mouse.getPressed(getTime=True)
#
#print('mouse data for round 2:', buttons2, rts2)

win.close()
core.quit()