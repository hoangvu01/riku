import logging
from homesys.app import app
from homesys import config

logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    app.run(**config["server"])
