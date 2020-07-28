import cv2

import csv
import os

with open('shut_frame.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
    for row in reader:
        time = float(row[0]) * 1000
        cap = cv2.VideoCapture('/Users/hungvngo/Documents/workspace/navigation-app/dataprep/GOPR0224.MP4')
        cap.set(cv2.CAP_PROP_POS_MSEC, time)      # Go to the 1 sec. position
        ret,frame = cap.read()                   # Retrieves the frame at the specified second

        # define the name of the directory to be created
        video_name = 'GOPR0224'
        path = "images/" + video_name

        # define the access rights
        access_rights = 0o755
        try:
            os.makedirs(path, access_rights)
        except OSError:
            print ("Creation of the directory %s failed" % path)
        else:
            print ("Successfully created the directory %s" % path)
        cv2.imwrite(os.getcwd() + '/' + path + "/image" + str(time) + ".jpg", frame)          # Saves the frame as an image