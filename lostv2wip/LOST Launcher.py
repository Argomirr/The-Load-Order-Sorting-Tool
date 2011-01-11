#!usr\bin\env python


# -- DETAILS
'''Launches the LOST application.'''

__author__ = 'Argomirr (argomirr@gmail.com)'
__version__ = 'Revision: 1.0.0'
__date__ = 'Date: 2011/01/01 12:14:01'
__copyright__ = 'Copyright (c) 2010 Argomirr'


# -- IMPORTS
from traceback import print_exc
try:
	import loadorder2

	import wx


	def main():
		'''Fire up the LOST app.'''
		app = loadorder2.LOSTApp(False)
		app.MainLoop()
		
		
	if __name__ == '__main__':
			main()
except:
	print_exc()
	input('\n\n\tPress ENTER to exit...')
