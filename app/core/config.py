import json
import os
from os import getenv
from dotenv import load_dotenv
from pydantic import BaseSettings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))


class ProjectConfig(BaseSettings):
    SERVICE_NAME = getenv("SERVICE_NAME", "ALGO_CLUSTERING")
    STOPWORD_PATH = BASE_DIR + r"/resources/vn_stopword.txt"
    FEATURES_PATH = BASE_DIR + r"/resources/features.txt"


project_config = ProjectConfig()
print("--- Algo Clustering Config:\n", json.dumps(project_config.dict(), indent=4))
