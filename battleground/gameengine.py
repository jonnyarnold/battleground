import pygame, copy
from pygame.locals import *

from objects import *

# GAME ENGINE - For handing active objects, backgrounds, etc.
class GameEngine:
	
	# Class constants
	ACT = 1
	BG = 2
	HOVER = 3
	EMPTYOBJ = pygame.sprite.Sprite()
	
	# Methods
	def __init__(self, windim, fps = 20):
		# Main drawing groups
		self.bobj = Group() # Background
		self.aobj = Group() # Active objects
		# Subgroups
		self.hovers = Group() # Hovering objects
		
		self.width, self.height = windim
		self.fps = fps
		self.run = 1
		self.active = 1
		self.hover = None # Used for tracking hovers
		
		# Pygame initialisation
		pygame.init()
		display_flags = DOUBLEBUF
		if pygame.display.mode_ok((self.width, self.height), display_flags ):
			self.screen = pygame.display.set_mode((self.width, self.height), display_flags)
		if pygame.image.get_extended == False:
			exit(-1, "Sorry, your version of pygame does not support extended image formats.")
	
	def addObject(self, obj, obj_type):
		if obj_type in [self.ACT, self.HOVER]:
			obj.add(self.aobj)
			if obj_type == self.HOVER: obj.add(self.hovers)
			obj.game = self # Used for callbacks
		elif obj_type == self.BG:
			obj.add(self.bobj)
	
	def addGroup(self, grp, obj_type):
		for obj in grp.sprites():
			self.addObject(obj, obj_type)
	
	def update(self):
		for obj_grp in [self.bobj, self.aobj]:
				obj_grp.update()
	
	def cleanup(self):
		for obj_grp in [self.bobj, self.aobj]:
			for obj in obj_grp:
				if obj.alive() == False:
					obj = None
	
	def draw(self):
		self.screen.fill((0,0,0))
		for obj_grp in [self.bobj, self.aobj]:
			obj_grp.draw(self.screen)
	
	def quit(self):
		self.run = 0
		
	def noHover(self):
		pass
	
	def handleEvents(self):
		if self.hover == None: self.hover = False
		# Respond to events
		events = pygame.event.get()
		for event in events:    
				if event.type == QUIT or (event.type == KEYDOWN and event.key == K_q):
					# Quit
					self.run = 0
				elif event.type == KEYDOWN:
					self.keydown(event.key)
				elif event.type == MOUSEBUTTONDOWN:
					for obj in self.aobj:
						if obj.pointInRect(event.pos) and obj.active:
							obj.mouseDown(event.button)
				elif event.type == MOUSEMOTION:
					self.hover = False
					for obj in self.aobj:
						if obj.active:
							if obj.pointInRect(event.pos) and self.hover != True:
								obj.hover()
								self.hover = True
							else:
								obj.noHover()
		# Have there been any hovers?
		if self.hover == False:
			self.noHover()
	
	def removeInactive(self):
		aobjcopy = copy.copy(self.aobj)
		for obj in aobjcopy:
			if not obj.active:
				self.aobj.remove(obj)
	
	def loop(self):
		### Game loop ###
		clock = pygame.time.Clock()
		while self.run:
			# Handle events
			self.handleEvents()
			# Update all objects, cleanup dead objects, draw screen and flip
			self.update()
			self.cleanup()
			self.draw(self.screen)
			pygame.display.flip()
			clock.tick(self.fps)
	
	def pause(self, ticks):
		clock = pygame.time.Clock()
		t = 0
		while t < ticks:
			# Update all objects, cleanup dead objects, draw screen and flip
			self.update()
			self.cleanup()
			self.draw(self.screen)
			pygame.display.flip()
			clock.tick(self.fps)
			t += 1
	
	def keydown(self, key):
		pass

class LayeredGameEngine(GameEngine):
	
	# Class constants
	TOP = 1
	BOTTOM = 2
	
	def __init__(self, windim, fps = 20):
		GameEngine.__init__(self, windim, fps)
		self.lyrs = []
		self.originalaobj = None # Used to keep track of active objects during layer deactivation

	def addLayer(self, layer, pos = None):
		if(pos == None):
			pos = self.TOP
		if(pos == self.TOP):
			self.lyrs.append(layer)
		else:
			self.lyrs.insert(0, layer)
		# Add BG and active objects to respective lists
		self.bobj.add(layer.bgs.sprites())
		self.aobj.add(layer.acts.sprites())
		# Link Active objects to game
		for s in layer.acts.sprites():
			s.game = self
	
	def removeLayer(self, layer):
		found = False
		l = 0
		while l < len(self.lyrs):
			if found == True: l = len(self.lyrs)
			elif self.lyrs[l] == layer:
				found = True
				del self.lyrs[l]
			else:
				l += 1
				
	
	def loop(self):
		### Game loop ###
		clock = pygame.time.Clock()
		while self.run:
			# Top layer is the only active layer!
			self.aobj.empty()
			self.aobj.add(self.lyrs[len(self.lyrs)-1].acts.sprites())
			# Handle events
			self.handleEvents()
			# Update all objects, cleanup dead objects, draw screen and flip
			self.update()
			self.cleanup()
			self.draw(self.screen)
			pygame.display.flip()
			clock.tick(self.fps)
	
	def cleanup(self):
		for l in self.lyrs:
			for obj_grp in [l.bgs, l.acts]:
				for obj in obj_grp:
					if obj.alive() == False:
						obj = None
	
	def addObject(self, obj, obj_type):
		layer = self.lyrs[len(self.lyrs) - 1]
		if obj_type == self.ACT or self.HOVER:
			layer.addActive(obj)
			if obj_type == self.HOVER: self.hovers.add(obj)
			obj.game = self
		elif obj_type == self.BG:
			layer.addBG(obj)
	
	def draw(self, surf):
		for l in self.lyrs:
			l.draw(surf)
