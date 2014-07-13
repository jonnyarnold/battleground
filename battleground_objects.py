import os, math
from objects import *
from menus import *
from pygame.locals import *
gamefontpath = os.path.join('font','pf_tempesta_seven.ttf')

class Space(ActiveObject):
	### Class to hold a unit ###
	
	# Class constants
	FRONT = 0
	BACK = 1
	size = (64,64)
	empty = pygame.image.load(os.path.join('art','space.png'))
	
	def __init__(self, player, pos, type):
		ActiveObject.__init__(self, self.empty, pygame.Rect(pos, self.size))
		self.image = self.empty
		self.unit = None
		self.type = type
		self.player = player # Used to assign player
		self.menupos = self.rect.topright[0] - 2, self.rect.topright[1]
	
	def isDead(self):
		if self.unit.ht <= 0:
			self.unit = None
			return True
		else:
			return False
	
	def update(self):
		if self.unit == None:
			self.image = self.empty
		else:
			self.image = self.empty.copy()
			# Get health of unit and convert into a colour!
			healthfraction = float(self.unit.ht) / float(self.unit.maxht)
			healthcolour = (int(255-(255*healthfraction)), int(255*healthfraction), 0)
			healthsurf = pygame.Surface(self.size)
			healthsurf.set_alpha(255)
			healthsurf.fill(healthcolour)
			self.image.blit(healthsurf, (0,0), special_flags=BLEND_RGB_MULT)
			self.image.blit(self.unit.image, pygame.rect.Rect((0,0),self.size))
	
	def addUnit(self, unit):
		if self.unit == None:
			self.unit = unit
			self.game.hovers.kill() # Clear menu
		else:
			Exception("Oops.")
	
	def attrDiff(self, attr):
		baseunit = None
		for u in self.player.unitlist:
			if u.name == self.unit.name:
				baseunit = u
				break
		if not baseunit: Exception('Oh bollocks.')
		curunitstats = {"st": self.unit.st, "df": self.unit.df, "ac": self.unit.ac, "sp": self.unit.sp}
		baseunitstats = {"st": baseunit.st, "df": baseunit.df, "ac": baseunit.ac, "sp": baseunit.sp}
		statdiff = curunitstats[attr] - baseunitstats[attr]
		if statdiff == 0: return ''
		elif statdiff > 0: return '(+' + str(statdiff) + ')'
		elif statdiff < 0: return '(-' + str(statdiff) + ')'
	
	def killUnit(self): 
		self.unit = None
		self.game.hovers.kill() # Clear menu
	
	def mouseDown(self, button):
		if button == self.BUTTON_LEFT and self.player == self.game.curplayer and self.game.pickenemy == False:
			# Display menu to the right of the space
			if (self.game.hovers.sprites() != []):
				self.game.hovers.kill()
			# Check if space is empty
			hovermenu = None
			if self.unit == None:
				if self.type == self.BACK:
					hovermenu = Button(self.menupos, (75,20), 'Add Unit', lambda: self.game.openEnlist(self))
					self.game.addObject(hovermenu, self.game.HOVER)		
			else:
				if self.type == self.FRONT:
					if self.game.canMoveUnit(self): hovermenu1 = Button(self.menupos, (75,20), 'Move to Back', lambda: self.game.moveUnit(self)) 
					else: hovermenu1 = Button(self.menupos, (75,20), 'Cannot Move') 
					movingpos = self.menupos[0], self.menupos[1]+19
					if self.game.canFight(self): hovermenu2 = Button(movingpos, (75,20), 'Attack', lambda: self.game.chooseTarget(self))
					else: hovermenu2 = Button(movingpos, (75,20), "Can't Attack")
					self.game.addObject(hovermenu2, self.game.HOVER)
				else:
					if self.game.canMoveUnit(self): hovermenu1 = Button(self.menupos, (75,20), 'Move to Front', lambda: self.game.moveUnit(self)) 
					else: hovermenu1 = Button(self.menupos, (75,20), 'Cannot Move') 
				self.game.addObject(hovermenu1, self.game.HOVER)				
				
			self.hover()
		elif button == self.BUTTON_LEFT and self.game.pickenemy and self.player == self.game.enemy and self.unit != None:
			if self.type == self.FRONT or (self.game.noFront(self.game.enemy) and self.type == self.BACK):
				self.game.getCombatStats(self)	
	
	def hover(self):
		if self.unit == None:
			self.game.status.update('Empty')
		else:
			btncls = Button((0,0),(0,0), '').__class__
			h = self.game.hovers.sprites()
			if (h and h[0].__class__ != btncls) or (not h):
				self.game.hovers.kill()
				statstr = self.unit.name + ' (' + str(self.unit.ht) + '/' + str(self.unit.maxht) + ')\nStrength: ' + str(self.unit.st) + ' ' + self.attrDiff("st") + '\nDefence: ' + str(self.unit.df) + ' ' + self.attrDiff("df") + '\nAccuracy: ' + str(self.unit.ac) + ' ' + self.attrDiff("ac") + '\nSpeed: ' + str(self.unit.sp) + ' ' + self.attrDiff("sp") + '\n'
				if self.unit.moved and self.unit.attacked: statstr += 'Moved, Attacked'
				elif self.unit.moved and not self.unit.attacked: statstr += 'Moved'
				elif not self.unit.moved and self.unit.attacked: statstr += 'Attacked'
				statstr += '\nPts to Fight/Move: ' + str(self.unit.a_cost)
				hovermenu = TextBox(self.menupos, (150, 100), statstr, 8)
				self.game.addObject(hovermenu, self.game.HOVER)
			else:
				self.game.status.update(self.unit.name)
	

