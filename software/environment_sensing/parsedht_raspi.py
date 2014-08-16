import sys
import time
import os
import requests
import json
import pickle
import thread
import dhtreader

# firebase
url = "https://timeseriesvisual.firebaseio.com/.json"

# DHT/Raspi setup
DHT22 = 22
dev_type = DHT22
dhtpin = 8

# block setup
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
	dhtreader.init()
	while True:
		time.sleep(2000)
		try:
			t, h = dhtreader.read(dev_type, dhtpin)
		except:
			continue
		if t and h:
			print("Temp = {0} *C, Hum = {1} %".format(t, h))
			output_dhc22 = dict()
			output_dhc22["timestamp"] = time.time()
			output_dhc22["data"] = dict()
			output_dhc22["data"]["%s-humidity"%machine_name] = h
			output_dhc22["data"]["%s-temperaturec"%machine_name] = t
			#output_dhc22["data"]["%s-temperaturef"%machine_name] = dht22[2]
			#output_dhc22["data"]["%s-heatindexf"%machine_name] = dht22[3]

			#block_list.append(output_dhc22)
			block_dict["raw"].append(output_dhc22)

			print len(block_list)
			#thread.start_new_thread(posttofirebase,())