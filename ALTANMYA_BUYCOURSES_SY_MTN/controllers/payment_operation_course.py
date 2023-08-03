import math

from odoo import http, _
from odoo.http import request
import base64
from datetime import datetime
import json
import string
import uuid
from bs4 import BeautifulSoup
from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo import http
import hashlib
import string
import numbers
from .syriatel_cash_api import SyriatelCashApi
from .mtn_cash_api import MTNCashApi
from .request_states import UserInsuranceState

from odoo.http import request
from werkzeug.utils import redirect


class paymentoperationC(http.Controller):
    def handle_status(self, user_request_status):
        print(' handle_status==>')
        if user_request_status in [UserInsuranceState.NO_REQUEST, UserInsuranceState.REQUEST_TYPE_1,
                                   UserInsuranceState.REQUEST_TYPE_2]:
            return self._render_insurance_form(user_request_status)
        elif user_request_status == UserInsuranceState.BOTH_PAYMENT_REQUIRED:
            return self._render_status_message(message=user_request_status,
                                               message_body=_(
                                                   "You have insurance fees for two requests need to be paid!"))
        elif user_request_status == UserInsuranceState.PAYMENT_REQUIRED:
            return self._render_status_message(message=user_request_status,
                                               message_body=_("You have to pay the insurance fees!"))
        elif user_request_status == UserInsuranceState.CANT_MAKE_REQUEST:
            return self._render_status_message(message=user_request_status,
                                               message_body=_("You can't make any new requests!"))
        elif user_request_status == UserInsuranceState.ONE_WAITING:
            return self._render_status_message(message=user_request_status,
                                               message_body=_("You have one waiting request!"))
        elif user_request_status == UserInsuranceState.BOTH_WAITING:
            return self._render_status_message(message=user_request_status,
                                               message_body=_("You have two waiting requests!"))

    def _render_status_message(self, message, message_body,soo_id):
        if message in [UserInsuranceState.PAYMENT_REQUIRED, UserInsuranceState.BOTH_PAYMENT_REQUIRED]:
            # print(' _render_status_message if==>', message)
            return request.render("ALTANMYA_BUYCOURSES_SY_MTN.portal_insurance_messageC",
                                  {'main_title': _("Payment Required"),
                                   'alert_type': "success",
                                   'message': message_body,
                                   'page_url': '/slides',
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.CANT_MAKE_REQUEST:
            print(' _render_status_message else==>', message)
            return request.render("ALTANMYA_BUYCOURSES_SY_MTN.portal_insurance_messageC",
                                  {'main_title': _("Can't Make Request"),
                                   'alert_type': "info",
                                   'message': message_body,
                                   'page_url': "/slides",
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.ONE_WAITING:
            return request.render("ALTANMYA_BUYCOURSES_SY_MTN.portal_insurance_messageC",
                                  {'main_title': _("One Waiting Request"),
                                   'alert_type': "info",
                                   'message': message_body,
                                   'page_url': "/slides",
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.BOTH_WAITING:
            return request.render("ALTANMYA_BUYCOURSES_SY_MTN.portal_insurance_messageC",
                                  {'main_title': _("Two Waiting Request"),
                                   'alert_type': "info",
                                   'message': message_body,
                                   'page_url': "/slides",
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.EXCEPTION:
            return request.render('ALTANMYA_BUYCOURSES_SY_MTN.portal_insurance_messageC',
                                  {'main_title': _('An Error has happened in your payment request!'),
                                   'alert_type': 'danger',
                                   'message': message_body,
                                   'page_url': '/my',
                                   'page_url_message': _('Go back to my account')
                                   })
        elif message == UserInsuranceState.PAID:
            return request.render('ALTANMYA_BUYCOURSES_SY_MTN.portal_insurance_messageC',
                                  {'main_title': _('Paid Successfully!'),
                                   'alert_type': 'success',
                                   'message': message_body,
                                   'page_url':  f'/payment/status',
                                   'page_url_message': _('go for next step')
                                   })
        elif message == UserInsuranceState.ACCESS_DENIED:
            return request.render('ALTANMYA_BUYCOURSES_SY_MTN.portal_insurance_messageC',
                                  {'main_title': _('Access Denied!'),
                                   'alert_type': 'danger',
                                   'message': message_body,
                                   'page_url': '/slides',
                                   'page_url_message': _('Go back to my requests')
                                   })

    @http.route('/payment_operationC/<string:ms_type>/<int:sale_order_id>', methods=['GET', 'POST'], type='http',
                auth='user', website=True,
                csrf=False)
    def payment_operation(self, ms_type, sale_order_id, **post):
        print('sale_order_id==>', sale_order_id)
        print('ms_type==>', ms_type)
        if post and request.httprequest.method == 'POST':
            # prepare payment request parameters
            payment_method = request.env['in.payment.method'].search([('ms_type', '=', post.get('payment_type'))])
            post_ms_type = post.get('payment_type')
            ins_req = request.env['sale.order'].sudo().search([
                ('id', '=', sale_order_id)])
            print('ins_req==>', ins_req.amount_total)
            if not ins_req.id:
                return self._render_status_message(UserInsuranceState.EXCEPTION,
                                                   _('This payment course request does not exist'))
            customer_number = post.get('phone_number')
            customer_number = ''.join([c for c in customer_number if c in string.digits])
            # amount = ins_req.insurance_type_id.insurance_fees
            amount = math.ceil(ins_req.amount_total)
            merchant_number = payment_method.mobile
            # This function generates an id with 32 characters
            transaction_id = str(uuid.uuid4())
            while transaction_id in request.env['in.payment.operation'].mapped('transaction_id'):
                transaction_id = str(uuid.uuid4())
            print('customer_number==>', customer_number)
            print('amount==>', amount)
            print('merchant_number==>', merchant_number)
            print('transaction_id==>', transaction_id)
            print('payment_method.id==>', payment_method.id)

            # GET TOKEN FOR MERCHANT ACCOUNT
            payment_operation = request.env['in.payment.operation'].sudo().create({
                'state': 'pending',
                'transaction_time': datetime.now(),
                'amount': amount,
                'merchant_MSISDN': merchant_number,
                'customer_MSISDN': customer_number,
                'transaction_id': transaction_id,
                'payment_method_id': payment_method.id
            })

            company = request.env.company
            currency_id = company.currency_id.id
            print('currency_id==>', currency_id)
            #
            # Create a new payment provider record
            new_provider_values = {
                'name': ms_type,  # Replace with the appropriate provider name
                'code': 'demo',  # Replace with the appropriate provider code
                'state': 'test',  # Set the appropriate state ('disabled', 'enabled', 'test')
                'company_id': company.id,  # Set the appropriate state ('disabled', 'enabled', 'test')
                'module_state': 'installed',
                # Add other fields as needed based on your payment.provider model definition
            }
            payment_provider = request.env['payment.provider'].sudo().create(new_provider_values)
            print('***=>**', payment_provider)
            # Now, you can get the provider_id from the created payment provider record

            provider_id = payment_provider.id
            partner_id = ins_req.partner_id.id
            print('partner_id==**>', partner_id)
            transaction_values = {
                'provider_id': provider_id,
                'company_id': company.id,
                'reference': transaction_id,  # Use your appropriate reference value here
                'amount': amount,  # Use your appropriate amount value here
                'currency_id': currency_id,  # Use your appropriate currency_id value here
                'provider_code': payment_provider.code,
                'partner_id': partner_id,
            }
            #
            # Create the payment.transaction record
            payment_transaction = request.env['payment.transaction'].sudo().create(transaction_values)
            print('payment_transaction==>**', payment_transaction)
            # ins_req.sudo().write({'payment_operation_id': payment_operation.id})

            if post_ms_type == 'syriatel':
                print('syriatel===syriatel==>')
                sy_cash_api = SyriatelCashApi()
                token = sy_cash_api.get_token(payment_method.merchant_username, payment_method.merchant_password)
                print('tokensy===tokensy==>', token)
                if token:
                    payment_operation.sudo().write({'token': token})
                    try:
                        # amount = str(amount)[0:str(amount).index('.')]
                        amount = str(amount)
                        print('amountsyr==>', amount)
                        payment_request = sy_cash_api.payment_request(customer_number, merchant_number, "1",
                                                                      transaction_id, token)
                        print('payment_request==>', payment_request)
                        if payment_request:
                            print('true')
                            return request.redirect(f"/payment_confirmationC/{payment_operation.id}/{ins_req.id}")
                            print('done')
                    except Exception as e:
                        print('except')
                        return self._render_status_message(UserInsuranceState.EXCEPTION, str(e))

            elif post_ms_type == 'mtn':
                print('mtn===mtn==>')
                mtn_cash_api = MTNCashApi()
                merchant_num = '963' + payment_method.mobile[1:]
                token = mtn_cash_api.authenticate_merchant(payment_method.merchant_username,
                                                           payment_method.merchant_password,
                                                           merchant_num)
                print('token===tokenmtn==>', token)
                if token:
                    payment_operation.sudo().write({'token': token})
                    try:
                        customer_number = '963' + customer_number[1:]
                        payment_request = mtn_cash_api.payment_request_init(token, customer_number, amount,
                                                                            transaction_id)
                        if payment_request:
                            return request.redirect(f"/payment_confirmationC/{payment_operation.id}/{ins_req.id}")
                    except Exception as e:
                        return self._render_status_message(UserInsuranceState.EXCEPTION, str(e))

                return self._render_status_message(UserInsuranceState.EXCEPTION, _('Something wrong has happened!'))
        else:
            if sale_order_id is not None:
                rec = request.env['sale.order'].sudo().search([('id', '=', sale_order_id)])
                print('rec==>', rec.amount_total)
                # if rec.id:
                #     if rec.request_owner_id.id != request.env.user.id:
                #         return request.not_found()
                # else:
                #     return request.not_found()

            referrer = request.httprequest.referrer
            print('referrer==>', referrer)
            if '/payment_methods' not in str(referrer):
                print('good')
                return self._render_status_message(UserInsuranceState.ACCESS_DENIED, _('You can not access this page!'))
                pass
            # If the user has an outdated insurance request or doesn't have one, allow him to access this template.
            return request.render('ALTANMYA_BUYCOURSES_SY_MTN.portal_user_payment_operationC', {'ms_type': ms_type})

    @http.route('/payment_confirmationC/<int:po_id>/<int:so_id>', methods=['GET', 'POST'], type='http', auth='user', website=True,
                csrf=False)
    def payment_confirmation(self, po_id,so_id, **post):
        if post and request.httprequest.method == 'POST':
            print('===>so_id==>',so_id)
            otp_code = post.get('otp_code')
            post_po_id = post.get('payment_operation_id')
            payment_operation_id = request.env['in.payment.operation'].sudo().search([('id', '=', int(post_po_id))])
            if payment_operation_id.payment_method_id.ms_type == 'mtn':
                mtn_cash_api = MTNCashApi()
                try:
                    payment_confirmation = mtn_cash_api.do_payment(payment_operation_id.token,
                                                                   otp_code,
                                                                   payment_operation_id.transaction_id)
                    if payment_confirmation:
                        payment_operation_id.write({'state': 'paid'})
                        insurance_request = request.env['insurance.request'].sudo().search(
                            [('payment_operation_id', '=', payment_operation_id.id)])
                        insurance_request.sudo().write({'state': 'paid'})
                        return self._render_status_message(UserInsuranceState.PAID,
                                                           message_body=_(
                                                               'Your payment request has been done successfully!'))
                except Exception as e:
                    payment_operation_id.sudo().unlink()
                    return self._render_status_message(UserInsuranceState.EXCEPTION,
                                                       _(f"An error occurred during payment confirmation: {e}"))

            elif payment_operation_id.payment_method_id.ms_type == 'syriatel':
                sy_cash_api = SyriatelCashApi()
                try:
                    payment_confirmation = sy_cash_api.payment_confirmation(otp_code,
                                                                            payment_operation_id.merchant_MSISDN,
                                                                            payment_operation_id.transaction_id,
                                                                            payment_operation_id.token)
                    if payment_confirmation:
                        payment_operation_id.sudo().write({'state': 'paid'})
                        insurance_request = request.env['insurance.request'].sudo().search(
                            [('payment_operation_id', '=', payment_operation_id.id)])
                        insurance_request.sudo().write({'state': 'paid'})
                        return self._render_status_message(UserInsuranceState.PAID, message_body=_(
                            'Your payment request has been done successfully!'),soo_id=so_id)
                except Exception as e:
                    post['error'] = e.args[0]
                    return request.render('ALTANMYA_BUYCOURSES_SY_MTN.portal_user_payment_otp_operationC', post)

        else:
            referrer = request.httprequest.referrer
            if '/payment_operation' not in str(referrer):
                return self._render_status_message(UserInsuranceState.ACCESS_DENIED, _('You can not access this page!'))

            # If the user has an outdated insurance request or doesn't have one, allow him to access this page.
            payment_operation_id = request.env['in.payment.operation'].sudo().search([('id', '=', po_id)])
            return request.render('ALTANMYA_BUYCOURSES_SY_MTN.portal_user_payment_otp_operationC', {
                'payment_operation_id': po_id,
                'ms_type': payment_operation_id.payment_method_id.ms_type,
            })

    @http.route('/resend_otp/<int:po_id>', methods=['GET'], type='http', auth='user', website=True)
    def resend_otp(self, po_id):
        payment_operation_id = request.env['in.payment.operation'].sudo().browse(po_id)
        sy_cash_api = SyriatelCashApi()
        try:
            result = sy_cash_api.resend_OTP(payment_operation_id.merchant_MSISDN,
                                            payment_operation_id.transaction_id,
                                            payment_operation_id.token)
            return result
        except Exception as e:
            raise e
