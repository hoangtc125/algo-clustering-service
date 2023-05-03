import json
import os
import base64
from socket import timeout
from google.cloud import vision
from app.core.config import project_config
from typing import List
from unidecode import unidecode
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = project_config.VISION_CONFIG_PATH

vision_client = vision.ImageAnnotatorClient()

def image_to_base64(path: str):
    with open(path, "rb") as image_file:
        image_data = image_file.read()
    encoded_image = base64.b64encode(image_data).decode("utf-8")
    return encoded_image

def detect_text_from_base64(image_base64: str):
    image = vision.Image()
    image.content = base64.b64decode(image_base64)
    try:
        response = vision_client.text_detection(image=image, timeout=3)
        info_text = response.text_annotations[0].description
        info_list = info_text.split("\n")
        if len(info_list) != 13 or not info_list[12].isdigit():
            raise Exception()
        return info_list
    except:
        return []

def gen_outlook_addr(info_list: List):
    name_parts = unidecode(info_list[3]).lower().split()
    mssv_part = info_list[12][2:]
    return name_parts[-1] + "." + "".join([part[0] for part in name_parts[:-1]]) + mssv_part + "@sis.hust.edu.vn"

if __name__ == "__main__":
    info_list = detect_text_from_base64(
        image_to_base64(r"C:\Users\ADMIN\Pictures\20194060-Trần Công Hoàng.jpg")
    )
    print(gen_outlook_addr(info_list))