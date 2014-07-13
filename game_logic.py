#!/usr/bin/env python
# -*- coding: utf-8 -*-

# BATTLEGROUND
# By Jonny Arnold

from battleground_objects import *

import time

PLAYER_ALL = 1
PLAYER_FRONT = 2
ENEMY_ALL = 3
ENEMY_FRONT = 4

class Game:
	
	playerturn = 1
	turnnum = 1

	ydict = {'f': 0, 'b': 1}
	
	def __init__(self):
		bg1 = Battleground()
		bg2 = Battleground()
		self.bgs = [bg1, bg2]
		self.unitlists = [[], []]
	
	def setUnitList(self, player, unitlist):
		self.unitlists[player-1] = unitlist
		return True
	
	def showField(self):
		for p in range(1,3):
			print "PLAYER ", p
			field = self.bgs[p-1].getField()
			print "FRONT:"
			front,back = field[0], field[1]
			if len(front) == 0:
				print "\tNo units"
			else:
				for unit in front:
					print "\t%s (%d/%d)" % (unit.name, unit.ht, unit.maxht),
					if unit.moved:
						print " [M]",
					if unit.attacked:
						print " [A]",
					print
			print "BACK:"
			if len(back) == 0:
				print "\tNo units"
			else:
				for unit in back:
					print "\t%s (%d/%d)" % (unit.name, unit.ht, unit.maxht),
					if unit.moved:
						print " [M]",
					if unit.attacked:
						print " [A]",
					print
			print
	
	def showTacticalField(self, section = 0, player = None):
		if player == None:
			player = self.playerturn
		
		p, y = player, section
		print ":: PLAYER ", p,
		if y == 0:
			print " FRONT ::"
		else:
			print " BACK ::"
		if self.bgs[p-1].isEmpty():
			print "\tNo units!"
		else:
			field = self.bgs[p-1].getField()
			# Format names
			names = ['(Empty)']
			for x in range(0, len(field[y])):
				names.append(field[y][x].name)
			maxlength = max(map(len,names))
			spacer = ''
			spacer = spacer.ljust(maxlength)
			print " ##   %s  Ht     St  Df  Ac  Sp  AcC  M  A" % (spacer)
			if y == 0:
				y = 'f'
			else:
				y = 'b'
			for x in range(0, self.bgs[p-1].MAX_WIDTH):
				try:
					unit = field[self.ydict[y]][x]
				except Exception:
					print "[%s%d]: (Empty)" % (y, x+1)
				else:
					m, a = ' ', ' '
					if unit.moved:
						m = 'X'
					if unit.attacked:
						a = 'X'
					print "[%s%d]: %s  %2d/%2d  %2d  %2d  %2d  %2d  %3d  %s  %s" % (y, x+1, unit.name.ljust(maxlength), unit.ht, unit.maxht, unit.st, unit.df, unit.ac, unit.sp, unit.a_cost, m, a)				

	def buyUnits(self):
		# Get current player's unit list
		print "\n:: BUY UNITS ::"
		self.showUnitList(self.playerturn)
		# Enter purchase loop
		done = False
		while not done:
			if len(self.bgs[self.playerturn-1].field[1]) == self.bgs[self.playerturn-1].MAX_WIDTH:
				print 'The back field is full, you cannot purchase any more units until some are moved.'
				break
			else:
				num = get_user_input('Enter a number to buy, or 0 to exit: ', int)
				if num == 0:
					done = True
				else:
					if 1 <= num <= len(self.unitlists[self.playerturn-1]):
						# Validate choice
						selectedunit = self.unitlists[self.playerturn-1][num-1]
						prompt = "Purchase %s for %d points? (y/n) " % (selectedunit.name, selectedunit.p_cost)
						response = get_user_input(prompt, str, valid_yn)
						if response == YES:
							success = self.bgs[self.playerturn-1].newUnit(selectedunit, 1)
							if success == OK:
								print "Success! %d points left." % self.bgs[self.playerturn-1].points
								self.showUnitList(self.playerturn)
							elif success == NOT_ENOUGH_POINTS:
								print 'Not enough points!'
							elif success == SECTION_FULL:
								print 'No room in this row!'
							else:
								print 'ERROR'
					else:
						print "Unknown unit: please try again."
			
	def fight(self):
		done = False
		while not done:
			self.showTacticalField(0)
			response = get_user_input('Enter a unit reference to attack, or 00 to exit e.g. b4: ', str, valid_ref, 2)
			if response == '00':
				return True
			else:
				pos = (self.ydict[response[0]], int(response[1])-1)
				attacker = self.bgs[self.playerturn-1].getUnit(pos)
				
				if attacker == UNIT_NO_EXIST:
					print 'Not a valid unit reference!'
				else:
					if attacker.attacked == True:
						print "Unit has already attacked this turn!"
						continue
					else:
						if self.playerturn == 1:
							enemy = 2
						else:
							enemy = 1
						enemyfield = self.bgs[enemy-1].getField()
						if enemyfield[0] == []:
							print "No front line!"
							self.showTacticalField(1, enemy)
						else:
							self.showTacticalField(0, enemy)
						response = get_user_input('Enter a enemy unit reference to attack, or 00 to cancel e.g. b4: ', str, valid_ref, 2)
						if response == '00':
							continue
						else:
							pos = (self.ydict[response[0]], int(response[1])-1)
							defender = self.bgs[enemy-1].getUnit(pos)
							if defender == UNIT_NO_EXIST:
								print 'Not a valid unit reference!'
							else:
								# Defender in back row has penalty!
								if pos[0] == 1:
									print "Back field ambush! 66% stats for defender!"
									oldst, olddf, oldac, oldsp = defender.st, defender.df, defender.ac, defender.sp
									defender.st = int(math.floor(defender.st*0.66))
									defender.df = int(math.floor(defender.df*0.66))
									defender.ac = int(math.floor(defender.ac*0.66))
									defender.sp = int(math.floor(defender.sp*0.66))
								
								showCombatStats(attacker, defender)
								print "%d points to attack (You have %d)" % (attacker.a_cost, self.bgs[self.playerturn-1].points)
								response = get_user_input('Attack? (y/n) ', str, valid_yn)
								if response == 'n':
									continue
								else:
									if attacker.a_cost > self.bgs[self.playerturn-1].points:
										print "Not enough points to attack!"
									else:
										atkdmg = attacker.attack(defender)
										self.bgs[self.playerturn-1].points = self.bgs[self.playerturn-1].points - attacker.a_cost
										time.sleep(1)
										if atkdmg == 0:
											print "Attacker misses! [Defender Sp+1]"
											defender.sp = defender.sp+1
										else:
											print "Attacker hits - ", atkdmg, " damage! [Ac+1]"
											attacker.ac = attacker.ac+1
										death = self.bgs[enemy-1].checkForDeath()
										if death:
											extrapts = math.ceil(defender.p_cost / 4)
											print "Defender has been killed! %d points gained" % extrapts
											self.bgs[self.playerturn-1].points = self.bgs[self.playerturn-1].points + extrapts
										else:
											time.sleep(1)
											# Defender counters
											dfndmg = defender.attack(attacker, True)
											if dfndmg == 0:
												print "Defender misses on counterattack! [Attacker Df+1]"
												attacker.df = attacker.df+1
											else:
												print "Defender counterattacks - ", dfndmg, " damage! [St+1]"
												defender.st = defender.st+1
												death = self.bgs[self.playerturn-1].checkForDeath()
												if death:
													extrapts = math.ceil(attacker.p_cost / 4)
													print "Attacker has been killed! (%d points gained by defender)" % extrapts
													self.bgs[enemy-1].points = self.bgs[enemy-1].points + extrapts
										time.sleep(1)
								# Return stats
								if pos[0] == 1:
									defender.st, defender.df, defender.ac, defender.sp = oldst, olddf, oldac, oldsp

	
	def moveUnits(self):
		print ":: MOVE UNITS ::"
		self.showTacticalField(0)
		self.showTacticalField(1)
		if self.bgs[self.playerturn-1].isEmpty():
			return True
		else:
			# Enter movement loop
			done = False
			while not done:
				response = get_user_input('Enter a unit reference to move, or 00 to exit e.g. b4: ', str, valid_ref, 2)
				if response == '00':
					done = True
					break
				else:
					pos = (self.ydict[response[0]], int(response[1])-1)
					unit = self.bgs[self.playerturn-1].getUnit(pos)
					if unit == UNIT_NO_EXIST:
						print 'Not a valid unit reference!'
					else:
						success = self.bgs[self.playerturn-1].moveUnit(pos)
						if success == OK:
							print 'Unit moved! %d points left' % self.bgs[self.playerturn-1].points
							self.showTacticalField(0)
							self.showTacticalField(1)
						elif success == NOT_ENOUGH_POINTS:
							print 'Not enough points!'
						elif success == SECTION_FULL:
							print 'Section is full: cannot move!'
						elif success == UNIT_ALREADY_MOVED:
							print 'Unit has already moved this turn!'
						else:
							print 'ERROR'
	
	def showUnitList(self, player = None):
		if player == None:
			player = self.playerturn
		
		unitlist = self.unitlists[player-1]
		# Format names
		names = []
		for u in unitlist:
			names.append(u.name)
		maxlength = max(map(len,names))
		spacer = ''
		spacer = spacer.ljust(maxlength)
		print "#  %s  Ht  St  Df  Ac  Sp  PrC  AcC" % (spacer)
		for u in range(0,len(unitlist)):
			print "%1d. %s  %2d  %2d  %2d  %2d  %2d  %3d  %3d" % (u+1, unitlist[u].name.ljust(maxlength), unitlist[u].ht, unitlist[u].st, unitlist[u].df, unitlist[u].ac, unitlist[u].sp, unitlist[u].p_cost, unitlist[u].a_cost)
	
	def playGame(self):
		victory = False
		# Give players a chance!
		while victory == False:
			print "\n"
			# Announce player's turn
			print "===[ PLAYER ", self.playerturn, ", TURN ", self.turnnum, " ]==="
			
			# Add points
			self.bgs[self.playerturn-1].newTurn()
			# Reset unit flags
			
			# Show field
			self.showField()
			
			# Enter action loop
			action = ''
			while(1):
				print "%d points left this turn. " % self.bgs[self.playerturn-1].points,
				action = raw_input('Enter a command: ')
				if action == 'help':
					print "Commands:"
					print "\tfield/units: Show field/units"
					print "\tnew/buy: Show Buy Units menu"
					print "\tfight/attack: Show Combat menu"
					print "\tmove: Show Movement menu"
					print "\tend: End turn"
					continue
				elif action == 'field':
					self.showField()
					continue
				elif action == 'units':
					self.showUnitList()
				elif action in ('new','buy'):
					self.buyUnits()
				elif action in ('fight', 'attack'):
					self.fight()
				elif action == 'move':
					self.moveUnits()
				elif action == 'end':
					# End of turn
					#Check victory conditions
					# Check to avoid suicide
					if self.bgs[self.playerturn-1].isEmpty():
						response = get_user_input('If you end your turn now, you will lose the game. Are you sure? (y/n) ', str, valid_yn)
						if response == 'n':
							continue
					# Check for victory
					if self.turnnum > 1:
						if self.bgs[0].isEmpty() and (not self.bgs[1].isEmpty()):
							victory = 2
						elif self.bgs[1].isEmpty() and (not self.bgs[0].isEmpty()):
							victory = 1
					break
				else:
					print "Command not recognised!"
					continue
					
				# Print field for next cycle
				self.showField()
			
			# Advance play
			if self.playerturn == 1:
				self.playerturn = 2
			elif self.playerturn == 2:
				self.turnnum = self.turnnum + 1
				self.playerturn = 1
		
		# Game has been won!
		print "===[ VICTORY FOR PLAYER ",victory,"! ]==="
