#!usr\bin\env python

# -- DETAILS
'''GUI code for the Load Order Sorting Tool package.'''

__author__ = 'Argomirr (argomirr@gmail.com)'
__copyright__ = 'Copyright (c) 2010 Argomirr'


# -- IMPORTS
import meat
import boss

import os
import sys
import re
import webbrowser

import iniparse
import wx, wx.html


# -- CONSTANTS
constants = {'WINDOW_HEIGHT':600,
			'WINDOW_WIDTH':800,
			'WINDOW_TITLE':'The Load Order Sorting Tool (Experimental Skyrim branch)',
			'DOCS_LOC':'http://argomirr.webs.com/py/loadorder/docs/docs.html',
			'ABOUT':'LOST revision 1.1.0 (Skyrim branch)\n(c) 2010 Argomirr\n\n\nDesigned for Python 2.7 & wxPython 2.8.12.0',
			'INI_PATH':os.getcwd() + '\settings.ini',
			'ICO_PATH':os.getcwd() + '\lost.ico',
			'LOST_DIR':os.getcwd(),
			'BOSS_START_PAGE':'''<html><body><center><h3>Better Oblivion Sorting Software</h3>BOSS is &copy; Random007 &amp; the BOSS development team, 2009-2010. Some rights reserved.</center><br><br>
								<p><i>Better Oblivion Sorting Software (BOSS) will reorder your mods to their correct positions (as listed in the masterlist.txt database file), putting any mods it doesn't
								 recognise after them, in the same order as they were before BOSS was run.
								BOSS is designed to assist in the installation and usage of mods, especially more complex mods such as FCOM and MMM, and help mod users avoid serious conflicts. It is not a complete solution to load ordering issues, 
								as there are far more mods out there (estimated at about 30,000) than BOSS knows about. To properly place mods BOSS doesn't know about, a good working knowledge of Oblivion mod load ordering is still necessary, 
								for which some research and documentation reading will go a long way.</i></p>
								<br><br><p><b>Quick links</b><ul><li><a href='http://www.tesnexus.com/downloads/file.php?id=20516'>BOSS on TESNexus</a>
								<li><a href='http://code.google.com/p/better-oblivion-sorting-software/'>BOSS Google Code pages</a>
								</ul><br><br><p>For both legal and practical reasons, BOSS is not included in the LOST package. If you want to make use of the integrated BOSS interface, download
								the BOSS installer from TESNexus. (See quick links)</p></body></html>'''}
			
settings = {}			
modeOB = 'OB'
modeNV = 'NV'
modeFO = 'FO3'
modeSK = 'SK'


# -- GUI
class UndefPanel(wx.Panel):
	'''Panel class for panel displayed when settings have not been configured.'''
	def __init__(self, parent, id=wx.ID_ANY):
		wx.Panel.__init__(self, parent, id)
		szr = wx.BoxSizer(wx.VERTICAL)
		szr.Add(wx.StaticText(self, wx.ID_ANY, 'It appears you have not configured your settings for this game.', style=wx.ALIGN_CENTER), flag=wx.EXPAND|wx.ALIGN_CENTER)
		self.SetSizer(szr)
		
		
class BaseFrame(wx.Frame):
	'''Base frame from which other frames in LOST derive.'''
	def show_error(self, error=''):
		'''Display an error message.'''
		msg = 'An error was encountered:\n' + error
		errorBox = wx.MessageDialog(self, caption='Error', message=msg, style=wx.ICON_ERROR|wx.STAY_ON_TOP|wx.OK)
		
		if errorBox.ShowModal() == wx.ID_OK:
			errorBox.Destroy()
			
	def show_message(self, msg=''):
		'''Display a message.'''
		box = wx.MessageDialog(self, caption='Load Order Sorting Tool', message=msg, style=wx.ICON_INFORMATION|wx.STAY_ON_TOP|wx.OK)
		
		if box.ShowModal() == wx.ID_OK:
			box.Destroy()
		
