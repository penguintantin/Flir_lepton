import numpy as np
import time

from mpsse import *
VOSPI_FRAME_SIZE=164
SEGMENT=4

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
class segment:
	def __init__(self):
		self.num=0
		self.packets=np.zeros((PacketsN,PacketSize))
class Lepton:
	def __init__(self):
		self.data = np.zeros((ImageY,ImageX))
		self.image = np.zeros((ImageY,ImageX))
		self.tlm = np.zeros((4,VOSPI_FRAME_SIZE))
		self.maxval = 0
		self.minval = 0xffff
		self.tlm_ena=False
		self.tlm_pos=0
		self.img_file="test_lepton3rd.pgm"
def imag2pgm(lep):
	rmax=255/(lep.maxval-lep.minval)
	#Image to pgm
	#data="P2\n160 120\n" + str(int(lep.maxval))+" "+str(int(lep.minval))+" "+str(int(fpa_temp)) + "\n"
	data="P2\n160 120\n" + str(int(rmax*(lep.maxval-lep.minval)))+" 0\n"
	for i in range(ImageY):
		#data+=' '.join(lep.image[i]) + "\n"
		for j in range(ImageX):
			data+=str(int(rmax*(lep.image[i][j]-lep.minval))) + " "
		data=data.rstrip()
		data+="\n"
	data+="\n\n"
	#print pgm
	pgm=open(lep.img_file,'w')
	pgm.write(data)
	pgm.close()

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
		for j in range(pnum_max+1):
		#for j in range(60):
			if lep.tlm_ena and segments[i].num==4:
				if j > 56:
					break
			#tmp_imgy=(segments[i].num-1)*30+int(j/2)+(pnum_max-59)*int(segments[i].num/3)
			tmp_imgy=int(((segments[i].num-1)*(pnum_max+1)+j)/2)
			for k in range(80):
				tmp_imgx=k+((j+(pnum_max-59)*(segments[i].num-1))%2)*80
				lep.image[tmp_imgy][tmp_imgx]=segments[i].packets[j][2*k]*256+segments[i].packets[j][2*k+1]
				#print j,k,segments[i].num,tmp_imgx,tmp_imgy,lep.image[tmp_imgy][tmp_imgx]
	lep.maxval=np.max(lep.image)
	lep.minval=np.min(lep.image)
	if lep.tlm_ena and tmp_segn:
		for i in range(4):
			for j in range(VOSPI_FRAME_SIZE-4):
				lep.tlm[i][j]=segments[tmp_segn].packets[57+i][j]
		fpa_temp=(lep.tlm[0][48]*256+lep.tlm[0][49])-ZeroK	#=8192
	print "fpa=",fpa_temp
	for i in range(ImageY):
		for j in range(ImageX):
			lep.data[i][j]=((lep.image[i][j]-Ccount)*LSB)+fpa_temp
def TlmSetEna(lep):
	io = MPSSE(BITBANG)
	io.SetDirection(0xBB);
	while (check_busy(io)):
		print("busy before")

	#Set LEP_I2C_DATA_0_REG
	#print("Set LEP_I2C_DATA_0_REG")
	i2cstart(io)
	i2cwrite(io,WRADDR)
	i2cwrite(io,0x00)
	i2cwrite(io,0x06)
	i2cwrite(io,0x00)
	i2cwrite(io,0x01)
	i2cstop(io)
	#Set LEP_I2C_DATA_LENGTH_REG
	#print("Set LEP_I2C_DATA_LENGTH_REG")
	i2cstart(io)
	i2cwrite(io,WRADDR)
	i2cwrite(io,0x00)
	i2cwrite(io,0x08)
	i2cwrite(io,0x00)
	i2cwrite(io,0x01)
	i2cstop(io)
	#Set LEP_I2C_COMMAND_REG
	#print("Set LEP_I2C_COMMAND_REG")
	i2cstart(io)
	i2cwrite(io,WRADDR)
	i2cwrite(io,0x00)
	i2cwrite(io,0x04)
	i2cwrite(io,0x02)
	i2cwrite(io,0x19)
	i2cstop(io)
	#Check Busy
	while (check_busy(io)):
		print("busy after")
	print "TLM enable done"
	lep.tlm_ena=True
	io.Close()
def check_busy(io):

	i2cstart(io)
	i2cwrite(io,WRADDR)

	i2cwrite(io,0x00)
	i2cwrite(io,0x02)
	i2cstart(io)
	i2cwrite(io,RDADDR)
	res0=i2cread(io)
	res1=i2creadnack(io)
	#print "reg:",res0,",",res1
	ret=res1 & 0x01
	return ret

def PPinHigh(io,pin):
	global onoffpin
	onoffpin |= (1<<pin)
	io.WritePins(onoffpin)

def PPinLow(io,pin):
	global onoffpin
	onoffpin &= ~(1 << pin)
	io.WritePins(onoffpin)

def i2cstop(io):
	PPinHigh(io, CLK)
	time.sleep(Wait0)
	PPinHigh(io, OUT)

def i2cstart(io):
	#Start
	PPinHigh(io, CLK)	#CLK
	time.sleep(Wait0)
	PPinLow(io, OUT)	#SDA
	time.sleep(Wait0)

def i2cwrite(io,out):
	for i in range(8):
		PPinLow(io, CLK)
		time.sleep(Wait0)
		if(out & (1<< (7-i))):
			PPinHigh(io, OUT)
		else:
			PPinLow(io, OUT)
		time.sleep(Wait0)
		PPinHigh(io, CLK)
		time.sleep(Wait0)
	PPinLow(io, CLK)
	time.sleep(Wait0)
	PPinHigh(io, OUT)
	time.sleep(Wait0)
	PPinHigh(io, CLK)
	#time.sleep(Wait0)

	if(io.PinState(IN, -1)==0):
		#print("ACK(S)")
		chkACK=0x01
	else:
		chkACK=0x00

	time.sleep(Wait0)
	PPinLow(io, CLK)
	time.sleep(Wait0)

def i2cread(io):
	indata=0x00

	for i in range(8):
		PPinHigh(io, CLK)
		time.sleep(Wait0)
		if(io.PinState(IN, -1)):
			indata|=(1<< (7-i))
		PPinLow(io, CLK)
		time.sleep(Wait0)
	#ACK(M)
	#print("ACK(M)\n")
	PPinLow(io, OUT)
	time.sleep(Wait0)
	PPinHigh(io, CLK)
	time.sleep(Wait0)
	PPinLow(io, CLK)
	time.sleep(Wait0)
	PPinHigh(io, OUT)
	return indata

def i2creadnack(io):
	indata=0x00
	for i in range(8):
		PPinHigh(io, CLK)
		time.sleep(Wait0)
		if(io.PinState(IN, -1)):
			indata|=(1<< (7-i))
		PPinLow(io, CLK)
		time.sleep(Wait0)
	#ACK(M)
	#time.sleep(Wait0)
	#print("NACK(M)\n")
	PPinHigh(io, OUT)
	time.sleep(Wait0)
	PPinHigh(io, CLK)
	time.sleep(Wait0)
	PPinLow(io, CLK)
	time.sleep(Wait0)
	#PPinHigh(io, OUT)
	return indata
