#!usr\bin\env python

# -- DETAILS
'''GUI code for the Load Order Sorting Tool package.'''

__author__ = 'Argomirr (argomirr@gmail.com)'
__copyright__ = 'Copyright (c) 2010 Argomirr'


# -- IMPORTS
import os
import sys
import re
import webbrowser

import iniparse
import wx

import meat


# -- CONSTANTS
constants = {'WINDOW_HEIGHT':600,
			'WINDOW_WIDTH':800,
			'WINDOW_TITLE':'The Load Order Sorting Tool',
			'DOCS_LOC':'http://argomirr.webs.com/py/loadorder/docs/docs.html',
			'ABOUT':'LOST revision 1.0.0\n(c) 2010 Argomirr\n\n\nDesigned for Python 2.6.6 & wxPython 2.8.11.0',
			'INI_PATH':os.getcwd() + '/settings.ini',
			'ICO_PATH':os.getcwd() + '/lost.ico',
			'LOST_DIR':os.getcwd()}
			
modeOB = 'OB'
modeNV = 'NV'
modeFO = 'FO3'


# -- GUI
class UndefPanel(wx.Panel):
	'''Panel class for panel displayed when settings have not been configured.'''
	def __init__(self, parent, id=wx.ID_ANY):
		wx.Panel.__init__(self, parent, id)
		szr = wx.BoxSizer(wx.VERTICAL)
		szr.Add(wx.StaticText(self, wx.ID_ANY, 'It appears you have not configured your settings for this game.', style=wx.ALIGN_CENTER), flag=wx.EXPAND|wx.ALIGN_CENTER)
		self.SetSizer(szr)
		
		
class LoadOrderPanel(wx.Panel):
	'''Panel class for load order editing GUI.'''
	def __init__(self, parent, id=wx.ID_ANY):
		wx.Panel.__init__(self, parent, id)
		
		self.actLi = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
		self.inactLi = wx.ListCtrl(self, wx.ID_ANY, style=wx.LC_REPORT)
		
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
		
		# First vsizer
		vszr1 = wx.BoxSizer(wx.VERTICAL)
		vszr1.Add(wx.StaticText(self, wx.ID_ANY, 'Active mods'), border=3, flag=wx.ALL|wx.EXPAND)
		vszr1.Add(self.actLi, proportion=1, border=3, flag=wx.ALL|wx.EXPAND)
		
		# Second vsizer
		vszr2 = wx.BoxSizer(wx.VERTICAL)
		vszr2.Add(wx.StaticText(self, wx.ID_ANY, 'Inactive mods'), border=3, flag=wx.ALL|wx.EXPAND)
		vszr2.Add(self.inactLi, proportion=1, border=3, flag=wx.ALL|wx.EXPAND)
		
		# Buttons
		top_btn = wx.Button(self, wx.ID_ANY, label='Top')
		up_btn = wx.Button(self, wx.ID_ANY, label='Move up')
		dwn_btn = wx.Button(self, wx.ID_ANY, label='Move down')
		btm_btn = wx.Button(self, wx.ID_ANY, label='Bottom')
		
		act_btn = wx.Button(self, wx.ID_ANY, label='Activate')
		dact_btn = wx.Button(self, wx.ID_ANY, label='Deactivate')
		
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
		
		self.SetSizer(sizer)


	def set_mod_count(self, count):
		'''Update displayed mod count.'''
		self._mcount.SetLabel('Active mod limit: %s/256' % count)
		if count > 256:
			self._mcount.SetForegroundColour(wx.RED)
		else:
			self._mcount.SetForegroundColour(wx.BLACK)
			
	
