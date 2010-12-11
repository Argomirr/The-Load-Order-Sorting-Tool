#!usr\bin\env python


# -- DETAILS
__author__ = 'Argomirr (argomirr@gmail.com)'
__version__ = '$Revision: 0.9.8 $'
__date__ = '$Date: 2010/11/08 19:41:43 $'
__copyright__ = 'Copyright (c) 2010 Argomirr'


# -- IMPORTS
import wx

import loadorder


def main():
	'''Fire up the LOST app.'''
	app = wx.App(False)
	frame = loadorder.LoadOrderApp()
	app.MainLoop()

	
if __name__ == '__main__':
	main()

