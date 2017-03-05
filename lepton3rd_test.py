#!/usr/bin/env python
import numpy as np
import time

from mpsse import *

#print "import ok"
VOSPI_FRAME_SIZE=164
SEGMENT=4
DUMMY=60
ImageX=160
ImageY=120
PacketsN=61
PacketSize=160
TLM=63
LOOP_LIM=1000
maxval=0
minval=0xffff
ZeroK=27315
#LSB=0.05
LSB=5
Ccount=8192
TlmData=[[0 for i in range(VOSPI_FRAME_SIZE)] for j in range(4)]
#For I2C
ADDRESS = 0x2A
WRADDR = 0x54
RDADDR = 0x55
CLK=4
OUT=5
IN=6
chkACK=0
onoffpin = 0xff
Wait0=0.0001

img_file="test_lepton3rd.pgm"
class segment:
	def __init__(self):
		self.num=0
		self.packets=np.zeros((PacketsN,PacketSize),dtype=np.uint8)
class Lepton:
	def __init__(self):
		self.data = np.zeros((ImageY,ImageX))
		self.image = np.zeros((ImageY,ImageX))
		self.tlm = np.zeros((4,VOSPI_FRAME_SIZE))
		self.maxval = 0
		self.minval = 0xffff
		self.tlm_ena=False
		self.tlm_pos=0

def main():
	print "start"
	lep=Lepton()
	GetLeptonImg(lep)
	imag2pgm(lep)
def GetLeptonImg(lep):
	fpa_temp=0

	pnum_max=59
	if lep.tlm_ena:
		pnum_max=60
	read_max=10
	read_n=0
	packet=""
	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	spi.Start()
	while 1:
		check_packet =spi.Read(VOSPI_FRAME_SIZE)
		if (ord(check_packet[0]) & 0x0f) == 0x0f:
			continue
		packet +=check_packet+spi.Read(VOSPI_FRAME_SIZE*60)
		read_n+=1
		if read_n> read_max:
			break
	spi.Stop()
	segments=[]
	for i in range(SEGMENT+1):
		segments.append(segment())
	tmp_seg=segment()
	for i in range(0,len(packet),VOSPI_FRAME_SIZE):
		pnum=ord(packet[i+1])
		if pnum==0:
			tmp_seg=segment()
		if pnum==20:
			tmp_seg.num=ord(packet[i])/16
		if pnum >pnum_max:
			continue
		for j in range(VOSPI_FRAME_SIZE-4):
			tmp_seg.packets[pnum][j]=ord(packet[i+4+j])
		if pnum==pnum_max:
			if tmp_seg.num <5:
				segments[tmp_seg.num]=tmp_seg
	tmp_segn=0
	#Segment to Image
	for i in range(1,SEGMENT+1):
		#print segments[i].num
		if segments[i].num <1:
			print "Error"
			continue
		if segments[i].num==4:	#Default
			tmp_segn=i
		#for j in range(pnum_max+1):
		for j in range(60):
			tmp_imgy=(segments[i].num-1)*30+int(j/2)
			for k in range(80):
				tmp_imgx=k+((j+(pnum_max-59)*(segments[i].num-1))%2)*80
				lep.image[tmp_imgy][tmp_imgx]=segments[i].packets[j][2*k]*256+segments[i].packets[j][2*k+1]
	lep.maxval=np.max(lep.image)
	lep.minval=np.min(lep.image)
	if lep.tlm_ena and tmp_segn:
		for i in range(4):
			for j in range(4,VOSPI_FRAME_SIZE):
				lep.tlm[i][j-4]=segments[tmp_segn].packets[57+i][j]
		fpa_temp=(lep.tlm[0][48]*256+lep.tlm[0][49])-ZeroK	#=8192

	for i in range(ImageY):
		for j in range(ImageX):
			lep.data[i][j]=((lep.image[i][j]-Ccount)*LSB)+fpa_temp
