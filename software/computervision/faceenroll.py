import os
import cv2
import time

biggest_face = None


def detectFaces(img, cascade):
    global biggest_face
    # convert to gray color to save some processing time
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    rects = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60), flags = 0)

    # if there is no faces found, use the previous detected faces saved in global list
    if rects.any():
        rects[:, 2:] += rects[:, :2]

    for f in rects:
        biggest_face = f
        break


if __name__ == "__main__":

    cascade = cv2.CascadeClassifier(os.path.join("xml", "haarcascade_frontalface_alt.xml"))
    cam = cv2.VideoCapture(0)
    counter = 0
    dir_name = "%.0f" % (time.time() * 1000.0)  # save face images to dir
    if not os.path.exists(os.path.join("data", "faces", dir_name)):
        os.makedirs(os.path.join("data", "faces", dir_name))

    face_file_counter = 0
    
    while face_file_counter < 10:
        ret, img = cam.read()
        detectFaces(img, cascade)
        if biggest_face is not None:
            x1, y1, x2, y2 = biggest_face
            if counter % 10 == 9:
                fname = "%.0f" % (time.time() * 1000.0)
                fullpath = os.path.join("data", "faces", dir_name, fname + ".jpg")
                cv2.imwrite(fullpath, img[y1:y2, x1:x2])
                face_file_counter += 1
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 1)

        cv2.imshow("camera", img)
        counter += 1
        key = cv2.waitKey(10)
    print "face enroll complete."
