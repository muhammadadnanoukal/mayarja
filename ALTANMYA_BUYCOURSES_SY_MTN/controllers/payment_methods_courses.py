from odoo import http, _
from odoo.http import request
import logging
logger = logging.getLogger(__name__)


class PaymentMethods(http.Controller):
    @http.route(['/payment_methods_c', '/payment_methods_c/<int:sale_order_id>'], methods=['GET'], type='http', auth='user', website=True)
    def payment_methods(self, sale_order_id=None, **kwargs):

        # if insurance_request_id is not None:
        #     rec = request.env['insurance.request'].sudo().search([('id', '=', insurance_request_id)])
        #     if rec.id:
        #         if rec.request_owner_id.id != request.env.user.id:
        #             return request.not_found()
        #     else:
        #         return request.not_found()

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
                    e_payment_url = f'/payment_operationC/mtn/{sale_order_id}'
                elif pm.ms_type == 'syriatel':
                    e_payment_url = f'/payment_operationC/syriatel/{sale_order_id}'

            # if self._check_for_user(insurance_request_id) != 'approved':
            #     e_payment_url = ''

            record_values = {
                'image': pm.image_256,
                'account_number': pm.account_number,
                'e_payment_url': e_payment_url
            }
            values['pms_record_values'].append(record_values)
            print('values==>',values)
        return request.render('ALTANMYA_BUYCOURSES_SY_MTN.new_tst', values)


