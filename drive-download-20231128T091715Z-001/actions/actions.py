# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

from termcolor import colored
import pandas as pd
import csv

ALLOWED_PIZZA_SIZES = [
    "small",
    "medium",
    "large",
    "extra-large",
    "extra large",
    "s",
    "m",
    "l",
    "xl",
]
ALLOWED_PIZZA_TYPES = ["mozzarella", "fungi", "veggie", "pepperoni", "hawaii"]
VEGETARIAN_PIZZAS = ["mozzarella", "fungi", "veggie"]
MEAT_PIZZAS = ["pepperoni", "hawaii"]

class ActionAccountLoginMessage(Action):
    def name(self) -> Text:
        """Unique identifier of the form"""
        return "action_account_login_message"


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if str(tracker.get_slot("cust_sex")) == "None":
            text = "Quý khách vui lòng đăng nhập tài khoản - mật khẩu để thực hiện các dịch vụ của ngân hàng!"
        else:
            text = "{} vui lòng đăng nhập tài khoản - mật khẩu để thực hiện các dịch vụ của ngân hàng!".format(tracker.get_slot("cust_sex"))
        buttons = [
            {"payload": "/affirm", "title": "Có"},
            {"payload": "/deny", "title": "Không"},
        ]

        dispatcher.utter_message(text=text, buttons=buttons)
        return []

class ActionBankTransferMessage(Action):
    def name(self) -> Text:
        """Unique identifier of the form"""
        return "action_bank_transfer_message"


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if str(tracker.get_slot("cust_sex")) == "None":
            text = "Quý khách muốn thực hiện chức năng chuyển tiền nào?"
        else:
            text = "{} muốn thực hiện chức năng chuyển tiền nào?".format(tracker.get_slot("cust_sex"))
        buttons = [
            {"payload": "/samebank_transfer", "title": "Cùng Ngân Hàng"},
            {"payload": "/interbank_transfer", "title": "Liên Ngân Hàng"},
        ]

        dispatcher.utter_message(text=text, buttons=buttons)
        return []

class ActionCheckAccountInDataBase(Action):
    def name(self) -> Text:
        """Unique identifier of the form"""
        return "action_check_account_in_database"


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # text = "Cảm ơn! Số tài khoản - mật khẩu của bạn là {} {}. Vui lòng đợi bot check số dư nhé!".format(tracker.get_slot("account_number", "password"))
        account_number = tracker.get_slot("account_number")
        password = tracker.get_slot("password")

        text_one = "Cảm ơn! Số tài khoản - mật khẩu của bạn là {} - {}. Vui lòng đợi bot check số dư nhé!".format(account_number, password)
        dispatcher.utter_message(text=text_one)

        #Check database
        data = pd.read_csv('Data_Bank.csv')
        dataset_bank = data.to_numpy()
        text = "Bot không thể check số dư. Quý khách vui lòng điền lại tài khoản - mật khẩu."
        check = False
        for i, row in enumerate(dataset_bank):
            account_number_check, password_check, name, so_du = row[0], row[1], row[2], row[3]
            if str(account_number_check) == str(account_number) and str(password_check) == str(password):
                text_true = "Quý Khách {} có số dư trong tài khoản ngân hàng là {}!".format(str(name), str(so_du))
                text = text_true
                check = True
        dispatcher.utter_message(text=text)
        if check is False:
            text_two = "Quý khách có muốn đăng nhập lại không?"
            buttons = [
                {"payload": "/cust_sign_in", "title": "Có"},
                {"payload": "/deny", "title": "Không"},
            ]
            dispatcher.utter_message(text=text_two, buttons=buttons)
        return [SlotSet("account_number", None), SlotSet("password", None)]


