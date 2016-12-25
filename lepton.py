import numpy as np
import time

from mpsse import *
VOSPI_FRAME_SIZE=164
ImageX=80
ImageY=60
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
class Lepton:
	def __init__(self):
		self.data = np.zeros((ImageY,ImageX))
		self.image = np.zeros((ImageY,ImageX))
		self.tlm = np.zeros((4,VOSPI_FRAME_SIZE))
		self.maxval = 0
		self.minval = 0xffff
def GetLeptonImg_test2(lep):	###Not so fast
	#tmpImg=[[0 for i in range(VOSPI_FRAME_SIZE)] for j in range(TLM)]
	lepton_image=[[0 for i in range(ImageX)] for j in range(ImageY)]
	frame_number=0
	count=0
	fpa_temp=0
	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	while 1:
		if count>LOOP_LIM:
			print "Error:Over loop limit:",LOOP_LIM
			spi.Close()
			time.sleep(0.5)
			spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
			count=0
			continue;
		spi.Start()
		packet =spi.Read(VOSPI_FRAME_SIZE*2)
		spi.Stop()
		if (ord(packet[0]) & 0x0f)==0x0f:
			count+=1
			continue
		if ord(packet[1]) !=0 or ord(packet[165])!=1:
			count+=1
			continue
		spi.Start()
		#packet.extend(spi.Read(VOSPI_FRAME_SIZE*(TLM-2)))
		packet+=spi.Read(VOSPI_FRAME_SIZE*(TLM-2))
		spi.Stop()
		break
	spi.Close()
	#print "count=",count

	for i in range(VOSPI_FRAME_SIZE*TLM):
		if (i%VOSPI_FRAME_SIZE==1):
			frame_number=ord(packet[i])
		if frame_number > 62:
			print "Error Frame Number",frame_number
			return lep.data
		j=i%VOSPI_FRAME_SIZE
		if j>3 and j%2:
			#print i,j
			if frame_number < 60:
				lepton_image[frame_number][(j-4)/2]=ord(packet[i-1])*256 + ord(packet[i])
			elif frame_number < 64:
				lep.tlm[frame_number-60][j-5]=ord(packet[i-1])
				lep.tlm[frame_number-60][j-4]=ord(packet[i])
	fpa_temp=(lep.tlm[0][48]*256+lep.tlm[0][49])-ZeroK	#=8192
	lep.maxval=max(max(lepton_image))
	lep.minval=min(min(lepton_image))
	for i in range(ImageY):
		for j in range(ImageX):
			lep.data[i][j]=((lepton_image[i][j]-Ccount)*LSB)+fpa_temp
def GetLeptonImg_test(lep):###Not so fast
	#tmpImg=[[0 for i in range(VOSPI_FRAME_SIZE)] for j in range(TLM)]
	#lepton_image=[[0 for i in range(ImageX)] for j in range(ImageY)]
	frame_number=0
	count=0
	fpa_temp=0
	#spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	spi = MPSSE(SPI3, 20000000, MSB)	#max 20MHZ
	while 1:
		
		spi.Start()
		packet =spi.Read(VOSPI_FRAME_SIZE*(TLM))
		spi.Stop()
		if count>LOOP_LIM:
			print "Error:Over loop limit:",LOOP_LIM
			spi.Close()
			time.sleep(0.5)
			#spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
			spi = MPSSE(SPI3, 20000000, MSB)	#max 20MHZ
			count=0
			continue;

		if (ord(packet[0]) & 0x0f)==0x0f:
			count+=1
			continue
		if ord(packet[1]) !=0 or ord(packet[165])!=1:
			count+=1
			continue
		break
	spi.Close()
	#print "count=",count

	for i in range(VOSPI_FRAME_SIZE*TLM):
		if (i%VOSPI_FRAME_SIZE==1):
			frame_number=ord(packet[i])
		if frame_number > 62:
			print "Error Frame Number",frame_number
			return lep.data
		j=i%VOSPI_FRAME_SIZE
		if j>3 and j%2:
			#print i,j
			if frame_number < 60:
				lep.image[frame_number][(j-4)/2]=ord(packet[i-1])*256 + ord(packet[i])
			elif frame_number < 64:
				lep.tlm[frame_number-60][j-5]=ord(packet[i-1])
				lep.tlm[frame_number-60][j-4]=ord(packet[i])
	fpa_temp=(lep.tlm[0][48]*256+lep.tlm[0][49])-ZeroK	#=8192
	lep.maxval=max(max(lep.image))
	lep.minval=min(min(lep.image))
	for i in range(ImageY):
		for j in range(ImageX):
			lep.data[i][j]=((lep.image[i][j]-Ccount)*LSB)+fpa_temp
def GetLeptonImg(lep):
	tmpImg=[[0 for i in range(VOSPI_FRAME_SIZE)] for j in range(TLM)]
	#lepton_image=[[0 for i in range(ImageX)] for j in range(ImageY)]
	frame_number=0
	count=0
	fpa_temp=0
	spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
	while 1:
		
		spi.Start()
		packet =spi.Read(VOSPI_FRAME_SIZE*(TLM))
		spi.Stop()
		if count>LOOP_LIM:
			print "Error:Over loop limit:",LOOP_LIM
			spi.Close()
			time.sleep(0.5)
			spi = MPSSE(SPI3, FIFTEEN_MHZ, MSB)
			count=0
			continue;

		if (ord(packet[0]) & 0x0f)==0x0f:
			count+=1
			continue
		if ord(packet[1]) !=0 or ord(packet[165])!=1:
			count+=1
			continue
		break
	spi.Close()
	#print "count=",count

	for i in range(VOSPI_FRAME_SIZE*TLM):
		#print i
		tmpImg[i/VOSPI_FRAME_SIZE][i%VOSPI_FRAME_SIZE]=packet[i];
	for i in range(TLM):
		frame_number=ord(tmpImg[i][1])
		if frame_number > 62:
			print "Error Frame Number",frame_number
			return lep.data
		#if frame_number > 59:
		#	print "fn=",frame_number
		for j in range(ImageX):
			if frame_number < 60:
				lep.image[frame_number][j]=ord(tmpImg[i][2*j+4])*256 + ord(tmpImg[i][2*j+5])
			elif frame_number < 64:
				#print "TLM"
				lep.tlm[frame_number-60][2*j]=ord(tmpImg[i][2*j+4])
				lep.tlm[frame_number-60][2*j+1]=ord(tmpImg[i][2*j+5])
	fpa_temp=(lep.tlm[0][48]*256+lep.tlm[0][49])-ZeroK	#=8192
	#lep.maxval=max(max(lep.image))
	#lep.minval=min(min(lep.image))
	lep.maxval=np.max(lep.image)
	lep.minval=np.min(lep.image)
	for i in range(ImageY):
		for j in range(ImageX):
			lep.data[i][j]=((lep.image[i][j]-Ccount)*LSB)+fpa_temp
def TlmSetEna():
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
