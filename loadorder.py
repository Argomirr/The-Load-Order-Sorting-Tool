#!usr\bin\env python

# -- DETAILS
__author__ = 'Argomirr (argomirr@gmail.com)'
__copyright__ = 'Copyright (c) 2010 Argomirr'


# -- IMPORTS
import os
import sys
import iniparse
import webbrowser
import re

import wx

import meat


# -- CONSTANTS
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500
WINDOW_TITLE = 'LOST - The Load Order Sorting Tool'
INI_PATH = '\settings.ini'
DOCS_LOC = 'http://argomirr.webs.com/py/loadorder/docs/docs.html'


class LoadOrderApp(wx.Frame):
	'''GUI framework for simple load order manager.'''
	def __init__(self):
		noResize_frameStyle = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX)
		wx.Frame.__init__(self, None, title=WINDOW_TITLE, size=(WINDOW_WIDTH, WINDOW_HEIGHT), style=noResize_frameStyle)
		self.Center()
	
		self.panel = wx.Panel(self)
		
		# Menubar
		self.menubar = wx.MenuBar()
		self.menuFile = wx.Menu()
		self.menuMode = wx.Menu()
		self.menuOptions = wx.Menu()
		self.menuAbout = wx.Menu()
		
		self.SetMenuBar(self.menubar)
		
		self.menubar.Append(self.menuFile, '&File')
		self.saveLO = self.menuFile.Append(-1, '&Save load order')
		self.reloadLO = self.menuFile.Append(-1, '&Refresh load order')
		self.importLO = self.menuFile.Append(-1, '&Import load order (.txt)')
		self.exportLO = self.menuFile.Append(-1, '&Export load order (.txt)')
		self.Bind(wx.EVT_MENU, self.saveLoadOrder, self.saveLO)
		self.Bind(wx.EVT_MENU, self.refreshLoadOrder, self.reloadLO)
		self.Bind(wx.EVT_MENU, self.importLoadOrder, self.importLO)
		self.Bind(wx.EVT_MENU, self.exportLoadOrder, self.exportLO)
		
		self.menubar.Append(self.menuMode, '&Mode')
		self.modeFO = self.menuMode.Append(-1, '&Fallout 3')
		self.modeOB = self.menuMode.Append(-1, '&Oblivion')
		self.modeNV = self.menuMode.Append(-1, '&New Vegas')
		self.Bind(wx.EVT_MENU, self.setModeFO3, self.modeFO)
		self.Bind(wx.EVT_MENU, self.setModeOB, self.modeOB)
		self.Bind(wx.EVT_MENU, self.setModeNV, self.modeNV)
		
		self.menubar.Append(self.menuOptions, '&Options')
		self.settingsItem = self.menuOptions.Append(-1, '&Settings')
		self.Bind(wx.EVT_MENU, self.showSettings, self.settingsItem)
		
		self.menubar.Append(self.menuAbout, '&Help')
		self.aboutItem = self.menuAbout.Append(-1, '&About')
		self.docsItem = self.menuAbout.Append(-1, '&Online docs')
		self.Bind(wx.EVT_MENU, self.aboutInf, self.aboutItem)
		self.Bind(wx.EVT_MENU, self.openDocs, self.docsItem)
		
		# Labels
		self.labelMode = wx.StaticText(self.panel, wx.ID_ANY, 'FALLOUT 3')
		self.labelAct = wx.StaticText(self.panel, wx.ID_ANY, ' Active mods')
		self.labelInAct = wx.StaticText(self.panel, wx.ID_ANY, ' Inactive mods')
		
		font1 = wx.Font(14, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Arial')
		self.labelMode.SetFont(font1)
	
		# Buttons + bindings
		self.up_btn = wx.Button(self.panel, wx.ID_ANY, label='Move up')
		self.dwn_btn = wx.Button(self.panel, wx.ID_ANY, label='Move down')
		self.act_btn = wx.Button(self.panel, wx.ID_ANY, label='Activate')
		self.dact_btn = wx.Button(self.panel, wx.ID_ANY, label='Deactivate')
		
		self.up_btn.Bind(wx.EVT_BUTTON, self.moveUp)
		self.dwn_btn.Bind(wx.EVT_BUTTON, self.moveDwn)
		self.act_btn.Bind(wx.EVT_BUTTON, self.setActive)
		self.dact_btn.Bind(wx.EVT_BUTTON, self.setInactive)
	
		# Lists
		self.listbox = wx.ListBox(self.panel, wx.ID_ANY, choices = [])
		self.listbox2 = wx.ListBox(self.panel, wx.ID_ANY, choices = [])
		
		self.listbox.Bind(wx.EVT_LISTBOX, self.listBoxClickLeft)
		self.listbox2.Bind(wx.EVT_LISTBOX, self.listBoxClickRight)
		
		# Description boxes
		self.authBox = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
		self.descrBox = wx.TextCtrl(self.panel, style=wx.TE_READONLY|wx.TE_MULTILINE)
		
		# Sizer
		sizer = wx.GridBagSizer(vgap=5, hgap=5)
		# pos=(row, column)  span=(rowspan, columnspan)
		
		sizer.Add(self.labelAct, pos=(0,0), flag=wx.ALL, border=1)
		sizer.Add(self.labelInAct, pos=(0,16), flag=wx.ALL, border=1)
		
		sizer.Add(self.listbox, pos=(1, 0), span=(15, 15), flag=wx.ALL|wx.EXPAND, border=5)
		
		sizer.Add(self.act_btn, pos=(1, 15), flag=wx.ALL, border=5)
		sizer.Add(self.dact_btn, pos=(2, 15), flag=wx.ALL, border=5)
		sizer.Add(self.up_btn, pos=(4, 15), flag=wx.ALL, border=5)
		sizer.Add(self.dwn_btn, pos=(5, 15), flag=wx.ALL, border=5)
		
		sizer.Add(self.listbox2, pos=(1, 16), span=(8, 15), flag=wx.ALL|wx.EXPAND, border=5)
		
		sizer.Add(self.authBox, pos=(9, 15), span=(1, 16), flag=wx.EXPAND, border=2)
		sizer.Add(self.descrBox, pos=(10, 15), span=(7, 16), flag=wx.EXPAND, border=2)
		
		sizer.Add(self.labelMode, pos=(16,0), flag=wx.ALL, border=3)
		
		
		# Other stuff
		self.Bind(wx.EVT_CLOSE, self.onCloseWindow)
		self.panel.SetSizer(sizer)
		self.panel.Fit()
		self.Show()
		
		# Settings
		self.cwd = os.getcwd()
		self.defaultMode = 'FO3'
		self.readINISettings()
		
		if self.firstRun == True:
			self.showSettings(None)
		else:
			try:
				self.setMode(self.defaultMode)
			except:
				pass

		
	# - Events
	def openDocs(self, event):
		'''Open the documentation for this app in browser.'''
		webbrowser.open_new_tab(DOCS_LOC)
		
	def onCloseWindow(self, event):
		'''Handle EVT_CLOSE.'''
		if self.saveOnExit:
			try:
				self.saveLoadOrder(None)
			except:
				pass
		self.Destroy()
		sys.exit(0)
			
	def showSettings(self, event):
		'''Invoke settings frame.'''
		wndw = SettingsPanel(parent=self, callOnExit=self.readINISettings, defaults={'defaultMode':self.defaultMode,
																					'showDescr':self.showDescr,
																					'saveOnExit':self.saveOnExit,
																					'firstRun':self.firstRun,
																					'FOPath':self.FOPath,
																					'OBPath':self.OBPath,
																					'NVPath':self.NVPath,
																					'OBpluginsTXT':self.OBpluginsTXT,
																					'FOpluginsTXT':self.FOpluginsTXT,
																					'NVpluginsTXT':self.NVpluginsTXT,
																					'cwd':self.cwd})

	def moveDwn(self, event):
		'''Move the curruntly selected (active mod) item up. (Down in the list)'''
		selected = self.getSelectedLeft()
		if selected == None: return False
		actOrder = self.getActList()
		if actOrder.index(selected) != len(actOrder) - 1:
			i = actOrder.index(selected)
			actOrder[i], actOrder[i + 1] = actOrder[i + 1], actOrder[i]
			self.listbox.Clear()
			for s in actOrder:
				self.listbox.Append(s)
			self.listbox.SetSelection(i + 1)
			return True
	
	def moveUp(self, event):
		'''Move the curruntly selected (active mod) item down. (Up in the list)'''
		selected = self.getSelectedLeft()
		if selected == None: return False
		actOrder = self.getActList()
		if actOrder.index(selected) != 0:
			i = actOrder.index(selected)
			actOrder[i], actOrder[i - 1] = actOrder[i - 1], actOrder[i]
			self.listbox.Clear()
			for s in actOrder:
				self.listbox.Append(s)
			self.listbox.SetSelection(i - 1)
			return True
		
	def setActive(self, event):
		'''Set an item active.'''
		if self.getSelectedRight() != None:
			selected = self.getSelectedRight()
			oldlist = self.getInActList()
			oldlist.remove(selected)
			self.listbox2.Clear()
			for s in oldlist:
				self.listbox2.Append(s)
			self.listbox.Append(selected)
			self.listbox.SetSelection(len(self.getActList()) - 1)
			return True
		else:
			return False
			
	def setInactive(self, event):
		'''Set an item inactive.'''
		if self.getSelectedLeft() != None:
			selected = self.getSelectedLeft()
			oldlist = self.getActList()
			oldlist.remove(selected)
			self.listbox.Clear()
			for s in oldlist:
				self.listbox.Append(s)
			newlist = self.getInActList()
			newlist.append(selected)
			newlist.sort()
			self.listbox2.Clear()
			for s in newlist:
				self.listbox2.Append(s)
			return True
		else:
			return False
			
	def aboutInf(self, event):
		'''Display some information related to the program.'''
		about = '''LOST revision 0.9.8\n(c) 2010 Argomirr\n\n\n Designed for Python 2.6.6 & wxPython 2.8.11.0'''
		aboutBox = wx.MessageDialog(self, caption='About', message=about, style=wx.ICON_INFORMATION|wx.STAY_ON_TOP|wx.OK)
		
		if aboutBox.ShowModal() == wx.ID_OK:
			aboutBox.Destroy()

	def refreshLoadOrder(self, event):
		'''Refresh values in the listboxes.'''
		try:
			if self.mode == 'FO3':
				if self.FOpluginsTXT == '' or self.FOPath == '':
					self.showErrorBox('Could not refresh load order. Check if your settings are correct.')
					return
				loObj = meat.LoadOrder(self.FOpluginsTXT, self.FOPath + '\\Data\\', self.mode)
			elif self.mode == 'NV':
				if self.NVpluginsTXT == '' or self.NVPath == '':
					self.showErrorBox('Could not refresh load order. Check if your settings are correct.')
					return
				loObj = meat.LoadOrder(self.NVpluginsTXT, self.NVPath + '\\Data\\', self.mode)
			else:
				if self.OBpluginsTXT == '' or self.OBPath == '':
					self.showErrorBox('Could not refresh load order. Check if your settings are correct.')
					return
				loObj = meat.LoadOrder(self.OBpluginsTXT, self.OBPath + '\\Data\\', self.mode)
		except meat.LoadOrderError:
			self.showErrorBox('Could not refresh load order. Check if your settings are correct.')
		
		loObj.parse()
		
		mods = loObj.inact
		mods.sort()
		
		self.listbox.Clear()
		self.listbox2.Clear()
		for s in mods:
			self.listbox2.Append(s)
		for s in loObj.order:
			self.listbox.Append(s)
		else:
			return False
		
				
	def saveLoadOrder(self, event):
		'''Save the load order to plugins.txt.'''
		try:
			loadorder = self.getActList()
			if self.mode == 'FO3':
				loObj = meat.LoadOrder(self.FOpluginsTXT, self.FOPath + '\\Data\\', self.mode)
			elif self.mode == 'NV':
				loObj = meat.LoadOrder(self.NVpluginsTXT, self.NVPath + '\\Data\\', self.mode)
			else:
				loObj = meat.LoadOrder(self.OBpluginsTXT, self.OBPath + '\\Data\\', self.mode)
			loObj.listToLoadOrder(loadorder)
			loObj.save()
		except meat.LoadOrderError:
			self.showErrorBox('Could not save load order. Check if your settings are correct, or if UAC is preventing the program from making the necessary changes.')
			
	def importLoadOrder(self, event):
		'''Import load order from a .txt file.'''
		loadBox = wx.FileDialog(self, message='Open', defaultDir=os.getcwd(), defaultFile='', style=wx.FD_OPEN, wildcard='Plain text files (*.txt)|*.txt')
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
		self.listbox.Clear()
		self.listbox2.Clear()
		if plugins != []:
			loadorder = self.getActList()
			if self.mode == 'FO3':
				loObj = meat.LoadOrder(self.FOpluginsTXT, self.FOPath + '\\Data\\', self.mode)
			elif self.mode == 'NV':
				loObj = meat.LoadOrder(self.NVpluginsTXT, self.NVPath + '\\Data\\', self.mode)
			else:
				loObj = meat.LoadOrder(self.OBpluginsTXT, self.OBPath + '\\Data\\', self.mode)
			loObj.listToLoadOrder(plugins)

			for s in loObj.order:
				self.listbox.Append(s)
				
			for s in loObj.inact:
				self.listbox2.Append(s)
				
	def exportLoadOrder(self, event):
		'''Export load order to a .txt file.'''
		saveBox = wx.FileDialog(self, message='Save', defaultDir=os.getcwd(), defaultFile='', style=wx.FD_SAVE, wildcard='Plain text files (*.txt)|*.txt')
		if saveBox.ShowModal() == wx.ID_OK:
			path = saveBox.GetPath()
			try:
				fil = open(path, 'w')
				try:
					for s in self.getActList():
						fil.write(s + '\n')
				finally:
					fil.close()
			except IOError:
				self.showErrorBox('Could not save txt file. Check if UAC is preventing the program from writing to that location.')

				
		saveBox.Destroy()
		
	def setModeFO3(self, event):
		'''Set mode to FO3 editing (loads up FO3 load order).'''
		self.setMode('FO3')
		
	def setModeOB(self, event):
		'''Set mode to FO3 editing (loads up FO3 load order).'''
		self.setMode('OB')
		
	def setModeNV(self, event):
		'''Set mode to NV editing (loads up NV load order).'''
		self.setMode('NV')
		
	def listBoxClickLeft(self, event):
		'''Handle clicks (update description) for left box.'''
		self.updateDescr(self.getSelectedLeft())
		
	def listBoxClickRight(self, event):
		'''Handle clicks (update description) for right box.'''
		self.updateDescr(self.getSelectedRight())
		
	# - Backend functionality
	def showErrorBox(self, errorMessage=''):
		'''Display an error box.'''
		msg = 'An error was encountered:\n' + errorMessage
		errorBox = wx.MessageDialog(self, caption='Error', message=msg, style=wx.ICON_ERROR|wx.STAY_ON_TOP|wx.OK)
		
		if errorBox.ShowModal() == wx.ID_OK:
			errorBox.Destroy()

	def readINISettings(self):
		'''Read INI file and set internal settings.'''
		try:
			ini = iniparse.ConfigParser()
			ini.read(self.cwd + INI_PATH)
			
			self.defaultMode = ini.get('General', 'DefaultGame')
			self.showDescr = ini.getboolean('General', 'ShowDescriptions')
			self.saveOnExit = ini.getboolean('General', 'SaveOnExit')
			self.firstRun = ini.getboolean('General', 'FirstRun')
			
			self.FOPath = ini.get('Paths', 'FO3Path')
			self.OBPath = ini.get('Paths', 'OBPath')
			self.NVPath = ini.get('Paths', 'NVPath')
			
			self.OBpluginsTXT = ini.get('Paths', 'OBPluginPath')
			self.FOpluginsTXT = ini.get('Paths', 'FO3PluginPath')
			self.NVpluginsTXT = ini.get('Paths', 'NVPluginPath')
		except:
			self.showErrorBox('Failed to read ini. Check if the file is misssing or damaged.')
		
	def updateDescr(self, modName):
		'''Update the author and description to display details of last selected mod.'''
		if self.showDescr == False: return
		try:
			if self.mode == 'FO3':
				res = meat.getModDetails(self.FOPath + '\\Data\\' + modName)
			elif self.mode == 'NV':
				res = meat.getModDetails(self.NVPath + '\\Data\\' + modName)
			else:
				res = meat.getModDetails(self.OBPath + '\\Data\\' + modName)
				
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
		
	def setMode(self, mode):
		'''Set mode as specified.'''
		if mode == 'FO3':
			self.mode = 'FO3'
			self.labelMode.SetLabel('FALLOUT 3')
			self.refreshLoadOrder(None)
		elif mode == 'NV':
			self.mode = 'NV'
			self.labelMode.SetLabel('NEW VEGAS')
			self.refreshLoadOrder(None)
		else:
			self.mode = 'OB'
			self.labelMode.SetLabel('OBLIVION')
			self.refreshLoadOrder(None)
			
	def getActList(self):
		'''Return contents of the left list, containing active mods.'''
		return self.listbox.GetItems()
	
	def getInActList(self):
		'''Return contents of the right list, containing inactive mods.'''
		return self.listbox2.GetItems()
		
	def getSelectedLeft(self):
		'''Return the selected item in left list, None otherwise.'''
		if self.listbox.GetStringSelection() == '':
			return None
		else:
			return self.listbox.GetStringSelection()
			
	def getSelectedRight(self):
		'''Return the selected item in right list, None otherwise.'''
		if self.listbox2.GetStringSelection() == '':
			return None
		else:
			return self.listbox2.GetStringSelection()
			
class SettingsPanel(wx.Frame):
	'''Panel for modifying INI settings.'''
	def __init__(self, parent, callOnExit, panelTitle='Settings', panelSize=(280,380), defaults={}):
		self.callOnExit = callOnExit

		frameStyle = wx.DEFAULT_FRAME_STYLE ^ (wx.RESIZE_BORDER | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX)
		wx.Frame.__init__(self, parent, wx.ID_ANY, panelTitle, size=panelSize, style=frameStyle)
		
		self.Center()
		
		self.backgrnd = wx.Panel(self)
		
		# Default game
		self.gameChoicesOptions = ['Fallout 3', 'Oblivion', 'New Vegas']
		self.gameBox = wx.RadioBox(self.backgrnd, wx.ID_ANY, 'Default game', choices=self.gameChoicesOptions, style=wx.VERTICAL)
		if defaults['defaultMode'] == 'FO3':
			self.gameBox.SetSelection(0)
		elif defaults['defaultMode'] == 'OB':
			self.gameBox.SetSelection(1)
		else:
			self.gameBox.SetSelection(2)
		
		# Various
		self.saveBox = wx.RadioBox(self.backgrnd, wx.ID_ANY, 'Save on exit', choices=['No', 'Yes'], style=wx.VERTICAL)
		self.descrBox = wx.RadioBox(self.backgrnd, wx.ID_ANY, 'Show descriptions', choices=['No', 'Yes'], style=wx.VERTICAL)
		if defaults['saveOnExit'] == True:
			self.saveBox.SetSelection(1)
		else:
			self.saveBox.SetSelection(0)
			
		if defaults['showDescr'] == True:
			self.descrBox.SetSelection(1)
		else:
			self.descrBox.SetSelection(0)
		
		# Paths
		# Oblivion
		self.label1 = wx.StaticText(self.backgrnd, wx.ID_ANY, label=' Oblivion path')
		self.OBPathBox = wx.TextCtrl(self.backgrnd, style=wx.TE_PROCESS_ENTER)
		self.OBPathBox.SetValue(defaults['OBPath'])
		self.OBbrowseBtn = wx.Button(self.backgrnd, label='Browse')
		self.OBbrowseBtn.Bind(wx.EVT_BUTTON, self.OBbrowse1)
		
		self.label2 = wx.StaticText(self.backgrnd, wx.ID_ANY, label=' Oblivion plugins.txt')
		self.OBpluginsBox = wx.TextCtrl(self.backgrnd, style=wx.TE_PROCESS_ENTER)
		self.OBpluginsBox.SetValue(defaults['OBpluginsTXT'])
		self.OBsearchBtn = wx.Button(self.backgrnd, label='Auto')
		self.OBsearchBtn.Bind(wx.EVT_BUTTON, self.OBpluginsPathSearch)
		self.OBbrowseBtn2 = wx.Button(self.backgrnd, label='Browse')
		self.OBbrowseBtn2.Bind(wx.EVT_BUTTON, self.OBbrowse2)
		
		# Fallout 3
		self.label3 = wx.StaticText(self.backgrnd, wx.ID_ANY, label=' Fallout 3 path')
		self.FOPathBox = wx.TextCtrl(self.backgrnd, style=wx.TE_PROCESS_ENTER)
		self.FOPathBox.SetValue(defaults['FOPath'])
		self.FObrowseBtn = wx.Button(self.backgrnd, label='Browse')
		self.FObrowseBtn.Bind(wx.EVT_BUTTON, self.FObrowse1)
		
		self.label4 = wx.StaticText(self.backgrnd, wx.ID_ANY, label=' Fallout 3 plugins.txt')
		self.FOpluginsBox = wx.TextCtrl(self.backgrnd, style=wx.TE_PROCESS_ENTER)
		self.FOpluginsBox.SetValue(defaults['FOpluginsTXT'])
		self.FOsearchBtn = wx.Button(self.backgrnd, label='Auto')
		self.FOsearchBtn.Bind(wx.EVT_BUTTON, self.FOpluginsPathSearch)
		self.FObrowseBtn2 = wx.Button(self.backgrnd, label='Browse')
		self.FObrowseBtn2.Bind(wx.EVT_BUTTON, self.FObrowse2)
		
		# New Vegas
		self.label5 = wx.StaticText(self.backgrnd, wx.ID_ANY, label=' New Vegas path')
		self.NVPathBox = wx.TextCtrl(self.backgrnd, style=wx.TE_PROCESS_ENTER)
		self.NVPathBox.SetValue(defaults['NVPath'])
		self.NVbrowseBtn = wx.Button(self.backgrnd, label='Browse')
		self.NVbrowseBtn.Bind(wx.EVT_BUTTON, self.NVbrowse1)
		
		self.label6 = wx.StaticText(self.backgrnd, wx.ID_ANY, label=' New Vegas plugins.txt')
		self.NVpluginsBox = wx.TextCtrl(self.backgrnd, style=wx.TE_PROCESS_ENTER)
		self.NVpluginsBox.SetValue(defaults['NVpluginsTXT'])
		self.NVsearchBtn = wx.Button(self.backgrnd, label='Auto')
		self.NVsearchBtn.Bind(wx.EVT_BUTTON, self.NVpluginsPathSearch)
		self.NVbrowseBtn2 = wx.Button(self.backgrnd, label='Browse')
		self.NVbrowseBtn2.Bind(wx.EVT_BUTTON, self.NVbrowse2)
		
		self.exitBtn = wx.Button(self.backgrnd, label='Save')
		self.exitBtn.Bind(wx.EVT_BUTTON, self.exit)
		
		
		# Sizers
		# General settings
		self.hBox1 = wx.BoxSizer()
		self.hBox1.Add(self.gameBox, proportion=0, flag=wx.EXPAND, border=3)
		self.hBox1.Add(self.saveBox, proportion=0, flag=wx.EXPAND, border=3)
		self.hBox1.Add(self.descrBox, proportion=0, flag=wx.EXPAND, border=3)
		
		# Oblivion settings
		self.hBox2 = wx.BoxSizer()
		self.hBox2.Add(self.OBPathBox, proportion=3, flag=wx.EXPAND)
		self.hBox2.Add(self.OBbrowseBtn, proportion=0)
		
		self.hBox3 = wx.BoxSizer()
		self.hBox3.Add(self.OBpluginsBox, proportion=3, flag=wx.EXPAND)
		self.hBox3.Add(self.OBsearchBtn, proportion=0)
		self.hBox3.Add(self.OBbrowseBtn2, proportion=0)
		
		# FO settings
		self.hBox4 = wx.BoxSizer()
		self.hBox4.Add(self.FOPathBox, proportion=3, flag=wx.EXPAND)
		self.hBox4.Add(self.FObrowseBtn, proportion=0)
		
		self.hBox5 = wx.BoxSizer()
		self.hBox5.Add(self.FOpluginsBox, proportion=3, flag=wx.EXPAND)
		self.hBox5.Add(self.FOsearchBtn, proportion=0)
		self.hBox5.Add(self.FObrowseBtn2, proportion=0)
		
		# NV settings
		self.hBox6 = wx.BoxSizer()
		self.hBox6.Add(self.NVPathBox, proportion=3, flag=wx.EXPAND)
		self.hBox6.Add(self.NVbrowseBtn, proportion=0)
		
		self.hBox7 = wx.BoxSizer()
		self.hBox7.Add(self.NVpluginsBox, proportion=3, flag=wx.EXPAND)
		self.hBox7.Add(self.NVsearchBtn, proportion=0)
		self.hBox7.Add(self.NVbrowseBtn2, proportion=0)

		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.hBox1, flag=wx.EXPAND, border=5)
		self.sizer.Add(self.label1, border=5)
		self.sizer.Add(self.hBox2, border=3, flag=wx.EXPAND)
		self.sizer.Add(self.label2, border=5)
		self.sizer.Add(self.hBox3, border=3, flag=wx.EXPAND)
		self.sizer.Add(self.label3, border=5)
		self.sizer.Add(self.hBox4, border=3, flag=wx.EXPAND)
		self.sizer.Add(self.label4, border=5)
		self.sizer.Add(self.hBox5, border=3, flag=wx.EXPAND)
		
		self.sizer.Add(self.label5, border=5)
		self.sizer.Add(self.hBox6, border=3, flag=wx.EXPAND)
		self.sizer.Add(self.label6, border=5)
		self.sizer.Add(self.hBox7, border=3, flag=wx.EXPAND)
		
		self.sizer.Add(wx.StaticText(self.backgrnd, wx.ID_ANY, label=' '))
		self.sizer.Add(self.exitBtn, proportion=1, flag=wx.EXPAND)
		
		
		self.backgrnd.SetSizer(self.sizer)
		
		self.Show()
		
		# To prevent the os.getcwd() issues, or at least till I have a better fix
		self.cwd = defaults['cwd']
		
	# - Events
	def OBpluginsPathSearch(self, event):
		'''Try to determine OB plugins.txt path and paste it into the box.'''
		if meat.getPluginsTXTPath('OB'):
			self.OBpluginsBox.SetValue(meat.getPluginsTXTPath('OB'))
		else:
			self.OBpluginsBox.SetValue('')
			
	def FOpluginsPathSearch(self, event):
		'''Try to determine OB plugins.txt path and paste it into the box.'''
		if meat.getPluginsTXTPath('FO3'):
			self.FOpluginsBox.SetValue(meat.getPluginsTXTPath('FO3'))
		else:
			self.FOpluginsBox.SetValue('')
			
	def NVpluginsPathSearch(self, event):
		'''Try to determine NV plugins.txt path and paste it into the box.'''
		if meat.getPluginsTXTPath('NV'):
			self.NVpluginsBox.SetValue(meat.getPluginsTXTPath('NV'))
		else:
			self.NVpluginsBox.SetValue('')
			
	def OBbrowse1(self, event):
		'''Browse for Oblivion directory.'''
		self.OBPathBox.SetValue(self.browseDir())
		
	def OBbrowse2(self, event):
		'''Browse for Oblivion plugins.txt.'''
		self.OBpluginsBox.SetValue(self.browseFile())
		
	def FObrowse1(self, event):
		'''Browse for Fallout 3 directory.'''
		self.FOPathBox.SetValue(self.browseDir())
		
	def FObrowse2(self, event):
		'''Browse for Fallout 3 plugins.txt.'''
		self.FOpluginsBox.SetValue(self.browseFile())
		
	def NVbrowse1(self, event):
		'''Browse for New Vegas directory.'''
		self.NVPathBox.SetValue(self.browseDir())
		
	def NVbrowse2(self, event):
		'''Browse for New Vegas plugins.txt.'''
		self.NVpluginsBox.SetValue(self.browseFile())
		
	def exit(self, event):
		'''Save data to INI and destroy frame.'''
		ini = iniparse.ConfigParser()
		ini.read(self.cwd + INI_PATH)
		print os.getcwd()
		if self.gameBox.GetSelection() == 0:
			ini.set('General', 'DefaultGame', 'FO3')
		elif self.gameBox.GetSelection() == 1:
			ini.set('General', 'DefaultGame', 'OB')
		else:
			ini.set('General', 'DefaultGame', 'NV')
		
		ini.set('General', 'ShowDescriptions', self.descrBox.GetSelection())
		ini.set('General', 'SaveOnExit', self.saveBox.GetSelection())
		ini.set('General', 'FirstRun', 0)
		
		ini.set('Paths', 'FO3Path', self.FOPathBox.GetValue())
		ini.set('Paths', 'FO3PluginPath', self.FOpluginsBox.GetValue())
		ini.set('Paths', 'OBPath', self.OBPathBox.GetValue())
		ini.set('Paths', 'OBPluginPath', self.OBpluginsBox.GetValue())
		ini.set('Paths', 'NVPath', self.NVPathBox.GetValue())
		ini.set('Paths', 'NVPluginPath', self.NVpluginsBox.GetValue())
		
		try:
			fil = open(self.cwd + INI_PATH, 'w')
			try:
				ini.write(fil)
			finally:
				fil.close()
		except IOError:
			self.showErrorBox('Failed to open settings.ini. Check if the file is misssing or damaged.')
		
		self.callOnExit()
		self.Destroy()
	
	# - Backend functionality
	def browseFile(self):
		'''Display browse box and return chosen path.'''
		path  = ''
		browseBox = wx.FileDialog(self, message='Browse', defaultDir=os.environ['USERPROFILE'])
		
		if browseBox.ShowModal() == wx.ID_OK:
			path = browseBox.GetPath()
		browseBox.Destroy()
		return path
		
	def browseDir(self):
		'''Display dir browse box and return chosen path.'''
		path  = ''
		browseBox = wx.DirDialog(self, message='Browse', defaultPath='C:\\')
		
		if browseBox.ShowModal() == wx.ID_OK:
			path = browseBox.GetPath()
		browseBox.Destroy()
		return path

	def showErrorBox(self, errorMessage=''):
		'''Display an error box.'''
		msg = 'An error was encountered:\n' + errorMessage
		errorBox = wx.MessageDialog(self, caption='Error', message=msg, style=wx.ICON_ERROR|wx.STAY_ON_TOP|wx.OK)
		
		if errorBox.ShowModal() == wx.ID_OK:
			errorBox.Destroy()
		

if __name__ == '__main__':
	pass
	
# i8~4Q40HiY4
# (0Hie
# o^^ndE?o?