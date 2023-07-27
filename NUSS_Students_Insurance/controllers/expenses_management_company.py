from odoo import http, _
from odoo.http import request
import logging

logger = logging.getLogger(__name__)
import base64


class EMCs(http.Controller):
    @http.route('/expenses_management_companies', methods=['GET'], type='http', auth='public', website=True)
    def insurance_request(self):
        expenses_management_companies = request.env['expenses.management.company'].search([])
        values = {
            'headers': [_('Company'), _('Communication Numbers'), _('Medical Network File'),
                        _('Medical Network Website')],
            'emcs_record_values': []
        }
        for emc in expenses_management_companies:
            record_values = {'name': emc.name, 'image': emc.image_256,
                             'numbers': [('qp', emc.quadruple_phone), ('ph', emc.phone), ('mn', emc.mobile_phone)],
                             'website': emc.website, 'file_link': emc.id}
            values['emcs_record_values'].append(record_values)

        return request.render('NUSS_Students_Insurance.expenses_management_companies', values)

    @http.route(["/expenses_management_companies/download/<int:emc_id>"],
                type='http', methods=['GET'], auth='user')
    def download_file(self, emc_id=None):
        emc = request.env['expenses.management.company'].browse(emc_id)
        if emc.medical_network_file:
            binary_data = emc.medical_network_file
            filename = emc.medical_network_filename
            headers = [
                ('Content-Disposition', 'attachment; filename="%s"' % filename),
                ('Content-Length', len(binary_data)),
                ('Content-Type', 'application/octet-stream'),
            ]
            return request.make_response(base64.b64decode(binary_data.decode("utf-8")), headers=headers)
        else:
            return request.redirect('/file_not_found')

    @http.route('/file_not_found', type='http', auth='public', website=True, sitemap=False)
    def request_file_not_found(self):
        return request.render('NUSS_Students_Insurance.portal_insurance_message',
                              {'main_title': _("File Not Found"),
                               'alert_type': 'danger',
                               'message': _('Sorry... The medical network file is not available at the current time.'),
                               'page_url': '/expenses_management_companies',
                               'page_url_message': _('Go to the previous page'),
                               })
