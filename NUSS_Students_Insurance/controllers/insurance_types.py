from odoo import http, _
from odoo.http import request
import logging
logger = logging.getLogger(__name__)
from werkzeug.wrappers import Response
import base64


class InsuranceTypes(http.Controller):
    @http.route('/insurance_types', methods=['GET'], type='http', auth='public', website=True)
    def insurance_types(self):
        insurance_types = request.env['insurance.type'].search([])
        values = {
            'headers': [_('Insurance Type'), _('Coverages'), _('Financial Limits'), _('Insurance Fees')],
            'in_types_record_values': []
        }
        for insurance_type in insurance_types:
            record_values = {'name': insurance_type.name,
                             'coverages': insurance_type.coverages,
                             'financial_limit': insurance_type.financial_limit,
                             'insurance_fees': insurance_type.insurance_fees
                             }
            values['in_types_record_values'].append(record_values)

        return request.render('NUSS_Students_Insurance.insurance_type_template', values)

