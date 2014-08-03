import sys
import serial
import time
import os
import requests
import json
import pickle
import thread

#block_list = []
block_dict = dict()

machine_name = "lee_raspi"

if not os.path.exists("data"):
    os.makedirs("data")

# remove old block
#if os.path.exists(os.path.join('data', "block.blk")):
#    os.remove(os.path.join('data', "block.blk"))

# save it to a block
if os.path.exists(os.path.join('data', "block.blk")):
    with open(os.path.join('data', 'block.blk'), 'rb') as f:
        block_dict.update(pickle.load(f))
else:
    # create a blank block
    with open(os.path.join('data', 'block.blk'), 'wb') as f:
        pickle.dump(block_dict, f)

#print "block_dict", block_dict

if "bio" in block_dict:
    print "found existing object data"
else:
    block_dict["bio"] = []

def posttofirebase():
	with open(os.path.join('data', 'block.blk'), 'wb') as output:
		#block_dict["bio"] = block_list
		pickle.dump(block_dict, output, pickle.HIGHEST_PROTOCOL)
		print "save it to file"

		try:
			# post to firebase
			response = requests.patch(url, data=json.dumps(dict(bio=block_dict["bio"])))
			print response
		except:
			print "posting error"

if __name__ == "__main__":

	url = "https://timeseriesvisual.firebaseio.com/.json"
	device = "/dev/tty.usbmodemfa131"
	ser = serial.Serial(device, 115200, timeout=5, parity="N", bytesize=8)

	t0 = time.time()

	while True:
	    line = ser.readline()
	    #print len(line)
	    #print line
	    if len(line) > 24 and len(line) < 28:
			try:
				biosig = map(lambda x:float(x), line.strip().split(' '))
			except:
				continue
			output_bio = dict()
			output_bio["timestamp"] = t0 + biosig[0] * .001
			output_bio["data"] = dict()
			output_bio["data"]["%s-temperaturec"%machine_name] = biosig[1]
			output_bio["data"]["%s-temperaturef"%machine_name] = biosig[2]
			output_bio["data"]["%s-ltfppg"%machine_name] = biosig[3]
			output_bio["data"]["%s-skfecg"%machine_name] = biosig[4]

			#print output_bio
			block_dict["bio"].append(output_bio)

			if len(block_dict["bio"]) % 301 == 300:
				thread.start_new_thread(posttofirebase,())
