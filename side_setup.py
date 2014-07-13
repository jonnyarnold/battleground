import pygtk, gtk, gtk.glade
import gobject

class SideSetupWindow:
	
	def __init__(self):
		#Set the Glade file
		self.gladefile = "sidesetup.glade"
		self.wTree = gtk.glade.XML(self.gladefile) 
		self.updateSideList()
		#Get the Main Window, and connect the "destroy" event
		self.window = self.wTree.get_widget("w_mainwin")
		if (self.window):
			self.window.connect("destroy", gtk.main_quit)
		else: raise Exception('Could not initialise window')
		self.wTree.signal_autoconnect(self)
		self.p1side, self.p2side = None, None
	
	def widget(self, name):
		"""Search for widget"""
		w = self.wTree.get_widget(name)
		if w != None: return w
		else: raise AttributeError('Widget `' + name + '` not found')
	
	def updateSideList(self, sidelist = []):
		# Build side list
		self.sidelist = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING) # Displayed name, file name
		self.sidelist.append(['Select a side...', ''])
		for s in sidelist:
			self.sidelist.append([s.replace('.txt', ''), s])
		#self.sidelist.append(['Custom Side', 'custom'])
		
		# Set side lists to combo boxes
		for combobox in self.widget('c_p1side'), self.widget('c_p2side'):
			combobox.set_model(self.sidelist)
			combobox.set_active(0)
			combobox.clear()
			cell = gtk.CellRendererText()
			combobox.pack_start(cell, True)
			combobox.add_attribute(cell, 'text', 0)

	def sides_changed(self, widget):
		p1, p2 = self.widget('c_p1side'), self.widget('c_p2side')
		if p1.get_active() >= 1 and p2.get_active() >= 1:
			self.widget('b_fight').set_sensitive(True)
		else:
			self.widget('b_fight').set_sensitive(False)

	def fight_clicked(self, widget):
		self.p1side = {'NAME': self.widget('t_p1name').get_text(), 'FILE': self.sidelist[self.widget('c_p1side').get_active()][0] + '.txt'}
		self.p2side = {'NAME': self.widget('t_p2name').get_text(), 'FILE': self.sidelist[self.widget('c_p2side').get_active()][0] + '.txt'}
		self.window.destroy()

	def get_sides(self):
		return self.p1side, self.p2side
