from datetime import datetime
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class InsuranceCardPortal(CustomerPortal):
    @route(['/my', '/my/home'], type='http', auth="user", website=True)
    def home(self, **kw):
        values = self._prepare_portal_layout_values()
        insurance_request = request.env['insurance.request'].search([('request_owner_id', '=', request.env.user.id),
                                                                     ('state', '=', 'paid')], limit=1, order='id desc')
        if insurance_request:
            values.update({
                'has_paid_ins_request': True
            })
        else:
            values.update({
                'has_paid_ins_request': False
            })
        return request.render("portal.portal_my_home", values)

    @route(['/my/insurance_card/<int:insurance_request_id>'], type='http', auth="user", website=True)
    def insurance_card(self, insurance_request_id):

        if insurance_request_id is not None:
            rec = request.env['insurance.request'].sudo().search([('id', '=', insurance_request_id)])
            if rec.id:
                if rec.request_owner_id.id != request.env.user.id:
                    return request.not_found()
            else:
                return request.not_found()

        ins_req = request.env['insurance.request'].sudo().search([('request_owner_id', '=', request.env.user.id),
                                                                  ('id', '=', insurance_request_id)])
        if ins_req.insurance_number != '' and ins_req.insurance_expiration_date and ins_req.insurance_expiration_date > datetime.today().date():
            return request.render("NUSS_Students_Insurance.insurance_card", {
                'card': True,
                'owner': ins_req.first_name + ' ' + ins_req.second_name,
                'insurance_number': ins_req.insurance_number,
                'insurance_expiration_date': ins_req.insurance_expiration_date,
                'birthday': ins_req.birthday,
                'insurance_type': ins_req.insurance_type_id.name,
                'emc': ins_req.expenses_company_id.name
            })
        else:
            return request.render("NUSS_Students_Insurance.insurance_card", {
                'card': False
            })


