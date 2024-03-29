import cv2 #OpenCV 영상처리

#classifier
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

#video caputure setting
capture = cv2.VideoCapture(0) # initialize, # is camera number
capture.set(cv2.CAP_PROP_FRAME_WIDTH,1280) #CAP_PROP_FRAME_WIDTH == 3
capture.set(cv2.CAP_PROP_FRAME_HEIGHT,720) #CAP_PROP_FRAME_HEIGHT == 4

#console message
face_id = input('\n enter user id end press <return> ==> ')
print("\n [INFO] Initializing face capture. Look the camera and wait ...")

count = 10 # # of caputre face images
#영상 처리 및 출력
while True: 
    ret, frame = capture.read() #카메라 상태 및 프레임
    # cf. frame = cv2.flip(frame, -1) 상하반전
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #흑백으로
    faces = faceCascade.detectMultiScale(
        gray,#검출하고자 하는 원본이미지
        scaleFactor = 1.2, #검색 윈도우 확대 비율, 1보다 커야 한다
        minNeighbors = 6, #얼굴 사이 최소 간격(픽셀)
        minSize=(20,20) #얼굴 최소 크기. 이것보다 작으면 무시
    )

    #얼굴에 대해 rectangle 출력
    for (x,y,w,h) in faces:
        cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
        #inputOutputArray, point1 , 2, colorBGR, thickness)
        count += 1
        cv2.imwrite("dataset/User."+str(face_id)+'.'+str(count)+".jpg",gray[y:y+h, x:x+w])
    cv2.imshow('image',frame)

    #종료 조건
    if cv2.waitKey(1) > 0 : break #키 입력이 있을 때 반복문 종료
    elif count >= 100 : break #100 face sample

print("\n [INFO] Exiting Program and cleanup stuff")

capture.release() #메모리 해제
cv2.destroyAllWindows()#모든 윈도우 창 닫기



import cv2
import numpy as np #배열 계산 용이
from PIL import Image #python imaging library
import os

path = r'dataset' #경로 (dataset 폴더)
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]
    #listdir : 해당 디렉토리 내 파일 리스트
    #path + file Name : 경로 list 만들기

    faceSamples = []
    ids = []
    for imagePath in imagePaths: #각 파일마다
        #흑백 변환
        PIL_img = Image.open(imagePath).convert('L') #L : 8 bit pixel, bw
        img_numpy = np.array(PIL_img, 'uint8')

        #user id
        id = int(os.path.split(imagePath)[-1].split(".")[1])#마지막 index : -1

        #얼굴 샘플
        faces = detector.detectMultiScale(img_numpy)
        for(x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)

    return faceSamples, ids

print('\n [INFO] Training faces. It will take a few seconds. Wait ...')
faces, ids = getImagesAndLabels(path)

recognizer.train(faces,np.array(ids)) #학습

recognizer.write('trainer/trainer.yml')

print('\n [INFO] {0} faces trained. Exiting Program'.format(len(np.unique(ids))))


import cv2
import numpy as np

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainer/trainer.yml')
cascadePath = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
faceCascade = cv2.CascadeClassifier(cascadePath)

font = cv2.FONT_HERSHEY_SIMPLEX

id = 0

names = ['None','jinsu','minsuk','boguk']

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1980)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

minW = 0.1 * cam.get(cv2.CAP_PROP_FRAME_WIDTH)
minH = 0.1 * cam.get(cv2.CAP_PROP_FRAME_HEIGHT)

while True:
    ret, img = cam.read()
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.2,
        minNeighbors=6,
        minSize=(int(minW), int(minH))
    )

    for(x,y,w,h) in faces:
        cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0),2)
        id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

        if confidence < 55 :
            id = names[id]
        else:
            id = "unknown"
        
        confidence = "  {0}%".format(round(100-confidence))

        cv2.putText(img,str(id), (x+5,y-5),font,1,(255,255,255),2)
        cv2.putText(img,str(confidence), (x+5,y+h-5),font,1,(255,255,0),1)
    
    cv2.imshow('camera',img)
    if cv2.waitKey(1) > 0 : break

print("\n [INFO] Exiting Program and cleanup stuff")
cam.release()
cv2.destroyAllWindows()