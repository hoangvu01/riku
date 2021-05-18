import sys
import logging
from homesys import config, logger
from homesys.surveillance import Surveillance


if __name__ == '__main__':
    logger.info("Initiating cctv...")
    system = Surveillance(**config["camera"], **config["hyperparams"])
    system.start()
