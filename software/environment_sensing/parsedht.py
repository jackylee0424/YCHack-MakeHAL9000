import sys
import serial
import time
import os
import requests
import json
import pickle
import thread

url = "https://timeseriesvisual.firebaseio.com/.json"
device = "/dev/tty.usbmodemfd111"

#block_list = []
block_dict = dict()
machine_name = "old_raspi"

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

if "raw" in block_dict:
	print "found existing DHT22 data"
else:
	block_dict["raw"] = []


def posttofirebase():
	with open(os.path.join('data', 'block.blk'), 'wb') as output:
		#block_dict["raw"] = block_list
		pickle.dump(block_dict, output, pickle.HIGHEST_PROTOCOL)
		print "save it to file"

		try:
			# post to firebase
			#response = requests.patch(url, data=json.dumps(dict(raw=block_list)))
			response = requests.patch(url, data=json.dumps(dict(raw=block_dict["raw"])))
			print response
		except:
			print "posting error"


if __name__ == "__main__":

	ser = serial.Serial(device, 9600, timeout=5, parity="N", bytesize=8)

	while True:
	    line = ser.readline()
	    if len(line) == 25:
			dht22 = map(lambda x:float(x), line.strip().split(' '))
			#print dht22
			output_dhc22 = dict()
			output_dhc22["timestamp"] = time.time()
			output_dhc22["data"] = dict()
			output_dhc22["data"]["%s-humidity"%machine_name] = dht22[0]
			output_dhc22["data"]["%s-temperaturec"%machine_name] = dht22[1]
			output_dhc22["data"]["%s-temperaturef"%machine_name] = dht22[2]
			output_dhc22["data"]["%s-heatindexf"%machine_name] = dht22[3]

			#block_list.append(output_dhc22)
			block_dict["raw"].append(output_dhc22)

			#print len(block_list)
			thread.start_new_thread(posttofirebase,())