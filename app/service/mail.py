import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from typing import Dict, List

from app.core.config import project_config
from app.core.exception import CustomHTTPException
from app.util.mail import is_valid_email, EmailContent, make_mail_content_card
from app.model.card import CardHUCE


def make_and_send_mail_card(card: Dict):
    mail_content = make_mail_content_card(card)
    Email(
        receiver_email=card.get("email"),
        subject="Yêu cầu xác thực tài khoản",
        content=mail_content,
    ).send()


class Email:
    def __init__(
        self, receiver_email: str, subject: str, content: EmailContent, cc_email: List = []
    ) -> None:
        if not is_valid_email(receiver_email):
            raise CustomHTTPException(error_type="mail_invalid")
        self.__receiver_email = receiver_email
        self.__message = MIMEMultipart()
        self.__message["From"] = Header(project_config.MAIL_USER, "utf-8")
        self.__message["To"] = Header(receiver_email, "utf-8")
        self.__message['Cc'] = ', '.join(cc_email)
        self.__message["Subject"] = Header(subject, "utf-8")
        self.__message.attach(MIMEText(content, "html", "utf-8"))

    def send(self):
        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.ehlo()
            server.starttls()
            server.login(project_config.MAIL_USER, project_config.MAIL_PASS)
            server.sendmail(
                project_config.MAIL_USER,
                self.__receiver_email,
                self.__message.as_string(),
            )
            print("Email sent successfully!")
        except Exception as e:
            print("Error sending email:", e)
        finally:
            server.quit()


if __name__ == "__main__":
    card = CardHUCE(
        school="NATIONAL UNIVERSITY OF CIVIL ENGINEERING",
        major="Khoa / Faculty. aaaa",
        expired_card="Khóa học / Course: 2011-2033",
        number="MSSV / ID No. 123123",
        email="Email: fffff@nuce.edu.vn",
        major_class="Lớp / Class: sdf",
        fullname="tran cong hoang",
        birth="1/2/2003",
    )
    mail_content = (
        EmailContent()
        .h1("h1")
        .h2("h2")
        .h3("h3")
        .h3("h3")
        .h4("h4")
        .h5("h5")
        .h6("h6")
        .img("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
        .table(card.__dict__)
        .ul([1, 2, 3, 4])
        .make_html()
    )
    print(mail_content)
    Email("hoang.tc194060@sis.hust.edu.vn", "Test", mail_content).send()
