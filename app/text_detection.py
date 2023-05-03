import os
import base64
import re
from google.cloud import vision
from datetime import datetime

from app.core.config import project_config
from app.core.exception import CustomHTTPException
from app.model.card import School, CardHUST
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = project_config.VISION_CONFIG_PATH


vision_client = vision.ImageAnnotatorClient()

def file_to_base64(path: str):
    with open(path, "rb") as image_file:
        image_data = image_file.read()
    encoded_image = byte_to_base64(image_data)
    return encoded_image

def byte_to_base64(data):
    return base64.b64encode(data).decode("utf-8")

def detect_text_from_base64(image_base64: str):
    image = vision.Image()
    image.content = base64.b64decode(image_base64)
    response = vision_client.text_detection(image=image, timeout=10)
    info_text = response.text_annotations[0].description
    info_list = info_text.split("\n")
    if School.HUST.value not in info_list:
        raise CustomHTTPException(error_type="detect_not_support")
    check_list = [id_item for id_item, item in enumerate(info_list) if re.match(r"^[^/]*\/[^/]*$", item)]
    print(check_list)
    if len(check_list) != 4:
        raise CustomHTTPException(error_type="detect_invalid")
    if datetime.today() > datetime.strptime(info_list[check_list[2] + 1], '%d/%m/%Y'):
        print(info_list[check_list[2] + 1])
        raise CustomHTTPException(error_type="detect_out_of_date")
    if not info_list[-1].isdigit():
        raise CustomHTTPException(error_type="detect_id_failure")
    return CardHUST(
                school=School.HUST.value,
                fullname=info_list[check_list[0] + 1],
                major=info_list[check_list[1] + 2],
                birth=info_list[check_list[1] + 1],
                expired_card=info_list[check_list[2] + 1],
                number=info_list[check_list[3] + 1],
            )

if __name__ == "__main__":
    info_list = detect_text_from_base64(
        file_to_base64(r"C:\Users\ADMIN\Pictures\20194060-Trần Công Hoàng.jpg")
    )