import os
import site
import sys
import shutil

detailsFile = 'DETAILS.TXT'
expectedDetailsContent = 'iCELink Firmware by MuseLab'
debug = False

if os.name == 'nt':  # sys.platform == 'win32':
	from ctypes import windll
	import string

def findDrive():
	if os.name == 'nt':
		bitmask = windll.kernel32.GetLogicalDrives()
		for letter in string.ascii_uppercase:
			if bitmask & 1:
				drive = (letter + ':\\')
				fullPath = drive + detailsFile;
				if (os.path.exists(fullPath)):
					with open(fullPath, 'r') as file:
						data = file.read()
						if (expectedDetailsContent in data):
							return drive
			bitmask >>= 1
	else:
		raise ImportError(
			"Sorry: no implementation for your platform ('{}') available".format(
				os.name
			)
		)
	return None

if __name__ == '__main__':
	try:
		if (debug):
			print('args ', sys.argv)
		path = findDrive();
		if path:
			print('iCESugar found at ' + path)
			shutil.copy2(sys.argv[1], path + '/' + sys.argv[1])
			print('Upload done!')
		else:
			raise RuntimeError('No iCESugar found')
	except Exception as err:
		if (debug):
			print('Handling run-time error:', err)
		raise err
	finally:
		if (debug):
			input("Press Enter to continue...")
