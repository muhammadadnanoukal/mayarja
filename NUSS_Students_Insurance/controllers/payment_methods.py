from odoo import http, _
from odoo.http import request
import logging
from .request_states import UserInsuranceState
logger = logging.getLogger(__name__)


class PaymentMethods(http.Controller):
    @http.route(['/payment_methods', '/payment_methods/<int:insurance_request_id>'], methods=['GET'], type='http', auth='user', website=True)
    def payment_methods(self, insurance_request_id=None, **kwargs):

        if insurance_request_id is not None:
            rec = request.env['insurance.request'].sudo().search([('id', '=', insurance_request_id)])
            if rec.id:
                if rec.request_owner_id.id != request.env.user.id:
                    return request.not_found()
            else:
                return request.not_found()

        payment_methods = request.env['in.payment.method'].search([])
        values = {
            'headers': [_('Bank/Company'), _('Link')],
            'pms_record_values': []
        }
        for pm in payment_methods:
            e_payment_url = ''
            e_payment_link = ''
            if pm.type == 'bank':
                e_payment_link = pm.e_payment_link

            else:
                if pm.ms_type == 'mtn':
                    e_payment_url = f'/payment_operation/mtn/{insurance_request_id}'
                elif pm.ms_type == 'syriatel':
                    e_payment_url = f'/payment_operation/syriatel/{insurance_request_id}'

            if self._check_for_user(insurance_request_id) != 'approved':
                e_payment_url = ''

            record_values = {
                'image': pm.image_256,
                'account_number': pm.account_number,
                'e_payment_url': e_payment_url
            }
            values['pms_record_values'].append(record_values)

        return request.render('NUSS_Students_Insurance.payment_methods', values)

    def _check_for_user(self, insurance_request_id):
        env_user = request.env.user.id
        env_user_requests = request.env['insurance.request'].search([('request_owner_id', '=', env_user),
                                                                     ('id', '=', insurance_request_id)])
        if len(env_user_requests) == 0:
            return UserInsuranceState.NO_REQUEST
        else:
            newest_request = env_user_requests[0]
            return newest_request.state