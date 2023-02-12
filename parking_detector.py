import cv2
import pickle
import cvzone
import numpy as np

def checkParkingSpace(imgPro, img, posList):
    '''
    checks parking space
    '''
    spaceCounter = 0
 
    for pos in posList:
        
        p1,p2,p3,p4 = pos
 
        # imgCrop = imgPro[y:y + height, x:x + width]

        # get polygon section of image
        imgCrop = imgPro[p1[1]:p3[1], p1[0]:p3[0]]
        count = cv2.countNonZero(imgCrop)
 
 
        if count < 800:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1
        else:
            color = (0, 0, 255)
            thickness = 2
 
        # cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cv2.fillPoly(img, np.array([pos]), color)
        center = (p1[0] + int((p3[0] - p1[0]) / 2), p1[1] + int((p3[1] - p1[1]) / 2))
        cvzone.putTextRect(img, f'{count}', center, scale=1, thickness=2, offset=10)
 
    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(0,200,0))

def detector(video=r'static\uploads\videos\carPark.mp4', posfile='asd'):
    print("video", video)
    print("posfile", posfile)

    if video == '0':
        video = 0
    
    cap = cv2.VideoCapture(video)
    with open(posfile, 'rb') as f:
        posList = pickle.load(f)
    
    while True:
    
        if cap.get(cv2.CAP_PROP_POS_FRAMES) == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        success, img = cap.read()
        bg  = img.copy()
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
        imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY_INV, 25, 16)
        imgMedian = cv2.medianBlur(imgThreshold, 3)
        kernel = np.ones((3, 3), np.uint8)
        imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
    
        checkParkingSpace(imgDilate,img, posList)
        cv2.addWeighted(bg, 0.5, img, 0.5, 0, img)
        cv2.imshow("dilate", imgDilate)
        cv2.imshow("I", img)
        cv2.imshow("median", imgMedian)
        if cv2.waitKey(10) == 27:
            break
    cap.release()
    cv2.destroyAllWindows()    


if __name__ == "__main__":
    detector(video=r'static/videos/vid3.mp4', posfile=r'parking_lulu_mall')