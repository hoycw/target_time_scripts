
from psychopy import visual, event, core, logging
import os

win = visual.Window(fullscr=False, size=[1100, 800], units='pix', monitor='testMonitor')

# Create slider instructions
rating_str = 'How likely is it that you responses in the target zone?'
rating_txt = visual.TextStim(win,text=rating_str,height=1,units='cm',
                                name='feedback_timing', color='black',pos=(0,-3),wrapWidth=14)

# Create slider stimuli
slider_ticks = (0, 50, 100)
slider_labels = ['Definitely Lost', '', 'Definitely Won']
slider_width = 10
slider_height = 1
slider_gran = 0             # 0 for continuous

rating_slider = visual.Slider(win, ticks=slider_ticks, labels=slider_labels, pos=(0,0), size=(slider_width, slider_height), 
                                    units='cm',granularity=slider_gran, style='rating', labelHeight=None, labelWrapWidth=None)


# Run slider
data = []
rating_slider.reset()
event.clearEvents()
while rating_slider.noResponse:  # show & update until a response has been made
    rating_txt.draw()
    rating_slider.draw()
    win.flip()
    if event.getKeys(['escape']):
        core.quit()

data.append([rating_slider.getRating(), rating_slider.getRT()])  # save for later

rating_slider.reset()

print(data)

core.quit()