#!usr\bin\env python


# -- DETAILS
'''Launches the LOST application.'''

__author__ = 'Argomirr (argomirr@gmail.com)'
__version__ = 'Revision: 1.0.0'
__date__ = 'Date: 2011/11/01 20:42:17'
__copyright__ = 'Copyright (c) 2010 Argomirr'


# -- IMPORTS
import loadorder2

import wx


def main():
	'''Fire up the LOST app.'''
	app = loadorder2.LOSTApp(False)
	app.MainLoop()
	
	
if __name__ == '__main__':
		main()

