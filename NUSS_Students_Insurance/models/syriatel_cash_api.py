# -*- coding: utf-8 -*-
import requests
import json


class SyriatelCashApi(object):

    def __init__(self):
        self.get_token_url = "https://Merchants.syriatel.sy:1443/ePayment_external_Json/rs/ePaymentExternalModule/getToken/"
        self.payment_request_url = "https://Merchants.syriatel.sy:1443/ePayment_external_Json/rs/ePaymentExternalModule/paymentRequest/"
        self.payment_confirmation_url = "https://Merchants.syriatel.sy:1443/ePayment_external_Json/rs/ePaymentExternalModule/paymentConfirmation/"
        self.resend_OTP_url = "https://Merchants.syriatel.sy:1443/ePayment_external_Json/rs/ePaymentExternalModule/resendOTP/"

    def get_token(self, username, password):
        headers = {
            "key": "Content-Type",
            "value": "application/json"
        }
        get_token_params = {
            "username": username,
            "password": password,
        }
        response = None
        try:
            response = requests.post(self.get_token_url, json=get_token_params, headers=headers)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                if response_dict.get('errorCode') == '0':
                    return response_dict.get('token')
                elif response_dict.get('errorCode') == '-100' or \
                        response_dict.get('errorCode') == '-101' or \
                        response_dict.get('errorCode') == '-102':
                    raise Exception("General Error In Generating Token!!")
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

    def payment_request(self, customerMSISDN, merchantMSISDN, amount, transaction_id, token):
        headers = {
            "key": "Content-Type",
            "value": "application/json"
        }
        payment_request_params = {
            "customerMSISDN": customerMSISDN,
            "merchantMSISDN": merchantMSISDN,
            "amount": amount,
            "transactionID": transaction_id,
            "token": token,
        }
        response = None
        try:
            response = requests.post(self.payment_request_url, json=payment_request_params, headers=headers)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                if response_dict.get('errorCode') == '0':
                    return True
                elif response_dict.get('errorCode') == '-3':
                    raise Exception(
                        "Invalid amount (the amount is negative or it contains comma, symbols or characters !!")
                elif response_dict.get('errorCode') == '-7':
                    raise Exception("Merchant MSISDN is not active !!")
                elif response_dict.get('errorCode') == '-10':
                    raise Exception("Merchant MSISDN does not have merchant wallet !!")
                elif response_dict.get('errorCode') == '-98':
                    raise Exception("Expired transaction (10 minutes have been passed) !!")
                elif response_dict.get('errorCode') == '-99':
                    raise Exception("one or more parameters are null !!")
                elif response_dict.get('errorCode') == '-100':
                    raise Exception("Technical error !!")
                elif response_dict.get('errorCode') == '-101':
                    raise Exception("Duplicated transaction id with different parameters !!")
                elif response_dict.get('errorCode') == '-102':
                    raise Exception("The caller IP or merchant MSISDN is not defined !!")
                elif response_dict.get('errorCode') == '-500':
                    raise Exception("The token is invalid !!")
            else:
                raise Exception(f"Error With Status Code {response.status_code}!!")
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)

    def payment_confirmation(self, OTP, merchantMSISDN, transactionID, token):
        headers = {
            "key": "Content-Type",
            "value": "application/json"
        }
        payment_confirmation_params = {
            "OTP": OTP,
            "merchantMSISDN": merchantMSISDN,
            "transactionID": transactionID,
            "token": token,
        }
        response = None
        try:
            response = requests.post(self.payment_confirmation_url, json=payment_confirmation_params, headers=headers)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                if response_dict.get('errorCode') == '0':
                    return True
                elif response_dict.get('errorCode') == '-6':
                    raise Exception("Customer MSISDN is not active !!")
                elif response_dict.get('errorCode') == '-8':
                    raise Exception("Customer MSISDN doesn’t have customer wallet !!")
                elif response_dict.get('errorCode') == '-13':
                    raise Exception("Customer MSISDN doesn’t have enough balance !!")
                elif response_dict.get('errorCode') == '-17':
                    raise Exception("Customer MSISDN will exceed the expenditure limit per day which is 100,000 SYP !!")
                elif response_dict.get('errorCode') == '-96':
                    raise Exception("Invalid OTP !!")
                elif response_dict.get('errorCode') == '-98':
                    raise Exception("Expired transaction (1 day has been passed) !!")
                elif response_dict.get('errorCode') == '-99':
                    raise Exception("One or more parameters are null !!")
                elif response_dict.get('errorCode') == '-100':
                    raise Exception("Technical error !!")
                elif response_dict.get('errorCode') == '-101':
                    raise Exception("Duplicated transaction id with different parameters!!")
                elif response_dict.get('errorCode') == '-102':
                    raise Exception("The caller IP or merchant MSISDN is not defined !!")
                elif response_dict.get('errorCode') == '-103':
                    raise Exception("Technical error in adding amount to merchant account.\n"
                                    "Customer deserves a refund from Syriatel side !!")
                elif response_dict.get('errorCode') == '-104':
                    raise Exception("Expired OTP !!")
            else:
                raise Exception(f"Error With Status Code {response.status_code}!!")
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)

    def resend_OTP(self, merchantMSISDN, transactionID, token):
        headers = {
            "key": "Content-Type",
            "value": "application/json"
        }
        resend_OTP_params = {
            "merchantMSISDN": merchantMSISDN,
            "transactionID": transactionID,
            "token": token,
        }
        response = None
        try:
            response = requests.post(self.resend_OTP_url, json=resend_OTP_params, headers=headers)
            if response.status_code == 200:
                response_dict = json.loads(response.text)
                if response_dict.get('errorCode') == '0':
                    return True
                elif response_dict.get('errorCode') == '-97':
                    raise Exception("Invalid or expired transaction !!")
                elif response_dict.get('errorCode') == '-98':
                    raise Exception("Expired transaction (10 minutes have been passed) !!")
                elif response_dict.get('errorCode') == '-99':
                    raise Exception("One or more parameters are null !!")
                elif response_dict.get('errorCode') == '-100':
                    raise Exception("Technical error !!")
                elif response_dict.get('errorCode') == '-102':
                    raise Exception("The caller IP or merchant MSISDN is not defined !!")
                elif response_dict.get('errorCode') == '-500':
                    raise Exception("The token is invalid !!")
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
