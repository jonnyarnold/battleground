#!/usr/bin/env python
# -*- coding: utf-8 -*-

# BATTLEGROUND
# By Jonny Arnold

from game_logic import *

def GetUnitListFromFile(filepath):
	### Reads a file and turns it into a unit list
	file = open(filepath)
	if file:
		unitlist = []
		for line in file:
			# Explode the line by tab
			line.rstrip("\n")
			attr = []
			lsplit = line.split("\t")
			if len(lsplit) == 6:
				name, attr = lsplit[0], map(int, lsplit[1:6])
				newunit = Unit(name, attr)
				unitlist.append(newunit)
		return unitlist
	else:
		return None

if __name__ == '__main__':
	# Run game
	gm = Game()
	gm.setUnitList(1, GetUnitListFromFile('specialists.txt'))
	gm.setUnitList(2, GetUnitListFromFile('experiment.txt'))
	print "BATTLEFIELD"
	print "Units loaded: let the games begin..."
	gm.playGame()
	