class ActionCreateAccountInDataBase(Action):
    def name(self) -> Text:
        """Unique identifier of the form"""
        return "action_create_account_in_database"


    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        account_number = tracker.get_slot("account_number")
        password = tracker.get_slot("password")
        name = tracker.get_slot("name")

        text_one = "Cảm ơn! Số tài khoản - mật khẩu - tên chủ thẻ của bạn là {} - {} - {}. Bot sẽ tạo tài khoản cho quý khách ngay!".format(account_number, password, name)
        dispatcher.utter_message(text=text_one)

        #Check database
        data = pd.read_csv('Data_Bank.csv')
        dataset_bank = data.to_numpy()
        text = "Số tài khoản của quý khách đã bị trùng trong dữ liệu. Quý khách vui lòng điền lại tài khoản - mật khẩu - tên chủ thẻ."
        check = False
        for i, row in enumerate(dataset_bank):
            account_number_check, _, _, _ = row[0], row[1], row[2], row[3]
            if str(account_number_check) == str(account_number):
                check = True
        if check is True:
            dispatcher.utter_message(text=text)
        if check is False:
            # Save row in database
            data_account = {'Số tài khoản': str(account_number), 'Mật Khẩu': str(password), 'Tên chủ thẻ': str(name), 'Số dư': str(0)}
            data_new = data.append(data_account, ignore_index=True)
            data_new.to_csv('Data_Bank.csv', header=True, index=False)

            text_true = "Tạo tài khoản thành công!"
            text = text_true
            dispatcher.utter_message(text=text)

            text_two = "Quý khách có muốn đăng nhập không?"
            buttons = [
                {"payload": "/cust_sign_in", "title": "Có"},
                {"payload": "/deny", "title": "Không"},
            ]
            dispatcher.utter_message(text=text_two, buttons=buttons)
        return [SlotSet("account_number", None), SlotSet("password", None), SlotSet("name", None)]



class ActionListServiceName(Action):
    def name(self) -> Text:
        return "action_list_service_name"

    def run(self, dispatcher, tracker: Tracker, domain: "DomainDict") -> List[Dict[Text, Any]]:
        text = "Gửi quý khách danh sách dịch vụ:"
        message = {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": "Thông báo số dư",
                        "subtitle": "Số dư hiện tại đang có:",
                        "image_url": "static/image_rasa/sodutaikhoan.jpg",
                        "buttons": [
                            {
                                "title": "Xem số dư",
                                "payload": "/check_money",
                                "type": "postback"
                            },
                            {
                                "title": "Tìm hiểu thêm",
                                "payload": "/information_banking_check_money",
                                "type": "postback"
                            }
                        ]
                    },

                    {
                        "title": "Chuyển khoản",
                        "subtitle": "Chức năng chuyển khoản của banking:",
                        "image_url": "static/image_rasa/chuyentien.jpg",
                        "buttons": [
                            {
                                "title": "Cùng ngân hàng",
                                "payload": "/samebank_transfer",
                                "type": "postback"
                            },
                            {
                                "title": "Liên ngân hàng",
                                "payload": "/interbank_transfer",
                                "type": "postback"
                            },
                            {
                                "title": "Tìm hiểu thêm",
                                "payload": "/information_banking_transfer",
                                "type": "postback"
                            },
                        ]
                    },

                    {
                        "title": "Đăng nhập tài khoản",
                        "subtitle": "Tạo mới:",
                        "image_url": "static/image_rasa/dangnhap.png",
                        "buttons": [
                            {
                                "title": "Đăng nhập tài khoản",
                                "payload": "/cust_sign_in",
                                "type": "postback"
                            },
                            {
                                "title": "Tìm hiểu thêm",
                                "payload": "/information_log_in",
                                "type": "postback"
                            },
                        ]
                    },

                    {
                        "title": "Đăng ký tài khoản",
                        "subtitle": "Tạo mới:",
                        "image_url": "static/image_rasa/dangki.jpg",
                        "buttons": [
                            {
                                "title": "Tạo tài khoản",
                                "payload": "/create_account",
                                "type": "postback"
                            },
                            {
                                "title": "Tìm hiểu thêm",
                                "payload": "/information_banking_create_account",
                                "type": "postback"
                            },
                        ]
                    },

                    {
                        "title": "Thông tin về ngân hàng",
                        "subtitle": "Các chính sách, khuyến mại, ...:",
                        "image_url": "static/image_rasa/thôngtinnganhang.jpg",
                        "buttons": [
                            {
                                "title": "Tìm hiểu thêm",
                                "url": "https://www.mbbank.com.vn/",
                                "type": "web_url"
                            },
                        ]
                    }
                ]
            }
        }
        dispatcher.utter_message(text=text, attachment=message)
        return []