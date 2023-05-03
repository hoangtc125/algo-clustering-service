from enum import Enum
from pydantic import BaseModel, root_validator
from unidecode import unidecode
from datetime import datetime

from app.core.exception import CustomHTTPException


class School(Enum):
    HUST = "HANOI UNIVERSITY OF SCIENCE AND TECHNOLOGY"


class Card(BaseModel):
    school: str
    major: str
    fullname: str
    birth: str
    expired_card: str
    number: str


class CardHUST(Card):
    @root_validator
    def create_email(cls, values):
        print(values)
        if values.get("school", "") != CardHUST.get_detect_guide()["school"]:
            raise CustomHTTPException(error_type="detect_not_support")
        if datetime.today() > datetime.strptime(
            values.get("expired_card", "1/1/2000"), "%d/%m/%Y"
        ):
            raise CustomHTTPException(error_type="detect_out_of_date")
        if not values.get("number", "").isdigit():
            raise CustomHTTPException(error_type="detect_id_failure")
        # Tạo email dựa trên thông tin trong values
        fullname = values.get("fullname", "")
        number = values.get("number", "")
        name_parts = unidecode(fullname).lower().split()
        email = (
            name_parts[-1]
            + "."
            + "".join([item[0] for item in name_parts[:-1]])
            + number[2:]
            + "@sis.hust.edu.vn"
        )
        values["email"] = email
        return values

    @classmethod
    def get_detect_guide(self):
        return {
            "school": "HANOI UNIVERSITY OF SCIENCE AND TECHNOLOGY",
            "fullname": "Họ tên / Name",
            "birth": "Ngày sinh / Date of Birth",
            "expired_card": "Giá trị đến / Valid Thru",
            "number": "MSSV / ID No.",
        }


if __name__ == "__main__":
    print(CardHUST.get_detect_guide())
