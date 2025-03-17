import os
import yaml
from utils.logger import logging

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPENAPI_PATH = os.path.join(BASE_DIR, 'docs', 'openapi.yaml')

def load_yaml_config(config_path):
    """
    Load YAML configuration file
    """
    try:
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except Exception as e:
        logging.error(f"Failed to load configuration from {config_path}: {e}")
        raise
    
def load_openapi_spec(file_path:str):
    try:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"OpenAPI specification not found at {file_path}")
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing OpenAPI specification: {e}")
        return None
    
openapi_spec = load_openapi_spec(OPENAPI_PATH)