def GetLeptonImg_old5(lep):
	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	pnum_max=59
	if lep.tlm_ena:
		pnum_max=60
	read_max=10
	read_n=0
	packet=""
	spi.Start()
	while 1:
		check_packet =spi.Read(VOSPI_FRAME_SIZE)
		if (ord(check_packet[0]) & 0x0f) == 0x0f:
			continue
		packet +=check_packet+spi.Read(VOSPI_FRAME_SIZE*60)
		read_n+=1
		if read_n> read_max:
			break
	spi.Stop()
	segments=[]
	for i in range(SEGMENT+1):
		segments.append(segment())
	tmp_seg=segment()
	for i in range(0,len(packet),VOSPI_FRAME_SIZE):
		pnum=ord(packet[i+1])
		if pnum==0:
			tmp_seg=segment()
		if pnum==20:
			tmp_seg.num=ord(packet[i])/16
		if pnum >pnum_max:
			continue
		for j in range(VOSPI_FRAME_SIZE-4):
			tmp_seg.packets[pnum][j]=ord(packet[i+4+j])
		if pnum==pnum_max:
			if tmp_seg.num <5:
				segments[tmp_seg.num]=tmp_seg
	#Segment to Image
	for i in range(1,SEGMENT+1):
		print segments[i].num
		if segments[i].num <1:
			continue
		for j in range(pnum_max+1):
			tmp_imgy=(segments[i].num-1)*30+int(j/2)
			for k in range(80):
				tmp_imgx=k+((j+(pnum_max-59)*(segments[i].num-1))%2)*80
				lep.image[tmp_imgy][tmp_imgx]=segments[i].packets[j][2*k]*256+segments[i].packets[j][2*k+1]
	lep.maxval=np.max(lep.image)
	lep.minval=np.min(lep.image)
def GetLeptonImg_old4(lep):
	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	pnum_max=59
	if lep.tlm_ena:
		pnum_max=60
	read_max=10
	read_n=0
	packet=""
	spi.Start()
	while 1:
		check_packet =spi.Read(VOSPI_FRAME_SIZE)
		#spi.Stop()
		if (ord(check_packet[0]) & 0x0f) == 0x0f:
			continue
		#print "start image"
		#print "p0=",int(ord(packet[0])/16),"p1=",ord(packet[1])
		#spi.Start()
		packet +=check_packet+spi.Read(VOSPI_FRAME_SIZE*60)
		read_n+=1
		#spi.Stop()
		if read_n> read_max:
			break
	spi.Stop()
	segments=[]
	for i in range(SEGMENT+1):
		segments.append(segment())
	tmp_seg=segment()
	for i in range(0,len(packet),VOSPI_FRAME_SIZE):
		pnum=ord(packet[i+1])
		if pnum==0:
			tmp_seg=segment()
		if pnum==20:
			tmp_seg.num=ord(packet[i])/16
		if pnum >pnum_max:
			continue
		for j in range(VOSPI_FRAME_SIZE-4):
			tmp_seg.packets[pnum][j]=ord(packet[i+4+j])
		if pnum==pnum_max:
			if tmp_seg.num <5:
				#print tmp_seg.num
				segments[tmp_seg.num]=tmp_seg
	#Segment to Image
	for i in range(1,SEGMENT+1):
		print segments[i].num
		for j in range(30):
			for k in range(80):
				lep.image[(segments[i].num-1)*30+j][k]=segments[i].packets[j*2][2*k]*256+segments[i].packets[j*2][2*k+1]
				lep.image[(segments[i].num-1)*30+j][k+80]=segments[i].packets[j*2+1][2*k]*256+segments[i].packets[j*2+1][2*k+1]
				#lep.image[(segments[i].num-1)*30+j][k]=segments[i].packets[j*2][2*k]
				#lep.image[(segments[i].num-1)*30+j][k+80]=segments[i].packets[j*2+1][2*k]
	lep.maxval=np.max(lep.image)
	lep.minval=np.min(lep.image)
def seg2img_tlm(lep,segments):
	#Segment to Image
	for i in range(1,SEGMENT+1):
		#print segments[i].num
		for j in range(61):
			tmp_imgy=(segments[i].num-1)*30+int(j/2)
			for k in range(80):
				tmp_imgx=k+((j%2)+(segments[i].num-1)%2)*80
				lep.image[tmp_imgy][tmp_imgx]=segments[i].packets[j][2*k]*256+segments[i].packets[j][2*k+1]
def imag2pgm(lep):
	rmax=255/(lep.maxval-lep.minval)
	#Image to pgm
	pgm="P2\n"
	pgm+="160 120\n"
	pgm+="100\n"
	for i in range(ImageY):
		#pgm+=' '.join(lep.image[i]) + "\n"
		for j in range(ImageX):
			pgm+=str(int(rmax*(lep.image[i][j]-lep.minval))) + " "
		pgm=pgm.rstrip()
		pgm+="\n"
	pgm+="\n\n"
	#print pgm
	write_pgm(pgm)
