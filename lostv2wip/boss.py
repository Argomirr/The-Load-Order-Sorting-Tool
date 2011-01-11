#!/usr/bin/env python

# -- DETAILS
'''Simple Python wrapper to the BOSS.exe command line interface.'''

__author__ = 'Argomirr (argomirr@gmail.com)'
__copyright__ = 'Copyright (c) 2010 Argomirr'

# BOSS is (c) the BOSS team and is not affiliated to LOST


# -- IMPORTS
import subprocess as sp
import re
import os


# -- CONSTANTS
paths = {'BOSS_PATH':'/Data/BOSS.exe',
		'BOSS_CWD':'/Data',
		'BOSS_PATH_ALT':'/Data/BOSS/BOSS.exe',	# Altertnate paths to provide support
		'BOSS_CWD_ALT':'/Data/BOSS',
		'BOSS_LOG_PATH':'/Data/BOSS/BOSSlog.html'}
		
RE_REVISION = re.compile('[0-9]+') # Will work for now


class BOSSError(Exception):
	'''Generic error class for BOSS command line operations.'''
	def __init__(self, msg='Unknown error'):
		self.value = msg
		
	def __str__(self):
		return repr(self.value)
		
class BOSSNotInstalledError(Exception):
	'''Error class in case BOSS is not installed.'''
	def __init__(self, msg='Could not locate BOSS.exe'):
		self.value = msg
		
	def __str__(self):
		return repr(self.value)

		
class BOSS:
	'''Class for interfacing with BOSS.exe through the command line.'''
	def __init__(self, gamePath):
		if os.path.exists(gamePath + paths['BOSS_PATH']):
			self.path = gamePath + paths['BOSS_PATH']
			self.cwd = gamePath + paths['BOSS_CWD']
		elif os.path.exists(gamePath + paths['BOSS_PATH_ALT']):
			self.path = gamePath + paths['BOSS_PATH_ALT']
			self.cwd = gamePath + paths['BOSS_CWD_ALT']
		else:
			raise BOSSNotInstalledError
			
		self.log = gamePath + paths['BOSS_LOG_PATH']
		
	def update(self):
		'''Run BOSS.exe with the -o argument, masterlist update only. Return masterlist revision if updated, None otherwise.'''
		arguments = [self.path, '-o', '-s']
		sub = sp.Popen(arguments, stdout=sp.PIPE, cwd=self.cwd)
		
		outpt = sub.communicate()[0] # May need to come up with a workaround... Waiting for BOSS.exe to finish can freeze the GUI if it takes too long
		rev = re.search(RE_REVISION, outpt)
		if rev:
			return rev.group(0)
		else:
			return None
		
	def revert(self, level=1):
		'''Run BOSS.exe with the -r argument, reverts changes.'''
		if not (level == 1 or level == 2): raise BOSSError('Invalid revert value')
		arguments = [self.path, '-r%s' % level,'-s']
		sub = sp.Popen(arguments, cwd=self.cwd, stdout=sp.PIPE)
		sub.wait()
		
	def run(self, update=False, versionparse=True):
		'''Run BOSS.exe regularly.'''
		arguments = [self.path, '-s']
		if not versionparse: arguments.append('-n')
		if update: arguments.append('-u')
		sub = sp.Popen(arguments, cwd=self.cwd, stdout=sp.PIPE)
		sub.wait()
		
	def get_log(self):
		'''Return the contents of BOSSLog.html.'''
		try:
			log = open(self.log, 'r')
			contents = log.read()
			log.close()
		except:
			return None
		return contents
		
if __name__ == '__main__':
	pass
