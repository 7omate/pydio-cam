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
			'# -*- coding: UTF-8 -*-\n'															+ \
			'# Settings to instantiate a PydioSDK\n'											+ \
			'# ----------------------------------------------------------------------------\n'	+ \
			'server = "https://"	# Pydio server URL\n'										+ \
			'ws = ""				# the target workspace\n'									+ \
			'destfolder = ""		# optional subfolder upload target\n'						+ \
			'archivefolder = ""		# optional archive folder target\n'							+ \
			'auth = ("", "")		# username, password\n'										+ \
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
		self.cam.set_controls(False, False, 30) # Trying to get a brighter picture

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

def remotenextname(foldername, base, extension, sdk):
	""" Lists foldername with sdk, find out what's the next name for archive
	"""
	files = sdk.list(foldername)
	maxnb = -1
	for p in files.keys():
		p = os.path.basename(p)
		p = p.replace(base, '')
		p = p.replace(extension, '')
		try:
			nb = int(p)
			if nb > maxnb:
				maxnb = nb
		except ValueError:
			pass
	return os.path.join(foldername, base + " " + str(maxnb+1) + extension)

def pydiocam_snap_and_upload(filename, destfolder, wcam, sdk):
	# Take a new picture
	filename = os.path.abspath(filename)
	print('Snapped ' + filename)
	wcam.snap(filename)
	time.sleep(2)  # wait for file write to end
	# TODO check if exists to rename and have latest pic top and history
	realstats = os.stat(filename)
	fakestats = {'size': realstats.st_size}
	destpath = os.path.join(destfolder, os.path.basename(filename))
	if sdk.upload(filename, fakestats, unicode(destpath)):
		print(filename + " -- Uploaded --> " + destpath )
	else:
		print("Failed to upload " + filename)

def pydiocam_archive_and_upload(filename, destfolder, archivefolder, wcam, sdk):
	# MV last pic to archive folder
	lastpicpath = os.path.join(destfolder, filename)
	if sdk.stat(lastpicpath):
		archivename = remotenextname(archivefolder, "image", ".jpg", sdk)
		print("Archiving " + lastpicpath + " as " + archivename) 
		sdk.copy(lastpicpath, archivename)
	# upload new pic
	if os.path.exists(filename):
		os.unlink(filename)
	pydiocam_snap_and_upload(filename, destfolder, wcam, sdk)

	
@atexit.register
def closecam():
	wcam.stop()

if __name__ == "__main__":
	wcam = Cam()
	sdk = PydioSdk(server, ws, '', '', auth=auth)
	# Ensure the destination folder exists and create it if it didn't
	destpath = os.path.join('/', destfolder)
	if not sdk.stat(destpath):
		sdk.mkdir(destpath)
	archivepath = os.path.join('/', destfolder, archivefolder)
	if not sdk.stat(archivepath):
		sdk.mkdir(archivepath)
	while True:
		#pydiocam_snap_and_upload(nextname('image', '.jpg'), '', wcam, sdk)
		filename = "pydiocam-latest.jpg"
		pydiocam_archive_and_upload(filename, destpath, archivepath, wcam, sdk)
		time.sleep(30) # in seconds

