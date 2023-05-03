from enum import Enum
import requests
from fastapi import APIRouter, Query

from app.core.model import HttpResponse, success_response
from app.core.api import DetectAPI
from app.core.exception import CustomHTTPException
from app.text_detection import (
    detect_text_from_base64,
    file_to_base64,
    make_card_huce,
    make_card_hust,
    byte_to_base64,
)


class School(str, Enum):
    HUST = "HUST"
    HUCE = "HUCE"


router = APIRouter()


@router.get("/detect/test-file", response_model=HttpResponse)
async def test_file(school: School = Query(...)):
    if school == School.HUST.value:
        file_path = r"/media/hoangtc125/Windows/Users/ADMIN/Pictures/20194060-Trần Công Hoàng.jpg"
        info_list = detect_text_from_base64(file_to_base64(file_path))
        card = make_card_hust(info_list)
    elif school == School.HUCE.value:
        file_path = r"/home/hoangtc125/Downloads/6447cd41859a5ac4038b.jpg"
        info_list = detect_text_from_base64(file_to_base64(file_path))
        card = make_card_huce(info_list)
    return success_response(data=card)


@router.get("/detect/test-cam", response_model=HttpResponse)
async def test_cam(school: School = Query(...)):
    url = "http://192.168.1.13:8080/photo.jpg"
    try:
        response = requests.get(url, timeout=2)
    except:
        raise CustomHTTPException(error_type="cam_timeout")
    img_data = response.content
    info_list = detect_text_from_base64(byte_to_base64(img_data))
    if school == School.HUST.value:
        card = make_card_hust(info_list)
    elif school == School.HUCE.value:
        card = make_card_huce(info_list)
    return success_response(data=card)
