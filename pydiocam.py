#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, sys, time, os
from pygame.locals import *
import pygame.camera
from pydiosdk.remote import PydioSdk
import atexit
try:
	from pydiocamconf import *
except:
	with open('pydiocamconf.py', 'w') as f:
		string = \
			'# -*- coding: UTF-8 -*-\n' + \
			'# Settings to instantiate a PydioSDK\n' + \
			'# ----------------------------------------------------------------------------\n' + \
			'server = "https://"	# Pydio server URL\n' + \
			'ws = ""				# the target workspace\n' + \
			'destfolder = ""		# optional subfolder upload target\n' + \
			'auth = ("", "")		# username, password\n' + \
			'# ----------------------------------------------------------------------------\n'
		f.write(string)
		print("Please fill your settings in the pydiocamconf.py file.")
	raise SystemExit

class Cam():
	def __init__(self):
		pygame.init()
		pygame.camera.init()
		width, height = 1280, 720
		self.cam = pygame.camera.Camera("/dev/video0", (width, height)) # 640x480
		self.cam.start()
		#self.cam.set_controls(False, False, 50) # Trying to get a brighter picture

	def snap(self, filename):
		image = self.cam.get_image()
		pygame.image.save(image, filename)

	def stop(self):
		self.cam.stop()

def nextname(base, extension):
	""" Returns the next name for a given filename base with simple increment
		Note: could be better... going through all the files in '.'
		image, .jpg -> image 1.jpg
	""" 
	maxcount = -1
	for f in os.listdir('.'):
		if f.startswith(base):
			f = f.replace(base, '')
			f = f.replace(extension, '')
			if f != '':
				nb = int(f)
				if nb > maxcount:
					maxcount = nb
			elif maxcount == -1:
				maxcount = 1
	if maxcount == -1:
		return base + extension
	else:
		return base + " " + str(maxcount + 1) + extension


def pydiocamupload():
	# Take a new picture
	filename = nextname('image', '.jpg')
	filename = os.path.abspath(filename)
	print('Snapped ' + filename)
	wcam.snap(filename)
	time.sleep(2)  # wait for file write to end
	# TODO check if exists to rename and have latest pic top and history
	realstats = os.stat(filename)
	fakestats = {'size': realstats.st_size}
	if sdk.upload(filename, fakestats, unicode(os.path.basename(filename))):
		print(filename + " -- Uploaded --> " + os.path.basename(filename))
	else:
		print("Failed to upload " + filename)

@atexit.register
def closecam():
	wcam.stop()

if __name__ == "__main__":
	wcam = Cam()
	sdk = PydioSdk(server, "uploads", '/', '', auth=auth)
	# Ensure the destination folder exists and create it if it didn't
	if not sdk.stat('/' + destfolder):
		sdk.mkdir(os.path.join('/' + destfolder))
	
	while True:
		pydiocamupload()
		time.sleep(30) # 30s

