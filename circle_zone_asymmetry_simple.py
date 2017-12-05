from psychopy import visual, core
from psychopy.tools.coordinatetools import pol2cart
import numpy as np


# Parameters
loop_radius = 10
n_circ = 30
interval_dur = 1                    # duration (in sec) of target time interval
angle_ratio = 360/float(interval_dur)
tolerances = 0.125                   # allowed error on EACH side
tolerance_step = [-0.003,0.012]     # change in tolerance after win, loss

target_upper_bound = angle_ratio * (tolerances*2)  # Get angle of total tolerance from interval_dur
target_origin = 180 - (tolerances * angle_ratio)   # zero starts at 12 oclock for radial stim.  
target_width = 1.5

# Stimuli
win = visual.Window(size=(1920, 1200), fullscr=True, color=(0,0,0),
                    monitor='testMonitor',
                    allowGUI=False, units='cm')#, waitBlanking=False); # !!! check on this waitBlank parameter!
target_zone = visual.RadialStim(win, tex='sqrXsqr', color='green', size=(loop_radius*2) + target_width,  # size = diameter
    visibleWedge=[0, target_upper_bound], radialCycles=1, angularCycles=0, interpolate=False,
    autoLog=False, units='cm')  
target_zone.visibleWedge = [0, target_upper_bound]
target_zone.ori = target_origin
target_zone_cover = visual.Circle(win, radius = loop_radius - target_width/2, edges=100,
    lineColor=None, fillColor=[0, 0, 0]) # Covers center of wedges used to draw tunnel and taret zone

circ_angles = np.linspace(-90,270,n_circ)
print circ_angles
print np.diff(circ_angles)
circ_X, circ_Y = pol2cart(circ_angles,[loop_radius] * n_circ)
circ_colors = [(-1,-1,-1)] * n_circ
circles = visual.ElementArrayStim(win, nElements=n_circ,sizes=.3,xys = zip(circ_X, circ_Y),
                           elementTex = None, elementMask = "circle",
                           colors=circ_colors)


# Plot first time
target_zone.draw()
target_zone_cover.draw()
circles.draw()
win.flip()
print 'origin = ', target_origin, 'upper =' ,target_upper_bound, 'origin+upper=',target_origin+target_upper_bound
print 'tolerances = ' ,tolerances, '180+(tolerances*angle)=', 180+(tolerances*angle_ratio)
print 'visibleWEdge = ', target_zone.visibleWedge, 'tz.ori = ', target_zone.ori

# Assume incorrect response, update target zone
tolerances+= tolerance_step[1]
target_origin = 180 - (tolerances * angle_ratio)
target_upper_bound =  2*tolerances*angle_ratio
target_zone.visibleWedge = [0, target_upper_bound]
target_zone.ori = target_origin
core.wait(3)

# Plot again, check for asymmetry
target_zone.draw()
target_zone_cover.draw()
circles.draw()
win.flip()
print 'origin = ', target_origin, 'upper =' ,target_upper_bound, 'origin+upper=',target_origin+target_upper_bound
print 'tolerances = ' ,tolerances, '180+(tolerances*angle)=', 180+(tolerances*angle_ratio)
print 'visibleWEdge = ', target_zone.visibleWedge, 'tz.ori = ', target_zone.ori

# Assume incorrect response, update target zone
#tolerances+= tolerance_step[1]
#target_origin = 180 - (tolerances * angle_ratio)
#target_upper_bound =  2*tolerances*angle_ratio
#target_zone.visibleWedge = [0, target_upper_bound]
#target_zone.ori = target_origin
core.wait(3)
