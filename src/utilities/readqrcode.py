import cv2
from pyzbar.pyzbar import decode
import time


def scan_qr_code():
	# Open the default camera
	cap = cv2.VideoCapture(0)

	if not cap.isOpened():
		print("Cannot open camera")
		return

	print("QR Code scanner is active. Point your camera at a QR code.")
	print("Press 'q' to quit.")

	# Set a time threshold to avoid constant rapid scanning of the same code
	last_scanned_time = 0
	scanned_data_list = []

	while True:
		# Read a frame from the camera
		ret, frame = cap.read()
		if not ret:
			break

		# Decode QR codes from the frame
		decoded_objects = decode(frame)

		print("decoded objects = %d" % len(decoded_objects))

		for obj in decoded_objects:
			# Check if this QR code has been recently scanned
			if obj.data.decode("utf-8") not in scanned_data_list or time.time() - last_scanned_time > 3:
				# Print the data
				print(f"Detected QR Code: {obj.data.decode('utf-8')}")

				# Update last scanned time and list
				last_scanned_time = time.time()
				if obj.data.decode("utf-8") not in scanned_data_list:
					scanned_data_list.append(obj.data.decode("utf-8"))

				# Draw a rectangle around the QR code
				(x, y, w, h) = obj.rect
				cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
				cv2.putText(frame, obj.data.decode("utf-8"), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

		# Display the frame
		cv2.imshow("QR Code Scanner", frame)

		# Break the loop when 'q' is pressed
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break

	# Release the camera and close all OpenCV windows
	cap.release()
	cv2.destroyAllWindows()


if __name__ == "__main__":
	scan_qr_code()