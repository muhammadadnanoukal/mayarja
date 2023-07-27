from odoo import http, _
from odoo.http import request
import base64
from datetime import datetime
import json
import string
import uuid
from .syriatel_cash_api import SyriatelCashApi
from .mtn_cash_api import MTNCashApi
from .request_states import UserInsuranceState


class InsuranceRequest(http.Controller):
    @http.route('/insurance_request', methods=['GET', 'POST'], type='http', auth='user', website=True, csrf=False)
    def insurance_request(self, **post):
        if post and request.httprequest.method == 'POST':
            insurance_request = request.env['insurance.request'].sudo().create({
                'request_owner_id': request.env.user.id,
                'university_id_number': post.get('university_id_number'),
                'academic_year': post.get('academic_year'),
                'faculty_id': post.get('collage'),
                'university_id': post.get('university'),
                'place_of_accommodation': post.get('accommodation_place'),
                'university_card': base64.b64encode(request.httprequest.files.get('university_card').read()),
                'id_card_back': base64.b64encode(request.httprequest.files.get('id_card_back').read()),
                'id_card_front': base64.b64encode(request.httprequest.files.get('id_card_front').read()),
                'id_number': post.get('id_number'),
                'social_status': post.get('social_status'),
                'birthday': datetime.strptime(post.get('birthday'), '%Y-%m-%d').date(),
                'gender': post.get('gender'),
                'mo_name': post.get('mother_name'),
                'fa_name': post.get('father_name'),
                'insurance_type_id': post.get('insurance_type'),
                'second_name': post.get('last_name'),
                'first_name': post.get('first_name'),
                'student_phone': post.get('phone_number'),
                'expenses_company_id': request.env['expenses.management.company'].sudo().browse(1).id
            })
            request.env['approval.request'].sudo().search([('insurance_request_id', '=', insurance_request.id)],
                                                          order='id desc', limit=1).action_confirm()
            # Use the form data to create or update records in your Odoo models
            files = [
                request.httprequest.files.get('id_card_front'),
                request.httprequest.files.get('id_card_back'),
                request.httprequest.files.get('university_card')
            ]
            if len(files) > 0:
                for file in files:
                    file_data = file.read()
                    file_name = file.filename
                    request.env['ir.attachment'].sudo().create({
                        'datas': base64.b64encode(file_data),
                        'name': file_name,
                        'res_model': 'insurance.request',
                    })
            return request.redirect('/my/insurance_requests')
        else:
            user_request_status = self._check_for_user()
            return self.handle_status(user_request_status)

    def handle_status(self, user_request_status):
        if user_request_status in [UserInsuranceState.NO_REQUEST, UserInsuranceState.REQUEST_TYPE_1, UserInsuranceState.REQUEST_TYPE_2]:
            return self._render_insurance_form(user_request_status)
        elif user_request_status == UserInsuranceState.BOTH_PAYMENT_REQUIRED:
            return self._render_status_message(message=user_request_status,
                                               message_body=_("You have insurance fees for two requests need to be paid!"))
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

    def _render_status_message(self, message, message_body):
        if message in [UserInsuranceState.PAYMENT_REQUIRED, UserInsuranceState.BOTH_PAYMENT_REQUIRED]:
            return request.render("NUSS_Students_Insurance.portal_insurance_message",
                                  {'main_title': _("Payment Required"),
                                   'alert_type': "success",
                                   'message': message_body,
                                   'page_url': '/my/insurance_requests',
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.CANT_MAKE_REQUEST:
            return request.render("NUSS_Students_Insurance.portal_insurance_message",
                                  {'main_title': _("Can't Make Request"),
                                   'alert_type': "info",
                                   'message': message_body,
                                   'page_url': "/my/insurance_requests",
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.ONE_WAITING:
            return request.render("NUSS_Students_Insurance.portal_insurance_message",
                                  {'main_title': _("One Waiting Request"),
                                   'alert_type': "info",
                                   'message': message_body,
                                   'page_url': "/my/insurance_requests",
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.BOTH_WAITING:
            return request.render("NUSS_Students_Insurance.portal_insurance_message",
                                  {'main_title': _("Two Waiting Request"),
                                   'alert_type': "info",
                                   'message': message_body,
                                   'page_url': "/my/insurance_requests",
                                   'page_url_message': _("Go back to my requests"),
                                   })
        elif message == UserInsuranceState.EXCEPTION:
            return request.render('NUSS_Students_Insurance.portal_insurance_message',
                                  {'main_title': _('An Error has happened in your payment request!'),
                                   'alert_type': 'danger',
                                   'message': message_body,
                                   'page_url': '/my',
                                   'page_url_message': _('Go back to my account')
                                   })
        elif message == UserInsuranceState.PAID:
            return request.render('NUSS_Students_Insurance.portal_insurance_message',
                                  {'main_title': _('Paid Successfully!'),
                                   'alert_type': 'success',
                                   'message': message_body,
                                   'page_url': '/my/insurance_requests',
                                   'page_url_message': _('Go back to my requests')
                                   })
        elif message == UserInsuranceState.ACCESS_DENIED:
            return request.render('NUSS_Students_Insurance.portal_insurance_message',
                                  {'main_title': _('Access Denied!'),
                                   'alert_type': 'danger',
                                   'message': message_body,
                                   'page_url': '/my/insurance_requests',
                                   'page_url_message': _('Go back to my requests')
                                   })

    def _render_insurance_form(self, user_request_status):
        values = self._prepare_insurance_request_values(user_request_status)
        return request.render('NUSS_Students_Insurance.portal_user_insurance_request',
                              {'ay_options': values.get('ay_options'),
                               'poa_options': values.get('poa_options'),
                               'ss_options': values.get('ss_options'),
                               'gender_options': values.get('gender_options'),
                               'insurance_types': values.get('insurance_types'),
                               'universities': values.get('universities'),
                               'collages': values.get('collages')
                               })

    def _prepare_insurance_request_values(self, user_request_status):
        options = http.request.env['insurance.request'].fields_get(
            allfields=['academic_year', 'social_status', 'gender', 'place_of_accommodation'])
        poa_options = options['place_of_accommodation']['selection']
        ay_options = options['academic_year']['selection']
        ss_options = options['social_status']['selection']
        gender_options = options['gender']['selection']
        domain = []
        if user_request_status == UserInsuranceState.REQUEST_TYPE_1:
            domain = [('insurance_type', '=', 'type_1')]
        elif user_request_status == UserInsuranceState.REQUEST_TYPE_2:
            domain = [('insurance_type', '=', 'type_2')]
        insurance_types_recs = request.env['insurance.type'].search(domain)
        insurance_types_names = insurance_types_recs.mapped('name')
        insurance_types_ids = insurance_types_recs.mapped('id')

        insurance_types = [(_id, name) for name, _id in zip(insurance_types_names, insurance_types_ids)]

        universities_recs = request.env['in.university'].search([('type', '=', 'university')])
        universities_names = universities_recs.mapped('name')
        universities_ids = universities_recs.mapped('id')

        universities = [(_id, name) for name, _id in zip(universities_names, universities_ids)]

        collages_recs = request.env['in.university'].search(
            [('parent_id', '=', universities_ids[0]), ('type', '=', 'collage')])
        collages_names = collages_recs.mapped('name')
        collages_ids = collages_recs.mapped('id')

        collages = [(_id, name) for name, _id in zip(collages_names, collages_ids)]

        return {
            'poa_options': poa_options,
            'ay_options': ay_options,
            'ss_options': ss_options,
            'gender_options': gender_options,
            'insurance_types': insurance_types,
            'universities': universities,
            'collages': collages
        }

    def _check_for_user(self):
        env_user = request.env.user.id
        request_type_1 = request.env['insurance.request'].search([('request_owner_id', '=', env_user),
                                                                  ('insurance_type_id.insurance_type', '=', 'type_1')],
                                                                 order='id desc', limit=1)
        request_type_2 = request.env['insurance.request'].search([('request_owner_id', '=', env_user),
                                                                  ('insurance_type_id.insurance_type', '=', 'type_2')],
                                                                 order='id desc', limit=1)
        if request_type_1.id and request_type_2.id:
            states = [request_type_1.state, request_type_2.state]

            if states[0] == 'approved' and states[1] == 'approved':
                return UserInsuranceState.BOTH_PAYMENT_REQUIRED

            if all(state in ['approved', 'waiting', 'paid'] for state in states) \
                    and not all(state in ['waiting', 'paid'] for state in states):
                return UserInsuranceState.PAYMENT_REQUIRED

            elif (states[0] in ['approved', 'paid', 'waiting']) and \
                 (states[1] in ['expired', 'refused']):
                return UserInsuranceState.REQUEST_TYPE_2

            elif (states[0] in ['refused', 'expired']) and \
                 (states[1] in ['approved', 'paid', 'waiting']):
                return UserInsuranceState.REQUEST_TYPE_1

            elif all(state in ['expired', 'refused'] for state in states):
                return UserInsuranceState.NO_REQUEST

            elif states[0] == 'paid' and states[1] == 'paid':
                return UserInsuranceState.CANT_MAKE_REQUEST

            elif (states[0] == 'paid' and states[1] == 'waiting') or \
                 (states[0] == 'waiting' and states[1] == 'paid'):
                return UserInsuranceState.ONE_WAITING

            elif states[0] == 'waiting' and states[1] == 'waiting':
                return UserInsuranceState.BOTH_WAITING

        elif request_type_1.id and not request_type_2.id:
            if request_type_1.state in ['waiting', 'approved', 'paid']:
                return UserInsuranceState.REQUEST_TYPE_2
            elif request_type_1.state in ['expired', 'refused']:
                return UserInsuranceState.NO_REQUEST

        elif request_type_2.id and not request_type_1.id:
            if request_type_2.state in ['waiting', 'approved', 'paid']:
                return UserInsuranceState.REQUEST_TYPE_1
            elif request_type_2.state in ['expired', 'refused']:
                return UserInsuranceState.NO_REQUEST

        else:
            return UserInsuranceState.NO_REQUEST

    @http.route('/payment_operation/<string:ms_type>/<int:insurance_request_id>', methods=['GET', 'POST'], type='http', auth='user', website=True,
                csrf=False)
    def payment_operation(self, ms_type, insurance_request_id, **post):
        if post and request.httprequest.method == 'POST':
            # prepare payment request parameters
            payment_method = request.env['in.payment.method'].search([('ms_type', '=', post.get('payment_type')),
                                                                      ('active_account', '=', True)])
            post_ms_type = post.get('payment_type')
            ins_req = request.env['insurance.request'].sudo().search([
                ('name', '=', post.get('insurance_sequence_code')),
                ('id', '=', insurance_request_id)])
            if not ins_req.id:
                return self._render_status_message(UserInsuranceState.EXCEPTION,
                                                   _('The insurance request does not exist'))
            customer_number = post.get('phone_number')
            customer_number = ''.join([c for c in customer_number if c in string.digits])
            amount = ins_req.insurance_type_id.insurance_fees
            merchant_number = payment_method.mobile
            # This function generates an id with 32 characters
            transaction_id = str(uuid.uuid4())
            while transaction_id in request.env['in.payment.operation'].mapped('transaction_id'):
                transaction_id = str(uuid.uuid4())

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
            ins_req.sudo().write({'payment_operation_id': payment_operation.id})

            if post_ms_type == 'syriatel':
                sy_cash_api = SyriatelCashApi()
                token = sy_cash_api.get_token(payment_method.merchant_username, payment_method.merchant_password)
                if token:
                    payment_operation.sudo().write({'token': token})
                    try:
                        # amount = str(amount)[0:str(amount).index('.')]
                        amount = str(amount)
                        payment_request = sy_cash_api.payment_request(customer_number, merchant_number, amount,
                                                                      transaction_id, token)
                        if payment_request:
                            return request.redirect(f"/payment_confirmation/{payment_operation.id}")
                    except Exception as e:
                        return self._render_status_message(UserInsuranceState.EXCEPTION, str(e))

            elif post_ms_type == 'mtn':
                mtn_cash_api = MTNCashApi()
                merchant_num = '963' + payment_method.mobile[1:]
                token = mtn_cash_api.authenticate_merchant(payment_method.merchant_username,
                                                           payment_method.merchant_password,
                                                           merchant_num)
                if token:
                    payment_operation.sudo().write({'token': token})
                    try:
                        customer_number = '963' + customer_number[1:]
                        payment_request = mtn_cash_api.payment_request_init(token, customer_number, amount,
                                                                            transaction_id)
                        if payment_request:
                            return request.redirect(f"/payment_confirmation/{payment_operation.id}")
                    except Exception as e:
                        return self._render_status_message(UserInsuranceState.EXCEPTION, str(e))

            return self._render_status_message(UserInsuranceState.EXCEPTION, _('Something wrong has happened!'))
        else:
            if insurance_request_id is not None:
                rec = request.env['insurance.request'].sudo().search([('id', '=', insurance_request_id)])
                if rec.id:
                    if rec.request_owner_id.id != request.env.user.id:
                        return request.not_found()
                else:
                    return request.not_found()

            referrer = request.httprequest.referrer
            if '/payment_methods' not in str(referrer):
                return self._render_status_message(UserInsuranceState.ACCESS_DENIED, _('You can not access this page!'))

            # If the user has an outdated insurance request or doesn't have one, allow him to access this template.
            return request.render('NUSS_Students_Insurance.portal_user_payment_operation', {'ms_type': ms_type})

    @http.route('/payment_confirmation/<int:po_id>', methods=['GET', 'POST'], type='http', auth='user', website=True,
                csrf=False)
    def payment_confirmation(self, po_id, **post):
        if post and request.httprequest.method == 'POST':
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
                        return self._render_status_message(UserInsuranceState.PAID,
                                                           message_body=_(
                                                               'Your payment request has been done successfully!'))
                except Exception as e:
                    post['error'] = e.args[0]
                    return request.render('NUSS_Students_Insurance.portal_user_payment_otp_operation', post)

        else:
            referrer = request.httprequest.referrer
            if '/payment_operation' not in str(referrer):
                return self._render_status_message(UserInsuranceState.ACCESS_DENIED, _('You can not access this page!'))

            # If the user has an outdated insurance request or doesn't have one, allow him to access this page.
            payment_operation_id = request.env['in.payment.operation'].sudo().search([('id', '=', po_id)])
            return request.render('NUSS_Students_Insurance.portal_user_payment_otp_operation', {
                'payment_operation_id': po_id,
                'ms_type': payment_operation_id.payment_method_id.ms_type,
            })

    def _insurance_expired(self):
        insurance_request_id = request.env['insurance.request'].sudo().search(
            [('request_owner_id', '=', request.env.user.id)], order='id desc', limit=1)
        if len(insurance_request_id) != 0:
            if insurance_request_id.insurance_expiration_date:
                if insurance_request_id.insurance_expiration_date < datetime.today().date():
                    return True
        return False

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
