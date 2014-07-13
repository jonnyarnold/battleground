#!/usr/bin/env python
# -*- coding: utf-8 -*-

# BATTLEGROUND
# By Jonny Arnold

import math, copy, random

# Constants
OK = 1
NOT_ENOUGH_POINTS = -1
UNIT_NO_EXIST = -2
UNIT_ALREADY_MOVED = -3
SECTION_FULL = -4
UNIT_ALREADY_ATTACKED = -5
INTERNAL_ERROR = -100

# Helper validation function
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

# Useful validation functions
non_negative = lambda x: True if x >= 0 else False
positive = lambda x: True if x > 0 else False
negative = lambda x: True if x < 0 else False
valid_l = lambda x: True if x <= n else False
valid_E_max = lambda x: True if x > E_min else False
valid_beta_max = lambda x: True if x > beta_min else False
# Yes/No
YES, NO = 'y', 'n'
valid_yn = lambda x: True if x in (YES, NO) else False
# Front/Back
FRONT, BACK = 'f', 'b'
valid_fb = lambda x: True if x in (FRONT, BACK) else False
# Unit reference
valid_ref = lambda x: True if (x[0] in (FRONT,BACK,'0')) and x[1].isdigit() else False

STR_KEYNUM = 8
def GetHitStrength(st, df):
	base = st - df + STR_KEYNUM
	if base < 1:
		return 1
	else:
		return base

HIT_KEYNUM = 18
PERCENT_PER_POINT = 5	
def GetHitChance(ac, sp):
	base = (ac - sp + HIT_KEYNUM) * PERCENT_PER_POINT # %
	if base < 20:
		return 20
	elif base > 100:
		return 100
	else:
		return base

class Unit:
	name = ''
	maxht = 0.0
	ht = 0.0
	st = 0.0
	df = 0.0
	ac = 0.0
	sp = 0.0
	p_cost = 0.0
	a_cost = 0.0
	
	def __init__(self, name, stats):
		### stats should be a dictionary of ht, st, df, ac, sp.
		
		# REQUIRES VALIDATION!!!
		self.name = name
		self.maxht, self.st, self.df, self.ac, self.sp = stats
		self.ht = self.maxht
		
		# Set up flags
		self.moved, self.attacked = False, False
		
		# Calculate production cost and action cost
		self.setPCost()
		self.setACost()
	
	def setPCost(self): 
		self.p_cost = math.ceil(((0.4*self.maxht)**2 + self.st**2 + self.df**2 + self.ac**2 + self.sp**2)/8)
	
	def setACost(self):
		if self.p_cost == 0.0:
			self.setPCost()
		self.a_cost = math.ceil(self.p_cost / 10)
	
	def attack(self, defender, counter = False):
		if self.attacked == True and counter == False:
			return UNIT_ALREADY_ATTACKED
		self.attacked = True
		hs, hc = GetHitStrength(self.st, defender.df), GetHitChance(self.ac, defender.sp)
		dice = random.randint(1,100)
		if dice <= hc:
			# Hit!
			defender.ht = defender.ht - hs
			return hs
		else:
			return 0 # Miss

def showCombatStats(atkr, dfnr):
	atk_hs, atk_hc = GetHitStrength(atkr.st, dfnr.df), GetHitChance(atkr.ac, dfnr.sp)
	def_hs, def_hc = GetHitStrength(dfnr.st, atkr.df), GetHitChance(dfnr.ac, atkr.sp)
	
	# Get size of columns
	colatk, coldfn = len(atkr.name), len(dfnr.name)
	
	# Print out!
	print "%s  VS  %s" % (atkr.name.center(colatk), dfnr.name.center(coldfn))
	print "%s  Ht  %s" % ((str(atkr.ht) + '/' + str(atkr.maxht)).center(colatk), (str(dfnr.ht) + '/' + str(dfnr.maxht)).center(coldfn))
	print "%s  St  %s" % (str(atkr.st).center(colatk), str(dfnr.st).center(coldfn))
	print "%s  Df  %s" % (str(atkr.df).center(colatk), str(dfnr.df).center(coldfn))
	print "%s  Ac  %s" % (str(atkr.ac).center(colatk), str(dfnr.ac).center(coldfn))
	print "%s  Sp  %s" % (str(atkr.sp).center(colatk), str(dfnr.sp).center(coldfn))
	print "%s" % (''.center(colatk+coldfn+6, '-'))
	print "%s  HS  %s" % (str(atk_hs).center(colatk), str(def_hs).center(coldfn))
	print "%s  HC  %s" % (str(atk_hc).center(colatk), str(def_hc).center(coldfn))
	

