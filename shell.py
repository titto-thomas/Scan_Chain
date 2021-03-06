#!/usr/bin/env python

#---------------------------------------------
# Scan chain implementation v2
# Titto Thomas
# WEL Lab, EE Dept. , IIT Bombay

# Credits : Deepak Bhat, designer of v1
#---------------------------------------------

import usb.core
import usb.util
import sys
import time
import os
from subprocess import call

mask_int = 0
out_pins = 0
expct_out = ""
mask = ""




print"Scan chain v2.0\nWadhwani Electronics Laboratory, IIT Bombay\n"

# Just checking for the necessary root access of the user
if os.geteuid() != 0:
    exit("You need to have root privileges to run this script.\nPlease try again, this time using 'sudo'. Exiting.\n")

log = 0;
# Check for the proper input format
if len(sys.argv) == 1 :
	print "Note : Log file will not be generated"
	log = 0;	
elif ( len(sys.argv) == 2 and sys.argv[1] == "-l") :
	print "Note : Log file will be generated"
	log = 1;
	log_file = open('log.txt',"w");
else:
	print "Error : Incorrect format"
	sys.exit(1)

print "\nEnter the commands in upper case..\n"


#----------------- Connecting to device -----------------------------------------------
def connect():
	print "Initiating connection with the device.."

	# find our device
	dev = usb.core.find(idVendor=0x03eb, idProduct = 0x2402)
	# was it found?
	if dev is None:
		raise ValueError('Error : Device not found')
	print "Device found.."

	# Note: The code below is for interface 0, check what interface is used
	if dev.is_kernel_driver_active(0) is True:
		dev.detach_kernel_driver(0)

	# set the active configuration. With no arguments, the first configuration will be the active one
	print "Please wait, Setting it's configuration... "
	dev.set_configuration()
	print "Done !"

	print "Claiming interface.."	
	usb.util.claim_interface(dev, 0)
	print "Connection established.\n"

	return dev

#--------------------- Hex input to binary conversion function ---------------------------------
def toBin(value, bits):
    value = bin(int(value,16))[2:]
    while ( len(value) < bits ):
    	value = '0' + value
    while ( len(value) > bits ):
    	value = value[1:]   
    return value

#----------------- Read the input and execute it ------------------------------------------------

def exec_sdr ( device, in_pins, data_in ):
	data_in_reverse = data_in[::-1]
	#Form the string to be sent to the microcontroller
	command_out = 'L'+chr(in_pins)+data_in_reverse
	print"Sending ",in_pins,"bit input data ",data_in
	
	for single in list(command_out):
		device.write(2,single,100)
		time.sleep(5)
	print "Successfully entered the input.."
	return
		
def exec_run ( device, time_sec, mask_int, out_pins):
		
	device.write(2,'A',100)		
	time.sleep(5)
	print"Applying input.."
	print "Waiting for execution to end.."
	# setup toolbar
	sys.stdout.write("[%s]" % (" " * 40))
	sys.stdout.flush()
	sys.stdout.write("\b" * (41)) # return to start of line, after '['
	
	for i in xrange(40):
		time.sleep(time_sec/40) # do real work here
		# update the bar
		sys.stdout.write("-")
		sys.stdout.flush()

	sys.stdout.write("\n")
	
	# Scan out the data if needed
	if ( mask_int != 0 ):
		device.write(2,'S',100)
		time.sleep(5)
		device.write(2,chr(out_pins),100)
		print "Sampling out data.."
		time.sleep(out_pins*5)
		inn = device.read(0x81,out_pins,100)
		recvd_data = ''.join(chr(e) for e in inn)
		print "\n Received : ",recvd_data
		
		bit_num = 0
		for mask_bit in mask.split():
			bit_num += 1
			if ( mask_bit == 1 ):
				if (inn(bit_num) != excpt_out(bit_num )):
					print " Compare failed !"
	return
#--------------------------------------------------------------------------------------------

while (1):
	user_input = raw_input(">> ")
	user_input = user_input.split(' ')

	if user_input[0] == "CONNECT":
		device = connect()
	elif ( user_input[0] == "SDR" ) :
		in_pins = int(user_input[1])
		out_pins = int(user_input[3])
		temp_in = user_input[2].rstrip(')').split('(')
		data_in = toBin(temp_in [1], in_pins)
		temp_out = user_input[4].rstrip(')').split('(')
		expct_out = toBin(temp_out [1], out_pins)
		temp_mask = user_input[5].rstrip(')').split('(')
		mask = toBin(temp_mask [1], out_pins)
		mask_int = int(temp_mask[1],16)

		exec_sdr ( device, in_pins, data_in)

	elif ( user_input[0] == "RUNTEST" ):
		time_sec = int(user_input[1])
		exec_run (device, time_sec, mask_int, out_pins)

	elif user_input[0] == "DISCONNECT" :
		print "Disconnecting.."
		log_file.close()
	elif user_input[0] == "QUIT" :
		sys.exit(1)
	else :
		print "Error : Unknown command"



call(["chmod", "770", "log.txt"])


	
