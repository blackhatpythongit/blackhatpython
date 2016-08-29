import cv2
import os
import sys

def face_detect(image_path):
	img = cv2.imread(image_path)
	cascade = cv2.CascadeClassifier("haarcascade_frontalface_alt.xml")
	rects = cascade.detectMultiScale(img, 1.3, 4, cv2.cv.CV_HAAR_SCALE_IMAGE, (20, 20))
	if len(rects) == 0:
		return False
	rects[:,2:] += rects[:,:2]
	# highlight the faces in the image
	for x1, y1, x2, y2 in rects:
		cv2.rectangle(img,(x1, y1),(x2, y2),(127, 255, 0), 2)
	cv2.imwrite("result%s" % os.path.splitext(image_path)[1], img)
	return True

if __name__ == "__main__":
	if len(sys.argv)!= 2:
		print "[*] Usage:%s image_path" % sys.argv[0]
	else:
		print face_detect(sys.argv[1])
