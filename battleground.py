# BATTLEFIELD
# v2 - PYGAME
# Jonny Arnold
# jonny@syphernet.com

from battleground_engine import *
import side_setup
import os
import gtk

# Load player window
ss = side_setup.SideSetupWindow()
ss.updateSideList(os.listdir('sides'))
gtk.main()

p1side, p2side = ss.get_sides()

if p1side != None and p2side != None:
	# Game initialisation
	game = Battleground((WIDTH, HEIGHT), p1 = p1side, p2 = p2side)
	game.loop()
