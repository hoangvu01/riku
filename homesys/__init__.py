import os
import sys
import yaml
import atexit
import logging
import threading
from flask import Flask
from collections import ChainMap
from homesys.core.surveillance import Surveillance

config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = yaml.safe_load(open(config_path))

for k,v in config.items():
    config[k] = os.environ.get(k, v)


logFormat = '%(asctime)s %(name)s [%(levelname)s]: %(message)s'
logging.basicConfig(
    level=logging.INFO,
    format=logFormat
)
logger = logging.getLogger("pie")
logger.setLevel(config.get("logLevel", logging.INFO))

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter(logFormat))

logger.addHandler(handler)

system = Surveillance(**ChainMap(config["camera"], config["hyperparams"]))

def create_app():
    app = Flask(__name__)
    sysThread = threading.Thread(target=system.start)

    def interrupt():
        sysThread.join(timeout=5)

    sysThread.start()
    atexit.register(interrupt)
    return app

app = create_app()
