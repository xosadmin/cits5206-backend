import os
import configparser
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def readConf(section, key):
    config_path = "config.ini"
    if not os.path.exists(config_path):
        logger.error(f"Config file {config_path} does not exist")
        raise FileNotFoundError(f"Config file {config_path} does not exist")
    
    config = configparser.ConfigParser()
    config.read(config_path)
    try:
        return config.get(section, key)
    except (configparser.NoSectionError, configparser.NoOptionError) as e:
        logger.error(f"Error reading config: {e}")
        raise
