import os
import yaml
from utils.logger import logging

from typing import List, Dict, AsyncGenerator

def load_yaml_config(file_path: str) -> Dict:
    """Loads configuration from a YAML file."""
    if not os.path.exists(file_path):
        logging.error(f"Configuration file '{file_path}' not found.")
        raise FileNotFoundError(f"Configuration file '{file_path}' not found.")
    
    logging.info(f"Loading configuration from '{file_path}'...")
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)
    logging.info(f"Configuration loaded successfully.")
    return config

