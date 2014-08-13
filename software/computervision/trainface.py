import sys
import os
import cv2
from tinyfacerec.util import read_cvimages
from tinyfacerec.model import EigenfacesModel
from tinyfacerec.model import FisherfacesModel
from tinyfacerec.distance import CosineDistance
import pickle
import time

if __name__ == '__main__':

    ## read images
    t = time.time()
    [X,y,z] = read_cvimages(os.path.join("data", "faces"))

    ## save to matrix data
    with open(os.path.join("data", 'mat.data'), 'wb') as output:
        pickle.dump({'X': X, 'y':y, 'z':z}, output, pickle.HIGHEST_PROTOCOL)

    with open(os.path.join("data", 'mat.data'), 'rb') as input:
        matdata = pickle.load(input)
    print matdata['z']

    t = time.time()
    model_eigen = EigenfacesModel(matdata['X'][1:], matdata['y'][1:], dist_metric = CosineDistance())
    model_fisher = FisherfacesModel(matdata['X'][1:], matdata['y'][1:], dist_metric = CosineDistance())

    with open(os.path.join("data", 'data.bin'), 'wb') as output:
        pickle.dump(dict(eigen=model_eigen, fisher=model_fisher), output, pickle.HIGHEST_PROTOCOL)


    print "testing prediction.."

    with open(os.path.join("data", 'data.bin'), 'rb') as input:
        mmodel = pickle.load(input)
    test_img = cv2.imread(os.path.join("data", "face.jpg"))
    test_img  = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
    test_img = cv2.resize(test_img, (128, 128), interpolation=cv2.INTER_CUBIC)
    t = time.time()
    output_name, min_dist =  mmodel["eigen"].predict(test_img,-.5)
    print "predicted (eigen)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)
    t = time.time()
    output_name, min_dist =  mmodel["fisher"].predict(test_img,-.5)
    print "predicted (fisher)= %s (%f). took %.3f ms"%(matdata["z"][output_name], min_dist,(time.time()-t)*1000.)

