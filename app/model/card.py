from enum import Enum
from pydantic import BaseModel, root_validator
from unidecode import unidecode

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
        # Tạo email dựa trên thông tin trong values
        fullname = values.get('fullname', '')
        number = values.get('number', '')
        name_parts =  unidecode(fullname).lower().split()
        email = name_parts[-1] + "." + "".join([item[0] for item in name_parts[:-1]]) + number[2:] + "@sis.hust.edu.vn"
        values['email'] = email
        return values

if __name__ == "__main__":
    card = CardHUST(school=School.HUST.value, fullname='Nguyen Van A', birth='01/01/2000', expired_card='01/01/2022', number='123456')
    print(card)