def GetLeptonImg_old3(lep):

	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	segments=[]
	for i in range(SEGMENT):
		segments.append(segment())
	sn=0
	#tmpImg=[[0 for i in range(VOSPI_FRAME_SIZE)] for j in range(SEGMENT*61)]
	#tmpImg = np.zeros((SEGMENT*61,VOSPI_FRAME_SIZE))
	while 1:
		spi.Start()
		packet =spi.Read(164)
		#spi.Stop()
		if ord(packet[1])==0:
			#for p in packet:
			#	print ord(p),
			#print "\n"
			packet+=spi.Read(164*59)
			if ord(packet[164*20])/16 < 5 and ord(packet[164*20])/16>0:
				print ord(packet[164*20])/16
				break
		spi.Stop()
	print len(packet)
	print ord(packet[164*20]),ord(packet[164*20])/16
#	else:
def GetLeptonImg_old2(lep):
	print "get image"
	#lepton_image=[[0 for i in range(ImageX)] for j in range(ImageY)]
	packet_number=0
	count=0
	fpa_temp=0
	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	segments=[]
	for i in range(SEGMENT):
		segments.append(segment())
	sn=0
	#tmpImg=[[0 for i in range(VOSPI_FRAME_SIZE)] for j in range(SEGMENT*61)]
	tmpImg = np.zeros((SEGMENT*61,VOSPI_FRAME_SIZE))

	total_size=VOSPI_FRAME_SIZE*SEGMENT*(PacketsN+DUMMY)

	print total_size
	print "get packet"
	spi.Start()
	packet =spi.Read(total_size)
	spi.Stop()
	for i in range(len(packet)):
		if i % 164==0:
			#print i,i/164,":p0=",int(ord(packet[i])/16),"p1=",ord(packet[i+1])
			if ord(packet[i+1]) < 61:
				#print i,i/164,":p0=",int(ord(packet[i])/16),"p1=",ord(packet[i+1])
				if i<len(packet)-165:
					if ord(packet[i+1])+1==ord(packet[i+165]):
						print i,i/164,":p0=",int(ord(packet[i])/16),"p1=",ord(packet[i+1])
						#segments[sn].packets[ord(packet[i+1])]=packet[4:]
						for k in range(160):
							segments[sn].packets[ord(packet[i+1])][k]=ord(packet[k+4])
						if ord(packet[i+1])==20:
							segments[sn].num=int(ord(packet[i])/16)
						if ord(packet[i+1])==59:
							sn+=1
	#Segment to Image
	for i in range(SEGMENT):
		print segments[i].num
		for j in range(30):
			for k in range(80):
				lep.image[segments[i].num*30+j][k]=segments[i].packets[j*2][2*k]*256+segments[i].packets[j*2][2*k+1]
				lep.image[segments[i].num*30+j][k+80]=segments[i].packets[j*2+1][k]*256+segments[i].packets[j*2+1][2*k+1]
	#Image to pgm
	pgm="P2\n"
	pgm+="160 120\n"
	pgm+="100\n"
	for i in range(ImageY):
		#pgm+=' '.join(lep.image[i]) + "\n"
		for j in range(ImageX):
			pgm+=str(int(lep.image[i][j])) + " "
		pgm=pgm.rstrip()
		pgm+="\n"
	pgm+="\n\n"
	#print pgm
	write_pgm(pgm)

def write_pgm(data):
	pgm=open(img_file,'w')
	pgm.write(data)
	pgm.close()
def GetLeptonImg_old(lep):
	print "get image"
	#lepton_image=[[0 for i in range(ImageX)] for j in range(ImageY)]
	packet_number=0
	count=0
	fpa_temp=0
	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	segments=[]
	for i in range(SEGMENT):
		segments.append(segment())
	sn=0
	#tmpImg=[[0 for i in range(VOSPI_FRAME_SIZE)] for j in range(SEGMENT*61)]
	tmpImg = np.zeros((SEGMENT*61,VOSPI_FRAME_SIZE))

	total_size=VOSPI_FRAME_SIZE*SEGMENT*60
	if lep.tlm_ena:
		total_size=VOSPI_FRAME_SIZE
	print total_size
	print "get packet"
	spi.Start()
	packet =spi.Read(total_size)
	spi.Stop()
	for i in range(len(packet)):
		if i % 164==0:
			print i,i/164,":p0=",int(ord(packet[i])/16),"p1=",ord(packet[i+1])

if __name__ == "__main__":
	main()
