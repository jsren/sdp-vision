import cv2
import subprocess
def nothing(x): 
	pass

class GUI:

	def __init__(self, pitch):
		self.frame = None


		# create GUI
		# The first numerical value is the starting point for the vision feed
		if pitch == 0:
			cv2.namedWindow('frame2')
			cv2.createTrackbar('bright','frame2',180,255,nothing)
			cv2.createTrackbar('contrast','frame2',120,127,nothing)
			cv2.createTrackbar('color','frame2',80,255,nothing)
			cv2.createTrackbar('hue','frame2',5,30,nothing)
			cv2.createTrackbar('Red Balance','frame2',5,20,nothing)
			cv2.createTrackbar('Blue Balance','frame2',0,20,nothing)
			cv2.createTrackbar('Gaussian blur','frame2',1,1,nothing)

		if pitch == 1:
			cv2.namedWindow('frame2')
			cv2.createTrackbar('bright','frame2',23000,40000,nothing)
			cv2.createTrackbar('contrast','frame2',28000,40000,nothing)
			cv2.createTrackbar('color','frame2',65000,100000,nothing)
			cv2.createTrackbar('hue','frame2',38000,60000,nothing)
			cv2.createTrackbar('Gaussian blur','frame2',1,1,nothing)



	def drawGUI(self):
		video0_new = {"bright": cv2.getTrackbarPos('bright', 'frame2'), "contrast": cv2.getTrackbarPos('contrast','frame2'), 
		"color": cv2.getTrackbarPos('color','frame2'), "hue": cv2.getTrackbarPos('hue', 'frame2'),
		"Red Balance": cv2.getTrackbarPos('Red Balance', 'frame2'), "Blue Balance" : cv2.getTrackbarPos('Blue Balance', 'frame2')}



		video0_old = {}
		attributes = ["bright", "contrast", "color", "hue", "Red Balance", "Blue Balance"]
		unknowns = []
		for attr in attributes:
			output, err = subprocess.Popen(["v4lctl", "show", attr],
								 stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			if not output.strip():
				print "[WARNING] Unknown video attribute '"+attr+"'"
				unknowns.append(attr)
			else:
				video0_old[attr] = int(output[len(attr)+1:])
				if video0_old[attr] != video0_new[attr]:
					p = subprocess.Popen(["v4lctl", "setattr", attr, str(video0_new[attr])], stdout=subprocess.PIPE)
					output, _ = p.communicate()

		# will only output restore file if any value was different.
		# this also prevents from resetting the file on each run
		# to run this bash file, cd to out main dir (where the .sh file is)
		# type "chmod 755 restore_v4lctl_settings.sh"
		# and then "./restore_v4lctl_settings.sh"
		if (video0_old != video0_new):
			f = open('restore_v4lctl_settings.sh','w')
			f.write('#!/bin/sh\n')
			f.write('echo \"restoring v4lctl settings to previous values\"\n')
			for attr in attributes:
				if attr in unknowns: continue
				f.write("v4lctl setattr " + attr + ' ' + str(video0_old[attr]) + "\n")
				f.write('echo \"setting ' + attr +' to ' + str(video0_old[attr]) + '"\n')
			f.write('echo \"v4lctl values restored\"')
			f.close()


	def warp_image(self, frame):
		# TODO: this might work in gui, but are the blur values saved anywhere?
		# TODO: implement blur value variations
		"""
		Creates trackbars and applies frame preprocessing for functions that actually require a frame,
		instead of setting the video device options
		:param frame: frame
		:return: preprocessed frame
		"""
		blur = cv2.getTrackbarPos('Gaussian blur', 'frame2')

		if blur >= 1:
			if blur % 2 == 0:
				blur += 1
			frame = cv2.GaussianBlur(frame, (121, 121), 0)

		return frame
