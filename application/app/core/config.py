from parameters import CONFIG_PATH
from utils.logger import logging
from utils.load_config import load_yaml_config
from dotenv import load_dotenv

try:
    config = load_yaml_config(CONFIG_PATH)
except Exception as e:
    logging.error(f"Failed to load configuration: {e}")
    raise

# Configuration Parameters
class Config:
    def __init__(self):
        try:

            _ = load_dotenv()
            self.LLM_MODEL = config["llm"]["model"]
            self.LLM_TEMPERATURE = config["llm"]["temperature"]
            self.CSV_FILE = config["files"]["csv_file"]
            self.TEST_CASE_TEMPLATE = config["templates"]["test_case"]
            self.TEST_DATA_PROMPT = config["templates"]["test_data_prompt"]
            self.SESSION_TIMEOUT = config.get("session", {}).get("timeout", 3600)  # Default 1 hour in seconds
        except Exception as e:
            logging.error(f"Configuration initialization failed: {e}")
            raise

config = Config()