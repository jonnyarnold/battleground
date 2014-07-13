# BUTTON AND MENU OVERLAYS

import pygame, os
from pygame.locals import *
from objects import *
from text_rect import *
gamefontpath = os.path.join('font','pf_tempesta_seven.ttf')

defcback = lambda: True

class Button(ActiveObject):
	
	# Class Constants
	bgnohover = (255,255,255)
	bghover = (255,255,0)
	
	def __init__(self, pos, size, text, cback = defcback, border = 2):
		self.size, self.text, self.cback, self.border = size, text, cback, border
		self.bg = self.bgnohover
		
		btn = self.makeSurface()
		ActiveObject.__init__(self, btn, pygame.rect.Rect(pos, self.size))
	
	def makeSurface(self):
		sysfont = pygame.font.Font(gamefontpath, int((self.size[1]-(2*self.border))/2))
		txtsurf = sysfont.render(self.text, True, (0,0,0))
		btn = pygame.surface.Surface(self.size)
		btn.fill(self.bg)
		btn.blit(txtsurf, ((self.size[0] - txtsurf.get_width())/2, (self.size[1] - txtsurf.get_height())/2))
		return btn
	
	def mouseDown(self, button):
		if button == self.BUTTON_LEFT:
			self.cback()
	
	def hover(self):
		self.bg = self.bghover
		self.image = self.makeSurface()
	
	def noHover(self):
		self.bg = self.bgnohover
		self.image = self.makeSurface()

class TextBox(ActiveObject):
	
	baseimg = pygame.image.load(os.path.join('art','hoverbg.png'))
	
	def makeSurface(self):
		sysfont = pygame.font.Font(gamefontpath, self.textsize)
		txt = pygame.surface.Surface(self.size, SRCALPHA)
		txt.blit(self.baseimg,(0,0))
		txtsurf = render_textrect(self.text, sysfont, pygame.rect.Rect(self.pos, self.size), self.tcolor, (255,0,255), self.horiz, self.vertjust)
		txtsurf.set_colorkey((255,0,255))
		txt.blit(txtsurf,(0,0))
		return txt
	
	def __init__(self, pos, size, text = '', textsize = 8, border = 3, vertjust = True, horiz = 1, tcolor = (0,0,0)):
		if textsize == None: textsize = (size[1] - (2*border))
		self.pos, self.size, self.text, self.textsize, self.border, self.vertjust, self.horiz,self.tcolor = pos, size, text, textsize, border, vertjust, horiz, tcolor
		txt = self.makeSurface()
		ActiveObject.__init__(self, txt, pygame.rect.Rect(pos, size))
	
	def update(self, text = None):
		if text != None:
			self.text = text
		self.image = self.makeSurface()