class LoadOrderPanel(wx.Panel):
	'''Panel class for load order editing GUI.'''
	def __init__(self, parent, mode, id=wx.ID_ANY):
		wx.Panel.__init__(self, parent, id)
		self.mode = mode
		
		self.actLi = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
		self.inactLi = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
		self.actLi.Bind(wx.EVT_LIST_ITEM_SELECTED, self.actlist_select)
		self.inactLi.Bind(wx.EVT_LIST_ITEM_SELECTED, self.inactlist_select)
		
		self.actLi.InsertColumn(0, 'Mod')
		self.actLi.InsertColumn(1, 'Type')
		self.actLi.InsertColumn(2, 'Hex value')
		self.actLi.SetColumnWidth(0, 220)
		self.actLi.SetColumnWidth(1, 100)
		self.actLi.SetColumnWidth(2, 100)
		
		self.inactLi.InsertColumn(0, 'Mod')
		self.inactLi.InsertColumn(1, 'Type')
		self.inactLi.SetColumnWidth(0, 180)
		self.inactLi.SetColumnWidth(1, 100)
		
		self.descrBox = wx.TextCtrl(self, style=wx.TE_READONLY|wx.TE_MULTILINE)
		self.authBox = wx.TextCtrl(self, style=wx.TE_READONLY)
		
		# First vsizer
		vszr1 = wx.BoxSizer(wx.VERTICAL)
		vszr1.Add(wx.StaticText(self, wx.ID_ANY, 'Active mods'), border=3, flag=wx.ALL|wx.EXPAND)
		vszr1.Add(self.actLi, proportion=1, border=3, flag=wx.ALL|wx.EXPAND)
		
		# Second vsizer
		vszr2 = wx.BoxSizer(wx.VERTICAL)
		vszr2.Add(wx.StaticText(self, wx.ID_ANY, 'Inactive mods'), border=3, flag=wx.ALL|wx.EXPAND)
		vszr2.Add(self.inactLi, proportion=7, border=3, flag=wx.ALL|wx.EXPAND)
		vszr2.Add(self.authBox, proportion=0, border=3, flag=wx.ALL|wx.EXPAND)
		vszr2.Add(self.descrBox, proportion=3, border=3, flag=wx.ALL|wx.EXPAND)
		
		# Buttons
		top_btn = wx.Button(self, wx.ID_ANY, label='Top')
		top_btn.Bind(wx.EVT_BUTTON, self.move_top)
		up_btn = wx.Button(self, wx.ID_ANY, label='Move up')
		up_btn.Bind(wx.EVT_BUTTON, self.move_up)
		dwn_btn = wx.Button(self, wx.ID_ANY, label='Move down')
		dwn_btn.Bind(wx.EVT_BUTTON, self.move_down)
		btm_btn = wx.Button(self, wx.ID_ANY, label='Bottom')
		btm_btn.Bind(wx.EVT_BUTTON, self.move_bottom)
		
		act_btn = wx.Button(self, wx.ID_ANY, label='Activate')
		act_btn.Bind(wx.EVT_BUTTON, self.activate)
		dact_btn = wx.Button(self, wx.ID_ANY, label='Deactivate')
		dact_btn.Bind(wx.EVT_BUTTON, self.deactivate)
		
		self._mcount = wx.StaticText(self, wx.ID_ANY, 'Active mod limit: 0/256', style=wx.ALIGN_RIGHT)
		self._mcount.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
		
		
		# hsizer (bottom row)
		hszr1 = wx.BoxSizer()
		hszr1.Add(top_btn, border=3, flag=wx.ALL)
		hszr1.Add(up_btn, border=3, flag=wx.ALL)
		hszr1.Add(dwn_btn, border=3, flag=wx.ALL)
		hszr1.Add(btm_btn, border=3, flag=wx.ALL)
		hszr1.Add(act_btn, border=3, flag=wx.ALL)
		hszr1.Add(dact_btn, border=3, flag=wx.ALL)

		
		# Main sizer
		sizer = wx.GridBagSizer(vgap=5, hgap=5)
		sizer.Add(self._mcount, pos=(1,1), border=3, flag=wx.EXPAND|wx.ALL)
		sizer.Add(vszr1, pos=(0,0), flag=wx.EXPAND)
		sizer.Add(vszr2, pos=(0,1), flag=wx.EXPAND)
		sizer.Add(hszr1, pos=(1,0), flag=wx.EXPAND)
		
		
		sizer.AddGrowableCol(0, proportion=62)
		sizer.AddGrowableCol(1, proportion=38)
		sizer.AddGrowableRow(0)
		
		# Keypress events
		for i in self.GetChildren():
			i.Bind(wx.EVT_KEY_DOWN, self.handle_hotkey)
		self.Bind(wx.EVT_KEY_DOWN, self.handle_hotkey)
		
		# Stuff
		self.sizer = sizer # So the show_descr_box method can update the sizer
		self.SetSizer(sizer)
		self.refresh_loadorder()
		
	def loadorder_to_clipboard(self):
		'''Copy loadorder to clipboard.'''
		if	wx.TheClipboard.Open():
			data = []
			for x in range(self.actLi.GetItemCount()):
				data.append(self.actLi.GetItemText(x) + '\n')
			data = ''.join(data)
			print data
		
			wx.TheClipboard.Clear()
			wx.TheClipboard.SetData(wx.TextDataObject(data))
			wx.TheClipboard.Close()
		
	def import_loadorder(self, event=None):
		'''Export load order to a .txt file.'''
		loadBox = wx.FileDialog(self, message='Open', defaultDir=os.environ['USERPROFILE'], defaultFile='', style=wx.FD_OPEN, wildcard='Plain text files (*.txt)|*.txt')
		text = ''
		if loadBox.ShowModal() == wx.ID_OK:
			path = loadBox.GetPath()
			try:
				txtf = open(path, 'rb')
				try:
					text = txtf.read()
				finally:
					txtf.close()
			except IOError:
				self.showErrorBox('Could not read file.')
			loadBox.Destroy()
			
		
		plugins = re.findall('.+\.{1}esm|.+\.{1}esp', text)
		self.actLi.DeleteAllItems()
		self.inactLi.DeleteAllItems()

		if plugins != []:
			try:
				if self.mode == modeFO:
					if settings['sFO_TXT'] == '' or settings['sFO_PATH'] == '':
						self.show_error('Could not refresh load order. Check if your settings are correct.')
						return None
					loObj = meat.LoadOrder(settings['sFO_TXT'], settings['sFO_PATH'] + '\\Data\\', self.mode)
				elif self.mode == modeNV:
					if settings['sNV_TXT'] == '' or settings['sNV_PATH'] == '':
						self.show_error('Could not refresh load order. Check if your settings are correct.')
						return None
					loObj = meat.LoadOrder(settings['sNV_TXT'], settings['sNV_PATH'] + '\\Data\\', self.mode)
				elif self.mode == modeSK:
					if settings['sSK_TXT'] == '' or settings['sSK_PATH'] == '':
						self.show_error('Could not refresh load order. Check if your settings are correct.')
						return None
					loObj = meat.LoadOrder(settings['sSK_TXT'], settings['sSK_PATH'] + '\\Data\\', self.mode)
				else:
					if settings['sOB_TXT'] == '' or settings['sOB_PATH'] == '':
						self.show_error('Could not refresh load order. Check if your settings are correct.')
						return None
					loObj = meat.LoadOrder(settings['sOB_TXT'], settings['sOB_PATH'] + '\\Data\\', self.mode)
			except meat.LoadOrderError:
				self.show_error('Could not refresh load order. Check if your settings are correct.')
			
			loObj.list_to_loadorder(plugins)
			
			mods = loObj.inact
			mods.sort()
			
			self.actLi.DeleteAllItems()
			self.inactLi.DeleteAllItems()
			for s in mods:
				num_items = self.inactLi.GetItemCount()
				self.inactLi.InsertStringItem(num_items, s)
				if s.endswith('.esm'):
					self.inactLi.SetStringItem(num_items, 1, 'Master file')
				else:
					self.inactLi.SetStringItem(num_items, 1, 'Plugin file')
					
			# get hex values
			hexvals = []
			
			for i in loObj.actMasters:
				h = str(hex(loObj.actMasters.index(i)))[2:]
				if len(h) < 2: h = '0' + h
				hexvals.append([i, h])

			for i in loObj.actPlugins:
				h = str(hex(loObj.actPlugins.index(i) + len(loObj.actMasters)))[2:]
				if len(h) < 2: h = '0' + h
				hexvals.append([i, h])
			
			order = []
			order.extend(loObj.order)

			for l in hexvals:
				order[order.index(l[0])] = l
			
			for l in hexvals:
				num_items = self.actLi.GetItemCount()
				self.actLi.InsertStringItem(num_items, l[0])
			
				if l[0].endswith('.esm'):
					self.actLi.SetStringItem(num_items, 1, 'Master file')
				else:
					self.actLi.SetStringItem(num_items, 1, 'Plugin file')
					
				self.actLi.SetStringItem(num_items, 2, l[1])
			
			self.set_mod_count(len(order))
		
	def export_loadorder(self, event=None):
		'''Export load order to a .txt file.'''
		saveBox = wx.FileDialog(self, message='Save', defaultDir=os.environ['USERPROFILE'], defaultFile='', style=wx.FD_SAVE, wildcard='Plain text files (*.txt)|*.txt')
		if saveBox.ShowModal() == wx.ID_OK:
			path = saveBox.GetPath()
			data = []
			for x in range(self.actLi.GetItemCount()):
				data.append(self.actLi.GetItemText(x))
			try:
				fil = open(path, 'w')
				try:
					for s in data:
						fil.write(s + '\n')
				finally:
					fil.close()
			except IOError:
				self.show_error('Could not save txt file. Check if UAC is preventing the program from writing to that location.')
		
	def handle_hotkey(self, event=None):
		'''Handle hotkeys.'''
		key = event.GetKeyCode()
		if key == 332: # Num-8 key
			self.move_up()
		elif key == 326: # Num-2 key
			self.move_down()
		elif key == 328: # Num-4 key
			self.activate()
		elif key == 330: # Num-6 key
			self.deactivate()
		elif key == 331: # Num-7 key
			self.move_top()
		elif key == 325: # Num-1 key
			self.move_bottom()
		else:
			event.Skip()
		
	def activate(self, event=None):
		'''Move the currently selected items to active list.'''
		items = self.get_selected_rows(1)
		if not items: return
		
		data = []
		inactData = []
		for x in range(self.actLi.GetItemCount()):
			data.append(self.actLi.GetItemText(x))
		for x in range(self.inactLi.GetItemCount()):
			inactData.append(self.inactLi.GetItemText(x))

		tmpLi = []
		for i in items:
			tmpLi.append(inactData[i])
		items.reverse()
		for i in items:
			del inactData[i]
		data.extend(tmpLi)
		inactData.sort()

		
		hexvals = []
		actMasters = []
		actPlugins = []
		
		for i in data:
			if i.endswith('.esm'):
				actMasters.append(i)
			else:
				actPlugins.append(i)
		
		for i in actMasters:
			h = str(hex(actMasters.index(i)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for i in actPlugins:
			h = str(hex(actPlugins.index(i) + len(actMasters)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for l in hexvals:
			data[data.index(l[0])] = l
		
		self.actLi.DeleteAllItems()
		self.inactLi.DeleteAllItems()
		
		for l in inactData:
			num_items = self.inactLi.GetItemCount()
			self.inactLi.InsertStringItem(num_items, l)
		
			if l.endswith('.esm'):
				self.inactLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.inactLi.SetStringItem(num_items, 1, 'Plugin file')

		for l in data:
			num_items = self.actLi.GetItemCount()
			self.actLi.InsertStringItem(num_items, l[0])
		
			if l[0].endswith('.esm'):
				self.actLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.actLi.SetStringItem(num_items, 1, 'Plugin file')	
				
			self.actLi.SetStringItem(num_items, 2, l[1])		
			self.actLi.SetStringItem(data.index(l), 2, l[1])
			
		for i in range(self.actLi.GetItemCount()):
			self.actLi.SetItemState(i, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
		for i in range(self.actLi.GetItemCount()-len(items), self.actLi.GetItemCount()):
			self.actLi.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
			self.actLi.EnsureVisible(i)
		
		self.set_mod_count(self.actLi.GetItemCount())
			
	def deactivate(self, event=None):
		'''Move the currently selected items to inactive list.'''
		items = self.get_selected_rows()
		if not items: return
		
		data = []
		inactData = []
		for x in range(self.actLi.GetItemCount()):
			data.append(self.actLi.GetItemText(x))
		for x in range(self.inactLi.GetItemCount()):
			inactData.append(self.inactLi.GetItemText(x))

		tmpLi = []
		for i in items:
			tmpLi.append(data[i])
		items.reverse()
		for i in items:
			del data[i]
		inactData.extend(tmpLi)
		inactData.sort()

		
		hexvals = []
		actMasters = []
		actPlugins = []
		
		for i in data:
			if i.endswith('.esm'):
				actMasters.append(i)
			else:
				actPlugins.append(i)
		
		for i in actMasters:
			h = str(hex(actMasters.index(i)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for i in actPlugins:
			h = str(hex(actPlugins.index(i) + len(actMasters)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for l in hexvals:
			data[data.index(l[0])] = l
		
		self.actLi.DeleteAllItems()
		self.inactLi.DeleteAllItems()
		
		for l in inactData:
			num_items = self.inactLi.GetItemCount()
			self.inactLi.InsertStringItem(num_items, l)
		
			if l.endswith('.esm'):
				self.inactLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.inactLi.SetStringItem(num_items, 1, 'Plugin file')

		for l in data:
			num_items = self.actLi.GetItemCount()
			self.actLi.InsertStringItem(num_items, l[0])
		
			if l[0].endswith('.esm'):
				self.actLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.actLi.SetStringItem(num_items, 1, 'Plugin file')	
				
			self.actLi.SetStringItem(num_items, 2, l[1])		
			self.actLi.SetStringItem(data.index(l), 2, l[1])
			
		self.set_mod_count(self.actLi.GetItemCount())
		
	def move_bottom(self, event=None):
		'''Move the currently selected items to the bottom of the list.'''
		items = self.get_selected_rows()
		if not items: return
		
		data = []
		for x in range(self.actLi.GetItemCount()):
			data.append(self.actLi.GetItemText(x))

		tmpLi = []
		for i in items:
			tmpLi.append(data[i])
		for i in items:
			del data[i]
			
		tmpLi.reverse()
		for i in tmpLi:
			data.append(i)

		
		hexvals = []
		actMasters = []
		actPlugins = []
		
		for i in data:
			if i.endswith('.esm'):
				actMasters.append(i)
			else:
				actPlugins.append(i)
		
		for i in actMasters:
			h = str(hex(actMasters.index(i)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for i in actPlugins:
			h = str(hex(actPlugins.index(i) + len(actMasters)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for l in hexvals:
			data[data.index(l[0])] = l
		
		self.actLi.DeleteAllItems()

		for l in data:
			num_items = self.actLi.GetItemCount()
			self.actLi.InsertStringItem(num_items, l[0])
		
			if l[0].endswith('.esm'):
				self.actLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.actLi.SetStringItem(num_items, 1, 'Plugin file')	
				
			self.actLi.SetStringItem(num_items, 2, l[1])		
			self.actLi.SetStringItem(data.index(l), 2, l[1])
			
		for i in range(self.actLi.GetItemCount()):
			self.actLi.SetItemState(i, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
		for i in range(self.actLi.GetItemCount()-len(items), self.actLi.GetItemCount()):
			self.actLi.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
			self.actLi.EnsureVisible(i)
	
	def move_top(self, event=None):
		'''Move the currently selected items to the top of the list.'''
		items = self.get_selected_rows()
		if not items: return
		
		data = []
		for x in range(self.actLi.GetItemCount()):
			data.append(self.actLi.GetItemText(x))

		tmpLi = []
		for i in items:
			tmpLi.append(data[i])
		items.reverse()
		for i in items:
			del data[i]
		tmpLi.reverse()
		for i in tmpLi:
			data.insert(0, i)
		
		hexvals = []
		actMasters = []
		actPlugins = []
		
		for i in data:
			if i.endswith('.esm'):
				actMasters.append(i)
			else:
				actPlugins.append(i)
		
		for i in actMasters:
			h = str(hex(actMasters.index(i)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for i in actPlugins:
			h = str(hex(actPlugins.index(i) + len(actMasters)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for l in hexvals:
			data[data.index(l[0])] = l
		
		self.actLi.DeleteAllItems()

		for l in data:
			num_items = self.actLi.GetItemCount()
			self.actLi.InsertStringItem(num_items, l[0])
		
			if l[0].endswith('.esm'):
				self.actLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.actLi.SetStringItem(num_items, 1, 'Plugin file')	
				
			self.actLi.SetStringItem(num_items, 2, l[1])		
			self.actLi.SetStringItem(data.index(l), 2, l[1])
			
		for i in range(self.actLi.GetItemCount()):
			self.actLi.SetItemState(i, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
		for i in range(len(items)):
			self.actLi.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
			self.actLi.EnsureVisible(i)
		
	def move_up(self, event=None):
		'''Move the currently selected items up in the list.'''
		items = self.get_selected_rows()
		if not items: return	
		
		for i in items:
			if not i == 0:
				tmp = self.actLi.GetItemText(i)
				self.actLi.SetItemText(i, self.actLi.GetItemText(i-1))
				self.actLi.SetItemText(i-1, tmp)
		
		data = []
		for x in range(self.actLi.GetItemCount()):
			data.append(self.actLi.GetItemText(x))
		
		hexvals = []
		actMasters = []
		actPlugins = []
		
		for i in data:
			if i.endswith('.esm'):
				actMasters.append(i)
			else:
				actPlugins.append(i)
		
		for i in actMasters:
			h = str(hex(actMasters.index(i)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for i in actPlugins:
			h = str(hex(actPlugins.index(i) + len(actMasters)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for l in hexvals:
			data[data.index(l[0])] = l
		
		for l in data:
			if l[0].endswith('.esm'):
				self.actLi.SetStringItem(data.index(l), 1, 'Master file')
			else:
				self.actLi.SetStringItem(data.index(l), 1, 'Plugin file')
				
			self.actLi.SetStringItem(data.index(l), 2, l[1])
		for i in range(self.actLi.GetItemCount()):
			self.actLi.SetItemState(i, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
		for i in items:
			if not i == 0:
				self.actLi.SetItemState(i-1, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
				self.actLi.EnsureVisible(i)
			
	
	def move_down(self, event=None):
		'''Move the currently selected items down in the list.'''
		items = self.get_selected_rows()
		if not items: return	
		
		items.reverse()
		for i in items:
			if not i >= self.actLi.GetItemCount() - 1:
				tmp = self.actLi.GetItemText(i)
				self.actLi.SetItemText(i, self.actLi.GetItemText(i+1))
				self.actLi.SetItemText(i+1, tmp)
		
		data = []
		for x in range(self.actLi.GetItemCount()):
			data.append(self.actLi.GetItemText(x))
		
		hexvals = []
		actMasters = []
		actPlugins = []
		
		for i in data:
			if i.endswith('.esm'):
				actMasters.append(i)
			else:
				actPlugins.append(i)
		
		for i in actMasters:
			h = str(hex(actMasters.index(i)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for i in actPlugins:
			h = str(hex(actPlugins.index(i) + len(actMasters)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])

		for l in hexvals:
			data[data.index(l[0])] = l
		
		for l in data:
			if l[0].endswith('.esm'):
				self.actLi.SetStringItem(data.index(l), 1, 'Master file')
			else:
				self.actLi.SetStringItem(data.index(l), 1, 'Plugin file')
				
			self.actLi.SetStringItem(data.index(l), 2, l[1])
		for i in range(self.actLi.GetItemCount()):
			self.actLi.SetItemState(i, 0, wx.LIST_STATE_SELECTED|wx.LIST_STATE_FOCUSED)
		for i in items:
			self.actLi.SetItemState(i+1, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
			self.actLi.EnsureVisible(i)
			
		
	def actlist_select(self, event=None):
		'''Handle wx.EVT_LIST_ITEM_SELECTED for actLi.'''
		self.set_mod_details(self.actLi.GetItemText(self.actLi.GetFirstSelected()))
		
	def inactlist_select(self, event=None):
		'''Handle wx.EVT_LIST_ITEM_SELECTED for inactLi.'''
		self.set_mod_details(self.inactLi.GetItemText(self.inactLi.GetFirstSelected()))
		
	def get_selected_rows(self, list=0):
		'''Return a list containing the id's of every item currently selected in actLi.'''
		res = []
		if list == 0:	# actLi
			if self.actLi.GetFirstSelected() != -1: 
				i = self.actLi.GetFirstSelected()
				while i != -1:
					res.append(i)
					i = self.actLi.GetNextSelected(i)
		else:	# inactLi
			if self.inactLi.GetFirstSelected() != -1: 
				i = self.inactLi.GetFirstSelected()
				while i != -1:
					res.append(i)
					i = self.inactLi.GetNextSelected(i)	
		return res

	def set_mod_count(self, count):
		'''Update displayed mod count.'''
		self._mcount.SetLabel('Active mod limit: %s/256' % count)
		if count > 256:
			self._mcount.SetForegroundColour(wx.RED)
		else:
			self._mcount.SetForegroundColour(wx.BLACK)
			
		self.sizer.Layout()
			
	def set_mod_details(self, modName):
		'''Update description box.'''
		if settings['bSHOW_DESCR'] == False or not modName: return
		try:
			if self.mode == modeFO:
				res = meat.get_mod_details(settings['sFO_PATH'] + '\\Data\\' + modName)
			elif self.mode == modeNV:
				res = meat.get_mod_details(settings['sNV_PATH'] + '\\Data\\' + modName)
			elif self.mode == modeSK:
				res = meat.get_mod_details(settings['sSK_PATH'] + '\\Data\\' + modName)
			else:
				res = meat.get_mod_details(settings['sOB_PATH'] + '\\Data\\' + modName)
				
			if res['author'] == '' or res['author'] == 'DEFAULT':
				self.authBox.SetValue('Unknown')
			else:
				self.authBox.SetValue(res['author'])
			if res['description'] == '':
				if res['masters'] != '':
					self.descrBox.SetValue('No description available.\n\n\nMASTERS:\n' + res['masters'])
				else:
					self.descrBox.SetValue('No description available.')
			else:
				self.descrBox.SetValue(res['description'] + '\n\n\nMASTERS:\n' + res['masters'])
		except meat.TES4ModError:
			pass
			
	def save_loadorder(self, event=None):
		'''Save the load order to plugins.txt, and update timestamps.'''
		try:
			loadorder = []
			for x in range(self.actLi.GetItemCount()):
				loadorder.append(self.actLi.GetItemText(x))
			if self.mode == modeFO:
				loObj = meat.LoadOrder(settings['sFO_TXT'], settings['sFO_PATH'] + '\\Data\\', self.mode)
			elif self.mode == modeNV:
				loObj = meat.LoadOrder(settings['sNV_TXT'], settings['sNV_PATH'] + '\\Data\\', self.mode)
			elif self.mode == modeSK:
				loObj = meat.LoadOrder(settings['sSK_TXT'], settings['sSK_PATH'] + '\\Data\\', self.mode)
			else:
				loObj = meat.LoadOrder(settings['sOB_TXT'], settings['sOB_PATH'] + '\\Data\\', self.mode)
			loObj.list_to_loadorder(loadorder)
			loObj.save()
		except meat.LoadOrderError:
			self.show_error('Could not save load order. Check if your settings are correct, or if UAC is preventing the program from making the necessary changes.')
		
	def refresh_loadorder(self, event=None):
		'''Refresh displayed load order.'''
		try:
			if self.mode == modeFO:
				if settings['sFO_TXT'] == '' or settings['sFO_PATH'] == '':
					self.show_error('Could not refresh load order. Check if your settings are correct.')
					return None
				loObj = meat.LoadOrder(settings['sFO_TXT'], settings['sFO_PATH'] + '\\Data\\', self.mode)
			elif self.mode == modeNV:
				if settings['sNV_TXT'] == '' or settings['sNV_PATH'] == '':
					self.show_error('Could not refresh load order. Check if your settings are correct.')
					return None
				loObj = meat.LoadOrder(settings['sNV_TXT'], settings['sNV_PATH'] + '\\Data\\', self.mode)
			elif self.mode == modeSK:
				if settings['sSK_TXT'] == '' or settings['sSK_PATH'] == '':
					self.show_error('Could not refresh load order. Check if your settings are correct.')
					return None
				loObj = meat.LoadOrder(settings['sSK_TXT'], settings['sSK_PATH'] + '\\Data\\', self.mode)
			else:
				if settings['sOB_TXT'] == '' or settings['sOB_PATH'] == '':
					self.show_error('Could not refresh load order. Check if your settings are correct.')
					return None
				loObj = meat.LoadOrder(settings['sOB_TXT'], settings['sOB_PATH'] + '\\Data\\', self.mode)
		except meat.LoadOrderError:
			self.show_error('Could not refresh load order. Check if your settings are correct.')
		
		loObj.parse()
		
		mods = loObj.inact
		mods.sort()
		
		self.actLi.DeleteAllItems()
		self.inactLi.DeleteAllItems()
		for s in mods:
			num_items = self.inactLi.GetItemCount()
			self.inactLi.InsertStringItem(num_items, s)
			if s.endswith('.esm'):
				self.inactLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.inactLi.SetStringItem(num_items, 1, 'Plugin file')
				
		# get hex values
		hexvals = []
		for i in loObj.order:
			h = str(hex(loObj.order.index(i)))[2:]
			if len(h) < 2: h = '0' + h
			hexvals.append([i, h])
		
		order = []
		order.extend(loObj.order)

		if len(loObj.order) - 1 > -1:
			for l in hexvals:
				if not l[0] in range(len(loObj.order)): continue # a quick hacky fix?
				loObj.order[loObj.order.index(l[0])] = l
		
		for l in hexvals:
			num_items = self.actLi.GetItemCount()
			self.actLi.InsertStringItem(num_items, l[0])
		
			if l[0].endswith('.esm'):
				self.actLi.SetStringItem(num_items, 1, 'Master file')
			else:
				self.actLi.SetStringItem(num_items, 1, 'Plugin file')
				
			self.actLi.SetStringItem(num_items, 2, l[1])
		
		self.set_mod_count(len(order))
			
	def show_error(self, error=''):
		'''Display an error message.'''
		msg = 'An error was encountered:\n' + error
		errorBox = wx.MessageDialog(self, caption='Error', message=msg, style=wx.ICON_ERROR|wx.STAY_ON_TOP|wx.OK)
		
		if errorBox.ShowModal() == wx.ID_OK:
			errorBox.Destroy()
			
	def show_descr_box(self, val=True):
		'''Set visibility of description and author boxes.'''
		if val:
			self.authBox.Show()
			self.descrBox.Show()
		else:
			self.authBox.Hide()
			self.descrBox.Hide()
		self.sizer.Layout()
			
	
class MainFrame(BaseFrame):
	'''Main frame class for LOST app.'''
	def __init__(self):
		wx.Frame.__init__(self, None, title=constants['WINDOW_TITLE'], size=(constants['WINDOW_WIDTH'], constants['WINDOW_HEIGHT']), style=wx.DEFAULT_FRAME_STYLE, id=wx.ID_ANY)	
		self.Center()
		self.SetIcon(wx.Icon(constants['ICO_PATH'], wx.BITMAP_TYPE_ICO))
		self.SetMinSize((800, 400))
		
		self.load_settings()
		
		def _init_menubar():
			self.menubar = wx.MenuBar()
			menuFile = wx.Menu()
			menuOptions = wx.Menu()
			menuTools = wx.Menu()
			menuAbout = wx.Menu()
			
			self.SetMenuBar(self.menubar)
			
			self.menubar.Append(menuFile, '&File')
			saveLO1 = menuFile.Append(wx.ID_ANY, '&Save current load order')
			saveLO2 = menuFile.Append(wx.ID_ANY, '&Save all load orders')
			menuFile.AppendSeparator()
			reloadLO1 = menuFile.Append(wx.ID_ANY, '&Refresh current load order')
			reloadLO2 = menuFile.Append(wx.ID_ANY, '&Refresh all load orders')
			menuFile.AppendSeparator()
			importLO = menuFile.Append(wx.ID_ANY, '&Import load order (.txt)')
			exportLO = menuFile.Append(wx.ID_ANY, '&Export load order (.txt)')
			clipboardLO = menuFile.Append(wx.ID_ANY, '&Copy load order to clipboard')
			self.Bind(wx.EVT_MENU, self.handle_save_single, saveLO1)
			self.Bind(wx.EVT_MENU, self.handle_save_all, saveLO2)
			self.Bind(wx.EVT_MENU, self.handle_refresh_single, reloadLO1)
			self.Bind(wx.EVT_MENU, self.handle_refresh_all, reloadLO2)
			self.Bind(wx.EVT_MENU, self.handle_import, importLO)
			self.Bind(wx.EVT_MENU, self.handle_export, exportLO)
			self.Bind(wx.EVT_MENU, self.handle_clipboard, clipboardLO)
			
			self.menubar.Append(menuOptions, '&Options')
			settingsItem = menuOptions.Append(wx.ID_ANY, '&Settings')
			self.Bind(wx.EVT_MENU, self.show_settings, settingsItem)
			
			self.menubar.Append(menuTools, '&Tools')
			bossItem = menuTools.Append(wx.ID_ANY, '&BOSS')
			self.Bind(wx.EVT_MENU, self.show_boss, bossItem)
			
			self.menubar.Append(menuAbout, '&Help')
			aboutItem = menuAbout.Append(wx.ID_ANY, '&About')
			docsItem = menuAbout.Append(wx.ID_ANY, '&Online docs')
			self.Bind(wx.EVT_MENU, self.show_about, aboutItem)
			self.Bind(wx.EVT_MENU, self.show_docs, docsItem)
		
		def _init_notebook():
			self.notebook = wx.Notebook(self, wx.ID_ANY, style=wx.NB_TOP)
			
			if settings['sNV_PATH'] and settings['sNV_TXT']:
				self.panelNV = LoadOrderPanel(self.notebook, modeNV)
			else:
				self.panelNV = UndefPanel(self.notebook)
			if settings['sFO_PATH'] and settings['sFO_TXT']:
				self.panelFO = LoadOrderPanel(self.notebook, modeFO)
			else:
				self.panelFO = UndefPanel(self.notebook)
			if settings['sOB_PATH'] and settings['sOB_TXT']:
				self.panelOB = LoadOrderPanel(self.notebook, modeOB)
			else:
				self.panelOB = UndefPanel(self.notebook)
			if settings['sSK_PATH'] and settings['sSK_TXT']:
				self.panelSK = LoadOrderPanel(self.notebook, modeSK)
			else:
				self.panelSK = UndefPanel(self.notebook)
			
			self.notebook.AddPage(self.panelSK, 'Skyrim')
			self.notebook.AddPage(self.panelNV, 'New Vegas')
			self.notebook.AddPage(self.panelFO, 'Fallout 3')
			self.notebook.AddPage(self.panelOB, 'Oblivion')
			
			self.set_tab(settings['sDEF_MODE'])
			
		def _init_hotkeys():
			for i in self.GetChildren():	# This is stupid, I know <.<
				i.Bind(wx.EVT_KEY_DOWN, self.handle_hotkey)
				for n in i.GetChildren():
					n.Bind(wx.EVT_KEY_DOWN, self.handle_hotkey)
					for m in n.GetChildren():
						m.Bind(wx.EVT_KEY_DOWN, self.handle_hotkey)				
			self.Bind(wx.EVT_KEY_DOWN, self.handle_hotkey)
		
		self.Bind(wx.EVT_CLOSE, self.handle_exit)
		if settings['bFIRST_RUN']: self.show_settings()
		
		_init_menubar()
		_init_notebook()
		_init_hotkeys()
		
		self.Show()
		
	# Backend
	def handle_clipboard(self, event=None):
		'''Call loadorder_to_clipboard() on appropriate LoadOrderPanel.'''
		if self.get_tab() == modeNV and not isinstance(self.panelNV, UndefPanel):
			self.panelNV.loadorder_to_clipboard()
		elif self.get_tab() == modeFO and not isinstance(self.panelFO, UndefPanel):
			self.panelFO.loadorder_to_clipboard()
		elif self.get_tab() == modeSK and not isinstance(self.panelSK, UndefPanel):
			self.panelSK.loadorder_to_clipboard()
		elif not isinstance(self.panelOB, UndefPanel):
			self.panelOB.loadorder_to_clipboard()
	
	def handle_import(self, event=None):
		'''Call export_loadorder() on appropriate LoadOrderPanel.'''
		if self.get_tab() == modeNV and not isinstance(self.panelNV, UndefPanel):
			self.panelNV.import_loadorder()
		elif self.get_tab() == modeFO and not isinstance(self.panelFO, UndefPanel):
			self.panelFO.import_loadorder()
		elif self.get_tab() == modeSK and not isinstance(self.panelSK, UndefPanel):
			self.panelSK.import_loadorder()
		elif not isinstance(self.panelOB, UndefPanel):
			self.panelOB.import_loadorder()
	
	def handle_export(self, event=None):
		'''Call export_loadorder() on appropriate LoadOrderPanel.'''
		if self.get_tab() == modeNV and not isinstance(self.panelNV, UndefPanel):
			self.panelNV.export_loadorder()
		elif self.get_tab() == modeFO and not isinstance(self.panelFO, UndefPanel):
			self.panelFO.export_loadorder()
		elif self.get_tab() == modeSK and not isinstance(self.panelSK, UndefPanel):
			self.panelSK.export_loadorder()
		elif not isinstance(self.panelOB, UndefPanel):
			self.panelOB.export_loadorder()
		
	def handle_exit(self, event=None):
		'''Handle exit event.'''
		if settings['bSAVE_EXIT']:
			try:
				self.handle_save_all()
			except:
				pass
		self.Destroy()
		sys.exit(0)
		
	def handle_refresh_single(self, event=None):
		'''Call refresh_loadorder() on current panel.'''
		if self.get_tab() == modeNV and not isinstance(self.panelNV, UndefPanel):
			self.panelNV.refresh_loadorder()
		elif self.get_tab() == modeFO and not isinstance(self.panelFO, UndefPanel):
			self.panelFO.refresh_loadorder()
		elif self.get_tab() == modeSK and not isinstance(self.panelSK, UndefPanel):
			self.panelSK.refresh_loadorder()
		elif not isinstance(self.panelOB, UndefPanel):
			self.panelOB.refresh_loadorder()
			
	def handle_refresh_all(self, event=None):
		'''Call refresh_loadorder() on all panels.'''
		if not isinstance(self.panelNV, UndefPanel):
			self.panelNV.refresh_loadorder()
		if not isinstance(self.panelFO, UndefPanel):
			self.panelFO.refresh_loadorder()
		if not isinstance(self.panelOB, UndefPanel):
			self.panelOB.refresh_loadorder()
		if not isinstance(self.panelSK, UndefPanel):
			self.panelSK.refresh_loadorder()
	
	def handle_save_single(self, event=None):
		'''Call save_loadorder() on current panel.'''
		if self.get_tab() == modeNV and not isinstance(self.panelNV, UndefPanel):
			self.panelNV.save_loadorder()
		elif self.get_tab() == modeFO and not isinstance(self.panelFO, UndefPanel):
			self.panelFO.save_loadorder()
		elif self.get_tab() == modeSK and not isinstance(self.panelSK, UndefPanel):
			self.panelSK.save_loadorder()
		elif not isinstance(self.panelOB, UndefPanel):
			self.panelOB.save_loadorder()
			
	def handle_save_all(self, event=None):
		'''Call save_loadorder() on all panels.'''
		if not isinstance(self.panelNV, UndefPanel):
			self.panelNV.save_loadorder()
		if not isinstance(self.panelFO, UndefPanel):
			self.panelFO.save_loadorder()
		if not isinstance(self.panelOB, UndefPanel):
			self.panelOB.save_loadorder()
		if not isinstance(self.panelSK, UndefPanel):
			self.panelSK.save_loadorder()
			
	def handle_hotkey(self, event=None):
		'''Handle (global) hotkeys for self and children.'''
		key = event.GetKeyCode()
		if key == 49: # 1 key
			self.set_tab(modeSK)
		elif key == 50: # 2 key
			self.set_tab(modeNV)
		elif key == 51: # 3 key
			self.set_tab(modeFO)
		elif key == 52: # 4 key
			self.set_tab(modeOB)
		elif key == 27: # ESC key
			self.handle_exit() # exit program
		else:
			event.Skip()
		
	def show_about(self, event=None):
		'''Display some information related to the program.'''
		aboutBox = wx.MessageDialog(self, caption='About', message=constants['ABOUT'], style=wx.ICON_INFORMATION|wx.STAY_ON_TOP|wx.OK)

		if aboutBox.ShowModal() == wx.ID_OK:
			aboutBox.Destroy()
			
	def show_docs(self, event=None):
		'''Open the documentation for this app in browser.'''
		webbrowser.open_new_tab(constants['DOCS_LOC'])
		
	def load_settings(self, event=None):
		'''Update settings from the INI file.'''
		try:			
			ini = iniparse.ConfigParser()
			ini.read(constants['INI_PATH'])
			
			settings['sDEF_MODE'] = ini.get('General', 'DefaultGame')
			settings['bSHOW_DESCR'] = ini.getboolean('General', 'ShowDescriptions')
			settings['bSAVE_EXIT'] = ini.getboolean('General', 'SaveOnExit')
			settings['bFIRST_RUN'] = ini.getboolean('General', 'FirstRun')
			
			settings['sFO_PATH'] = ini.get('Paths', 'FO3Path')
			settings['sOB_PATH'] = ini.get('Paths', 'OBPath')
			settings['sNV_PATH'] = ini.get('Paths', 'NVPath')
			settings['sSK_PATH'] = ini.get('Paths', 'SKPath')
			
			settings['sOB_TXT'] = ini.get('Paths', 'OBPluginPath')
			settings['sFO_TXT'] = ini.get('Paths', 'FO3PluginPath')
			settings['sNV_TXT'] = ini.get('Paths', 'NVPluginPath')
			settings['sSK_TXT'] = ini.get('Paths', 'SKPluginPath')
		except:
			self.show_error('Failed to read ini. Check if the file is misssing or damaged.')
			sys.exit(1)

	def show_settings(self, event=None):
		'''Invoke settings frame.'''
		wndw = SettingsFrame(parent=self, defaults=settings)
		
	def show_boss(self, event=None):
		'''Invoke BOSS frame.'''
		wndw = BOSSFrame(self, defGame=self.get_tab())
	
	def get_tab(self):
		'''Return the game tab that is currently displayed.'''
		if self.notebook.GetSelection() == 0:
			return modeSK
		elif self.notebook.GetSelection() == 1:
			return modeNV
		elif self.notebook.GetSelection() == 2:
			return modeFO
		else:
			return modeOB
		
	def set_tab(self, mode):
		'''Set the game tab that is currently displayed.'''
		if mode == modeSK:
			self.notebook.SetSelection(0)
		elif mode == modeNV:
			self.notebook.SetSelection(1)
		elif mode == modeFO:
			self.notebook.SetSelection(2)
		else:
			self.notebook.SetSelection(3)
			
	def handle_setting_update(self):
		'''Apply new settings to GUI.'''
		if settings['bSHOW_DESCR']:
			if not isinstance(self.panelNV, UndefPanel):
				self.panelNV.show_descr_box()
			if not isinstance(self.panelFO, UndefPanel):
				self.panelFO.show_descr_box()
			if not isinstance(self.panelOB, UndefPanel):
				self.panelOB.show_descr_box()
			if not isinstance(self.panelSK, UndefPanel):
				self.panelSK.show_descr_box()
		else:
			if not isinstance(self.panelNV, UndefPanel):
				self.panelNV.show_descr_box(False)
			if not isinstance(self.panelFO, UndefPanel):
				self.panelFO.show_descr_box(False)
			if not isinstance(self.panelOB, UndefPanel):
				self.panelOB.show_descr_box(False)
			if not isinstance(self.panelSK, UndefPanel):
				self.panelSK.show_descr_box(False)
			

# SettingsFrame class needs to be tidied some time
class SettingsFrame(BaseFrame):
	'''Frame for modifying INI settings.'''
	def __init__(self, parent, panelTitle='Settings', panelSize=(450,565), defaults={}):
		wx.Frame.__init__(self, parent, wx.ID_ANY, panelTitle, size=panelSize, style=wx.STAY_ON_TOP|wx.DEFAULT_FRAME_STYLE^(wx.MINIMIZE_BOX))
		self.SetIcon(wx.Icon(constants['ICO_PATH'], wx.BITMAP_TYPE_ICO))
		self.SetMinSize((300, 565))		
		self.Center()
		
		backgrnd = wx.Panel(self)
		
		self.parent = parent
		
		# Default game
		self.gameChoicesOptions = ['Fallout 3', 'Oblivion', 'New Vegas', 'Skyrim']
		self.gameBox = wx.RadioBox(backgrnd, wx.ID_ANY, 'Default game', choices=self.gameChoicesOptions, style=wx.VERTICAL)
		if defaults['sDEF_MODE'] == modeFO:
			self.gameBox.SetSelection(0)
		elif defaults['sDEF_MODE'] == modeOB:
			self.gameBox.SetSelection(1)
		elif defaults['sDEF_MODE'] == modeSK:
			self.gameBox.SetSelection(3)
		else:
			self.gameBox.SetSelection(2)
		
		# Various
		self.saveBox = wx.RadioBox(backgrnd, wx.ID_ANY, 'Save on exit', choices=['No', 'Yes'], style=wx.VERTICAL)
		self.descrBox = wx.RadioBox(backgrnd, wx.ID_ANY, 'Show descriptions', choices=['No', 'Yes'], style=wx.VERTICAL)
		if defaults['bSAVE_EXIT'] == True:
			self.saveBox.SetSelection(1)
		else:
			self.saveBox.SetSelection(0)
			
		if defaults['bSHOW_DESCR'] == True:
			self.descrBox.SetSelection(1)
		else:
			self.descrBox.SetSelection(0)
		
		# Paths
		# Oblivion
		label1 = wx.StaticText(backgrnd, wx.ID_ANY, label=' Oblivion path')
		self.OBPathBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.OBPathBox.SetValue(defaults['sOB_PATH'])
		self.OBbrowseBtn = wx.Button(backgrnd, label='Browse')
		self.OBbrowseBtn.Bind(wx.EVT_BUTTON, self.OBbrowse1)
		
		label2 = wx.StaticText(backgrnd, wx.ID_ANY, label=' Oblivion plugins.txt')
		self.OBpluginsBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.OBpluginsBox.SetValue(defaults['sOB_TXT'])
		self.OBsearchBtn = wx.Button(backgrnd, label='Auto')
		self.OBsearchBtn.Bind(wx.EVT_BUTTON, self.OBpluginsPathSearch)
		self.OBbrowseBtn2 = wx.Button(backgrnd, label='Browse')
		self.OBbrowseBtn2.Bind(wx.EVT_BUTTON, self.OBbrowse2)
		
		# Fallout 3
		label3 = wx.StaticText(backgrnd, wx.ID_ANY, label=' Fallout 3 path')
		self.FOPathBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.FOPathBox.SetValue(defaults['sFO_PATH'])
		self.FObrowseBtn = wx.Button(backgrnd, label='Browse')
		self.FObrowseBtn.Bind(wx.EVT_BUTTON, self.FObrowse1)
		
		label4 = wx.StaticText(backgrnd, wx.ID_ANY, label=' Fallout 3 plugins.txt')
		self.FOpluginsBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.FOpluginsBox.SetValue(defaults['sFO_TXT'])
		self.FOsearchBtn = wx.Button(backgrnd, label='Auto')
		self.FOsearchBtn.Bind(wx.EVT_BUTTON, self.FOpluginsPathSearch)
		self.FObrowseBtn2 = wx.Button(backgrnd, label='Browse')
		self.FObrowseBtn2.Bind(wx.EVT_BUTTON, self.FObrowse2)
		
		# New Vegas
		label5 = wx.StaticText(backgrnd, wx.ID_ANY, label=' New Vegas path')
		self.NVPathBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.NVPathBox.SetValue(defaults['sNV_PATH'])
		self.NVbrowseBtn = wx.Button(backgrnd, label='Browse')
		self.NVbrowseBtn.Bind(wx.EVT_BUTTON, self.NVbrowse1)
		
		label6 = wx.StaticText(backgrnd, wx.ID_ANY, label=' New Vegas plugins.txt')
		self.NVpluginsBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.NVpluginsBox.SetValue(defaults['sNV_TXT'])
		self.NVsearchBtn = wx.Button(backgrnd, label='Auto')
		self.NVsearchBtn.Bind(wx.EVT_BUTTON, self.NVpluginsPathSearch)
		self.NVbrowseBtn2 = wx.Button(backgrnd, label='Browse')
		self.NVbrowseBtn2.Bind(wx.EVT_BUTTON, self.NVbrowse2)
		
		# Skyrim
		label8 = wx.StaticText(backgrnd, wx.ID_ANY, label=' Skyrim path')
		self.SKPathBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.SKPathBox.SetValue(defaults['sSK_PATH'])
		self.SKbrowseBtn = wx.Button(backgrnd, label='Browse')
		self.SKbrowseBtn.Bind(wx.EVT_BUTTON, self.NVbrowse1)
		
		label9 = wx.StaticText(backgrnd, wx.ID_ANY, label=' Skyrim plugins.txt')
		self.SKpluginsBox = wx.TextCtrl(backgrnd, style=wx.TE_PROCESS_ENTER)
		self.SKpluginsBox.SetValue(defaults['sSK_TXT'])
		self.SKsearchBtn = wx.Button(backgrnd, label='Auto')
		self.SKsearchBtn.Bind(wx.EVT_BUTTON, self.SKpluginsPathSearch)
		self.SKbrowseBtn2 = wx.Button(backgrnd, label='Browse')
		self.SKbrowseBtn2.Bind(wx.EVT_BUTTON, self.SKbrowse2)
		
		
		self.exitBtn = wx.Button(backgrnd, label='Save')
		self.exitBtn.Bind(wx.EVT_BUTTON, self.exit)
		
		
		# Sizers
		# General settings
		hBox1 = wx.BoxSizer()
		hBox1.Add(self.gameBox, proportion=1, flag=wx.EXPAND, border=3)
		hBox1.Add(self.saveBox, proportion=1, flag=wx.EXPAND, border=3)
		hBox1.Add(self.descrBox, proportion=1, flag=wx.EXPAND, border=3)
		
		# Oblivion settings
		hBox2 = wx.BoxSizer()
		hBox2.Add(self.OBPathBox, proportion=3, flag=wx.EXPAND)
		hBox2.Add(self.OBbrowseBtn, proportion=0)
		
		hBox3 = wx.BoxSizer()
		hBox3.Add(self.OBpluginsBox, proportion=3, flag=wx.EXPAND)
		hBox3.Add(self.OBsearchBtn, proportion=0)
		hBox3.Add(self.OBbrowseBtn2, proportion=0)
		
		# FO settings
		hBox4 = wx.BoxSizer()
		hBox4.Add(self.FOPathBox, proportion=3, flag=wx.EXPAND)
		hBox4.Add(self.FObrowseBtn, proportion=0)
		
		hBox5 = wx.BoxSizer()
		hBox5.Add(self.FOpluginsBox, proportion=3, flag=wx.EXPAND)
		hBox5.Add(self.FOsearchBtn, proportion=0)
		hBox5.Add(self.FObrowseBtn2, proportion=0)
		
		# NV settings
		hBox6 = wx.BoxSizer()
		hBox6.Add(self.NVPathBox, proportion=3, flag=wx.EXPAND)
		hBox6.Add(self.NVbrowseBtn, proportion=0)
		
		hBox7 = wx.BoxSizer()
		hBox7.Add(self.NVpluginsBox, proportion=3, flag=wx.EXPAND)
		hBox7.Add(self.NVsearchBtn, proportion=0)
		hBox7.Add(self.NVbrowseBtn2, proportion=0)
		
		# SK settings
		hBox8 = wx.BoxSizer()
		hBox8.Add(self.SKPathBox, proportion=3, flag=wx.EXPAND)
		hBox8.Add(self.SKbrowseBtn, proportion=0)
		
		hBox9 = wx.BoxSizer()
		hBox9.Add(self.SKpluginsBox, proportion=3, flag=wx.EXPAND)
		hBox9.Add(self.SKsearchBtn, proportion=0)
		hBox9.Add(self.SKbrowseBtn2, proportion=0)

		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(backgrnd, wx.ID_ANY, label='You may have to restart LOST in order for your changes to take effect!'), border=8, proportion=0, flag=wx.EXPAND|wx.ALL)
		sizer.Add(hBox1, flag=wx.EXPAND|wx.ALL, border=5)
		sizer.Add(label1, border=3, flag=wx.ALL)
		sizer.Add(hBox2, border=1, flag=wx.EXPAND|wx.ALL)
		sizer.Add(label2, border=3, flag=wx.ALL)
		sizer.Add(hBox3, border=1, flag=wx.EXPAND|wx.ALL)
		sizer.Add(label3, border=3, flag=wx.ALL)
		sizer.Add(hBox4, border=1, flag=wx.EXPAND|wx.ALL)
		sizer.Add(label4, border=3, flag=wx.ALL)
		sizer.Add(hBox5, border=1, flag=wx.EXPAND|wx.ALL)
		
		sizer.Add(label5, border=3, flag=wx.ALL)
		sizer.Add(hBox6, border=1, flag=wx.EXPAND|wx.ALL)
		sizer.Add(label6, border=3, flag=wx.ALL)
		sizer.Add(hBox7, border=1, flag=wx.EXPAND|wx.ALL)
		
		sizer.Add(label8, border=3, flag=wx.ALL)
		sizer.Add(hBox8, border=1, flag=wx.EXPAND|wx.ALL)
		sizer.Add(label9, border=3, flag=wx.ALL)
		sizer.Add(hBox9, border=1, flag=wx.EXPAND|wx.ALL)
		
		sizer.Add(wx.StaticLine(backgrnd, style=wx.LI_VERTICAL), border=3, proportion=0, flag=wx.EXPAND|wx.ALL)
		sizer.Add(self.exitBtn, proportion=0, flag=wx.ALIGN_RIGHT)
		
		
		backgrnd.SetSizer(sizer)
		
		self.Show()
		
		
	# - Events
	def OBpluginsPathSearch(self, event):
		'''Try to determine OB plugins.txt path and paste it into the box.'''
		tmp = meat.get_txt_path(modeOB)
		if tmp != False:
			self.OBpluginsBox.SetValue(tmp)
		else:
			self.OBpluginsBox.SetValue('')
			
	def FOpluginsPathSearch(self, event):
		'''Try to determine OB plugins.txt path and paste it into the box.'''
		tmp = meat.get_txt_path(modeFO)
		if tmp != False:
			self.FOpluginsBox.SetValue(tmp)
		else:
			self.FOpluginsBox.SetValue('')
			
	def NVpluginsPathSearch(self, event):
		'''Try to determine NV plugins.txt path and paste it into the box.'''
		tmp = meat.get_txt_path(modeNV)	#To hopefully prevent some very obscure issue where the second call to get_txt_path returns false while the first one did not
		if tmp != False:
			self.NVpluginsBox.SetValue(tmp)
		else:
			self.NVpluginsBox.SetValue('')
			
	def SKpluginsPathSearch(self, event):
		'''Try to determine SK plugins.txt path and paste it into the box.'''
		tmp = meat.get_txt_path(modeSK)	#To hopefully prevent some very obscure issue where the second call to get_txt_path returns false while the first one did not
		if tmp != False:
			self.SKpluginsBox.SetValue(tmp)
		else:
			self.SKpluginsBox.SetValue('')
			
	def OBbrowse1(self, event):
		'''Browse for Oblivion directory.'''
		self.OBPathBox.SetValue(self.browse_dir())
		
	def OBbrowse2(self, event):
		'''Browse for Oblivion plugins.txt.'''
		self.OBpluginsBox.SetValue(self.browse_file())
		
	def FObrowse1(self, event):
		'''Browse for Fallout 3 directory.'''
		self.FOPathBox.SetValue(self.browse_dir())
		
	def FObrowse2(self, event):
		'''Browse for Fallout 3 plugins.txt.'''
		self.FOpluginsBox.SetValue(self.browse_file())
		
	def NVbrowse1(self, event):
		'''Browse for New Vegas directory.'''
		self.NVPathBox.SetValue(self.browse_dir())
		
	def NVbrowse2(self, event):
		'''Browse for New Vegas plugins.txt.'''
		self.NVpluginsBox.SetValue(self.browse_file())
		
	def SKbrowse1(self, event):
		'''Browse for Skyrim directory.'''
		self.SKPathBox.SetValue(self.browse_dir())
		
	def SKbrowse2(self, event):
		'''Browse for Skyrim plugins.txt.'''
		self.SKpluginsBox.SetValue(self.browse_dir())
		
	def exit(self, event):
		'''Save data to INI and destroy frame.'''
		set = self.get_settings()
		
		ini = iniparse.ConfigParser()
		ini.read(constants['INI_PATH'])

		ini.set('General', 'DefaultGame', set['sDEF_MODE'])
		ini.set('General', 'ShowDescriptions', set['bSHOW_DESCR'])
		ini.set('General', 'SaveOnExit', set['bSAVE_EXIT'])
		ini.set('General', 'FirstRun', 0)
		
		ini.set('Paths', 'FO3Path', set['sFO_PATH'])
		ini.set('Paths', 'FO3PluginPath', set['sFO_TXT'])
		ini.set('Paths', 'OBPath', set['sOB_PATH'])
		ini.set('Paths', 'OBPluginPath', set['sOB_TXT'])
		ini.set('Paths', 'NVPath', set['sNV_PATH'])
		ini.set('Paths', 'NVPluginPath', set['sNV_TXT'])
		ini.set('Paths', 'SKPath', set['sSK_PATH'])
		ini.set('Paths', 'SKPluginPath', set['sSK_TXT'])
		
		try:
			fil = open(constants['INI_PATH'], 'w')
			try:
				ini.write(fil)
			finally:
				fil.close()
		except IOError:
			self.show_error('Failed to open settings.ini. Check if the file is misssing or damaged.')
		
		self.parent.load_settings()
		self.parent.handle_setting_update()
		self.Destroy()
	
	# - Backend functionality
	def get_settings(self):
		'''Return a dictionary containing the settings the user entered.'''
		settings = {}
		if self.gameBox.GetSelection() == 0:
			settings['sDEF_MODE'] = modeFO
		elif self.gameBox.GetSelection() == 1:
			settings['sDEF_MODE'] = modeOB
		elif self.gameBox.GetSelection() == 2:
			settings['sDEF_MODE'] = modeNV
		else:
			settings['sDEF_MODE'] = modeSK
			
		settings['bSHOW_DESCR'] = self.descrBox.GetSelection()
		settings['bSAVE_EXIT'] = self.saveBox.GetSelection()
		settings['bFIRST_RUN'] = False
		
		settings['sFO_PATH'] = self.FOPathBox.GetValue()
		settings['sOB_PATH'] = self.OBPathBox.GetValue()
		settings['sNV_PATH'] = self.NVPathBox.GetValue()
		settings['sSK_PATH'] = self.SKPathBox.GetValue()
		
		settings['sOB_TXT'] = self.OBpluginsBox.GetValue()
		settings['sFO_TXT'] = self.FOpluginsBox.GetValue()
		settings['sNV_TXT'] = self.NVpluginsBox.GetValue()
		settings['sSK_TXT'] = self.SKpluginsBox.GetValue()
		
		return settings
		
	def browse_file(self):
		'''Display browse box and return chosen path.'''
		path = ''
		browseBox = wx.FileDialog(self, message='Browse', defaultDir=os.environ['USERPROFILE'], wildcard='Plain text files (*.txt)|*.txt')
		
		if browseBox.ShowModal() == wx.ID_OK:
			path = browseBox.GetPath()
			browseBox.Destroy()
		return path
		
	def browse_dir(self):
		'''Display dir browse box and return chosen path.'''
		path = ''
		browseBox = wx.DirDialog(self, message='Browse', defaultPath='C:\\')
		
		if browseBox.ShowModal() == wx.ID_OK:
			path = browseBox.GetPath()
			browseBox.Destroy()
		return path
			
class SimplerHtmlWindow(wx.html.HtmlWindow):
	'''wx.html.HtmlWindow that opens hyperlinks in webbrowser.'''
	def OnLinkClicked(self, event=None):
		'''Open selected hyperlink in webbrowser.'''
		webbrowser.open_new_tab(event.GetHref())

			
class BOSSFrame(BaseFrame):
	def __init__(self, parent, title='BOSS interface', size=(750,500), defGame=modeNV):
		wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=size, style=wx.DEFAULT_FRAME_STYLE)
		self.SetIcon(wx.Icon(constants['ICO_PATH'], wx.BITMAP_TYPE_ICO))
		self.SetMinSize((700, 400))		
		self.Center()
		
		self.panel = wx.Panel(self)
		self.parent = parent
		
		subpanel = wx.Panel(self.panel, style=wx.SUNKEN_BORDER)
		self.html = SimplerHtmlWindow(subpanel)
		self.log_select = wx.ComboBox(self.panel, wx.ID_ANY, choices=['Quick links', 'New Vegas', 'Fallout 3', 'Oblivion'], style=wx.CB_READONLY)
		self.log_select.SetSelection(0)
		self.log_select.Bind(wx.EVT_COMBOBOX, self.switch_log)
		
		subpanelszr = wx.BoxSizer(wx.VERTICAL)
		subpanelszr.Add(self.html, proportion=1, flag=wx.EXPAND|wx.ALL)
		subpanel.SetSizer(subpanelszr)
		
		# Controls
		sort_btn = wx.Button(self.panel, label='Run BOSS')
		sort_btn.Bind(wx.EVT_BUTTON, self.boss_run)
		self.sort_opt = wx.ComboBox(self.panel, wx.ID_ANY, choices=['New Vegas', 'Fallout 3', 'Oblivion'], style=wx.CB_READONLY)
		if defGame == modeNV:
			self.sort_opt.SetSelection(0)
		elif defGame == modeFO:
			self.sort_opt.SetSelection(1)
		else:
			self.sort_opt.SetSelection(2)
		
		revert_btn = wx.Button(self.panel, label='Revert changes')
		revert_btn.Bind(wx.EVT_BUTTON, self.boss_revert)
		self.revert_opt = wx.ComboBox(self.panel, wx.ID_ANY, choices=['1', '2'], style=wx.CB_READONLY)
		self.revert_opt.SetSelection(0)
		
		update_btn = wx.Button(self.panel, label='Update masterlists')
		update_btn.Bind(wx.EVT_BUTTON, self.boss_update)
		
		vbox = wx.BoxSizer(wx.VERTICAL)
		
		vbox.Add(sort_btn, border=3, flag=wx.ALL|wx.EXPAND)
		vbox.Add(wx.StaticText(self.panel, label='Currently running BOSS on'), border=1, flag=wx.ALL)
		vbox.Add(self.sort_opt, border=3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
		vbox.Add(wx.StaticLine(self.panel), border=8, flag=wx.ALL|wx.EXPAND)
		
		vbox.Add(revert_btn, border=3, flag=wx.ALL|wx.EXPAND)
		vbox.Add(wx.StaticText(self.panel, label='Revert level'), border=1, flag=wx.ALL)
		vbox.Add(self.revert_opt, border=3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
		vbox.Add(wx.StaticLine(self.panel), border=8, flag=wx.ALL|wx.EXPAND)
		
		vbox.Add(update_btn, border=3, flag=wx.ALL|wx.EXPAND)
		
		vbox.Add(wx.StaticLine(self.panel), border=8, flag=wx.ALL|wx.EXPAND)
		vbox.Add(wx.StaticText(self.panel, label='Display log'), border=1, flag=wx.ALL)
		vbox.Add(self.log_select, border=3, flag=wx.LEFT|wx.RIGHT|wx.EXPAND)
		
		sizer = wx.BoxSizer()
		sizer.Add(vbox, proportion=0, border=3, flag=wx.ALL|wx.EXPAND)
		sizer.Add(subpanel, proportion=1, border=3, flag=wx.EXPAND|wx.ALL)
		
		self.panel.SetSizer(sizer)
		self.Show()
		
		self.set_log(constants['BOSS_START_PAGE'])
		
	def set_log(self, source):
		'''Set the HTML to be displayed.'''
		self.html.SetPage(source)		
		
	def switch_log(self, event=None):
		'''Handle log switch event.'''
		path = ''
		
		if self.log_select.GetCurrentSelection() == 0:
			self.set_log(constants['BOSS_START_PAGE'])
		elif self.log_select.GetCurrentSelection() == 1:
			if settings['sNV_PATH']:
				path = settings['sNV_PATH']
			else:
				self.show_error('Your settings for this game have not been set properly.')
		elif self.log_select.GetCurrentSelection() == 2:
			if settings['sFO_PATH']:
				path = settings['sFO_PATH']
			else:
				self.show_error('Your settings for this game have not been set properly.')
		elif self.log_select.GetCurrentSelection() == 3:
			if settings['sOB_PATH']:
				path = settings['sOB_PATH']
			else:
				self.show_error('Your settings for this game have not been set properly.')	
		try:
			bossexe = boss.BOSS(path)			
			log = bossexe.get_log()
			
			if log:
				self.set_log(log)
			else:
				self.set_log('BOSSLog could not be read.')		
		except boss.BOSSNotInstalledError:
			pass
		
	def boss_revert(self, event=None):
		'''Revert changes made by BOSS.'''
		level = self.revert_opt.GetCurrentSelection() + 1

		if self.sort_opt.GetCurrentSelection() == 0:
			if settings['sNV_PATH']:
				path = settings['sNV_PATH']
				self.log_select.SetSelection(1)
			else:
				self.show_error('Your settings for this game have not been set properly.')
		elif self.sort_opt.GetCurrentSelection() == 1:
			if settings['sFO_PATH']:
				path = settings['sFO_PATH']
				self.log_select.SetSelection(2)
			else:
				self.show_error('Your settings for this game have not been set properly.')
		elif self.sort_opt.GetCurrentSelection() == 2:
			if settings['sOB_PATH']:
				path = settings['sOB_PATH']
				self.log_select.SetSelection(3)
			else:
				self.show_error('Your settings for this game have not been set properly.')
				
		try:
			bossexe = boss.BOSS(path)
			bossexe.revert(level)
			
			log = bossexe.get_log()
			if log:
				self.set_log(log)
			else:
				self.set_log('BOSSLog could not be read.')
				
			self.parent.handle_refresh_all()
			self.show_message('BOSS has been run. LOST will now display the log.')
			
		except boss.BOSSNotInstalledError:
			self.show_error('You have not installed BOSS for this game.')
				
		
	def boss_update(self, event=None):
		'''Run BOSS masterlist update for all available games.'''
		res = ''
		try:
			bossexe = boss.BOSS(settings['sNV_PATH'])
			x = bossexe.update()
			if x:
				res += 'BOSS-NV masterlist was updated to revision %s\n' % x
		except:
			pass
		try:
			bossexe = boss.BOSS(settings['sFO_PATH'])
			x = bossexe.update()
			if x:
				res += 'BOSS-F masterlist was updated to revision %s\n' % x
		except:
			pass
		try:
			bossexe = boss.BOSS(settings['sOB_PATH'])
			x = bossexe.update()
			if x:
				res += 'BOSS-OB masterlist was updated to revision %s\n' % x
		except:
			pass
		
		if res:
			self.show_message(res)
		
	def boss_run(self, event=None):
		'''Run BOSS.'''
		if self.sort_opt.GetCurrentSelection() == 0:
			if settings['sNV_PATH']:
				path = settings['sNV_PATH']
				self.log_select.SetSelection(1)
			else:
				self.show_error('Your settings for this game have not been set properly.')
		elif self.sort_opt.GetCurrentSelection() == 1:
			if settings['sFO_PATH']:
				path = settings['sFO_PATH']
				self.log_select.SetSelection(2)
			else:
				self.show_error('Your settings for this game have not been set properly.')
		elif self.sort_opt.GetCurrentSelection() == 2:
			if settings['sOB_PATH']:
				path = settings['sOB_PATH']
				self.log_select.SetSelection(3)
			else:
				self.show_error('Your settings for this game have not been set properly.')
				
		try:
			bossexe = boss.BOSS(path)
			bossexe.run()
			
			log = bossexe.get_log()
			if log:
				self.set_log(log)
			else:
				self.set_log('BOSSLog could not be read.')
				
			self.parent.handle_refresh_all()
			self.show_message('BOSS has been run. LOST will now display the log.')
			
		except boss.BOSSNotInstalledError:
			self.show_error('You have not installed BOSS for this game.')
			
		
class LOSTApp(wx.App):
	'''wx.App convenience wrapper. Launches a loadorder2.MainFrame instance when initialized.'''
	def OnInit(self):
		frame = MainFrame()
		return True