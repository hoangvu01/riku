import cv2
import logging
from picamera import PiCamera
from picamera.array import PiRGBArray

logger = logging.getLogger('sys')

class Surveillance:

    def __init__(self, resolution=[640, 380], fps=16, delta_thresh=5, min_area=5000):
        self.resolution = resolution
        self.fps = fps
        self.delta_thresh = delta_thresh
        self.min_area = min_area
        self.observers = []

    def start(self):
        avg = None
        with PiCamera() as camera:
            camera.resolution = tuple(self.resolution)
            camera.framerate = self.fps
            rawCapture = PiRGBArray(camera, size=tuple(self.resolution))

            for f in camera.capture_continuous(
                rawCapture,
                format="bgr",
                use_video_port=True
            ):
                rgb = f.array
                grayscale = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(grayscale, (21, 21), 0)

                if avg is None:
                    avg = blurred.copy().astype("float")
                    rawCapture.truncate(0)

                cv2.accumulateWeighted(blurred, avg, 0.5)
                frameDelta = cv2.absdiff(blurred, cv2.convertScaleAbs(avg))

                thresh = cv2.threshold(frameDelta, self.delta_thresh, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                for c in contours:
                    if cv2.contourArea(c) < self.min_area:
                        continue

                    x, y, w, h = cv2.boundingRect(c)
                    cv2.rectangle(rgb, (x, y), (x+w, y + h), (0, 255, 0), 2)
                    text = "Intruder"
                    cv2.putText(rgb, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                cv2.imshow("Normal", rgb)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

                rawCapture.truncate(0)


    def addObserver(self, observer):
        self.observers.append(observer)

    def notifyObservers(self):
        for obs in self.observers:
            obs.eventTriggered()