# Basic backgrounds
bgimg = pygame.image.load(os.path.join('art','bg.jpg'))
mainbg = BGObject(bgimg, pygame.Rect((0,0),(640,480)))
disabledimg = pygame.image.load(os.path.join('art','disabledbg.png'))
disabledbg = BGObject(disabledimg, pygame.Rect((0,250),(640,240)))

class EnlistButton(Button):
	
	def __init__(self, pos, size, unit, space):
		Button.__init__(self, pos, size,'Enlist')
		self.unit, self.space = unit, space
		self.cback = self.add
	
	def add(self):
		self.game.addUnit(self.space, self.unit)

class Unit:
	
	def __str__(self):
		return '<Unit: ' + self.name + '>'
	
	def __init__(self, name, stats, art = 'unknown'):
		self.name = name
		self.image = pygame.image.load(os.path.join('art',art + '.png'))
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
		self.p_cost = int(math.ceil(((0.4*self.maxht)**2 + self.st**2 + self.df**2 + self.ac**2 + self.sp**2)/8.0))
	
	def setACost(self):
		if self.p_cost == 0.0:
			self.setPCost()
		self.a_cost = int(math.ceil(self.p_cost / 10.0))

class Player:
	
	# Class Constants
	INITIAL_POINTS = 150
	INIT_POINTS_PER_TURN = 100
	PPT_INCREASE = 0
	
	def __init__(self, name, sidefile):
		self.name = name
		self.points = self.INITIAL_POINTS
		self.ppt = self.INIT_POINTS_PER_TURN
		# Import side
		self.unitlist = self.loadFile(os.path.join('sides', sidefile))
	
	def loadFile(self, filepath):
		### Reads a file and turns it into a unit list
		file = open(filepath)
		if file:
			unitlist = []
			for line in file:
				# Explode the line by tab
				line.rstrip("\n")
				attr = []
				lsplit = line.split("\t")
				if 8 > len(lsplit) >= 6:
					if len(lsplit) == 6: art = 'unknown'
					else: art = lsplit[6].rstrip('\n')
					name, attr = lsplit[0], map(int, lsplit[1:6])
					newunit = Unit(name, attr, art)
					unitlist.append(newunit)
			return unitlist
		else:
			return None

class HitBubble(ActiveObject):
	
	def __init__(self, initpos, text, txtcol=(255,0,0), speed = 1, killframes = 30):
		self.pos = list(initpos)
		self.text = text
		self.txtcol = txtcol
		self.opacity = 255
		self.image = self.makeSurface()
		ActiveObject.__init__(self, self.image, pygame.Rect(self.pos, self.image.get_rect().size))
		self.frames = 0
		self.killframes = killframes
		self.speed = speed
	
	def makeSurface(self):
		sysfont = pygame.font.Font(gamefontpath, 20)
		txtsurf = sysfont.render(self.text, True, self.txtcol)
		tsurf = pygame.Surface(txtsurf.get_rect().size)
		tsurf.set_colorkey((0,0,0))
		tsurf.blit(txtsurf,(0,0))
		tsurf.set_alpha(self.opacity)
		return tsurf

	def update(self):
		if self.killframes < self.frames:
			self.kill()
			del self
		else:
			self.pos[1] -= self.speed
			self.opacity = int(-(255/self.killframes)*self.frames + 255)
			self.image = self.makeSurface()
			self.frames += 1
			self.rect = pygame.Rect(self.pos, self.image.get_rect().size)