class MainFrame(wx.Frame):
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
			menuAbout = wx.Menu()
			
			self.SetMenuBar(self.menubar)
			
			self.menubar.Append(menuFile, '&File')
			saveLO = menuFile.Append(wx.ID_ANY, '&Save load order')
			reloadLO = menuFile.Append(wx.ID_ANY, '&Refresh load order')
			menuFile.AppendSeparator()
			importLO = menuFile.Append(wx.ID_ANY, '&Import load order (.txt)')
			exportLO = menuFile.Append(wx.ID_ANY, '&Export load order (.txt)')
		#	self.Bind(wx.EVT_MENU, self.saveLoadOrder, saveLO)
		#	self.Bind(wx.EVT_MENU, self.refreshLoadOrder, reloadLO)
		#	self.Bind(wx.EVT_MENU, self.importLoadOrder, importLO)
		#	self.Bind(wx.EVT_MENU, self.exportLoadOrder, exportLO)
			
			self.menubar.Append(menuOptions, '&Options')
			settingsItem = menuOptions.Append(wx.ID_ANY, '&Settings')
		#	self.Bind(wx.EVT_MENU, self.showSettings, settingsItem)
			
			self.menubar.Append(menuAbout, '&Help')
			aboutItem = menuAbout.Append(wx.ID_ANY, '&About')
			docsItem = menuAbout.Append(wx.ID_ANY, '&Online docs')
			self.Bind(wx.EVT_MENU, self.show_about, aboutItem)
			self.Bind(wx.EVT_MENU, self.show_docs, docsItem)
		
		def _init_notebook():
			self.notebook = wx.Notebook(self, wx.ID_ANY, style=wx.NB_TOP)
			
			if self.settings['sNV_PATH'] and self.settings['sNV_TXT']:
				self.panelNV = LoadOrderPanel(self.notebook)
			else:
				self.panelNV = UndefPanel(self.notebook)
			if self.settings['sFO_PATH'] and self.settings['sFO_TXT']:
				self.panelFO = LoadOrderPanel(self.notebook)
			else:
				self.panelFO = UndefPanel(self.notebook)
			if self.settings['sOB_PATH'] and self.settings['sOB_TXT']:
				self.panelOB = LoadOrderPanel(self.notebook)
			else:
				self.panelOB = UndefPanel(self.notebook)
			
			self.notebook.AddPage(self.panelNV, 'New Vegas')
			self.notebook.AddPage(self.panelFO, 'Fallout 3')
			self.notebook.AddPage(self.panelOB, 'Oblivion')
			
		def _init_panels():
			pass
		
		_init_menubar()
		_init_notebook()
		
		self.Show()
		
	# Backend
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
			self.settings = {}
			
			ini = iniparse.ConfigParser()
			ini.read(constants['INI_PATH'])
			
			self.settings['sDEF_MODE'] = ini.get('General', 'DefaultGame')
			self.settings['bSHOW_DESCR'] = ini.getboolean('General', 'ShowDescriptions')
			self.settings['bSAVE_EXIT'] = ini.getboolean('General', 'SaveOnExit')
			self.settings['bFIRST_RUN'] = ini.getboolean('General', 'FirstRun')
			
			self.settings['sFO_PATH'] = ini.get('Paths', 'FO3Path')
			self.settings['sOB_PATH'] = ini.get('Paths', 'OBPath')
			self.settings['sNV_PATH'] = ini.get('Paths', 'NVPath')
			
			self.settings['sOB_TXT'] = ini.get('Paths', 'OBPluginPath')
			self.settings['sFO_TXT'] = ini.get('Paths', 'FO3PluginPath')
			self.settings['sNV_TXT'] = ini.get('Paths', 'NVPluginPath')
		except:
			self.show_error('Failed to read ini. Check if the file is misssing or damaged.')
			
	def show_error(self, error=''):
		'''Display an error message.'''
		msg = 'An error was encountered:\n' + error
		errorBox = wx.MessageDialog(self, caption='Error', message=msg, style=wx.ICON_ERROR|wx.STAY_ON_TOP|wx.OK)
		
		if errorBox.ShowModal() == wx.ID_OK:
			errorBox.Destroy()
		
		
class LOSTApp(wx.App):
	'''wx.App convenience wrapper. Launches a loadorder.MainFrame instance when initialized.'''
	def OnInit(self):
		frame = MainFrame()
		return True