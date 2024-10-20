# coding: utf-8

import cv2


# Crear captura de video usando el pipeline de GStreamer
gstformat = "NV12"
str = "/dev/video50"
cap = cv2.VideoCapture("v4l2src device=" + str + " ! video/x-raw,format=" + gstformat + ",width=3840,height=2160,framerate=30/1 ! videoconvert ! appsink")
if not cap.isOpened():
    print("Error al abrir la camara")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error al leer el frame")
        break

    # Aquí puedes procesar el frame con OpenCV
    #cv2.imshow('Frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()