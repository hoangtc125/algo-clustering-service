import os
import base64
import difflib
from google.cloud import vision
from typing import Dict, List

from app.core.config import project_config
from app.core.exception import CustomHTTPException
from app.model.card import CardHUST

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = project_config.VISION_CONFIG_PATH


def file_to_base64(path: str):
    with open(path, "rb") as image_file:
        image_data = image_file.read()
    encoded_image = byte_to_base64(image_data)
    return encoded_image


def byte_to_base64(data):
    return base64.b64encode(data).decode("utf-8")


def detect_info(detect_guide: Dict, info_list: List):
    return {attr: search(info_list, guide) for attr, guide in detect_guide.items()}


def search(info_list: List, value: str):
    match_list = difflib.get_close_matches(value, info_list)
    if not match_list:
        raise CustomHTTPException(error_type="detect_invalid")
    return info_list.index(match_list[0])


def detect_text_from_base64(image_base64: str):
    vision_client = vision.ImageAnnotatorClient()
    image = vision.Image()
    image.content = base64.b64decode(image_base64)
    response = vision_client.text_detection(image=image, timeout=10)
    info_text = response.text_annotations[0].description
    info_list = info_text.split("\n")
    return info_list


def make_card_hust(info_list):
    ids_detect = detect_info(CardHUST.get_detect_guide(), info_list)
    return CardHUST(
        school=info_list[ids_detect["school"]],
        fullname=info_list[ids_detect["fullname"] + 1],
        major=info_list[ids_detect["birth"] + 2],
        birth=info_list[ids_detect["birth"] + 1],
        expired_card=info_list[ids_detect["expired_card"] + 1],
        number=info_list[ids_detect["number"] + 1],
    )


if __name__ == "__main__":
    info_list = detect_text_from_base64(
        file_to_base64(r"C:\Users\ADMIN\Pictures\20194060-Trần Công Hoàng.jpg")
    )
