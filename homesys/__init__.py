import os
import sys
import yaml
import logging

config_path = os.path.join(os.path.dirname(__file__), "config.yaml")
config = yaml.safe_load(open(config_path))

for k,v in config.items():
    config[k] = os.environ.get(k, v)

logger = logging.getLogger("pie")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
