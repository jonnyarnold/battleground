import pygame
from pygame.locals import *

# GameObject - base class for abstracting sprite handling
class GameObject(pygame.sprite.Sprite):
	
	# Class constants
	BUTTON_LEFT = 1
	BUTTON_RIGHT = 3
	
	def __init__(self, img, rect):
		pygame.sprite.Sprite.__init__(self)
		self.imgsurf = img
		self.rect = rect
		self.updateImage()
		self.game = None # Reassigned by game
		self.visible = True
	
	def updateImage(self):
		self.image = pygame.Surface((self.rect.width, self.rect.height), SRCALPHA) # Lossy!
		self.image.blit(self.imgsurf, (0,0))
	
	def kill(self):
		pygame.sprite.Sprite.kill(self)
		return None
	
	def draw(self):
		if self.visible: pygame.sprite.Sprite.draw(self)
	
	def pointInRect(self, point):
		if (self.rect.left < point[0] < self.rect.right) and (self.rect.top < point[1] < self.rect.bottom):
			return True
		else:
			return False
	

# ActiveObject - class that requires user interaction
class ActiveObject(GameObject):
	
	def __init__(self, img, rect):
		self.active = True
		GameObject.__init__(self, img, rect)
	
	def mouseDown(self, button):
		pass
	
	def hover(self):
		pass
	
	def noHover(self):
		pass

# BGObject - class that does not interact with user
class BGObject(GameObject):
	def __init__(self, img, rect):
		GameObject.__init__(self, img, rect)

# Group - extension of basic group class
class Group(pygame.sprite.OrderedUpdates):
	
	def activate(self):
		for obj in self:
			obj.active = True
	
	def deactivate(self):
		for obj in self:
			obj.active = False
	
	def kill(self):
		for obj in self:
			obj.kill()
	
	def __init__(self):
		pygame.sprite.OrderedUpdates.__init__(self)

# Layer - BG/active object pair
class Layer(Group):
	
	BG = 1
	ACT = 2
	
	def __init__(self):
		self.bgs = Group()
		self.acts = Group()
		self.active = True
		self.visible = True
		Group.__init__(self)
	
	def __repr__(self):
		numspr = len(self.bgs) + len(self.acts)
		return "<Layer(" + str(numspr) + " sprites)>"
	
	def draw(self, surf):
		# draw BG, then active
		if self.visible:
			self.bgs.draw(surf)
			self.acts.draw(surf)
	
	def addBG(self, bgobj):
		self.bgs.add(bgobj)
	
	def addActive(self, aobj):
		self.acts.add(aobj)
	
	def addGroup(self, grp, obj_type):
		for sprt in grp.sprites():
			if obj_type == self.BG:
				self.addBG(sprt)
			else:
				self.addActive(sprt)

class DelayedEvent(ActiveObject):
	
	def __init__(self, delay, cback):
		self.delay = delay
		self.cback = cback
		self.counter = 0
		ActiveObject.__init__(self, pygame.Surface((1,1)), pygame.Rect((0,0),(1,1)))
	
	def update(self):
		if self.counter >= self.delay:
			self.cback()
			self.kill()
			del self
		else:
			self.counter += 1
