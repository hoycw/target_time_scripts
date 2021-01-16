
from psychopy import visual, event, core, logging
import os

win = visual.Window(fullscr=True, size=[800, 600], units='pix', monitor='testMonitor')

# Create slider instructions
rating_str = 'How likely is it that you won on this trial by responding in the target zone?'
rating_txt = visual.TextStim(win,text=rating_str,height=2,units='cm',
                                name='feedback_timing', color='black',pos=(0,5),wrapWidth=36)

# Create slider stimuli
slider_ticks = [0, 50, 100]
slider_labels = ['Definitely Lost', '', 'Definitely Won']
slider_width = 10
slider_height = 1
slider_gran = 0             # 0 for continuous

rating_scale = visual.RatingScale(win, mouseOnly=True, pos=(0,-6),
    low=0, high=100, tickMarks=[0, 100], labels=['Definitely Lost','Definitely Won'], 
    showValue=False, acceptText='Submit Answer', acceptSize=1.5, size=1, name='rating_scale')

#low=0, high=100, marker='slider',
#    tickMarks=[0, 50, 82, 100], stretch=1.5, tickHeight=1.5,  # singleClick=True,
#    labels=["0%", "half/half", "kinda", "100%"])
#visual.Slider(win, ticks=slider_ticks, labels=slider_labels, pos=(0,0), size=(slider_width, slider_height), 
#                                    units='cm',granularity=slider_gran, style='rating', labelHeight=None, labelWrapWidth=None)

# Run slider
data = []
rating_scale.reset()
event.clearEvents()
while rating_scale.noResponse:  # show & update until a response has been made
    rating_txt.draw()
    rating_scale.draw()
    win.flip()
    if event.getKeys(['escape']):
        core.quit()

data.append([rating_scale.getRating(), rating_scale.getRT()])  # save for later

rating_scale.reset()

print(data)

core.quit()