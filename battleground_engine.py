# Battlefield game engine

import pygame, random, math
from gameengine import *
from battleground_objects import *
from menus import *

# Preferences
FRONT_ROW_WIDTH, BACK_ROW_WIDTH = 3, 4
WIDTH, HEIGHT = 640,480
WINDOWTITLE = 'Battleground'
gamefontpath = os.path.join('font','pf_tempesta_seven.ttf')

p1side = {"NAME": 'The Experiment', "FILE": 'experiment.txt'}
p2side = {"NAME": 'The Experiment', "FILE": 'experiment.txt'}

### TWEAKABLE GAME CONSTANTS ####
STR_KEYNUM = 9 					# Base strength
HIT_KEYNUM = 9					# Base 'hit points'
PERCENT_PER_POINT = 10			# Chance of hitting inc./dec. per hit point
KILL_POINTS_FRACTION = 0.33		# Fraction of defender's points given to other team if killed
#################################

def GetHitStrength(st, df):
	base = st - df + STR_KEYNUM
	if base < 1:
		return 1
	else:
		return base
	
def GetHitChance(ac, sp):
	base = (ac - sp + HIT_KEYNUM) * PERCENT_PER_POINT # %
	if base < 20:
		return 20
	elif base > 100:
		return 100
	else:
		return base

