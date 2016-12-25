#!/usr/bin/python
import os
import sys
import matplotlib.pyplot as plt
import math
import time
import glob
import numpy as np

from matplotlib.widgets import Button
from matplotlib import cm
from mpsse import *

import lepton

Read=True
maxval=0
ImgID=0
class Index:
	ind = 0
	def __init__(self, lep):
		self.lepton=lep
	def reset(self, event):
		print("Reset")
	def save(self, event):
		print("save")
		saveimage(self.lepton)
	def stop(self, event):
		global Read
		print("stop")
		Read=False
	def start(self, event):
		global Read
		print("start")
		Read=True
	def next(self, event):
		self.ind += 1
		i = self.ind % len(freqs)
		ydata = np.sin(2*np.pi*freqs[i]*t)
		l.set_ydata(ydata)
		plt.draw()

	def prev(self, event):
		self.ind -= 1
		i = self.ind % len(freqs)
		ydata = np.sin(2*np.pi*freqs[i]*t)
		l.set_ydata(ydata)
		plt.draw()


def main():
	lep=lepton.Lepton()
	#Set Tlm
	lepton.TlmSetEna()
	lepton.GetLeptonImg(lep)
	fpa_temp=lep.tlm[0][48]*256+lep.tlm[0][49]
	diff = lep.maxval-lep.minval
	fig, ax = plt.subplots()
	ax.set_title('Image')

	#cax = ax.imshow(data, interpolation='nearest', cmap=cm.coolwarm, picker=True)
	#cax = ax.imshow(data, interpolation='nearest', cmap=cm.coolwarm, picker=5)
	cax = ax.imshow(lep.data, interpolation='nearest')
	cbar = fig.colorbar(cax, ticks=[0, diff/2, diff])
	cbar.ax.set_yticklabels([lep.minval, lep.minval+diff/2, lep.maxval])  # vertically oriented colorbar
	#fig.canvas.mpl_connect('pick_event', onpick)
	#'''
	callback = Index(lep)
	axstart = plt.axes([0.3, 0.05, 0.1, 0.075])
	axstop = plt.axes([0.41, 0.05, 0.1, 0.075])
	axsave = plt.axes([0.52, 0.05, 0.1, 0.075])
	axreset = plt.axes([0.63, 0.05, 0.1, 0.075])

	bsave = Button(axsave, 'Save')
	bsave.on_clicked(callback.save)
	breset = Button(axreset, 'Reset')
	breset.on_clicked(callback.reset)
	bstart = Button(axstart, 'Start')
	bstart.on_clicked(callback.start)
	bstop = Button(axstop, 'Stop')
	bstop.on_clicked(callback.stop)
	#'''
	plt.ion()
	plt.show()
	while 1:
		maxval=0
		minval=0xffff
		if Read:
			lepton.GetLeptonImg(lep)
			print "Redraw",lep.maxval,lep.minval
			#print "FPA temp=",TlmData[0][48]*256+TlmData[0][49]
			fpa_temp=lep.tlm[0][48]*256+lep.tlm[0][49]
			diff = lep.maxval-lep.minval
			#ax.cla()
			#ax.imshow(data)
			#ax.imshow(data, interpolation='nearest', cmap=cm.coolwarm, picker=5)
			cax = ax.imshow(lep.data, interpolation='nearest')
			#cbar = fig.colorbar(cax, ticks=[0, diff/2, diff])
			#cbar.ax.set_yticklabels([minval, minval+diff/2, maxval])
			#cax.set_data(data)	#OK .Faster?
			#ax.set_title('Image')
			#plt.draw()	#OK
			fig.canvas.blit()	#OK
			#time.sleep(0.5)	##NG!!!
		#plt.pause(0.05)	#OK
		#http://stackoverflow.com/questions/3441874/matplotlib-animation-either-freezes-after-a-few-frames-or-just-doesnt-work
		#fig.canvas.blit() # or draw()
		fig.canvas.start_event_loop(0.0001)	#OK

def saveimage(lep):
	global ImgID
	maxval=0
	minval=0xffff
	fpa_temp=lep.tlm[0][48]*256+lep.tlm[0][49]
	img_file="./img2/img_" + str(ImgID) + ".pgm"
	diff = lep.maxval-lep.minval
	pgm=open(img_file,'w')
	data="P2\n80 60\n" + str(int(lep.maxval))+" "+str(int(lep.minval))+" "+str(int(fpa_temp)) + "\n"
	for i in range(lepton.ImageY):
		for j in range(lepton.ImageX):
			#data+=str(lep.image[i][j]-lep.minval)+" "
			data+=str(int(lep.image[i][j]))+" "
		data+="\n"
	data+="\n\n"
	pgm.write(data)
	pgm.close()
	ImgID+=1
def open_file(dirname, filename):
	file_name = os.path.join(dirname, filename)
	try:
		f = open(file_name,'r')
	except IOError, (errno, strerror):
		print "Unable to open the file: \"" + file_name + "\"\n"
		return []
	else:
		ret = f.read()
		return ret.split("\n")

if __name__ == "__main__":
	main()
