import json
import os
from os import getenv
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
load_dotenv(BASE_DIR + r"/.env")

class ProjectConfig(BaseSettings):
    SERVICE_NAME = getenv("SERVICE_NAME", "ALGO_CLUSTERING")
    STOPWORD_PATH = BASE_DIR + r"/resources/vn_stopword.txt"
    FEATURES_PATH = BASE_DIR + r"/resources/features.txt"
    VISION_CONFIG_PATH = BASE_DIR + r"/resources/cclub-cloud-vision-api.json"
    ALGO_PORT = int(getenv("ALGO_PORT", 8002))
    RESPONSE_CODE_DIR = BASE_DIR + r"/resources/response_code.json"
    MAIL_USER = str(getenv("MAIL_USER", ""))
    MAIL_PASS = str(getenv("MAIL_PASS", ""))


project_config = ProjectConfig()
print("--- Algo Clustering Config:\n", json.dumps(project_config.dict(), indent=4))