class Battleground:
	MAX_WIDTH = 4
	STARTING_POINTS = 50
	POINTS_PER_TURN = 100
	
	def __init__(self):
		self.field = [[],[]]
		self.points = self.STARTING_POINTS
		
	def addUnit(self, unit, pos = 1):
		### Add the unit to the front (0) or back (1) line
		if len(self.field[pos]) < self.MAX_WIDTH:
			self.field[pos].append(unit)
			return OK
		else:
			return SECTION_FULL
	
	def removeUnit(self, pos):
		### Remove the unit from the (y,x) position
		try:
			del self.field[pos[0]][pos[1]]
		except Exception:
			return UNIT_NO_EXIST
		else:
			return OK
	
	def newUnit(self, unit, pos):
		if self.points - unit.p_cost < 0:
			return NOT_ENOUGH_POINTS
		copiedunit = copy.deepcopy(unit)
		success = self.addUnit(copiedunit, pos)
		if success == OK:
			self.points = self.points - unit.p_cost
			return OK
		else:
			return success
	
	def moveUnit(self, pos):
		### Move the unit in the (y,x) position to the other side of the field
		try:
			unit = self.field[pos[0]][pos[1]]
		except Exception:
			return UNIT_NO_EXIST
		else:
			if unit.moved:
				return UNIT_ALREADY_MOVED
			elif self.points - unit.a_cost < 0:
				return NOT_ENOUGH_POINTS
			else:
				unit.moved = True
				if pos[0] == 0:
					success = self.addUnit(unit, 1)
				elif pos[0] == 1:
					success = self.addUnit(unit, 0)
				if success:
					self.removeUnit(pos)
					self.points = self.points - unit.a_cost
					return OK
				else:
					return success
	
	def getUnit(self, pos):
		### Grab the unit at (y,x) position
		try:
			unit = self.field[pos[0]][pos[1]]
		except IndexError:
			return UNIT_NO_EXIST
		else:
			return unit
	
	def getField(self):
		return self.field
	
	def isEmpty(self):
		if (self.field[0] == []) and (self.field[1] == []):
			return True
		else:
			return False
	
	def isFull(self):
		if (len(self.field[0]) == self.MAX_WIDTH) and (len(self.field[0]) == self.MAX_WIDTH):
			return True
		else:
			return False
	
	def checkForDeath(self):
		deaths = []
		for y in (0,1):
			for x in range(0, len(self.field[y])):
				if self.field[y][x].ht <= 0:
					# Record death for later
					deaths.append((y,x))
		for d in deaths:
			del self.field[d[0]][d[1]]
		return len(deaths)
	
	def resetFlags(self):
		### Reset all movement and attacking flags ###
		for y in (0,1):
			for x in range(0, len(self.field[y])):
				self.field[y][x].moved = False
				self.field[y][x].attacked = False
	
	def newTurn(self):
		self.points = self.points + self.POINTS_PER_TURN
		self.resetFlags()
		# Heal 10% on back row
		for unit in self.field[1]:
			unit.ht = unit.ht + int(math.floor(0.15*unit.maxht))
			if unit.ht > unit.maxht:
				unit.ht = unit.maxht

