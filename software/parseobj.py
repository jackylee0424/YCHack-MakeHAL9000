import os
import subprocess
import cv2
import thread
import pickle
import time
import requests
import json

#block_list = []
block_dict = dict()
url = "https://timeseriesvisual.firebaseio.com/.json"

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

print "block_dict", block_dict

if "objects" in block_dict:
    print "found existing object data"
else:
    block_dict["objects"] = []

#block_list = []
machine_name = "lee_air"

biggest_face = None
found_objects = []
found_face = []
with open(os.path.join("data", 'data.bin'), 'rb') as input:
    mmodel = pickle.load(input)
with open(os.path.join("data", 'mat.data'), 'rb') as input:
    matdata = pickle.load(input)

def detectFaces(img, cascade):
    global mmodel, matdata, found_face
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    rects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60), flags = 0)
    if len(rects)>0:
        rects[:, 2:] += rects[:, :2]

    for f in rects:
        x1, y1, x2, y2 = f
        biggest_face = f
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 1)

        test_img = img[y1:y2, x1:x2]
        test_img  = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
        test_img = cv2.resize(test_img, (128, 128), interpolation=cv2.INTER_CUBIC)
        t = time.time()
        #output_name, min_dist =  mmodel["eigen"].predict(test_img,-.5)
        #print "predicted (eigen)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)
        t = time.time()
        output_name, min_dist =  mmodel["fisher"].predict(test_img,-.5)
        found_face = [matdata["z"][output_name] + " " + str(min_dist)]
        #print "predicted (fisher)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)
        break


def objectrecog():
    global found_objects

    ## super slow 4~5 sec
    cmd = "~/code/overfeat/bin/macos/overfeat -n 6 tmp.jpg"
    print "recogizing objects..."
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    stdoutput = process.stdout.read()
    if stdoutput:
        #found_objects = stdoutput.strip().split("\n")
        #print found_objects
        for i in stdoutput.strip().split("\n"):
            tmp = (i.split(", ")[-1]).split(" ")
            found_objects.append(dict(obj_name=" ".join(tmp[:-1]), obj_score=float(tmp[-1])))
        print found_objects

def posttofirebase():
    with open(os.path.join('data', 'block.blk'), 'wb') as output:
        #block_dict["objects"] = block_list
        pickle.dump(block_dict, output, pickle.HIGHEST_PROTOCOL)
        print "save it to file"

        try:
            # post to firebase
            response = requests.patch(url, data=json.dumps(dict(objects=block_dict["objects"])))
            print response
        except:
            print "posting error"


if __name__ == "__main__":
    cascade = cv2.CascadeClassifier(os.path.join("xml", "haarcascade_frontalface_alt.xml"))
    cam = cv2.VideoCapture(0)
    counter = 0

    while True:
        ret, img = cam.read()
        if counter % 120 == 1:
        	cv2.imwrite("tmp.jpg", img)
        	thread.start_new_thread(objectrecog,())
        detectFaces(img, cascade)
        cv2.putText(img, "" if not any(found_face) else (found_face[0]), (20, 40), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), thickness=2, lineType=cv2.CV_AA)
        cv2.putText(img, "" if not any(found_objects) else (found_objects[0]["obj_name"]), (20, 80), cv2.FONT_HERSHEY_PLAIN, 2, (255, 55, 100), thickness=2, lineType=cv2.CV_AA)
        cv2.putText(img, "" if not any(found_objects) else (found_objects[1]["obj_name"]), (20, 120), cv2.FONT_HERSHEY_PLAIN, 2, (255, 100, 55), thickness=2, lineType=cv2.CV_AA)
        cv2.putText(img, "" if not any(found_objects) else (found_objects[2]["obj_name"]), (20, 160), cv2.FONT_HERSHEY_PLAIN, 2, (55, 255, 100), thickness=2, lineType=cv2.CV_AA)
        
        cv2.imshow("camera", img)

        if counter % 90 == 25:
            output_objs = dict()
            output_objs["timestamp"] = time.time()
            output_objs["data"] = dict()
            output_objs["data"]["%s-facestring"%machine_name] = found_face
            output_objs["data"]["%s-objstring"%machine_name] = found_objects

            block_dict["objects"].append(output_objs)
            #print len(block_list)
            thread.start_new_thread(posttofirebase,())
        counter += 1
        print counter
        key = cv2.waitKey(10)
