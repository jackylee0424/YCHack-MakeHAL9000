import os
import subprocess
import cv2
import thread


found_objects = []


def detectFaces(img, cascade):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    rects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60), flags = 0)
    if rects.any():
        rects[:, 2:] += rects[:, :2]

    for f in rects:
        x1, y1, x2, y2 = f
        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 1)


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
        detectFaces(img, cascade)
        if counter % 120 == 1:
        	cv2.imwrite("tmp.jpg", img)
        	thread.start_new_thread(objectrecog,())
        cv2.putText(img, "" if not any(found_objects) else found_objects[0], (20, 400), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 0), thickness=1, lineType=cv2.CV_AA)
        cv2.imshow("camera", img)
        counter += 1
        key = cv2.waitKey(10)
