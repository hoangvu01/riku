import cv2
import logging
from time import sleep
from threading import Lock
from picamera import PiCamera
from picamera.array import PiRGBArray

logger = logging.getLogger('sys')
logger.setLevel(logging.INFO)

class Surveillance:


    def __init__(self, visible=False, resolution=[640, 380], fps=16, acc_weight_alpha=0.05, delta_thresh=5, min_area=5000):
        self.resolution = resolution
        self.fps = fps
        self.delta_thresh = delta_thresh
        self.min_area = min_area
        self.acc_weight_alpha = acc_weight_alpha

        self.camera = PiCamera(resolution=tuple(self.resolution), framerate=self.fps)
        self.visible = visible
        self.avg_frame = None
        self.prev_motion = False
        self.prev_frame = None
        self.frame_lock = Lock()
        self.observers = []

    def start(self):
        rawCapture = PiRGBArray(self.camera, size=tuple(self.resolution))

        for f in self.camera.capture_continuous(
            rawCapture,
            format="bgr",
            use_video_port=True
        ):
            self.__process_frame(f)
            ret, buffer = cv2.imencode(".jpg", f.array)
            with self.frame_lock:
                self.prev_frame = buffer.tobytes()

            if self.visible:
                cv2.imshow("Live", f.array)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    cv2.destroyAllWindows()
                    self.visible = False
            rawCapture.truncate(0)

    def generate_frames(self):
        while True:
            sleep(0)
            with self.frame_lock:
                if self.prev_frame is not None:
                    yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + self.prev_frame + b'\r\n')


    def __process_frame(self, frame):
        rgb = frame.array
        grayscale = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(grayscale, (21, 21), 0)

        if self.avg_frame is None:
            self.avg_frame = blurred.copy().astype("float")
            return

        cv2.accumulateWeighted(blurred, self.avg_frame, self.acc_weight_alpha)
        frameDelta = cv2.absdiff(blurred, cv2.convertScaleAbs(self.avg_frame))

        thresh = cv2.threshold(frameDelta, self.delta_thresh, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        motion_detected = False
        for c in contours:
            if cv2.contourArea(c) < self.min_area:
                continue

            motion_detected = True
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(rgb, (x, y), (x+w, y + h), (0, 255, 0), 2)
            text = "Intruder"
            cv2.putText(rgb, "Room Status: {}".format(text), (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        if motion_detected and (not self.prev_motion):
            logger.warning("Intruder alert!")
            self.__notify_observers()

        self.prev_motion = motion_detected


    def add_observer(self, observer):
        self.observers.append(observer)

    def __notify_observers(self):
        for obs in self.observers:
            obs.eventTriggered()