class Battleground(LayeredGameEngine):
	
	# Class constants
	P1 = 0
	P2 = 1
	
	def __init__(self, windim, p1 = p1side, p2 = p2side, fps = 20):
		LayeredGameEngine.__init__(self, windim, fps)
		pygame.display.set_caption(WINDOWTITLE)
		
		# Build players
		self.p1, self.p2 = Player(p1['NAME'], p1['FILE']), Player(p2['NAME'], p2['FILE'])
		self.curplayer, self.enemy = self.p1,self.p2
		self.turn = 1
		
		self.pickenemy = False
		
		# Build the battlefield
		self.battlefield = Layer()
		self.battlefield.addBG(mainbg)
		self.battlefield.addBG(disabledbg)
		SPACE_SIZE = Space.size[0]
		FRONT_HEIGHT = 128
		BACK_HEIGHT = 32
		SPACING = 0.05 * WIDTH # 5%
		self.p1spaces, self.p2spaces = Group(), Group()
		for s in range(0, FRONT_ROW_WIDTH):
			position = (WIDTH/2) + (s - (FRONT_ROW_WIDTH-1)/2)*SPACING + (s - FRONT_ROW_WIDTH/2)*SPACE_SIZE
			self.p1spaces.add(Space(self.p1, (position, FRONT_HEIGHT), Space.FRONT))
			self.p2spaces.add(Space(self.p2, (position, HEIGHT - FRONT_HEIGHT - SPACE_SIZE), Space.FRONT))
		for s in range(0, BACK_ROW_WIDTH):
			position = (WIDTH/2) + (s - (BACK_ROW_WIDTH-1)/2)*SPACING + (s - BACK_ROW_WIDTH/2)*SPACE_SIZE
			self.p1spaces.add(Space(self.p1, (position, BACK_HEIGHT), Space.BACK))
			self.p2spaces.add(Space(self.p2, (position, HEIGHT - BACK_HEIGHT - SPACE_SIZE), Space.BACK))
		self.battlefield.addGroup(self.p1spaces, Layer.ACT)
		self.battlefield.addGroup(self.p2spaces, Layer.ACT)
		self.p1.spaces = self.p1spaces
		self.p2.spaces = self.p2spaces
		
		# Build menus and overlay
		self.status = TextBox((0,460), (540,20), '', 8) 
		self.battlefield.addActive(self.status)
		self.battlefield.addActive(Button((540,460), (100, 20), 'End Turn', self.endTurn, 2))
		
		self.addLayer(self.battlefield)
	
	def openEnlist(self, space):
		# Open Enlist dialog
		self.enlist = Layer()
		baseimg = pygame.image.load(os.path.join('art','disabledbg.png'))
		overlay = BGObject(baseimg, pygame.Rect((0,0),(640,480)))
		self.enlist.addBG(overlay)
		self.enlist.addActive(Button((50,125),(75,20),'Exit',self.closeEnlist))
		# Get all unit list information, and tabulate it
		headings = 'Name\nHits\nStrength\nDefence\nAccuracy\nSpeed\nEnlist Cost\nAction Cost'
		self.enlist.addActive(TextBox((25,215), (80,120),headings,8,3,True))
		xpos = 105
		colwidth = 85
		unitbgimg = pygame.image.load(os.path.join('art','hoverbg.png'))
		unitbg = BGObject(unitbgimg, pygame.Rect((25,145),(590,70)))
		self.enlist.addBG(unitbg)
		for unit in self.curplayer.unitlist:
			self.enlist.addBG(BGObject(unit.image, pygame.Rect((xpos+(colwidth-Space.size[0])/2,148),Space.size)))
			unittext = unit.name + '\n' + str(unit.maxht) + '\n' + str(unit.st) + '\n' + str(unit.df) + '\n' + str(unit.ac) + '\n' + str(unit.sp) + '\n' + str(unit.p_cost) + '\n' + str(unit.a_cost)
			self.enlist.addActive(TextBox((xpos,215), (colwidth,120),unittext,8))
			btn = EnlistButton((xpos,335),(colwidth,20),unit, space)
			if self.curplayer.points - unit.p_cost >= 0: self.enlist.addActive(btn)
			else: self.enlist.addActive(TextBox((xpos,335),(colwidth,20),'xxxxxx', 8))
			xpos += colwidth
		self.addLayer(self.enlist)
	
	def addUnit(self, space, unit):
		self.curplayer.points -= unit.p_cost
		space.addUnit(unit)
		self.closeEnlist()		
	
	def closeEnlist(self):
		self.removeLayer(self.enlist)
		del self.enlist
	
	def moveUnit(self, space):
		self.curplayer.points -= space.unit.a_cost
		for destspace in self.curplayer.spaces:
			if destspace.unit == None and destspace.type != space.type:
				destspace.addUnit(copy.copy(space.unit))
				space.killUnit()
				destspace.unit.moved = True
				break	
		Exception('Shit.')
	
	def canMoveUnit(self, space):
		if (self.curplayer.points - space.unit.a_cost < 0): return False
		elif space.unit.moved == True: return False
		else:
			for destspace in self.curplayer.spaces:
				if destspace.unit == None and destspace.type != space.type:
					return True
			return False # If this code is run, no space to move exists
	
	def noFront(self, player):
		for s in player.spaces:
			if s.type == s.FRONT and s.unit != None:
				return False
		return True # Runs if no front spaces exist
	
	def canFight(self, space):
		if space.unit.attacked == True or (space.player.points - space.unit.a_cost < 0): return False
		else: 
			enemies = False
			for s in self.enemy.spaces:
				if s.unit != None:
					return True
			return False # If here, no enemies on opposition
	
	def chooseTarget(self, attacker):
		self.pickenemy = True
		self.aspace = attacker
		self.attacker = attacker.unit
		
		self.choosetargetobjs = Group()
		
		self.toggleBG(self.curplayer)
		
		selecttarget = TextBox((0,230), (540,20), 'Select a target', 8) 
		self.choosetargetobjs.add(selecttarget)
		self.choosetargetobjs.add(Button((540,230), (100, 20), 'Cancel', self.stopChooseTarget, 2))
		
		self.battlefield.addGroup(self.choosetargetobjs, self.battlefield.ACT)
	
	def getCombatStats(self, defender):
			
		self.dspace = defender
		self.defender = defender.unit
		if self.dspace.type == self.dspace.BACK:
			# Back attack penalty
			self.attacker.hs, self.defender.hs = GetHitStrength(self.attacker.st, int(math.floor(self.defender.df*0.66))), GetHitStrength(int(math.floor(self.defender.st*0.66)), self.attacker.df)
			self.attacker.hc, self.defender.hc = GetHitChance(self.attacker.ac, int(math.floor(self.defender.sp*0.66))), GetHitChance(int(math.floor(self.defender.ac*0.66)), self.attacker.sp)
		else:	
			self.attacker.hs, self.defender.hs = GetHitStrength(self.attacker.st, self.defender.df), GetHitStrength(self.defender.st, self.attacker.df)
			self.attacker.hc, self.defender.hc = GetHitChance(self.attacker.ac, self.defender.sp), GetHitChance(self.defender.ac, self.attacker.sp)
		
		# Overlay combat stats
		self.combat = Layer()
		baseimg = pygame.image.load(os.path.join('art','disabledbg.png'))
		overlay = BGObject(baseimg, pygame.Rect((0,0),(640,480)))
		self.combat.addBG(overlay)
		self.combat.addActive(Button((275,335),(75,20),'Attack',self.attack))
		self.combat.addActive(Button((350,335),(75,20),'Cancel',self.closeCombatStats))
		# Get all unit list information, and tabulate it
		headings = 'Name\nHits\nStrength\nDefence\nAccuracy\nSpeed\n\nDamage\nHit Chance'
		self.combat.addActive(TextBox((195,205), (80,130),headings,8,3,True))
		xpos = 275
		colwidth = 85
		unitbgimg = pygame.image.load(os.path.join('art','hoverbg.png'))
		unitbg = BGObject(unitbgimg, pygame.Rect((195,135),(250,70)))
		self.combat.addBG(unitbg)
		for unit in self.attacker, self.defender:
			if unit == self.defender and self.dspace.type == self.dspace.BACK: 
				tcolor = (128,0,0)
				self.combat.addBG(BGObject(unit.image, pygame.Rect((xpos+(colwidth-Space.size[0])/2,143),Space.size)))
				unittext = unit.name + '\n' + str(unit.ht) + '/' + str(unit.maxht) + '\n' + str(int(math.floor(unit.st*0.66))) + '\n' + str(int(math.floor(unit.df*0.66))) + '\n' + str(int(math.floor(unit.ac*0.66))) + '\n' + str(int(math.floor(unit.sp*0.66))) + '\n\n' + str(unit.hs) + '\n' + str(unit.hc)
			else: 
				tcolor = (0,0,0)
				self.combat.addBG(BGObject(unit.image, pygame.Rect((xpos+(colwidth-Space.size[0])/2,143),Space.size)))
				unittext = unit.name + '\n' + str(unit.ht) + '/' + str(unit.maxht) + '\n' + str(unit.st) + '\n' + str(unit.df) + '\n' + str(unit.ac) + '\n' + str(unit.sp) + '\n\n' + str(unit.hs) + '\n' + str(unit.hc)
			self.combat.addActive(TextBox((xpos,205), (colwidth,130),unittext,8, tcolor=tcolor))
			xpos += colwidth
		self.addLayer(self.combat)
	
	def attack(self):
		
		# Clear menus
		self.closeCombatStats()
		
		# Do the attack!
		self.curplayer.points -= self.attacker.a_cost
		self.attacker.attacked = True
		dice = random.randint(1,100)
		if dice < self.attacker.hc: # Attacker Hit!
			self.defender.ht -= self.attacker.hs
			hb = HitBubble(self.dspace.rect.midtop, '-' + str(self.attacker.hs))
			self.addObject(hb, self.ACT)
			self.attacker.ac += 1
			self.addObject(HitBubble(self.aspace.rect.midright, 'Ac+1', (0,255,255)), self.ACT)
		else: # Attacker Miss
			self.addObject(HitBubble(self.dspace.rect.midtop, 'Miss!', (255,255,255)), self.ACT)
			self.defender.sp += 1
			self.addObject(HitBubble(self.dspace.rect.midright, 'Sp+1', (0,255,255)), self.ACT)
		# Check for death
		if self.dspace.isDead():
			reward = int(math.ceil(self.defender.p_cost * KILL_POINTS_FRACTION)) # Point reward for killing
			self.aspace.player.points += reward
			self.addObject(HitBubble(self.aspace.rect.midtop, '+' + str(reward) + 'pts', (0,255,255)), self.ACT)
			self.stopChooseTarget()
		else:
			self.addObject(DelayedEvent(10,self.counter), self.ACT)
	
	def counter(self):
		# Counterattack
		dice = random.randint(1,100)
		if dice < self.defender.hc: # Defender Hit!
			self.attacker.ht -= self.defender.hs
			self.addObject(HitBubble(self.aspace.rect.midtop, '-' + str(self.defender.hs)), self.ACT)
			self.defender.st += 1
			self.addObject(HitBubble(self.dspace.rect.midright, 'St+1', (0,255,255)), self.ACT)
		else: # Defender Miss
			self.addObject(HitBubble(self.aspace.rect.midtop, 'Miss!', (255,255,255)), self.ACT)
			self.attacker.df += 1
			self.addObject(HitBubble(self.aspace.rect.midright, 'Df+1', (0,255,255)), self.ACT)
		# Check for death
		if self.aspace.isDead():
			reward = int(math.ceil(self.attacker.p_cost * KILL_POINTS_FRACTION)) # Point reward for killing
			self.dspace.player.points += reward
			self.addObject(HitBubble(self.dspace.rect.midtop, '+' + str(reward) + 'pts', (0,255,255)), self.ACT)
		self.stopChooseTarget()
	
	def closeCombatStats(self):
		self.removeLayer(self.combat)
		del self.combat
	
	def stopChooseTarget(self):
		self.attacker, self.defender, self.aspace, self.dspace = None, None, None, None
		self.pickenemy = False
		self.choosetargetobjs.kill()
		self.toggleBG(self.enemy)
	
	def endTurn(self):
		self.curplayer, self.enemy = self.enemy, self.curplayer
		if self.curplayer == self.p1: self.turn += 1
		self.toggleBG(self.enemy)
		
		# Check for victory
		victory = True
		for s in self.curplayer.spaces:
			if s.unit != None:
				victory = False
				break
		if victory and self.turn > 1:
			# VICTORY
			self.victory = Layer()
			baseimg = pygame.image.load(os.path.join('art','disabledbg.png'))
			overlay = BGObject(baseimg, pygame.Rect((0,0),(640,480)))
			self.victory.addBG(overlay)
			self.victory.addBG(TextBox((0,200),(640,80),'Victory for ' + self.enemy.name + '!', 16))
			self.victory.addActive(Button((555,280),(75,20),'Exit',self.quit))
			self.addLayer(self.victory)
		else:
			if self.turn > 1: 
				self.curplayer.points += self.curplayer.ppt
				self.curplayer.ppt += self.curplayer.PPT_INCREASE
			# Unset flags from all units
			for p in self.p1,self.p2:
				for s in p.spaces:
					if s.unit != None: 
						s.unit.moved = False
						s.unit.attacked = False
			# Heal back row
			for s in self.curplayer.spaces:
				if s.unit != None and s.type == s.BACK:
					heal = int(math.floor(0.15*s.unit.maxht))
					if s.unit.ht + heal > s.unit.maxht: heal = s.unit.maxht - s.unit.ht
					if heal > 0:
						s.unit.ht += heal
						self.addObject(HitBubble(s.rect.midtop, '+' + str(heal), (0,200,0)), self.ACT)
			
			self.noHover() # Updates status bar
	
	def toggleBG(self, disabledplayer):
		if disabledplayer == self.p1:
			disabledbg.rect = pygame.Rect((0,0),(640,230))
		else:
			disabledbg.rect = pygame.Rect((0,250),(640,210))
		disabledbg.updateImage()
	
	def noHover(self):
		# No active hovers, remove status text and any active popups
		if self.hovers.sprites() != []: 
			self.hovers.kill()
						
		self.status.update(str(self.curplayer.name) + ': ' + str(self.curplayer.points) + ' points [Turn ' + str(self.turn) + ']')
	
	def keydown(self, key):
		pass
