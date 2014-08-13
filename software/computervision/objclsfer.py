import os
import subprocess
import cv2
import thread
import pickle
import time

biggest_face = None
found_objects = []
with open(os.path.join("data", 'data.bin'), 'rb') as input:
    mmodel = pickle.load(input)
with open(os.path.join("data", 'mat.data'), 'rb') as input:
    matdata = pickle.load(input)

def detectFaces(img, cascade):
    global mmodel, matdata
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
        output_name, min_dist =  mmodel["eigen"].predict(test_img,-.5)
        print "predicted (eigen)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)
        t = time.time()
        output_name, min_dist =  mmodel["fisher"].predict(test_img,-.5)
        print "predicted (fisher)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)
        break


def objectrecog():
	global found_objects

	## super slow 4~5 sec
	cmd = "~/code/overfeat/bin/macos/overfeat -n 6 tmp.jpg"
	print "recogizing objects..."
	process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
	stdoutput = process.stdout.read()
	if stdoutput:
		found_objects = stdoutput.strip().split("\n")
		print found_objects


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
        cv2.putText(img, "" if not any(found_objects) else found_objects[0], (20, 400), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), thickness=1, lineType=cv2.CV_AA)
        cv2.imshow("camera", img)
        counter += 1
        key = cv2.waitKey(10)
