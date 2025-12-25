import cv2
import time

# Access the webcam (0 indicates the default camera)
cap = cv2.VideoCapture(0)
# Optional: Set camera window properties (may not work on all systems)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cap.set(cv2.CAP_PROP_AUTOFOCUS, 0)
cap.set(cv2.CAP_PROP_FOCUS, 100)

detector = cv2.QRCodeDetector()

print("Scanner started. Press 'q' to quit.")

while cap.isOpened():
	# Read frames from the camera
	success, img = cap.read()
	start = time.perf_counter()

	value, points, qrcode = detector.detectAndDecode(img)
	if value != "":
		x1 = points[0][0][0]
		y1 = points[0][0][1]
		x2 = points[0][2][0]
		y2 = points[0][2][1]

		xcenter = (x2 - x1) / 2 + x1
		ycenter = (y2 - y1) / 2 + y1

		cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 5)
		cv2.circle(img, (int(xcenter), int(ycenter)), 3, (0, 0, 255), 3)
		cv2.putText(img, str(value), (30, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))

	end = time.perf_counter()
	totalTime = end - start
	fps = 1/totalTime

	cv2.putText(img, f'FPS: {int(fps)}', (30, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0))
	cv2.imshow('img', img)

	if cv2.waitKey(1) & 0xFF == 27:
		break

cap.release()
cv2.destroyAllWindows()
