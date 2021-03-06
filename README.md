## Basic IP Camera (Pi & PiCamera)

__Requirements__:
1. Raspberry Pi (Raspbian OS)
2. PiCamera Module
3. Internet Connection

### Overview

Basic set up and demonstration of how you can build your own home surveillance with minimum equipments. 
First, we need to implement a motion detector using our camera module. This can easily be done with a simple implementation 
using accumulated weighted mean of the colour ranges. Then, we livestream this video using the streaming capabilities of Flask.

### Usage

**IMPORTANT** - Only use this for learning purposes and do NOT expose this webserver to the outside world before implementing proper 
authentication. Failure to do so may put your security at risk !

Move to the root of this repository, create a virtual environment and install required packages:
```
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
```

Start the web server:
```
gunicorn -b 0.0.0.0:5000 homesys.app:app
```

From the web browser (on this machine or another machine connected to the same network), visit `http://<ip_web_server>:5000` to view your webcam.

### Further ideas

1. UDP: Since we are running on a single board, comparatively slow machine, we might want to improve the streaming performance by using UDP instead of TCP for the live streaming. 
2. Authentication: Implement authentication so you can safely stream this while away from home!
3. Multi-cam setup: What if you're running multiple cameras ? Try de-coupling the cameras and the web server. One idea might be to have a dedicated that _receives_ cameara video streams and _exposes_ these streams to users so that the cameras will now only need to send footage to the server (and not the user).


### References

1. Motion detector with openCV and Pi - [https://pyimagesearch.com/2015/06/01/home-surveillance-and-motion-detection-with-the-raspberry-pi-python-and-opencv/]
