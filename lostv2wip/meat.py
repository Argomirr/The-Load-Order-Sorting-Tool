#!usr\bin\env python

# -- DETAILS
'''Various load order and other backend operations for LOST.'''

__author__ = 'Argomirr (argomirr@gmail.com)'
__copyright__ = 'Copyright (c) 2010 Argomirr'


# -- IMPORTS
import os
import sys
import re
import glob
import struct

from iniparse import ConfigParser


# -- CONSTANTS
LO_BASE_TIMESTAMP = 1286604027.0
modeOB = 'OB'
modeNV = 'NV'
modeFO = 'FO3'


class LoadOrderError(Exception):
	'''Generic load order error class.'''
	pass
	
class TES4ModError(Exception):
	'''Generic .esp/.esm parsing error class.'''
	pass

class LoadOrder:
	'''Class representing a load order.'''
	def __init__(self, txtPath='', gameDataPath='', type=''):
		self.txtPath = txtPath
		self.gameDataPath = gameDataPath
		self.type = type
		
		self.actMasters = []
		self.actPlugins = []
		self.order = []
		self._orderTimestamped = []
		
		self.inact = []
		
	def parse(self):
		'''Parse plugins.txt and store the active plugins in memory, then retrieve load order via timestamps.'''
		if self.txtPath == '': raise LoadOrderError('Invalid file txtPath/txtPath not set')
		if self.txtPath.endswith('.txt') == False: raise LoadOrderError('Invalid file extension on txtPath')
		
		try:
			fil = open(self.txtPath, 'r')
			try:
				txt = fil.read()
			finally:
				fil.close()
		except IOError:
			raise LoadOrderError('Could not read file')
			
		self.actMasters = re.findall('.+\.{1}esm', txt, re.I)
		self.actPlugins = re.findall('.+\.{1}esp', txt, re.I)
		
		if 'Fallout3.esm' in self.actMasters:
			self.type = 'FO3'
		elif 'Oblivion.esm' in self.actMasters:
			self.type = 'OB'
		elif 'FalloutNV.esm' in self.actMasters:
			self.type = 'NV'
		else:
			self.type = 'UNKNOWN'

		self.inact = self._get_data_contents()
		
		tmpLi = []	# Put inactive mods in temporarly list first, .remove()'ing them right away causes some issues with the for loop
		for i in self.inact:
			if i in self.actMasters or i in self.actPlugins:
				tmpLi.append(i)
		for i in tmpLi:
			self.inact.remove(i)
		
		tmpList =[]
		tmpList.extend(self.actMasters)
		tmpList.extend(self.actPlugins)
		
		for i in tmpList:
			if os.path.exists(self.gameDataPath + i) == True:
				self._orderTimestamped.append((os.path.getmtime(self.gameDataPath + i), i))
			
		self._orderTimestamped.sort()
		
		for i in self._orderTimestamped:
			self.order.append(i[1])
			
	def list_to_loadorder(self, loadOrder):
		'''Take a list containing a load order and populate the LoadOrder object with it.'''
		if self.txtPath == '': raise LoadOrderError('Invalid file txtPath/txtPath not set')
		if self.txtPath.endswith('.txt') == False: raise LoadOrderError('Invalid file extension on txtPath')
		
		self.reset()
		for i in loadOrder:
			if i.endswith('.esm') or i.endswith('.ESM'):
				self.actMasters.append(i)
				self.order.append(i)
			elif i.endswith('.esp') or i.endswith('.ESP'):
				self.actPlugins.append(i)
				self.order.append(i)
			else:
				raise LoadOrderError('Invalid extenstion')
		
		if 'Fallout3.esm' in self.actMasters:
			self.type = 'FO3'
		elif 'Oblivion.esm' in self.actMasters:
			self.type = 'OB'
		elif 'FalloutNV.esm' in self.actMasters:
			self.type = 'NV'
		else:
			self.type = 'UNKNOWN'
			
		self.inact = self._get_data_contents()
		
		tmpLi = []
		for i in self.inact:
			if i in self.actMasters or i in self.actPlugins:
				tmpLi.append(i)
		for i in tmpLi:
			self.inact.remove(i)
			
	def save(self):
		'''Save the load order and any changes made to it, update timestamps.'''
		if len(self.order) <= 0: return
		if self.txtPath == '': raise LoadOrderError('Invalid file txtPath/txtPath not set')
		if self.txtPath.endswith('.txt') == False: raise LoadOrderError('Invalid file extension on txtPath')
		
		data = self._get_data_contents()
		
		tmpLi = []
		for i in self.order:
			if i not in data:
				tmpLi.append(i)
		for i in tmpLi:
			self.order.remove(i)
			
		timeInc = LO_BASE_TIMESTAMP
		for i in self.order:
			if os.path.exists(self.gameDataPath + i) == True:
				os.utime(self.gameDataPath + i, (-1, timeInc))
				timeInc += 120
			
		if os.path.exists(self.txtPath) == True:
			try:
				fil = open(self.txtPath, 'r')
				try:
					buffer = fil.read()
				finally:
					fil.close()
			except IOError:
				raise LoadOrderError('Could not read file')

			buffer = re.findall('#.+\n?', buffer)
			if buffer != []:
				buffer = ''.join(buffer)
			else:
				buffer = ''
		
		for s in self.order:
			buffer += str(s) + '\n'
			
		try:
			fil = open(self.txtPath, 'w')
			try:
				fil.write(buffer)
			finally:
				fil.close()
		except IOError:
			raise LoadOrderError('Could not write to file')
		
		
		
	def reset(self):
		'''Reset load order lists on LoadOrder object.'''
		self.actMasters = []
		self.actPlugins = []
		self.order = []
		self._orderTimestamped = []	
		self.inact = []
		
	def _get_data_contents(self):
		'''Retrieve a list of all .esps and .esms in the data folder.'''
		if self.gameDataPath == '': raise LoadOrderError('Invalid file gameDataPath/gameDataPath not set')
		con = [os.path.split(i)[1] for i in glob.glob(self.gameDataPath + '\\*.esp')]
		con.extend([os.path.split(i)[1] for i in glob.glob(self.gameDataPath + '\\*.esm')])
		return con
		
		
