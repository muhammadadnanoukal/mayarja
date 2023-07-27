# -*- coding: utf-8 -*-
import requests
import json


class MTNCashApi(object):

    def __init__(self):
        self.authenticate_merchant_url = "https://services.mtnsyr.com:2021/authenticateMerchant"
        self.payment_request_url = "https://services.mtnsyr.com:2021/paymentRequestInit"
        self.do_payment_url = "https://services.mtnsyr.com:2021/doPayment"

    def authenticate_merchant(self, username, password, merchantGSM):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        authenticate_merchant_data = f"inputObj={{\"userName\":\"{username}\"," \
                                     f" \"password\":\"{password}\"," \
                                     f" \"merchantGSM\":\"{merchantGSM}\"}}"
        response = None
        try:
            response = requests.post(self.authenticate_merchant_url,
                                     data=authenticate_merchant_data,
                                     headers=headers)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                if response_dict.get('result') == 'True' and response_dict.get('error') == "":
                    return response_dict.get('data').get('token')
                elif response_dict.get('result') == 'False':
                    if response_dict.get('error') == "60000":
                        raise Exception("Other Error !!")
                    elif response_dict.get('error') == "60001":
                        raise Exception("User not found or Password doesn’t match or Invalid IP Address !!")
                    elif response_dict.get('error') == "60002":
                        raise Exception("Failed to generate token !!")
            else:
                raise Exception(f"Error With Status Code {response.status_code}!!")
        except requests.exceptions.HTTPError as errh:
            print("Http Error :", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting :", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error :", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else, ", err)

    def payment_request_init(self, token, customerGSM, amount, bparty_transaction_id):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payment_request_data = f"inputObj={{\"token\":\"{token}\"," \
                               f" \"customerGSM\":\"{customerGSM}\"," \
                               f" \"amount\":\"{amount}\"," \
                               f" \"BpartyTransactionID\":\"{bparty_transaction_id}\"}}"
        response = None
        try:
            response = requests.post(self.payment_request_url, data=payment_request_data,
                                     headers=headers)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                if response_dict.get('result') == 'True' and response_dict.get('error') == "":
                    return True
                elif response_dict.get('result') == 'False':
                    if response_dict.get('error') == "60000":
                        raise Exception("Other Error !!")
                    elif response_dict.get('error') == "60003":
                        raise Exception("Invalid token !!")
                    elif response_dict.get('error') == "60004":
                        raise Exception("Failed to generate OTP !!")
                    elif response_dict.get('error') == "60007":
                        raise Exception("OTP message not sent !!")
                    elif response_dict.get('error') == "60020":
                        raise Exception("User doesn’t have a cash mobile account !!")
            else:
                raise Exception(f"Error With Status Code {response.status_code}!!")
        except requests.exceptions.HTTPError as errh:
            print("Http Error :", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting :", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error :", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else, ", err)

    def do_payment(self, token, otp, bparty_transaction_id):
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        do_payment_data = f"inputObj={{\"token\":\"{token}\", \"OTP\":\"{otp}\", \"BpartyTransactionID\":\"{bparty_transaction_id}\"}}"
        response = None
        try:
            response = requests.post(self.do_payment_url, data=do_payment_data, headers=headers)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                if response_dict.get('result') == 'True' and response_dict.get('error') == "":
                    return True
                elif response_dict.get('result') == 'False':
                    if response_dict.get('error') == "60000":
                        raise Exception("Other Error !!")
                    elif response_dict.get('error') == "60003":
                        raise Exception("Invalid token !!")
                    elif response_dict.get('error') == "60005":
                        raise Exception("Invalid OTP !!")
                    elif response_dict.get('error') == "60015":
                        raise Exception("The sender GSM and receiver GSM are the same !!")
                    elif response_dict.get('error') == "60008":
                        raise Exception("Sender GSM balance is less than transaction amount balance !!")
                    elif response_dict.get('error') == "60018":
                        raise Exception("The receiver GSM is not merchant !!")
                    elif response_dict.get('error') == "60010":
                        raise Exception("The transaction Amount is over the payment transaction limit !!")
                    elif response_dict.get('error') == "60011":
                        raise Exception("Cannot get the transaction Amount from sender GSM !!")
                    elif response_dict.get('error') == "60112":
                        raise Exception("Cannot refund the transaction Amount to sender GSM !!")
                    elif response_dict.get('error') == "60012":
                        raise Exception("Cannot transfer the transaction Amount to receiver GSM !!")
                    elif response_dict.get('error') == "60017":
                        raise Exception("Error while checking balance !!")
                    elif response_dict.get('error') == "60006":
                        raise Exception("Missing parameters !!")
            else:
                raise Exception(f"Error With Status Code {response.status_code}!!")
        except requests.exceptions.HTTPError as errh:
            print("Http Error :", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting :", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error :", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else, ", err)
