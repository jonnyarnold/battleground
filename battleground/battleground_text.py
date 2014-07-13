# BATTLEFIELD
# v2 - PYGAME
# Jonny Arnold
# jonny@syphernet.com

from battleground_engine import *
import os

def get_user_input(question, type, validation = lambda x: True, length = None):
	'''Gets a user input and validates it according to given function'''
	while 1:
		try:
			input = type(raw_input(question))
		except Exception:
			print "Could not determine value. Please try again!"
		else:
			if (length <> None) and (len(input) <> length):
				print "Not the right size!"
			elif validation(input) == False:
				print "Invalid value. Please try again!"
			else:
				break
	return input

# Load all sides
sides = os.listdir('sides')

if not sides: print "No sides available - exiting!"
else:
	print "Please choose from the following sides:"
	for side in sides:
		print side

p1side['FILE'] = get_user_input('Type a side from the above list for Player 1: ', str, lambda x: True if x in sides else False)
p1side['NAME'] = get_user_input("Type the name of Player 1's side: ", str)

p2side['FILE'] = get_user_input('Type a side from the above list for Player 2: ', str, lambda x: True if x in sides else False)
p2side['NAME'] = get_user_input("Type the name of Player 2's side: ", str)		

# Game initialisation
game = Battleground((WIDTH, HEIGHT))

game.loop()