def get_txt_path(game=modeFO):
	'''Return the path to plugins.txt, or False if not found.'''
	if game == modeFO:
		if os.path.exists(os.environ['USERPROFILE'] + '\\AppData\\Local\\Fallout3\\plugins.txt'):
			return os.environ['USERPROFILE'] + '\\AppData\\Local\\Fallout3\\plugins.txt'
		elif os.path.exists(os.environ['USERPROFILE'] + '\\Local Settings\\Application Data\\Fallout3\\plugins.txt'):
			return os.path.exists(os.environ['USERPROFILE'] + '\\Local Settings\\Application Data\\Fallout3\\plugins.txt')
		else:
			return False
	elif game == modeNV:
		if os.path.exists(os.environ['USERPROFILE'] + '\\AppData\\Local\\FalloutNV\\plugins.txt'):
			return os.environ['USERPROFILE'] + '\\AppData\\Local\\FalloutNV\\plugins.txt'
		elif os.path.exists(os.environ['USERPROFILE'] + '\\Local Settings\\Application Data\\FalloutNV\\plugins.txt'):
			return os.path.exists(os.environ['USERPROFILE'] + '\\Local Settings\\Application Data\\FalloutNV\\plugins.txt')
		else:
			return False	
	else:
		if os.path.exists(os.environ['USERPROFILE'] + '\\AppData\\Local\\Oblivion\\plugins.txt'):
			return os.environ['USERPROFILE'] + '\\AppData\\Local\\Oblivion\\plugins.txt'
		elif os.path.exists(os.environ['USERPROFILE'] + '\\Local Settings\\Application Data\\Oblivion\\plugins.txt'):
			return os.path.exists(os.environ['USERPROFILE'] + '\\Local Settings\\Application Data\\Oblivion\\plugins.txt')
		else:
			return False
			
def get_mod_details(path):
	'''Parse the first few headers of an .esp/.esm file and return a dictionary containing the data.'''
	data = {'author':'', 'description':'', 'masters':''}
	if path.endswith('.esp') == False and path.endswith('.esm') == False: raise TES4ModError('Invalid extension')
	try:
		f = open(path, 'rb')
		try:
			hedr = f.read(4)
			if hedr != 'TES4':
				raise TES4ModError('TES4 header missing')
			else:
				f.seek(f.tell() + 16)
				hedr = f.read(4)
				if hedr != 'HEDR':
					# We're dealing with FO3 .esps here; meaning 4 more bytes until HEDR
					hedr = f.read(4)

			if hedr == 'HEDR':
				f.seek(f.tell() + 14)
				hedr = f.read(4)
			if hedr == 'CNAM':
				dataSize = struct.unpack('H', f.read(2))[0]
				data['author'] = f.read(dataSize).replace('\x00', '')
				hedr = f.read(4)
			if hedr == 'SNAM':
				dataSize = struct.unpack('H', f.read(2))[0]
				data['description'] = f.read(dataSize).replace('\x00', '')
				hedr = f.read(4)
			if hedr == 'MAST':
				dataSize = struct.unpack('H', f.read(2))[0]
				data['masters'] = f.read(dataSize).replace('\x00', '')
		finally:
			f.close()
	except IOError:
		pass

	return data
	
	
def archive_inv(gameDir, dummyPath, game='FO3', mode=True):
	'''Apply ArchiveInvalidationInvalidated.'''
	if mode:
		if game == 'NV':
			try:
				ini = ConfigParser()
				ini.read(os.environ['USERPROFILE'] + '\\My Games\\FalloutNV\\Fallout.ini')
				ini.set('Archive', 'bInvalidateOlderFiles', '1')
				ini.set('Archive', 'SArchiveList', 'Dummy.bsa,' + ini.get('Archive', 'SArchiveList'))
				
				iniFile = open(os.environ['USERPROFILE'] + '\\My Games\\FalloutNV\\Fallout.ini', 'w')
				ini.write(iniFile)
				
				bsa = open(dummyPath, 'rb').read()
				dummy = open(gameDir + '\\Data\\Dummy.bsa', 'wb')
				dummy.write(bsa)
				dummy.close()
				
				return True
			except IOError:
				return False
	
	
if __name__ == '__main__':
	pass
